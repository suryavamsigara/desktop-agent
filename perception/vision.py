import time
import pytesseract
import pyautogui
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

def get_ocr_data(image: Image.Image):
    """
    Returns OCR data with boudning boxes.
    """
    return pytesseract.image_to_data(
        image,
        output_type=pytesseract.Output.DICT
    )

def find_text_position(target: str, image: Image.Image):
    """
    Find center (x, y) of the first OCR box that approximately matches target text
    """
    target = target.lower().strip()
    data = get_ocr_data(image)

    n = len(data["text"])
    for i in range(n):
        word = data["text"][i].strip().lower()
        if not word:
            continue

        if target in word or word in target:
            x = data["left"][i]
            y = data["top"][i]
            w = data["width"][i]
            h = data["height"][i]

            cx = x + w // 2
            cy = y + h // 2

            return cx, cy
    return None

def detect_clickables(image):
    """
    Returns a list of visible text elements with positions.
    """
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

    items = []
    for i, text in enumerate(data["text"]):
        text = text.strip()
        if (len(text) < 4):
            continue

        if text.startswith("earch"):
            text = "Search"

        items.append({
            "text": text,
            "x": data["left"][i] + data["width"][i] // 2,
            "y": data["top"][i] + data["height"][i] // 2
        })
    return items