# Sentinel - AI That Controls Your Computer

Imagine telling your computer:
> "Open YouTube, find the last video I watched and write a post about it on Twitter."
..and it **just does it** in a **human like manner**.

**Sentinel is that agent.**

It's an open-source, 'always-on', LLM-powered automation system you can chat with through telegram.
It combines:
- **Real Desktop Control** (Windows apps, FIle Explorer, Settings, Spotify,..) using accessibility trees and keyboard/mouse simulation.
- **Full Browser Automation** (Playwright + persistent Chrome sessions in headed mode)
- **Natural Language Understanding** powered by OpenAI compatible model

All in **one agent loop** that reasons, acts, asks you when stuck, downloads files, and gives updates.

## Demo:

https://github.com/user-attachments/assets/9f3650df-4dbd-46ba-8990-087a33256aff

## Examples of what it can do: (The following are sent via telegram)
1. "Download the latest paper from DeepSeek and send it."
2. "I'm driving now. Order chapathi and biryani on Zomato."
3. "I'm outside I forgot to submit (a file). It's on my computer. Send it to me."
4. "Open my github, rate my profile, go through the projects and add README.md for the repositories that don't have it."

### Installation:
```
# 1. Clone the repo
git clone https://github.com/suryavamsigara/desktop-agent.git
cd desktop-agent

# 2. Create virtual env and install
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 3. Set environment variables
DEEPSEEK_API_KEY="your api key"
TELEGRAM_BOT_TOKEN="your token" # Not required if you wish to run from the terminal

# 4. Run it
python main.py
```
