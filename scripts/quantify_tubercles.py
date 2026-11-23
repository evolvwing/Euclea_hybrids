"""Estimate the color of projecting scoli in standardized larval photographs."""
from base64 import b64encode
from struct import pack

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

WIDTH, HEIGHT = 168, 280


def centerline(warmth):
    # Align the paired yellow/orange longitudinal stripes, allowing a curved body.
    smoothed = ndi.gaussian_filter(warmth, (8, 2))
    candidates = np.arange(42, 126)
    best = None
    for radius in range(8, 30, 3):
        a, b = smoothed[:, candidates - radius], smoothed[:, candidates + radius]
        signal = np.minimum(a, b) + 0.45 * np.maximum(a, b)
        signal -= 0.25 * smoothed[:, candidates]
        signal -= 0.012 * ((candidates - WIDTH / 2) / 22) ** 2
        score = signal[0]
        trace = []
        offsets = np.array([-2, -1, 0, 1, 2])
        previous = np.clip(np.arange(len(candidates)) + offsets[:, None], 0, len(candidates) - 1)
        for row in signal[1:]:
            paths = score[previous] - np.abs(offsets[:, None]) * 0.022
            choice = np.argmax(paths, axis=0)
            trace.append(previous[choice, np.arange(len(candidates))])
            score = row + np.max(paths, axis=0)
        idx = np.argmax(score)
        if best is None or score[idx] > best[0]:
            path = [idx]
            for previous_row in reversed(trace):
                path.append(previous_row[path[-1]])
            best = (score[idx], ndi.gaussian_filter1d(candidates[path[::-1]].astype(float), 6), radius)
    return best[1:]


def directional_contrast(chroma):
    # Projections have a narrow cross-section. A directional ridge filter
    # suppresses broad color fields, including the longitudinal body stripes.
    y, x = np.mgrid[-9:10, -9:10]
    response = np.zeros_like(chroma)
    vertical = np.zeros_like(chroma)
    for degrees in (-55, -30, 0, 30, 55, 90):
        angle = np.deg2rad(degrees)
        along = x * np.cos(angle) + y * np.sin(angle)
        across = -x * np.sin(angle) + y * np.cos(angle)
        for sigma in (1.3, 2.4):
            narrow = np.exp(-0.5 * ((along / 3.3) ** 2 + (across / sigma) ** 2))
            wide = np.exp(-0.5 * ((along / 3.3) ** 2 + (across / (sigma * 2.3)) ** 2))
            ridge = ndi.convolve(chroma, narrow / narrow.sum() - wide / wide.sum(), mode='nearest')
            target = vertical if degrees == 90 else response
            np.maximum(target, ridge, out=target)
    return response, vertical


def measure(path):
    with Image.open(path) as image:
        image = image.convert('RGB').resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    rgb = np.asarray(image, dtype=np.float32) / 255
    hue, saturation, value = np.moveaxis(np.asarray(image.convert('HSV')) / 255, -1, 0)
    r, g, b = np.moveaxis(rgb, -1, 0)
    warmth = np.maximum(np.minimum(r, g) - b, 0)
    axis, radius = centerline(warmth)
    y, x = np.ogrid[:HEIGHT, :WIDTH]
    distance = abs(x - axis[:, None])
    lateral = (distance >= radius + 6) & (distance < radius + 32)
    end_rows = (y < 45) | (y > HEIGHT - 45)
    ends = end_rows & (distance > 11) & (distance < radius + 17)
    margin = lateral | ends
    chroma = np.maximum(np.maximum(r, g) - b, 0)
    ridge, vertical = directional_contrast(chroma)
    colored = (saturation >= .36) & (value >= .23)
    orange = colored & ((hue <= .106) | (hue >= .94)) & (r - g >= .065)
    yellow_green = colored & (hue > .106) & (hue <= .26) & (warmth >= .095)
    projecting = (ridge >= .031) & ((ridge >= vertical * 1.12) | (end_rows & (ridge >= vertical * .84)))
    # Color that persists longitudinally at the same body-relative offset is
    # likely to be a body band. Follow the fitted axis when comparing rows.
    def longitudinal(color):
        band = np.zeros((HEIGHT, WIDTH), dtype=np.uint8)
        smoothed_color = ndi.maximum_filter1d(color, 3, axis=1)
        for offset in (-16, -10, 10, 16):
            row = np.clip(y + offset, 0, HEIGHT - 1)
            col = np.clip(np.rint(x + axis[row] - axis[y]).astype(int), 0, WIDTH - 1)
            band += smoothed_color[row, col]
        return band >= 3

    selected = ((orange & ~longitudinal(orange)) | yellow_green) & margin & projecting
    labels, count = ndi.label(selected, structure=np.ones((3, 3), dtype=int))
    sizes = np.bincount(labels.ravel(), minlength=count + 1)
    selected &= sizes[labels] >= 6
    rejected = np.zeros(count + 1, dtype=bool)
    for i, bounds in enumerate(ndi.find_objects(labels), 1):
        if bounds:
            height, width = (sl.stop - sl.start for sl in bounds)
            rejected[i] = height > 20 and height > width * 1.7
    selected &= ~rejected[labels]
    left, right = selected & (x < axis[:, None]), selected & (x >= axis[:, None])
    def occupied_rows(side):
        return sum(block.sum() >= 15 for block in np.array_split(side, 7))
    coverage = (
        min(left.sum(), right.sum()) >= 85
        and min(occupied_rows(left), occupied_rows(right)) >= 3
        and np.ptp(axis) <= 54
    )
    colors = np.where(selected, np.where(orange, 1, 2), 0).astype(np.uint8)
    return colors, (int((colors == 1).sum()), int((colors == 2).sum())), coverage


def encode_mask(colors):
    """Encode runs as little-endian start offsets, lengths and color classes."""
    flat = colors.reshape(-1)
    changes = np.flatnonzero(np.diff(flat, prepend=0, append=0))
    encoded = bytearray()
    for start, end in zip(changes, changes[1:]):
        if flat[start]:
            for offset in range(int(start), int(end), 255):
                encoded.extend(pack('<HBB', offset, min(int(end) - offset, 255), flat[start]))
    return b64encode(encoded).decode('ascii')


def quantify(rows, assets):
    """Add serializable measurements and return overlays for ranked images."""
    batches = {}
    for row in rows:
        row.update(scoli_orange_pink_percent='', scoli_orange_pink_pixels='',
                   scoli_yellow_green_pixels='', scoli_exclusion_reason='')
        if row['scoli_previously_ambiguous'] == 'yes':
            row['scoli_exclusion_reason'] = 'Previously ambiguous'
            continue
        image_id = row['image_id']
        colors, (orange, green), coverage = measure(assets / f'{image_id}.jpg')
        if not coverage:
            row['scoli_exclusion_reason'] = 'Insufficient automated coverage'
            continue
        row.update(scoli_orange_pink_percent=f'{100 * orange / (orange + green):.2f}',
                   scoli_orange_pink_pixels=str(orange), scoli_yellow_green_pixels=str(green))
        batch = (int(image_id.rsplit('-', 1)[1]) - 1) // 80
        batches.setdefault(batch, {})[image_id] = encode_mask(colors)
    return {
        batch: {'width': WIDTH, 'height': HEIGHT, 'masks': masks}
        for batch, masks in batches.items()
    }
