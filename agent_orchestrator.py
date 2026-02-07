import os
from openai import OpenAI
from dotenv import load_dotenv
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
