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

