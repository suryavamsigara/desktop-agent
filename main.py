from planner.state import state
from executor.dispatcher import execute_decision
from agent_orchestrator import next_decision
from perception.screen import observe_screen
from google.genai import types

state["goal"] = input(">> ")

contents = [
    types.Content(
        role="user",
        parts=[types.Part(text=f"GOAL: {state['goal']}")]
    ),
]

observation = ""

MAX_TURNS = 10
turns = 0

while True and turns < MAX_TURNS:
    turns += 1

    decision = next_decision(contents)
    print(f"\nDecision:\n{decision.model_dump()}")

    if (decision.action == state["last_action"] and decision.action != "observe"):
        print("Duplicate action detected, forcing observe.")
        observation = observe_screen()
        continue

    result = execute_decision(decision)

    result_text = f"""
    ACTION EXECUTED: {decision.action}

    STATUS: {result['status']}

    DETAILS: {result['details']}
    """
    contents.append(
        types.Content(
            role="user",
            parts=[types.Part(text=result_text)]
        )
    )

    print(f"Result: {result}\n-----------\n")

    if result["type"] == "OBSERVE":
        observation = observe_screen()
        
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part(text=f"SCREEN OBSERVATION:\n{observation}")]
            )
        )
        print(f"--Observation--: {observation}")

    elif result["type"] == "DONE":
        print("DONE")
        break




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
