import os
import time
import subprocess
import pyautogui
from perception.screen import take_screenshot
from perception.vision import find_text_position

def ask_user(question: str) -> str:
    """
    Pauses execution and asks the user for input.
    """
    print(f"\n[Sentinel Asking]: {question}")
    answer = input("Answer: ")
    return f"User replied: {answer}"

# Keyboard actions

def wait(seconds: float):
    """Pauses execution"""
    time.sleep(seconds)
    return f"Waited for {seconds} seconds"

def type_text(text: str, interval: float = 0.05):
    """Types text like a human"""
    pyautogui.write(text, interval=interval)
    return f"Typed {len(text)} characters"
    
def press_key(key: str):
    """Presses a single key (enter, tab, esc, etc..)"""
    pyautogui.press(key)
    return f"Pressed {key} key."

def hot_key(keys: list[str]):
    """Presses a key combination"""
    pyautogui.hotkey(*keys)
    return "Pressed hotkey: " + "+".join(keys)


# Mouse actions

def semantic_click(target: str):
    image = take_screenshot()
    pos = find_text_position(target, image)

    if pos is None:
        raise RuntimeError(f"Could not find target '{target}' on screen")
    
    x, y = pos
    pyautogui.moveTo(x, y, duration=0.2)
    pyautogui.click()
    return f"Clicked on '{target}' at ({x}, {y})"

def move_mouse(x: int, y: int, duration: float = 0.2):
    """Move mouse pointer to absolute screen position"""
    pyautogui.moveTo(x, y, duration=duration)
    return f"Moved mouse pointer to ({x}, {y})"

def click_mouse(x: int=None, y: int=None, button: str="left"):
    """
    Click mouse.
    if x, y not provided, click current position
    """
    if x is not None and y is not None:
        pyautogui.click(x, y, button=button)
        return f"Clicked at ({x, {y}}) with {button}"
    else:
        pyautogui.click(button=button)
        px, py = pyautogui.position()
        return f"Clicked at current position ({px}, {py}) with {button}"
    
def double_click(x: int=None, y: int=None):
    """Double click"""
    if x is not None and y is not None:
        pyautogui.doubleClick(x, y)
        return "Double clicked at ({x}, {y})"
    else:
        pyautogui.doubleClick()
        px, py = pyautogui.position()
        return "Double clicked at ({px}, {py})"

def scroll(amount: int):
    pyautogui.scroll(amount)
    return f"Scrolled {amount}"

# Application actions

def open_app(app_name: str):
    """
    Opens an application
    """
    app = app_name.lower()

    if app in ["explorer", "file explorer", "files"]:
        subprocess.Popen(["explorer"])
        return
    
    if app in ["settings", "windows settings"]:
        subprocess.Popen(["cmd", "/c", "start", "ms-settings:"])
        return
    
    if app in ["control panel"]:
        subprocess.Popen(["control"])
        return
    try:
        os.startfile(app_name)
        return
    except Exception as e:
        raise RuntimeError(f"Failed to open app '{app_name}': {e}")

# Screen actions
def screenshot(path: str="screenshot.png"):
    """Takes a screenshot"""
    img = pyautogui.screenshot()
    img.save(path)
    return path

def abort():
    """Immediate stop"""
    raise KeyboardInterrupt("Automation aborted by safety trigger")