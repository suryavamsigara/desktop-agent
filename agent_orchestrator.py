import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from google.genai import types
from planner.state import state
from planner.step import Decision
from executor.dispatcher import execute_tool
from executor.tools_list import tools
from logs.action_log import ActionLog

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

def extract_final_text(text: str) -> str:
    start_tag = "[FINAL ANSWER]"
    end_tag = "[/FINAL ANSWER]"

    if start_tag in text:
        start = text.find(start_tag) + len(start_tag)
        end = text.find(end_tag, start)
        if end == -1:
            return text[start:].strip()
        return text[start:end].strip()
    return text.strip()


def run_agent(user_query: str, max_turns=20):
    log = ActionLog(goal=user_query)

    messages = [
        {
            "role": "system",
            "content": """You are an automation agent.
            
            Call **only one tool at a time** unless they are clearly independent and parallel.
            Use the exact format for tool calls.
            After executing a tool, decide based on the result.
            Observe after everytime screen changes.
            If the user's request is now fully satisfied, immediately output the final answer wrapped in [FINAL ANSWER]…[/FINAL ANSWER].
            Do not continue calling tools unnecessarily.
            """
        },
        {"role": "user", "content": user_query},
    ]

    for turn in range(max_turns):
        print(f"\n──── Turn {turn+1} ────")

        # print("Messages so far:")
        # print(json.dumps(messages, indent=2, default=str))
        # print("=" * 60)

        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.3,
            max_tokens=200, # 4096
        )

        message = response.choices[0].message

        if hasattr(message, "reasoning_content") and message.reasoning_content:
            print(f"Reasoning: ", message.reasoning_content.strip())
        
        if message.content:
            print("Content: ", message.content.strip())
        
        clean_message = {
            "role": message.role
        }

        if message.content is not None:
            clean_message["content"] = message.content
        if message.tool_calls:
            clean_message["tool_calls"] = message.tool_calls
        if hasattr(message, "reasoning_content") and message.reasoning_content:
            clean_message["reasoning_content"] = message.reasoning_content

        messages.append(clean_message)
        # print("*"*60)
        # print(message)
        # print("*"*50)

        if message.content and "[FINAL ANSWER]" in message.content:
            final_text = extract_final_text(message.content)
            print("\n Final answer found.")
            print(final_text)

            # Log the final answer in action_log.json
            log.log_final(final_text)
            return
        
        if not message.tool_calls:
            print("No tool calls and no [FINAL ANSWER]")
            return message.content.strip() if message.content else "Completed"

        for tool_call in message.tool_calls:
            tool_result = execute_tool(tool_call)

            # Logging the tool in action_log.json
            log.log_tool(
                name=tool_call.function.name,
                tool_input=tool_call.function.arguments,
                tool_output=tool_result if len(tool_result) < 100 else tool_result[:100]
            )

            print(f"-> {tool_call.function.name} -> {tool_result}")

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.function.name,
                    "content": tool_result,
                }
            )
        

    print(f"\nReached max turns ({max_turns}) without final answer.")
    return "Max turns reached. Last model message:\n" + (message.content or "")











run_agent("open youtube on brave")





        


















        



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
