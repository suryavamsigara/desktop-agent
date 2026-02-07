import os
import time
import pyautogui
import pytesseract
from PIL import Image
from .vision import detect_clickables

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

SCREENSHOT_DIR = "screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def take_screenshot() -> Image.Image:
    """
    Captures current screen as PIL image
    """
    time.sleep(0.5)
    return pyautogui.screenshot()

def extract_text(image: Image.Image) -> str:
    """
    Extracts visible text using OCR
    """
    text = pytesseract.image_to_string(image)
    return text.strip()

def observe_screen() -> str:
    image = take_screenshot()

    filename = f"{SCREENSHOT_DIR}/screen_{int(time.time())}.png"
    image.save(filename)

    text = extract_text(image)
    clickables = detect_clickables(image)

    clickable_lines = []
    for item in clickables:
        clickable_lines.append(
            f"- {item['text']} @ ({item['x']}, {item['y']})"
        )

    observation = f"""
    SCREEN OBSERVATION:
    --------------------
    Visible text:
    {text if text else "No readable text detected."}

    Clickable elements:
    {chr(10).join(clickable_lines) if clickable_lines else "None detected."}
    """.strip()

    return observation
