# open_quotex_hd.py

import asyncio
from playwright.async_api import async_playwright

PROFILE_PATH = "quotex_user_data"  # Your persistent Chrome profile

async def open_quotex_hd():
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_PATH,
            headless=False,
            args=[
                "--window-position=0,0",
                "--window-size=1366,720",  # Exact visible screen size
                "--disable-infobars",  # Removes automation banner
                "--start-maximized",
                "--force-device-scale-factor=1",
                "--disable-blink-features=AutomationControlled",  # Hide "controlled by automation"
            ]
        )
        page = browser.pages[0] if browser.pages else await browser.new_page()

        print("🌐 Opening Quotex in perfect native view...")
        await page.goto("https://market-qx.pro/en/demo-trade")

        print("✅ Quotex opened perfectly (same as personal browser).")
        print("📸 Take screenshots for ML now with full chart, zoom buttons, and time bar.")
        print("⏸️ Keep this window open while working.")
        await asyncio.sleep(9999)

asyncio.run(open_quotex_hd())
