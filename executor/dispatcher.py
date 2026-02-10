import json
from typing import Any
from .actions import *
from .browser_manager import *
from perception.screen import observe_screen

async def execute_tool(tool_call: Any):
    """
    Executes one tool call and return its string result / error message
    
    :param tool_call: function
    :type tool_call: Any
    """
    func_name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)

    try:
        # Browser tools (Async)

        if func_name == "browser_navigate":
            return await browser_navigate(**args)

        elif func_name == "browser_get_tree":
            return await browser_get_tree(**args)
        
        elif func_name == "browser_click":
            return await browser_click(**args)
        
        elif func_name == "browser_type":
            return await browser_type(**args)
        
        elif func_name == "browser_scroll":
            return await browser_scroll(**args)
        
        elif func_name == "browser_download":
            return await browser_download(**args)

        # Desktop tools (Sync)

        elif func_name == "wait":
            seconds = float(args.get("seconds", 0))
            return wait(seconds)
        
        elif func_name == "type_text":
            return type_text(**args)

        elif func_name == "press_key":
            return press_key(**args)

        elif func_name == "hot_key":
            return hot_key(**args)

        elif func_name == "semantic_click":
            return semantic_click(**args)
        
        elif func_name == "move_mouse":
            return move_mouse(**args)
        
        elif func_name == "click_mouse":
            return click_mouse(**args)

        elif func_name == "double_click":
            return double_click(**args)
        
        elif func_name == "scroll":
            return scroll(**args)

        elif func_name == "screenshot":
            return screenshot(**args)
        
        elif func_name == "observe_screen":
            return observe_screen()
        
        elif func_name == "ask_user":
            return ask_user(**args)
        
        elif func_name == "abort":
            return abort()

    except Exception as e:
        return f"Error in {func_name}: {str(e)}"
    
