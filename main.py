import asyncio
from agent_orchestrator import run_agent
from telegram_bot import run_telegram_bot

def main():
    print("Sentinel - 🤖 Desktop Automation Agent")
    print("1. Terminal Mode")
    print("2. Telegram Bot Mode")

    choice = input("Select Mode (1/2): ").strip()

    if choice == "1":
        goal = input("\nEnter: ")
        
        try:
            asyncio.run(run_agent(user_query=goal))
        except KeyboardInterrupt:
            print("\nStopped by user.")

    elif choice == "2":
        run_telegram_bot()
    
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()
