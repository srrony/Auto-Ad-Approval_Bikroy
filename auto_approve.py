import asyncio
import re
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PWTimeout

# ========== CONFIGURATION ==========
URLS = [
    "https://admin.bikroy.com/item/68f8b27a06522345gfdd",
    # Add more links here
]

STORAGE_STATE = "bikroy_login.json"   # Will store your login session
HEADLESS = False                      # Keep False for first run (so you can log in)
BUTTON_CLASS = "ui-btn.is-secondary.btn-submit.has-busy.is-auto"
BUTTON_LABEL = "Save & Approve"
# ====================================


# ---------- LOGIN HANDLER ----------
async def ensure_login(context, page):
    """Ensures login and saves session if not already saved."""
    print("[i] Please log in manually in the browser window...")
    await page.goto(URLS[0], wait_until="load")
    input("👉 Press ENTER once you’re logged in and can see the page: ")
    await context.storage_state(path=STORAGE_STATE)
    print(f"[✔] Login session saved to {STORAGE_STATE}")


# ---------- LIMIT CHECKER ----------
async def check_ad_limit(page):
    """
    Detects text like '3 of 3 ads in Electronics Free' inside:
    <span class="ui-bubble is-membership-limits"> ... </span>
    Returns True if ad limit is full (AOL), else False.
    """
    selector = "span.ui-bubble.is-membership-limits"
    ts = datetime.now().strftime("%H%M%S")

    try:
        # Wait for the element to appear and be visible
        await page.wait_for_selector(selector, timeout=15000, state="visible")
        el = await page.query_selector(selector)
        if not el:
            print("   ⚠️ Span not found after wait — continuing.")
            return False

        # Read visible text
        raw = (await el.inner_text() or "").strip().replace("\n", " ")
        print(f"   🟡 Limit text: '{raw}'")

        # Normalize and parse
        txt = re.sub(r"[,\s]+", " ", raw)
        m = re.search(r"(\d+)\s*of\s*(\d+)", txt, re.IGNORECASE)
        if not m:
            print("   ⚠️ Couldn’t parse 'X of Y' — continuing.")
            return False

        cur, mx = int(m.group(1)), int(m.group(2))
        print(f"   📊 Parsed: {cur} of {mx}")

        if cur >= mx:
            print("   🚫 Limit reached (AOL). Skipping ad.")
            return True

        print("   ✅ Limit not full — continue normally.")
        return False

    except PWTimeout:
        print("   ⏳ Timeout waiting for limit span — continuing by default.")
        return False
    except Exception as e:
        print(f"   ❌ Error in check_ad_limit: {e}")
        await page.screenshot(path=f"debug_limit_error_{ts}.png", full_page=True)
        return False


# ---------- APPROVAL BUTTON HANDLER ----------
async def click_save_and_approve(page):
    """Clicks the 'Save & Approve' button by class and label."""
    selector = f"button.{BUTTON_CLASS}:has-text('{BUTTON_LABEL}')"
    try:
        await page.wait_for_selector(selector, timeout=15000)
        await page.locator(selector).click()
        print("   ✅ Clicked 'Save & Approve'")
        await page.wait_for_timeout(2000)
        return True
    except PWTimeout:
        print("   ⚠️ 'Save & Approve' button not found.")
        return False


# ---------- MAIN LOGIC ----------
async def process_ads():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        context = await browser.new_context(
            storage_state=STORAGE_STATE if Path(STORAGE_STATE).exists() else None
        )
        page = await context.new_page()

        # Handle login if needed
        if not Path(STORAGE_STATE).exists():
            await ensure_login(context, page)

        success, failed, skipped = [], [], []

        for idx, url in enumerate(URLS, 1):
            print(f"\n[{idx}/{len(URLS)}] Opening: {url}")
            try:
                await page.goto(url, wait_until="load", timeout=20000)
                await page.wait_for_load_state("domcontentloaded")

                # ✅ LIMIT CHECK
                limit_reached = await check_ad_limit(page)
                if limit_reached:
                    print("   ⛔ Skipped due to posting limit (AOL).")
                    skipped.append(url)
                    continue

                # ✅ APPROVAL
                clicked = await click_save_and_approve(page)
                if clicked:
                    success.append(url)
                else:
                    failed.append(url)

            except Exception as e:
                print(f"   ❌ Error on {url}: {e}")
                failed.append(url)

        # ---------- SUMMARY ----------
        print("\n========= SUMMARY =========")
        print(f"✅ Approved: {len(success)}")
        print(f"🚫 Skipped (AOL): {len(skipped)}")
        print(f"❌ Failed: {len(failed)}")
        if skipped:
            print("\nSkipped Ads (AOL):")
            for s in skipped:
                print(" -", s)
        print("===========================\n")

        await browser.close()


# ---------- RUNNER ----------
if __name__ == "__main__":
    asyncio.run(process_ads())
