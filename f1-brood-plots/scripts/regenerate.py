"""Rebuild the analytic panels and assemble a draft with the current schematic."""
from pathlib import Path
import subprocess
import sys

import fitz

root = Path(__file__).resolve().parents[1]
output = root / "outputs"
output.mkdir(exist_ok=True)

for script in ("plot_eggs_and_development.py", "plot_cocoon_outcomes.py", "plot_forewings.py"):
    subprocess.run([sys.executable, str(root / "scripts" / script)], cwd=root, check=True)

figure_width = 540
schematic_height = 116
middle_height = 180
forewing_height = 230

with (
    fitz.open(root / "record/Fig2_F1-broods_v2.ai") as record,
    fitz.open(output / "panels_bd.pdf") as bd,
    fitz.open(output / "panel_C_parental.pdf") as cocoon,
    fitz.open(output / "vector_ef.pdf") as ef,
    fitz.open() as draft,
):
    page = draft.new_page(width=figure_width, height=schematic_height + middle_height + forewing_height)
    schematic = fitz.Rect(0, 0, figure_width, schematic_height)
    page.show_pdf_page(schematic, record, 0, clip=schematic)

    middle_bottom = schematic_height + middle_height
    page.show_pdf_page(fitz.Rect(0, schematic_height, figure_width, middle_bottom), bd, 0)
    page.show_pdf_page(fitz.Rect(113, schematic_height, 403, middle_bottom), cocoon, 0)
    page.show_pdf_page(fitz.Rect(0, middle_bottom, figure_width, page.rect.height), ef, 0)
    draft.save(output / "regenerated_from_data.pdf", garbage=4, deflate=True)
    page.get_pixmap(dpi=160, alpha=False).save(output / "regenerated_from_data.png")
