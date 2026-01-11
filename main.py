from planner.state import state
from executor.dispatcher import execute
from agent_orchestrator import create_plan
from perception.screen import observe_screen

state["goal"] = input(">> ")

observation = ""

MAX_TURNS = 10
turns = 0

while not state["done"] and turns < MAX_TURNS:
    turns += 1
    plan = create_plan(observation)
    print(plan.model_dump())
    result = execute(plan)

    if result == "OBSERVE":
        observation = observe_screen()
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
