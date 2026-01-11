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

def execute(plan):
    """
    Executes steps until observe
    """

    for step in plan.steps:

        if step.action == "observe":
            return "OBSERVE"
        
        if step.action not in ACTION_MAP:
            raise ValueError(f"Blocked action: {step.action}")
        
        fn = ACTION_MAP[step.action]

        try:
            if step.parameters is not None:
                fn(**step.parameters.model_dump())
            else:
                fn()

            state["last_action"] = step.action
            state["current_step"] += 1

        except Exception as e:
            state["errors"] += 1
            raise RuntimeError(f"Execution failed: {e}")
        
    return "DONE"