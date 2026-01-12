from .actions import *
from planner import state

ACTION_MAP = {
    "wait": wait,
    "type": type_text,
    "press": press_key,
    "hotkey": hot_key,
    "move_mouse": move_mouse,
    "click": click_mouse,
    "open_app": open_app,
    "screenshot": screenshot,
}

def execute_decision(decision):
    """
    Executes steps until observe
    """
    if decision.action == "observe":
        return {
            "type": "OBSERVE",
            "action": decision.action,
            "status": "Observing"
        }
    if decision.action == "done":
        return {
            "type": "DONE",
            "action": decision.action,
            "status": "SUCCESS"
        }

    fn = ACTION_MAP[decision.action]

    try:
        if decision.parameters is not None:
            fn(**decision.parameters.model_dump())
        else:
            fn()

        feedback = {
            "type": "ACTION_RESULT",
            "action": decision.action,
            "status": "SUCCESS",
            "details": "Completed successfully"
        }

        state["last_action"] = decision.action
        state["history"].append(decision.action)
        state["current_step"] += 1
        return feedback

    except Exception as e:
        state["errors"] += 1
        return {
            "type": "ACTION_RESULT",
            "action": decision.action,
            "status": "error",
            "details": str(e)
        }
