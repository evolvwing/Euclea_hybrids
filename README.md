# Euclea_Larvae

**[Open the interactive contact sheets](https://evolvwing.github.io/Euclea_Larvae/)**

Larval color phenotyping in *Euclea incisa*, *E. incisa × E. delphinii* F1 hybrids, F2 broods, and backcrosses. Includes 474 cropped photographs, editable contact sheets, phenotype calls, and reproducible segregation analyses.

## Authoritative data

`data/larval_color_scores_reviewed.csv` is the public edition of the reviewed CSV from 22 November 2026, including the updated F2 and BC dorsal crimson patch calls. This edition omits private source links and uses project-specific image IDs. It is the source for the website and analyses. Tubercles are quantified automatically from the bundled photos. The input CSV records which images were previously ambiguous. The earlier provisional CSV is retained separately as `data/larval_color_scores_initial.csv`.

Each F2 and BC image represents one unique larva, as confirmed by the user. Parental and F1 individual identities remain unresolved. The dataset includes 252 F2, 125 BC, 45 F1, and 52 parental image records. F2-6 and BC-4 are not represented.

## Review photographs

On the crimson tab, browse images grouped by brood and state. Each card has **0 (absent)**, **1 (present)**, and **Ambiguous** buttons. A click saves locally and updates the selected state without moving images. Images regroup after refreshing. Export CSV to retain and share new edits.

**Autosave is browser-local:** it does not commit to GitHub, synchronize devices, or update the repository CSV. The GitHub Pages site uses a separate storage key from the earlier review site. The uploaded CSV is already incorporated as its baseline.

## Traits and scoring

- **Dorsal crimson patches:** paired patches at the recurring dorsal positions identified by the user. Faint patches count as present, including darker patches embedded within orange-pink bands. Exact segment numbering is not established here.
- **Orange-pink tubercles (scoli):** estimated percentage of orange-pink pixels among the classified orange-pink and yellow-green pixels in projecting structures. Sort across images, filter by brood, and open a photo to inspect the pixels counted.
- **Ambiguous (A):** relevant anatomy is blurred, obscured, or insufficiently visible. A clear positive can be recorded in a partial image.

The `crimson` field uses 0, 1, or A. Its numeric state field is blank for ambiguous calls. Review-status fields retain provenance. A visible absence does not establish genotype or absence at later instars.

Legacy `analysis_include=0` and blank `individual_id` columns are preserved from the upload; the analysis explicitly uses user-confirmed unique F2/BC images and excludes A scores, rather than relying on these legacy flags. Instars and photo-sampling representativeness remain unresolved.

## Automated tubercle estimates

The pipeline resamples the photos to 168 × 280 pixels, estimates the body axis from paired longitudinal color stripes, and finds narrow, colored ridges near that axis's margins. It filters out longitudinal color bands and classifies the remaining candidate pixels by hue, saturation and brightness. The ranking is the orange-pink count divided by the combined orange-pink and yellow-green count. The site's CSV includes both counts and the resulting percentage.

Previously ambiguous photos appear under **Excluded**. The algorithm also excludes photos with insufficient bilateral coverage or a strongly displaced fitted axis. These image-based estimates can be affected by body pose, lighting, adjacent larvae, and the resemblance between body markings and scoli. They measure the classified regions shown in the overlay. The method has been visually spot-checked on sample images and lacks validation against reference segmentations.

## Dorsal crimson patch segregation

Counts and ratios are **present : absent**. Ambiguous records are excluded from tests.

| Model | Cross | Present | Absent | Ambiguous excluded | Expected ratio | Pearson χ² (df = 1) | p |
|---|---|---:|---:|---:|---:|---:|---:|
| Single locus, complete dominance | F2 | 123 | 106 | 23 | 3:1 | 55.3493 | 1.009 × 10⁻¹³ |
| Single locus, complete dominance | BC | 25 | 90 | 10 | 1:1 | 36.7391 | 1.350 × 10⁻⁹ |
| Two loci, complementary dominance | F2 | 123 | 106 | 23 | 9:7 | 0.5995 | 0.4388 |
| Two loci, complementary dominance | BC | 25 | 90 | 10 | 1:3 | 0.6522 | 0.4193 |

Pearson goodness-of-fit tests have no continuity correction. The two-locus model requires a dominant allele at both loci (A_B_), AaBb F1 parents, aabb backcross parents, and independent assortment. The data fit these expectations, but do not prove this mechanism. The two-locus hypothesis was considered after inspecting the observed counts; it is exploratory. Tests pool broods and assume independent segregation and representative sampling. Developmental expression, viability, and scoring can affect observed ratios.

Full-precision results and per-brood counts are in `analysis/`.

## Crosses (mother × father)

| Cross | Mother | Father |
|---|---|---|
| F2-1 | F1-1 | F1-1 |
| F2-2 | F1-1 | F1-1 |
| F2-3 | F1-1 | F1-2 |
| F2-4 | F1-2 | F1-1 |
| F2-5 | F1-1 | F1-3 |
| F2-6 (no images) | F1-3 | F1-3 |
| BC-1 | E. incisa sib-cross | F1-1 |
| BC-2 | F1-1 | E. incisa sib-cross |
| BC-3 | E. incisa sib-cross | F1-2 |
| BC-4 (no images) | E. incisa sib-cross | F1-3 |

Filename prefixes Dihybrid_N and Backcross_N map to F2-N and BC-N. F1 brood identity is unresolved in the image filenames.

## Reproduce

```bash
python -m pip install -r requirements.txt
python scripts/build.py
python -m http.server 8000 --directory docs
```

Visit `http://localhost:8000`. The build validates image IDs, states, and image availability; writes website JSON and CSV from the reviewed upload; and regenerates counts and tests. No image generation or classifier inference is needed. `docs/` is a self-contained static site with bundled JPG images.

`source/` preserves the original inventory, provisional calls, and color-QC script. Optional `python source/build_data.py` reconstructs initial calls into separate `source/reconstructed_initial_*` files; it never overwrites the reviewed baseline. Heuristic color fractions use a fixed central rectangle, not anatomical segmentation, and did not determine phenotype calls. These metrics and gradient energy are audit aids, not a validated classifier. Image hashes refer to bundled display images.

## Publishing

A GitHub Actions workflow deploys `docs/` to GitHub Pages on pushes to `main`. Set repository Settings → Pages → Source to **GitHub Actions**. The repository is intended to be public. No blanket reuse license is assigned to the photographs or dataset in this project.
