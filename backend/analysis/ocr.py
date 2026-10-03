import pytesseract
from PIL import Image
from io import BytesIO


def extract_text(file_bytes):
    image = Image.open(BytesIO(file_bytes))
    text = pytesseract.image_to_string(image)

    return text.strip()