"""Select an installed font for analytic plot regeneration."""
from pathlib import Path

from matplotlib import font_manager, rcParams

for path in Path("assets/fonts").glob("*.ttf"):
    font_manager.fontManager.addfont(str(path))

available = {font.name for font in font_manager.fontManager.ttflist}
plot_font = next(font for font in ("Arial", "Liberation Sans", "DejaVu Sans") if font in available)

rcParams["font.cursive"] = [plot_font]
