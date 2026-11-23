# F1 Brood Plots style guide

Use the [current Figure 2](../outputs/Fig2_F1-broods_record.pdf) as the visual reference and the [plotting scripts](../scripts/) for reusable chart settings.

## Layout and typography

Use a white artboard, 7.5 in (540 pt) wide for a full-width figure. Set panel letters in bold Arial and align them at the upper left of each panel. Use Arial for labels, italicize scientific names, and keep labels as editable text. Keep axes thin, omit gridlines and median bars, and align plots that share a unit or category scale.

| Panel | Design |
| --- | --- |
| A | Place the crossing schematic and timeline across the full width. Color developmental paths consistently with the brood and diapause encodings below. |
| B | Show cross-level observations over mean bars with SEM. Use translucent points and report the number of crosses. |
| C | Group cocoon outcomes by brood. Draw mortality in grayscale and adult counts by sex and diapause status. Label bar totals and bracket the adult male–female comparison. |
| D | Show duration violins with raw observations and display the group sample sizes above the plots. |
| E–F | Use the same forewing-length scale for males and females. Align donuts above brood labels and report measured sample sizes beneath the D and ND positions. Use a light divider before pooled F1 and keep the parental controls in the same order in both panels. |

## Palette

| Meaning | Hex |
| --- | --- |
| Diapaused | `#4E7994` |
| Non-diapaused | `#B28B57` |
| F1 crosses | `#A16B8D` |
| *E. incisa* sibling crosses | `#648B76` |
| 2024 *E. incisa* parental brood | `#8D9C65` |
| Unsexed larval deaths | `#CCCCCC` |
| Male pupal deaths | `#808080` |
| Female pupal deaths | `#333333` |
| Main text | `#292D31` |

## Chart settings

- **Violins.** Use a 16% category-color fill on white and an opaque 1.2 pt outline. Evaluate Gaussian density on 256 points between the observed minimum and maximum. Use bandwidths of 0.8 days for development and 0.22 mm for forewing length for these data. Normalize each violin to its own peak and show sample sizes separately.
- **Points.** Use 40% opacity for egg counts and 29% for development and wing measurements. Seed the jitter so point positions stay stable across rebuilds.
- **Donuts.** Use a 30.24 pt diameter, a ring thickness of 48% of the radius, and start the diapause wedge at noon, clockwise. Place white counts in the ring and the percent diapaused in the center. Set the percent sign at 60% of the numeric font size. Use all eligible individuals in the denominator.
- **Annotations.** Put statistical letters above the relevant violins and retain individual F1 broods as descriptive groups when the tested group is pooled F1. Review each significance label against the current output tables when inputs change.

Before export, check ordering and alignment, legibility at final size, continuous text labels, and agreement between counts, plotted values, and [methods](METHODS.md).
