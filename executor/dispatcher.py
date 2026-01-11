from .actions import *
from planner import state

ACTION_MAP = {
    "wait": wait,
    "type": type_text,
    "press": press_key,
    "move_mouse": move_mouse,
    "click": click_mouse,
    "open_app": open_app
}

def execute(plan: dict):
    """
    Executes steps until observe
    """
    steps = plan.get("steps", [])

    for step in steps:
        action = step.get("action")

        if action == "observe":
            return "OBSERVE"
        
        if action not in ACTION_MAP:
            raise ValueError(f"Blocked unknown action: {action}")
        
        fn = ACTION_MAP[action]
        params = {k: v for k, v in step.items() if k != "action"}

        try:
            fn(**params)
            state["last_action"] = action
            state["current_step"] += 1

        except Exception as e:
            raise RuntimeError(f"Execution failed: {e}")
        
    return "DONE"