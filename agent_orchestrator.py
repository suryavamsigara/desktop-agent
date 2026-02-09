import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv
from executor.dispatcher import execute_tool
from executor.tools_list import tools
from logs.action_log import ActionLog

load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise EnvironmentError("GEMINI_API_KEY not set")

client = AsyncOpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)

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


async def run_agent(user_query: str, max_turns=50):
    log = ActionLog(goal=user_query)

    messages = [
        {
            "role": "system",
            "content": """You are a Hybrid Automation Agent.
            
            1. **CONTEXT MATTERS:**
               - If the task is inside a website, use `browser_*` tools (Playwright).
               - If the task is on the Windows Desktop (File Explorer, Settings, Spotify,....), use Desktop tools (`click_mouse`, `open_app`).

            2. **INTERACTIVE HELP:**
               - **NEVER GUESS** credentials, file paths, or ambiguous details.
               - If you encounter a Login Screen, missing file, or need clarification, call `ask_user`.
               - Example: "I need the password for GitHub."
            
            3. **BROWSER RULES:**
               - Always use `browser_get_tree` after navigating to see the page.
               - Prefer `browser_click` (semantic) over `click_mouse` (coordinates) when inside the browser.
            
            4. **GENERAL:**
               - Call one tool at a time.
               - If satisfied, return [FINAL ANSWER]...[/FINAL ANSWER].
            """
        },
        {"role": "user", "content": user_query},
    ]

    for turn in range(max_turns):
        print(f"\n──── Turn {turn+1} ────")

        response = await client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.2,
            # max_tokens=200, # 4096
        )

        message = response.choices[0].message

        messages.append(message)

        if message.content:
            print("🤖 Sentinel:", message.content)
            if "[FINAL ANSWER]" in message.content:
                print(message.content)

                log.log_final(message.content)
                return

        if message.tool_calls:
            for tool_call in message.tool_calls:
                print(f"⚡ Executing: {tool_call.function.name}")

                tool_result = await execute_tool(tool_call)

                print(f"✅ Result: {str(tool_result)[:100]}...")

                log.log_tool(
                    name=tool_call.function.name,
                    tool_input=tool_call.function.arguments,
                    tool_output=tool_result if len(tool_result) < 100 else tool_result[:100]
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(tool_result),
                    }
                )
        else:
            pass

    print(f"\nReached max turns ({max_turns}) without final answer.")
    return "Max turns reached. Last model message:\n" + (message.content or "")

