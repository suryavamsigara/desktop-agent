import os
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types
from planner.state import state
from planner.step import Step

class Plan(BaseModel):
    steps: list[Step]
    description: Optional[str] = None


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise EnvironmentError("GEMINI_API_KEY not set")

client = genai.Client(api_key=api_key)

SYSTEM_PROMPT = """
    You are an automation planning agent.

    Rules:
    - You DO NOT execute actions
    - You ONLY output structured JSON
    - Use ONLY allowed actions
    - Never hallucinate coordinates unless necessary
    - Use observe ONLY if you must read screen content or next action depends on reading screen content.
    - Do NOT observe between deterministic actins.
    - Continue from the current state

    Allowed actions:
    open_app, type, press, click, wait, observe

    Output must strictly follow the JSON schema.
"""

def create_plan(observation: str = "") -> Plan:
    """
    Ask LLM what to do next based on goal + observation
    """

    user_prompt = f"""
        GOAL: {state["goal"]}

        ALREADY EXECUTED ACTIONS:
        {state["history"]}
        
        LAST OBSERVATION: {observation if observation else None}

        What should be done next?
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=[
            types.Content(
                role="user",
                parts=[types.Part(text=user_prompt)]
            )
        ],
        config={
            "system_instruction": SYSTEM_PROMPT,
            "response_mime_type": "application/json",
            "response_json_schema": Plan.model_json_schema(),
        },
    )

    try:
        return Plan.model_validate_json(response.text)
    except Exception as e:
        raise ValueError(f"Invalid plan from LLM: {e}")
    