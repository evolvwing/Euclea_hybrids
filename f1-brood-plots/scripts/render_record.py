"""Render the current Illustrator file's publication PDF and PNG."""
import hashlib
from pathlib import Path

import fitz

root = Path(__file__).resolve().parents[1]
source = root / "record/Fig2_F1-broods_v2.ai"
output = root / "outputs"
output.mkdir(exist_ok=True)

with fitz.open(source) as document:
    document.save(output / "Fig2_F1-broods_record.pdf")
    document[0].get_pixmap(dpi=450, alpha=False).save(output / "Fig2_F1-broods_record.png")

print("Record SHA-256:", hashlib.sha256(source.read_bytes()).hexdigest())
