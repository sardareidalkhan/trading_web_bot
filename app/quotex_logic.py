import asyncio
import json
import os
import logging
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

SESSION_FILE = "quotex_session.json"

class QuotexLogic:
    def __init__(self):
        self.browser = None
        self.page = None
        self.context = None
        self.playwright = None
        self.is_initialized = False

    async def initialize_browser(self):
        """Initialize browser and reuse saved login session if available"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=False,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()
            await self.page.set_viewport_size({"width": 1920, "height": 1080})
            await self.page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })

            # Load session if available
            if os.path.exists(SESSION_FILE):
                with open(SESSION_FILE, "r") as f:
                    storage = json.load(f)
                await self.context.add_cookies(storage.get("cookies", []))
                await self.page.goto("https://quotex.io", wait_until="networkidle")
                if "localStorage" in storage:
                    for key, value in storage["localStorage"].items():
                        await self.page.evaluate(f"localStorage.setItem('{key}', '{value}')")

            await self.page.goto('https://quotex.io/en/demo-trade', wait_until='networkidle', timeout=30000)

            # If login is required, let user log in manually and save session
            if "sign-in" in self.page.url:
                print("🛑 Manual login required — please log in to Quotex.")
                print("✅ After logging in successfully, press ENTER here to continue...")
                input("⏸️ Waiting for manual login...")

                # Save session
                cookies = await self.context.cookies()
                local_storage = await self.page.evaluate("JSON.stringify(localStorage)")
                with open(SESSION_FILE, "w") as f:
                    json.dump({
                        "cookies": cookies,
                        "localStorage": json.loads(local_storage)
                    }, f)
                print("✅ Session saved — future runs will auto-login.")

            self.is_initialized = True
            logger.info("Browser initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Browser initialization failed: {str(e)}")
            return False

    async def close_browser(self):
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("Browser cleanup completed")
        except Exception as e:
            logger.error(f"Error during browser cleanup: {str(e)}")

    async def get_signal(self, symbol: str, timeframe: str, expiration: str):
        if not self.is_initialized:
            success = await self.initialize_browser()
            if not success:
                return {"signal": "error", "confidence": 0}

        try:
            # Wait for the signal element to appear on the page
            # IMPORTANT: Update these selectors to match actual Quotex page elements!
            await self.page.wait_for_selector("div.signal-indicator", timeout=15000)

            # Extract the signal text (e.g., "call" or "put")
            signal_element = await self.page.query_selector("div.signal-indicator")
            signal_text = (await signal_element.inner_text()).strip().lower() if signal_element else "error"

            # Extract confidence percentage text (e.g., "80%")
            confidence_element = await self.page.query_selector("span.confidence-value")
            confidence_text = await confidence_element.inner_text() if confidence_element else "0%"

            # Parse confidence number, fallback to 0 if invalid format
            try:
                confidence_value = float(confidence_text.strip('%')) / 100
            except Exception:
                confidence_value = 0

            # Validate signal_text; only accept "call" or "put"
            if signal_text not in ["call", "put"]:
                signal_text = "error"

            return {
                "signal": signal_text,
                "confidence": confidence_value
            }

        except Exception as e:
            logger.error(f"Error extracting signal: {str(e)}")
            return {"signal": "error", "confidence": 0}

        finally:
            await self.close_browser()
