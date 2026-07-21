from pathlib import Path
import fitz

pdf = fitz.open("reference_master.pdf")
output = Path("reference_pages")
output.mkdir(exist_ok=True)

for page_number, page in enumerate(pdf, start=1):
    image = page.get_pixmap(dpi=200, alpha=False)
    image.save(output / f"page_{page_number}.png")

print(f"Saved {len(pdf)} reference pages to {output.resolve()}")