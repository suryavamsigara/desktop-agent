import os
import requests
import asyncio
from typing import Any
from playwright.async_api import async_playwright

# Global state to keep the browser open between turns
SESSIONS: dict[str, Any] = {}

async def _ensure_session(session_id: str = "default") -> dict[str, Any]:
    if session_id in SESSIONS:
        return SESSIONS[session_id]
    
    print(f"Launching Browser Session: {session_id}")
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(
        headless=False,
        slow_mo=1000,
        args=["--start-maximized"]
    )
    context = await browser.new_context(no_viewport=True)
    page = await context.new_page()

    SESSIONS[session_id] = {"playwright": playwright, "browser": browser, "page": page}
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
    Clicks an element using semantic role/name or CSS selector
    """
    session = await _ensure_session()
    page = session["page"]
    try:
        if role and name:
            await page.get_by_role(role, name=name).click()
            return f"Clicked {role} '{name}'"
        elif selector:
            await page.click(selector)
            return f"Clicked selector '{selector}'"
        else:
            return f"Error: Provide (role+name) or selector"
    except Exception as e:
        return f"Click failed: {e}"

async def browser_type(value: str, label: str = None, selector: str = None, role: str = None, name: str = None):
    """
    Types into a field. Supports Label, Selector, OR Role+Name (e.g. role="combobox", name="Search").
    """
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
            return "Error: You must provide (role+name), 'label', or 'selector'."

        await target.click()
        await target.fill(value)
        await page.keyboard.press("Enter")
        
        return f"Typed '{value}' into {name or label or selector} and clicked enter."
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
    context = session["browser"].contexts[0]
    
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