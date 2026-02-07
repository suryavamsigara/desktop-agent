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
    }
]