from planner.state import state
from executor.dispatcher import execute
from agent_orchestrator import create_plan

state["goal"] = input(">> ")

observation = ""

while not state["done"]:
    plan = create_plan(observation)
    result = execute(plan)

    if result == "OBSERVE":
        state["done"] = True
    else:
        state["done"] = True

    print(result)




"""
plan = {
        "steps": [
            {"action": "open_app", "app_name": "brave"},
            {"action": "wait", "seconds": 2},
            {"action": "move_mouse", "x": 500, "y": 60},
            {"action": "click"},
            {"action": "type", "text": "black holes"},
            {"action": "press", "key": "enter"}
        ]
    }
"""
