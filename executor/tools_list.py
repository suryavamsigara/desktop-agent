tools = [
    {
        "type": "function",
        "function": {
            "name": "wait",
            "description": "Pauses execution for the specified number of seconds.",
            "parameters": {
                "type": "object",
                "properties": {
                    "seconds": {
                        "type": "number",
                        "description": "Number of seconds to wait (float allowed)."
                    }
                },
                "required": ["seconds"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "press_key",
            "description": "Presses a single key (enter, tab, esc, etc...)",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "The key to press (pyautogui key name)."
                    }
                },
                "required": ["key"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "type_text",
            "description": "Types text like a human",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to type."
                    },
                    "interval": {
                        "type": "number",
                        "description": "Time in seconds between each keystroke (default 0.05). Smaller = faster.",
                        "default": 0.05
                    }
                },
                "required": ["text"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "hot_key",
            "description": "Presses a combination of keys simultaneously (e.g. Ctrl+C, Alt+Tab, Win+R).",
            "parameters": {
                "type": "object",
                "properties": {
                    "keys": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of keys to press together, e.g. ['ctrl', 'c'] or ['win', 'r']."
                    }
                },
                "required": ["keys"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "semantic_click",
            "description": "Locates text on the screen using OCR/image processing and clicks on it. Raises error if text not found.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "The exact or approximate text to find and click on the screen."
                    }
                },
                "required": ["target"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "move_mouse",
            "description": "Moves the mouse cursor to an absolute screen position (x, y).",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {"type": "integer", "description": "X coordinate (pixels from left)"},
                    "y": {"type": "integer", "description": "Y coordinate (pixels from top)"},
                    "duration": {
                        "type": "number",
                        "description": "Time in seconds for the movement (human-like).",
                        "default": 0.2
                    }
                },
                "required": ["x", "y"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "click_mouse",
            "description": "Performs a mouse click. If x and y are provided, moves to that position first. Otherwise clicks at current position.",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "X coordinate (optional). If omitted, uses current position."
                    },
                    "y": {
                        "type": "integer",
                        "description": "Y coordinate (optional). If omitted, uses current position."
                    },
                    "button": {
                        "type": "string",
                        "description": "Which button: 'left', 'right', 'middle'.",
                        "default": "left"
                    }
                },
                "required": []
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "double_click",
            "description": "Performs a double mouse click. If x and y are provided, moves there first.",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "X coordinate (optional)."
                    },
                    "y": {
                        "type": "integer",
                        "description": "Y coordinate (optional)."
                    }
                },
                "required": []
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "scroll",
            "description": "Scrolls the mouse wheel up (positive) or down (negative).",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "integer",
                        "description": "Scroll amount. Positive = up, negative = down."
                    }
                },
                "required": ["amount"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "screenshot",
            "description": "Takes a screenshot of the entire screen and saves it to the given path. Returns the path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path to save the screenshot (e.g. 'screenshot.png').",
                        "default": "screenshot.png"
                    }
                },
                "required": []
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "abort",
            "description": "Immediately stops the automation by raising a KeyboardInterrupt (safety trigger).",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "observe_screen",
            "description": "Observe the current screen, extract visible text, and clickable elements using OCR, and return a human readable description of what is on the screen.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]