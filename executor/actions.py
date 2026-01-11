import os
import sys
import time
import pyautogui

# Keyboard actions

def wait(seconds: float):
    """Pauses execution"""
    time.sleep(seconds)

def type_text(text: str, interval: float = 0.05):
    """Types text like a human"""
    pyautogui.write(text, interval=interval)
    
def press_key(key: str):
    """Presses a single key (enter, tab, esc, etc..)"""
    pyautogui.press(key)


# Mouse actions

def move_mouse(x: int, y: int, duration: float = 0.2):
    """Move mouse to absolute screen positino"""
    pyautogui.moveTo(x, y, duration=duration)

def click_mouse(x: int=None, y: int=None, button: str="left"):
    """
    Click mouse.
    if x, y not provided, click current position
    """
    if x is not None and y is not None:
        pyautogui.click(x, y, button=button)
    else:
        pyautogui.click(button=button)
    
def double_click(x: int=None, y: int=None):
    """Double click"""
    if x is not None and y is not None:
        pyautogui.doubleClick(x, y)
    else:
        pyautogui.doubleClick()

# Application actions

def open_app(app_name: str):
    """
    Opens an application
    """
    try:
        os.startfile(app_name)
    except Exception as e:
        raise RuntimeError(f"Failed to open app '{app_name}': {e}")
    

def abort():
    """Immediate stop"""
    raise KeyboardInterrupt("Automation aborted by safety trigger")