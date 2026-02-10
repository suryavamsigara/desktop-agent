import os
import json
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

async def default_output_handler(text: str):
    """Default: Print"""
    print(f"\n{text}")

async def default_input_handler(question: str) -> str:
    """Default: Ask user via temrinal"""
    return input(f"\n[Sentinel Asking]: {question}\nAnswer: ")

import re

def extract_final_text(text: str) -> str:
    pattern = r"(?i)(?:^|\n)\s*\[FINAL ANSWER\]"
    
    match = re.search(pattern, text)
    
    if match:
        start_index = match.end()
        end_tag = "[/FINAL ANSWER]"
        end_index = text.find(end_tag, start_index)
        
        if end_index == -1:
            return text[start_index:].strip()
        return text[start_index:end_index].strip()
    return text.strip()


async def run_agent(user_query: str,
    max_turns=50,
    output_handler=default_output_handler,
    input_handler=default_input_handler
):
    log = ActionLog(goal=user_query)

    messages = [
        {
            "role": "system",
            "content": """You are a Hybrid Automation Agent.
            
            1. **CONTEXT MATTERS:**
               - If the task is inside a website, use `browser_*` tools (Playwright).
               - If the task is on the Windows Desktop (File Explorer, Settings, Spotify,....), use Desktop tools.

            2. **INTERACTIVE HELP:**
               - **NEVER GUESS** credentials, file paths, or ambiguous details.
               - If you encounter a Login Screen, missing file, or need clarification, call `ask_user`.
               - Example: "I need the password for GitHub."
            
            3. **BROWSER RULES:**
               - Always use `browser_get_tree` after navigating to see the page.
               - Prefer `browser_click` (semantic) over `click_mouse` (coordinates) when inside the browser.
               - If you fail to click an option inside a dropdown, try clicking the dropdown first, then sending the 'ArrowDown' and 'Enter' keys using the press_key tool.
               - Open through browser navigate
               - *If a tool fails*, you **must** get the browser tree to see what happened and what to do, and whether it really failed.

            4. **DESKTOP RULES:**
               - You can open apps other than browsers by clicking win and typing the app name, then enter.
               - Get accessibility tree OFTEN to see what to click.
               - DO NOT spam key presses.

            4. **GENERAL:**
               - Call one tool at a time.
               - If satisfied, return [FINAL ANSWER]...[/FINAL ANSWER].
               - If the user greets, talk and have a normal conversation.
               - Don't start to do anything if the user doesn't tell.

            5.  To post on X/Twitter, you can click Post in the sidebar and write and post.
            """
        },
        {"role": "user", "content": user_query},
    ]

    for turn in range(max_turns):
        await output_handler(f"Thinking... (Turn {turn+1})")

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
            await output_handler(f"🤖 Sentinel: {message.content}")
            if "[FINAL ANSWER]" in message.content:
                log.log_final(message.content)
                return

        if message.tool_calls:
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                args = tool_call.function.arguments
                await output_handler(f"⚡ Executing: {func_name}")

                if func_name == "ask_user":
                    q_args = json.loads(args)
                    user_reply = await input_handler(q_args["question"])
                    tool_result = f"User replied: {user_reply}"
                else:
                    tool_result = await execute_tool(tool_call)

                await output_handler(f"✅ Result: {str(tool_result)[:100]}...")

                MAX_LEN = 50000

                if len(tool_result) > MAX_LEN:
                    tool_result = tool_result[:MAX_LEN] +"\n...[Output truncated due to length]..."

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


