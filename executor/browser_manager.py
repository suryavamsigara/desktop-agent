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

async def browser_type(value: str, label: str = None, selector: str = None):
    session = await _ensure_session()
    page = session["page"]
    try:
        target = page.get_by_label(label) if label else page.locator(selector)
        await target.click()
        await target.fill(value)
        await page.keyboard.press("Enter")
        return f"Typed '{value}' into {label or selector}"
    except Exception as e:
        return f"Typing failed: {e}"

async def browser_scroll(direction: str = "down"):
    session = await _ensure_session()
    page = session["page"]
    key = "PageDown" if direction == "down" else "PageUp"
    await page.keyboard.press(key)
    await asyncio.sleep(1)
    return f"Scrolled {direction}"
