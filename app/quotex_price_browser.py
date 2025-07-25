# app/quotex_price_browser.py

import asyncio
from pyppeteer import launch

USER_DATA_DIR = "./userdata"  # Persistent browser session

async def get_real_quotex_price(symbol: str) -> float:
    try:
        # Normalize asset name to format seen in Quotex
        formatted_symbol = symbol.upper().replace(" ", "").replace("/", "")

        # Launch browser with user data dir (persistent session)
        browser = await launch(
            headless=False,  # Set to True after first login
            userDataDir=USER_DATA_DIR,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )

        page = await browser.newPage()

        # Go to Quotex trading page
        await page.goto("https://market-qx.pro/en/trade", timeout=60000)

        # Wait for tab items to load
        await page.waitForSelector(".tab__item", timeout=20000)
        await asyncio.sleep(2)  # Give some time for assets to render

        # Select the price container for the asset
        price_selector = f'div[data-asset-id*="{formatted_symbol}"] .chart__price'
        await page.waitForSelector(".chart__price", timeout=20000)

        price_elements = await page.querySelectorAll(".chart__price")

        for el in price_elements:
            text = await (await el.getProperty("textContent")).jsonValue()
            text = text.strip().replace("$", "").replace(",", "")
            try:
                price = float(text)
                if price > 0:
                    await browser.close()
                    return round(price, 5)
            except ValueError:
                continue

        await browser.close()
        raise Exception(f"Unable to locate real-time price for {symbol}")

    except Exception as e:
        raise Exception(f"Failed to fetch real price: {e}")

# Test run
if __name__ == "__main__":
    price = asyncio.get_event_loop().run_until_complete(get_real_quotex_price("EUR/USD"))
    print("Real Quotex price:", price)
