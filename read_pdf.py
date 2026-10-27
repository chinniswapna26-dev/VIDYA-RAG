from pypdf import PdfReader
from pathlib import Path

pdf_path = Path("data/textbooks/science.pdf")

print("Checking textbook...")

if pdf_path.exists():
    reader = PdfReader(str(pdf_path))
    print("SUCCESS! Textbook opened.")
print("Total pages:", len(reader.pages))

for page_number, page in enumerate(reader.pages[:3], start=1):
    text = page.extract_text() or ""
    print(f"\n--- PAGE {page_number} ---")
    print(text[:1000])

print("\nTextbook reading completed!")