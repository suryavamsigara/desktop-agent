import ctypes
from pywinauto import Desktop, Application

def _get_active_wrapper():
    """
    Gets the Pywinauto wrapper for the FOREGROUND window.
    Uses Windows API (ctypes) to get the exact Handle (HWND).
    """
    # ID of the window user is looking at
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    
    app = Application(backend="uia").connect(handle=hwnd)
    return app.top_window()

def get_accessibility_tree(max_depth: int = 3):
    """
    Scans the active window and returns clickable elements.
    """
    try:
        dlg = _get_active_wrapper()
        window_title = dlg.window_text()
        
        output = [f"Active Window: '{window_title}'"]
        
        def _walk(control, depth):
            if depth > max_depth: return
            
            try:
                children = control.children()
            except Exception:
                return 

            for child in children:
                try:
                    text = child.window_text()
                    ctrl_type = child.element_info.control_type
                    
                    # Filter for useful elements
                    if text and ctrl_type in ["Button", "Edit", "MenuItem", "ListItem", "Hyperlink", "TabItem", "Document"]:
                        indent = "  " * depth
                        output.append(f"{indent}- [{ctrl_type}] \"{text}\"")
                    
                    _walk(child, depth + 1)
                except:
                    continue

        _walk(dlg, 1)
        return "\n".join(output)

    except Exception as e:
        return f"Error reading screen: {str(e)}"

def click_element(name: str, control_type: str = None):
    """
    Clicks an element in the ACTIVE window by name.
    """
    try:
        dlg = _get_active_wrapper()
        
        # Search for element
        if control_type:
            target = dlg.child_window(title=name, control_type=control_type)
        else:
            target = dlg.child_window(title=name)

        if target.exists():
            target.set_focus()
            target.click_input()
            return f"Clicked '{name}'"
        else:
            return f"Element '{name}' not found in '{dlg.window_text()}'"

    except Exception as e:
        return f"Click failed: {str(e)}"