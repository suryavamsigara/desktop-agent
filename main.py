from agent_orchestrator import run_agent
# from telegram_bot import main

goal = input(">> ")

# main()

run_agent(user_query=goal, max_turns=20)
