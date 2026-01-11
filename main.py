from planner import state
from executor.dispatcher import execute

state["goal"] = input(">> ")

observation = ""

while not state["done"]:
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
    result = execute(plan)
    state["done"] = True

    print(result)