# Telegram
async def run_agent_telegram(
    user_query: str,
    max_turns=50,
    output_handler=default_output_handler,
    input_handler=default_input_handler
):
    log = ActionLog(goal=user_query)

    messages = [
        {
            "role": "system",
            "content": """You are a Hybrid Automation Agent. You're being operated remotely from telegram.
            
            1. **CONTEXT MATTERS:**
               - If the task is inside a website, use `browser_*` tools (Playwright).
               - If the task is on the Windows Desktop (File Explorer, Settings, Spotify,....), use Desktop tools.

            2. **INTERACTIVE HELP:**
               - **NEVER GUESS** credentials, file paths, or ambiguous details.
               - If you encounter a Login Screen, missing file, or need clarification, call `ask_user`.
               - Example: "I need the password for GitHub."
            
            3. **BROWSER RULES:**
               - Always use `browser_get_tree` after navigating to see the page.
               - Prefer `browser_click` (semantic) over `click_mouse` (coordinates) when inside the browser.
               - Before clicking hot keys (ctrl+a/backspace), make sure the focus is on the area to prevent deleting something else.
               - Open through browser navigate
               - If a tool/method fails, you **MUST** get the browser tree to see what happened, what to do, and whether it really failed.

            4. **DESKTOP RULES:**
               - You can open apps other than browsers by clicking win and typing the app name, then enter.
               - Get accessibility tree OFTEN to see what to click.
               - DO NOT spam key presses.
            
            5. **GENERAL:**
               - Call one tool at a time.
               - If satisfied, return [FINAL ANSWER]...[/FINAL ANSWER].
               - Downloaded files are *automatically* sent to the user via telegram.
            
            6. **Chatting:** If the user just says "Hi" or asks a general question, just reply naturally.

            7.  To post on X/Twitter, you can click Post in the sidebar and write and post. Post should be very short because it has a character limit.
            """
        },
        {"role": "user", "content": user_query},
    ]

    await output_handler("Working on it..")

    recent_actions_buffer = []
    SUMMARY_INTERVAL = 5

    for turn in range(max_turns):
        print(f"Thinking... (Turn {turn+1})")
        if turn > 0 and turn % SUMMARY_INTERVAL == 0 and recent_actions_buffer:
            history_text = "\n".join(recent_actions_buffer)

            summary = await summarize_progress(history_text)

            if summary:
                await output_handler(f"📝 Update: {summary}")
            
            recent_actions_buffer = []
        response = await client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.2,
        )

        message = response.choices[0].message
        messages.append(message)

        if message.content:
            clean_text = message.content
            print(f"🤖 Sentinel: {clean_text}")
            if "[FINAL ANSWER]" in message.content:
                final_text = extract_final_text(message.content)
                await output_handler(f"🤖 {final_text}")
                log.log_final(final_text)
                return

            if not message.tool_calls:
                await output_handler(f"{clean_text}")

        if message.tool_calls:
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                args = tool_call.function.arguments

                recent_actions_buffer.append(f"Action: {func_name} {args}")

                print(f"⚡ Executing: {func_name}")

                if func_name == "ask_user":
                    q_args = json.loads(args)
                    user_reply = await input_handler(q_args["question"])
                    tool_result = f"User replied: {user_reply}"
                else:
                    tool_result = await execute_tool(tool_call)

                recent_actions_buffer.append(f"Result: {str(tool_result)[:100]}")
                
                if "[FILE_DOWNLOADED]" in str(tool_result):
                    await output_handler(str(tool_result))
                
                print(f"✅ Result: {str(tool_result)[:100]}...")

                log.log_tool(name=func_name, tool_input=args, tool_output=tool_result[:200])

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(tool_result)
                })
        else:
            print("No tools called. Ending turn to wait for user.")
            return
    await output_handler("⚠️ Max turns reached. Stopping..")


async def summarize_progress(history_text: str) -> str:
    """
    Takes raw execution logs and converts them into a 1-sentence status update.
    """
    if not history_text.strip():
        return ""

    messages = [
        {
            "role": "system",
            "content": """You are a progress reporter. 
            Read the recent technical execution logs and output a SINGLE sentence explaining what was just accomplished.
            - No technical jargon (don't say 'clicked selector .btn').
            - Say things like "I navigated to YouTube and searched for the video."
            - Be brief.
            """
        },
        {"role": "user", "content": f"Logs:\n{history_text}"},
    ]

    try:
        response = await client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.7,
            max_tokens=60
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return ""
    