"""Trace paired dorsal stripes and estimate their orange-pink pixel fraction."""
from base64 import b64encode
from struct import Struct

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

WIDTH, HEIGHT = 300, 500
TRACE_WIDTH, TRACE_HEIGHT = 150, 250
BAND_RADIUS = 7
BATCH_SIZE = 32
MASK_RUN = Struct('<IBB')
MEASUREMENT_FIELDS = (
    'dorsal_orange_pink_percent', 'dorsal_orange_pink_pixels',
    'dorsal_yellow_green_pixels', 'dorsal_exclusion_reason',
)


def smooth_path(signal, moves):
    """Recover the strongest continuous path through per-row evidence."""
    shape = signal.shape[1:]
    indices = np.indices(shape)
    neighbors, costs = [], []
    for offset, cost in moves:
        neighbor = tuple(np.clip(axis + step, 0, n - 1)
                         for axis, step, n in zip(indices, offset, shape))
        neighbors.append(np.ravel_multi_index(neighbor, shape).ravel())
        costs.append(cost)
    neighbors = np.asarray(neighbors)
    costs = np.asarray(costs)[:, None]
    flat = signal.reshape(len(signal), -1)
    scores = flat[0]
    traceback = np.empty((len(signal) - 1, scores.size), dtype=np.int32)
    columns = np.arange(scores.size)
    for i, row in enumerate(flat[1:]):
        options = scores[neighbors] - costs
        choice = options.argmax(axis=0)
        traceback[i] = neighbors[choice, columns]
        scores = row + options[choice, columns]
    path = [int(scores.argmax())]
    for row in reversed(traceback):
        path.append(row[path[-1]])
    return np.unravel_index(path[::-1], shape)


def stripe_traces(rgb, h, s, v):
    """Find two warm, approximately parallel stripes and a thin yellow ridge between them."""
    r, g, b = np.moveaxis(rgb, -1, 0)
    warmth = np.maximum(np.minimum(r, g) - b, 0)
    # Both yellow and orange contribute to the tracking signal.
    stripe = ndi.gaussian_filter(np.maximum(.78 * np.maximum(r, g) + .22 * np.minimum(r, g) - b, 0), (4, 1.6))
    contrast = stripe - ndi.gaussian_filter(stripe, (1, 5))
    yellow = (h >= .105) & (h <= .27) & (s >= .22) & (v >= .30)
    yellow_ridge = ndi.gaussian_filter(warmth * yellow, (2.0, .8))
    yellow_ridge -= ndi.gaussian_filter(yellow_ridge, (.5, 2.3))
    # Limit scoring to the central span where the flanking stripes are visible
    # before they turn into the terminal projections.
    rr = np.arange(45, 201)
    cols = np.arange(29, 121)
    radii = np.arange(10, 30)
    left, right = cols[:, None] - radii, cols[:, None] + radii
    left = np.clip(left, 0, TRACE_WIDTH - 1)
    right = np.clip(right, 0, TRACE_WIDTH - 1)
    left_value = stripe[rr[:, None, None], left]
    right_value = stripe[rr[:, None, None], right]
    ridge = contrast[rr[:, None, None], left] + contrast[rr[:, None, None], right]
    signal = .9 * np.minimum(left_value, right_value) + .40 * np.maximum(left_value, right_value) + 1.65 * ridge
    signal -= .022 * ((cols - 75) / 24)[None, :, None] ** 2
    signal -= .012 * ((radii - 18) / 10)[None, None, :] ** 2
    move = [((dx, dr), .052 * abs(dx) + .095 * abs(dr))
            for dx in range(-2, 3) for dr in range(-1, 2)]
    ci, ri = smooth_path(signal, move)
    lx = ndi.gaussian_filter1d((cols[ci] - radii[ri]).astype(float), 2.4)
    rx = ndi.gaussian_filter1d((cols[ci] + radii[ri]).astype(float), 2.4)
    # The midline follows yellow contrast within the central part of the
    # space between the stripes. The midpoint acts as a soft prior.
    xx = np.arange(TRACE_WIDTH)
    center = (lx + rx) / 2
    middle = yellow_ridge[rr] - .009 * ((xx - center[:, None]) / 2) ** 2
    middle[abs(xx - center[:, None]) > .35 * (rx - lx)[:, None]] = -10
    (mid,) = smooth_path(middle, [((dx,), .036 * abs(dx)) for dx in range(-2, 3)])
    mid = ndi.gaussian_filter1d(mid.astype(float), 1.7)
    left_ix, right_ix, mid_ix = (np.rint(a).astype(int) for a in (lx, rx, mid))
    support = (
        (stripe[rr, left_ix] >= .12) & (stripe[rr, right_ix] >= .12)
        & (contrast[rr, left_ix] >= .010) & (contrast[rr, right_ix] >= .010)
    )
    mid_support = yellow_ridge[rr, mid_ix] >= .006
    # Require paired stripe evidence along the crop, and a visible yellow
    # ridge in more than a small isolated portion of the midline.
    reliable = (
        support.mean() >= .51
        and min(block.mean() for block in np.array_split(support, 4)) >= .22
        and mid_support.mean() >= (.30 if support.mean() >= .95 else .40)
    )
    return rr, lx, mid, rx, reliable, (support.mean(), mid_support.mean())


