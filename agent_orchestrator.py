import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from google import genai
from google.genai import types
from planner.state import state
from planner.step import Decision

load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise EnvironmentError("GEMINI_API_KEY not set")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)

SYSTEM_PROMPT = """
    You are an automation agent.

    CRITICAL OUTPUT RULES (MUST FOLLOW):
    - You MUST return EXACTLY ONE action per response
    - You MUST return a SINGLE JSON OBJECT
    - ***You MUST observe** EVERYTIME screen changes or after every action to decide next step***
    - DO NOT return arrays or lists
    - DO NOT use the key "actions"
    - DO NOT return multiple steps
    - The top-level JSON MUST contain the key "action"
    - Wait after every action

    You MUST ALWAYS include a short "thought" describing what you're doing. The thought must be one sentence.
    You can press win to search for apps.


    VALID FORMAT (EXAMPLE):
    {
        "action": "open_app",
        "parameters": {
            "app_name": "Brave"
        }
    }

    Allowed actions:
    open_app, type, press, hotkey, click, scroll, wait, observe

    - observe shouldn't have parameters
    - parameters for click is 'target'

    If the goal is complete, return:
    { "action": "done" }

    Any violation of the format is incorrect.
"""

def convert_contents(contents):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    for c in contents:
        text = "\n".join(p.text for p in c.parts if p.text)
        messages.append({
            "role": "assistant" if c.role == "assistant" else "user",
            "content": text
        })
    return messages

def next_decision(contents: list[types.Content]) -> Decision:
    """
    Ask LLM what to do next based on goal + observation
    """
    messages = convert_contents(contents)

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        temperature=0.2,
        response_format={"type": "json_object"}
    )

    raw = response.choices[0].message.content

    if raw is None or not raw.strip():
        return Decision(action="done")

    contents.append(
        types.Content(
            role="assistant",
            parts=[types.Part(text=raw)]
        )
    )

    data = json.loads(raw)

    if data.get("action") in ("observe", "done"):
        if data.get("parameters") == {}:
            data.pop("parameters")

    try:
        return Decision.model_validate(data)
    except Exception as e:
        raise ValueError(f"Invalid plan from LLM: {e}")
    