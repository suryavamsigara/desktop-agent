from planner.state import state
from executor.dispatcher import execute_decision
from agent_orchestrator import next_decision
from perception.screen import observe_screen
from perception.vision import detect_clickables
from google.genai import types
from telegram_bot import main

# state["goal"] = input(">> ")

main()

contents = [
    types.Content(
        role="user",
        parts=[types.Part(text=f"GOAL: {state['goal']}")]
    ),
]

observation = ""

MAX_TURNS = 20
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
        observation, image = observe_screen()
        clickables = detect_clickables(image)
        
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part(text=f"""
                        CONTENT ON SCREEN: {observation}
                        ----------------------------------------
                        
                        {len(clickables)} clickable text elements detected
                        CLICKABLE OPTIONS: {[c['text'] for c in clickables]}
                """)]
            )
        )
        print(f"--Clickables--: {clickables}")

    elif result["type"] == "DONE":
        print("DONE")
        break
