# app/updated_quotex_browser.py ✅ Final Fixed for Background Launch
import asyncio
import logging
from pyppeteer import launch

logger = logging.getLogger(__name__)

async def launch_background():
    try:
        logger.info("🚀 Launching Quotex browser in background...")

        browser = await launch(
            headless=False,  # Show browser (False = visible for debugging)
            userDataDir="./userdata",  # Keep session (no login required)
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )

        page = await browser.newPage()

        # ✅ Load Quotex platform directly
        await page.goto("https://market-qx.pro/en/trade", timeout=60000)

        # Optional: wait for main page element to confirm it's loaded
        await page.waitForSelector(".tab__item", timeout=15000)

        logger.info("✅ Quotex platform loaded successfully in background.")

    except Exception as e:
        logger.error(f"❌ Failed to launch background Quotex browser: {e}")