def measure(path):
    with Image.open(path) as im:
        image = im.convert('RGB').resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    small = image.resize((TRACE_WIDTH, TRACE_HEIGHT), Image.Resampling.LANCZOS)
    rgbs = np.asarray(small, dtype=np.float32) / 255
    hsvs = np.asarray(small.convert('HSV'), dtype=np.float32) / 255
    rr, lx, mid, rx, reliable, support = stripe_traces(rgbs, *np.moveaxis(hsvs, -1, 0))
    rows = np.arange(2 * rr[0], 2 * rr[-1] + 1)
    lx, mid, rx = (np.interp(rows, 2 * rr, 2 * coords) for coords in (lx, mid, rx))
    x = np.arange(WIDTH)
    left = abs(x - lx[:, None]) < BAND_RADIUS
    right = abs(x - rx[:, None]) < BAND_RADIUS
    r, g, b = np.moveaxis(np.asarray(image, dtype=np.float32)[rows] / 255, -1, 0)
    h, s, v = np.moveaxis(np.asarray(image.convert('HSV'), dtype=np.float32)[rows] / 255, -1, 0)
    colored = (s >= .36) & (v >= .23)
    orange = colored & ((h <= .106) | (h >= .94)) & (r - g >= .065)
    green = colored & (h > .106) & (h <= .26) & (np.minimum(r, g) - b >= .095)
    classes = np.where(orange, 1, np.where(green, 2, 0))
    for band in (left, right):
        counted = (classes > 0) & band
        reliable &= counted.sum() >= .80 * band.sum()
        for strip, visible in zip(np.array_split(band, 4), np.array_split(counted, 4)):
            reliable &= visible.sum() >= .55 * strip.sum()
    mask = np.zeros((HEIGHT, WIDTH), dtype=np.uint8)
    mask[rows] = np.where(left | right, classes, 0)
    return mask, reliable, (rows, lx, mid, rx), support


def encode_mask(colors):
    """Encode pixel runs as a 32-bit start offset, length and class."""
    flat = colors.reshape(-1)
    changes = np.flatnonzero(np.diff(flat, prepend=0, append=0))
    encoded = bytearray()
    for start, end in zip(changes, changes[1:]):
        if flat[start]:
            for offset in range(int(start), int(end), 255):
                encoded.extend(MASK_RUN.pack(offset, min(int(end) - offset, 255), flat[start]))
    return b64encode(encoded).decode('ascii')


def quantify(rows, assets):
    """Analyze every photograph, including previously excluded images."""
    batches = {}
    for row in rows:
        row.update(dict.fromkeys(MEASUREMENT_FIELDS, ''))
        image_id = row['image_id']
        colors, reliable, traces, _ = measure(assets / f'{image_id}.jpg')
        if not reliable:
            row['dorsal_exclusion_reason'] = 'Dorsal lines could not be traced reliably'
            continue
        orange = int(np.count_nonzero(colors == 1))
        green = int(np.count_nonzero(colors == 2))
        row.update(dorsal_orange_pink_percent=f'{100 * orange / (orange + green):.2f}',
                   dorsal_orange_pink_pixels=str(orange), dorsal_yellow_green_pixels=str(green))
        batch = (int(image_id.rsplit('-', 1)[1]) - 1) // BATCH_SIZE
        overlay = batches.setdefault(batch, {'width': WIDTH, 'height': HEIGHT, 'masks': {}, 'midlines': {}})
        overlay['masks'][image_id] = encode_mask(colors)
        scan_rows, _, mid, _ = traces
        overlay['midlines'][image_id] = [
            int(scan_rows[0]),
            b64encode(np.rint(mid).astype('<u2').tobytes()).decode('ascii'),
        ]
    return batches
