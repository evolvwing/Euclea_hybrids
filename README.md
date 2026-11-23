# Euclea_hybrids

**[Open the interactive contact sheets](https://evolvwing.github.io/Euclea_hybrids/)**

Larval color phenotyping in *Euclea incisa*, *E. incisa × E. delphinii* F1 hybrids, F2 broods, and backcrosses. Includes a developmental contact sheet with 308 displayed F1 larval crops, plus 474 phenotype-review photographs, phenotype calls, and reproducible segregation analyses.

## F1 Brood Plots

[Figure 2, plotting workflow, and style guide](f1-brood-plots/README.md) for the crossing design, egg production, cocoon outcomes, development time, diapause, and forewing size.

## F1 hybrid larvae (L1 to L8)

The first contact sheet documents larvae of *E. incisa* × *E. delphinii* from instars L1 through L8. Photographs are grouped by instar, with a filter for L1 through L8. Counts refer to image views. The same larva may appear in multiple frames.

The 3:5 crops are bundled as web-sized WebP files in `docs/instar-assets/`. White vertical scale bars are retained on crops calibrated against a ruler in the original photograph. `docs/instars.json` records the original crop filename and instar.

The reviewed baseline is `data/f1_larval_instars_reviewed.csv`. Its 317 records include nine crops marked `instar_review_excluded=yes`. The gallery reads the same flags from `docs/instars.json` and displays the 308 included crops. The CSV export includes the complete reviewed baseline.

## Authoritative data

`data/larval_color_scores_reviewed.csv` is the public edition of the reviewed CSV from 23 November 2026, including the updated F2 and BC dorsal crimson patch calls. This edition omits private source links and uses project-specific image IDs. It is the source for the website and analyses. The dorsal orange lines are quantified from the bundled photos.

Each F2 and BC image represents one unique larva, as confirmed by the user. Parental and F1 individual identities remain unresolved. The dataset includes 252 F2, 125 BC, 45 F1, and 52 parental image records. F2-6 and BC-4 are not represented.

## Review photographs

On the crimson tab, browse images grouped by brood and state. Each card has **0 (absent)**, **1 (present)**, and **Ambiguous** buttons. A click saves locally and updates the selected state without moving images. Images regroup after refreshing. Use **Exclude** to hide a photo from the crimson contact sheet on reload. Turn on **Show excluded** to review or restore it. Export CSV to retain and share new edits, including the `crimson_review_excluded` flag.

**Autosave is browser-local:** it does not commit to GitHub, synchronize devices, or update the repository CSV. The GitHub Pages site uses a separate storage key from the earlier review site. The uploaded CSV is already incorporated as its baseline.

## Traits and scoring

- **Dorsal crimson patches:** paired patches at the recurring dorsal positions identified by the user. Faint patches count as present, including darker patches embedded within orange-pink bands. Exact segment numbering is not established here.
- **Dorsal orange lines:** estimated orange-pink coverage in two bands along the body stripes that flank the thin yellow midline. Sort by coverage within each brood and open a photo to inspect the scored pixels.
- **Ambiguous (A):** relevant anatomy is blurred, obscured, or insufficiently visible. A clear positive can be recorded in a partial image.

The `crimson` field uses 0, 1, or A. Its numeric state field is blank for ambiguous calls. Review-status fields retain provenance. A visible absence does not establish genotype or absence at later instars.

Legacy `analysis_include=0` and blank `individual_id` columns are preserved from the upload; the analysis explicitly uses user-confirmed unique F2/BC images and excludes A scores, rather than relying on these legacy flags. Instars and photo-sampling representativeness remain unresolved.

## Dorsal orange lines

On a 300 × 500 pixel crop, the pipeline traces two warm longitudinal stripes and follows the narrow yellow ridge between them. It counts orange-pink and yellow-green pixels in narrow bands centered on the flanking stripes, omitting the ends where the stripes turn into projections. Hue, saturation, brightness and channel contrast determine the color classes. The score is the orange-pink count divided by the sum of both color counts. The export includes both counts and the resulting percentage.

The analysis evaluates all images. The **Excluded** section holds images with insufficient evidence for a pair of continuous stripes, a visible yellow midline, or enough classified pixels on both sides. The pilot used visually placed guide points. The published pipeline estimates all three traces automatically. The overlays have been visually spot-checked. Pose, lighting, overlapping larvae, and indistinct stripes can affect the automatic traces.

### Review dorsal exclusions

Use **Exclude** or **Restore** on scored photos. The gallery keeps your place and stores draft changes in your browser. Use **Export current CSV** to share edits. To publish them, update the `dorsal_review_excluded` column in the reviewed CSV and regenerate the gallery files. Manually excluded photos retain their measured scores and overlays for review.

## Dorsal crimson patch segregation

Counts and ratios are **present : absent**. Ambiguous scores are excluded from tests. The crimson review exclusion flag controls visibility in the contact sheet.

| Model | Cross | Present | Absent | Ambiguous excluded | Expected ratio | Pearson χ² (df = 1) | p |
|---|---|---:|---:|---:|---:|---:|---:|
| Single locus, complete dominance | F2 | 127 | 104 | 21 | 3:1 | 49.3867 | 2.102 × 10⁻¹² |
| Single locus, complete dominance | BC | 29 | 87 | 9 | 1:1 | 29.0000 | 7.238 × 10⁻⁸ |
| Two loci, complementary dominance | F2 | 127 | 104 | 21 | 9:7 | 0.1518 | 0.6968 |
| Two loci, complementary dominance | BC | 29 | 87 | 9 | 1:3 | 0.0000 | 1.0000 |

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

The `source/inventory.json` file lists the bundled photographs. The reviewed CSV also provides image hashes, central-crop color fractions, and image gradient energy for quality checks. These metrics did not determine the phenotype calls.

## Publishing

Run `python scripts/build.py` after updating scores or photos and commit the generated files. GitHub Actions verifies the committed scores and overlays before deploying `docs/` to GitHub Pages. Serving the committed measurements keeps the published ranking stable across runners. Set repository Settings → Pages → Source to **GitHub Actions**. The repository is intended to be public. No blanket reuse license is assigned to the photographs or dataset in this project.
