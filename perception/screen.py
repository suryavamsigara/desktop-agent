import os
import time
import pyautogui
import pytesseract
from PIL import Image

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

    observation = f"""
    SCREEN OBSERVATION:
    --------------------
    Visible text on screen:
    {text if text else "No readable text detected."}
    """
    return observation
