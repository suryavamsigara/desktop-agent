import asyncio
from agent_orchestrator import run_agent
# from telegram_bot import main

device = input(">> Terminal or Telegram\n>> ")

if (device == "Terminal" or device == "terminal"):
    goal = input(">> ")
    asyncio.run(run_agent(user_query=goal, max_turns=50))

# main()

