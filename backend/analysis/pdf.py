from io import BytesIO

from pypdf import PdfReader


def extract_text(file_bytes):
    reader = PdfReader(BytesIO(file_bytes))

    pages = []

    for page in reader.pages:
        text = page.extract_text() or ""

        if text.strip():
            pages.append(text.strip())

    return "\n\n".join(pages).strip()