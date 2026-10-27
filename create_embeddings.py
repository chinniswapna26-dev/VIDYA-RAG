import re
import json
import math
from collections import Counter
from pathlib import Path
from pypdf import PdfReader

PDF_PATH = Path("data/textbooks/science.pdf")
OUTPUT_PATH = Path("data/textbooks/embeddings.json")

CHUNK_SIZE = 1000
OVERLAP = 200


def tokenize(text):
    return re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())


def clean_text(text):
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_into_chunks(text):
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks = []
    current_sentences = []
    current_length = 0

    for sentence in sentences:
        sentence = sentence.strip()

        if not sentence:
            continue

        if len(sentence) > CHUNK_SIZE:
            if current_sentences:
                chunks.append(" ".join(current_sentences))
                current_sentences = []
                current_length = 0

            for start in range(0, len(sentence), CHUNK_SIZE - OVERLAP):
                part = sentence[start:start + CHUNK_SIZE].strip()
                if part:
                    chunks.append(part)
            continue

        if current_length + len(sentence) + 1 > CHUNK_SIZE:
            if current_sentences:
                chunks.append(" ".join(current_sentences))

            # Retain recent sentences for context.
            overlap_sentences = []
            overlap_length = 0

            for old_sentence in reversed(current_sentences):
                if overlap_length + len(old_sentence) > OVERLAP:
                    break
                overlap_sentences.insert(0, old_sentence)
                overlap_length += len(old_sentence)

            current_sentences = overlap_sentences
            current_length = sum(
                len(item) + 1 for item in current_sentences
            )

        current_sentences.append(sentence)
        current_length += len(sentence) + 1

    if current_sentences:
        chunks.append(" ".join(current_sentences))

    return chunks


def create_vectors(chunks):
    tokenized_chunks = [tokenize(chunk) for chunk in chunks]
    document_frequency = Counter()

    for tokens in tokenized_chunks:
        document_frequency.update(set(tokens))

    total_documents = len(tokenized_chunks)
    embeddings = []

    for tokens in tokenized_chunks:
        counts = Counter(tokens)
        vector = {}

        for word, count in counts.items():
            tf = count / max(len(tokens), 1)
            idf = math.log(
                (total_documents + 1)
                / (document_frequency[word] + 1)
            ) + 1

            vector[word] = round(tf * idf, 8)

        embeddings.append(vector)

    return embeddings


def main():
    print("Reading textbook...", flush=True)

    if not PDF_PATH.exists():
        print("ERROR: PDF file not found:", PDF_PATH)
        return

    try:
        reader = PdfReader(str(PDF_PATH))
        page_texts = [
            page.extract_text() or ""
            for page in reader.pages
        ]
    except Exception as error:
        print("Could not read the PDF:", error)
        return

    full_text = clean_text(" ".join(page_texts))

    if not full_text:
        print("ERROR: No text could be extracted from the PDF.")
        return

    print("Textbook read successfully!", flush=True)
    print("Total characters:", len(full_text), flush=True)

    print("Splitting textbook into chunks...", flush=True)
    chunks = split_into_chunks(full_text)
    print("Total chunks:", len(chunks), flush=True)

    if not chunks:
        print("ERROR: No text chunks were created.")
        return

    print("Creating text vectors...", flush=True)
    embeddings = create_vectors(chunks)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        json.dump(
            {"chunks": chunks, "embeddings": embeddings},
            file,
            ensure_ascii=False
        )

    print("Text vectors created successfully!", flush=True)
    print("Number of vectors:", len(embeddings), flush=True)
    print("Saved text vectors to:", OUTPUT_PATH, flush=True)
    print("Vidya-RAG text processing completed!", flush=True)


if __name__ == "__main__":
    main()