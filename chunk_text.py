from pypdf import PdfReader

pdf_path = "data/textbooks/science.pdf"

print("Reading textbook...", flush=True)

reader = PdfReader(pdf_path)

full_text = ""

for page in reader.pages:
    text = page.extract_text() or ""
    full_text += text + "\n"

print("Textbook read successfully!", flush=True)
print("Total characters:", len(full_text), flush=True)

chunk_size = 500
overlap = 100

chunks = []

for start in range(0, len(full_text), chunk_size - overlap):
    end = start + chunk_size
    chunk = full_text[start:end]
if chunk.strip():
    chunks.append(chunk)

print("Textbook successfully split into chunks!", flush=True)
print("Total chunks:", len(chunks), flush=True)

if chunks:
    print("\nExample of the first chunk:", flush=True)
    print(chunks[0], flush=True)