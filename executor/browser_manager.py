import os
import requests
import asyncio
from typing import Any
from playwright.async_api import async_playwright

SESSIONS: dict[str, Any] = {}

async def _ensure_session(session_id: str = "default") -> dict[str, Any]:
    if session_id in SESSIONS:
        return SESSIONS[session_id]
    
    print(f"Launching Persistent Browser Session: {session_id}")
    
    # Path to store the profile (cookies, cache, etc.)
    user_data_dir = os.path.join(os.getcwd(), "browser_profiles", session_id)
    os.makedirs(user_data_dir, exist_ok=True)

    playwright = await async_playwright().start()
    
    context = await playwright.chromium.launch_persistent_context(
        user_data_dir,
        headless=False,
        channel="chrome",
        slow_mo=1000,
        args=[
            "--start-maximized",
            "--disable-blink-features=AutomationControlled"
        ],
        no_viewport=True,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    )

    page = context.pages[0] if context.pages else await context.new_page()

    SESSIONS[session_id] = {"playwright": playwright, "context": context, "page": page}
    return SESSIONS[session_id]

async def browser_navigate(url: str):
    session = await _ensure_session()
    try:
        await session["page"].goto(url, timeout=60000, wait_until="domcontentloaded")
        return f"Navigated to {url}"
    except Exception as e:
        return f"Error navigating to {url}: {e}"

async def browser_get_tree():
    session = await _ensure_session()

    try:
        return await session["page"].locator("body").aria_snapshot()
    except Exception as e:
        f"Error getting tree: {e}"

async def browser_click(role: str = None, name: str = None, selector: str = None):
    """
    Tries normal click -> Force click -> JS Click.
    """
    session = await _ensure_session()
    page = session["page"]
    
    try:
        target = None
        if role and name:
            target = page.get_by_role(role, name=name).first
        elif selector:
            target = page.locator(selector).first
        else:
            return "Error: Provide (role+name) or selector"

        try:
            await target.highlight()
        except:
            pass
        try:
            await target.click(timeout=2000)
            return f"✅ Clicked {name or selector}"
        except Exception as e:
            print(f"Standard click failed ({e}), escalating...")
        try:
            await target.click(force=True, timeout=2000)
            return f"Force-clicked {name or selector}"
        except Exception as e:
            print(f"Force click failed ({e}), escalating to JS...")

        await target.evaluate("element => element.click()")
        return f"JS-clicked {name or selector}"

    except Exception as e:
        return f"❌ All click methods failed: {e}"

async def browser_type(value: str, label: str = None, selector: str = None, role: str = None, name: str = None):
    session = await _ensure_session()
    page = session["page"]
    try:
        target = None
        if role and name:
            target = page.get_by_role(role, name=name).first
        elif label:
            target = page.get_by_label(label).first 
        elif selector:
            target = page.locator(selector).first
        
        if not target:
            return "Error: Target not found."
        await target.click(force=True)
        await target.press_sequentially(value, delay=50) 
        
        await page.keyboard.press("Enter")
        return f"Typed '{value}'"
    except Exception as e:
        return f"Typing failed: {str(e)}"

async def browser_scroll(direction: str = "down"):
    session = await _ensure_session()
    page = session["page"]
    key = "PageDown" if direction == "down" else "PageUp"
    await page.keyboard.press(key)
    await asyncio.sleep(1)
    return f"Scrolled {direction}"

async def browser_download(url: str, filename: str = None, session_id: str = "default"):
    """
    Downloads a file from a URL using the current browser session (cookies).
    - url: The direct link to the file.
    - filename: (Optional) Name to save as. If None, tries to guess from URL.
    """
    session = await _ensure_session(session_id)
    context = session["context"]
    
    try:
        cookies = await context.cookies()
        session_cookies = {c['name']: c['value'] for c in cookies}
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        if not filename:
            filename = url.split("/")[-1].split("?")[0]
            if not filename or "." not in filename:
                filename = "downloaded_file.pdf"

        download_dir = "downloads"
        os.makedirs(download_dir, exist_ok=True)
        filepath = os.path.join(download_dir, filename)

        print(f"⬇️ Downloading {url}...")
        response = requests.get(url, cookies=session_cookies, headers=headers, stream=True)
        response.raise_for_status()

        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return f"[FILE_DOWNLOADED] {filepath}"

    except Exception as e:
        return f"Download failed: {str(e)}"