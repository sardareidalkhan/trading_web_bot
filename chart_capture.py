# ✅ chart_capture.py (Multi-user safe version, FIXED & working as before)

import asyncio
from playwright.async_api import async_playwright
import cv2
import numpy as np
import os
import sys

# =============== SCREENSHOT SETTINGS =============== #
x_full = 8
y_full = 70
width_full = 494
height_full = 560

left_trim = 406    # trim from LEFT
right_trim = 0     # trim from RIGHT
top_trim = 0       # trim from TOP
bottom_trim = 0    # trim from BOTTOM
# =================================================== #

PROFILE_PATH = "quotex_user_data"
timeframe_arg = sys.argv[2] if len(sys.argv) > 2 else "1m"
raw_symbol = sys.argv[1] if len(sys.argv) > 1 else "EUR/JPY"
output_folder = sys.argv[3] if len(sys.argv) > 3 else "temp_data"

is_otc = "otc" in raw_symbol.lower()
search_symbol = raw_symbol.replace("OTC", "").replace("otc", "").strip()

SUPPORTED_TIMEFRAMES = [
    "5s", "10s", "15s", "30s", "1m", "2m", "3m",
    "5m", "10m", "15m", "30m", "1h", "4h", "1d"
]

async def capture_chart():
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(PROFILE_PATH, headless=False)
        page = browser.pages[0] if browser.pages else await browser.new_page()

        print("🌐 Opening Quotex demo trade page (with saved session)...")
        await page.goto("https://market-qx.pro/en/demo-trade", wait_until="networkidle")
        await page.wait_for_timeout(3000)

        if "login" in page.url or "sign-in" in page.url:
            print("🔐 Waiting for manual login (up to 60 seconds)...")
            for _ in range(60):
                await asyncio.sleep(1)
                if "trade" in page.url:
                    print("✅ Login completed.")
                    break
            else:
                print("❌ Login not completed in time.")
                await browser.close()
                return

        if timeframe_arg in SUPPORTED_TIMEFRAMES:
            print(f"🕒 Selecting timeframe: {timeframe_arg}")
            try:
                timeframe_dropdown_selector = "div#root > div:nth-of-type(1) > div:nth-of-type(1) > main:nth-of-type(1) > div:nth-of-type(1) > div:nth-of-type(1) > div:nth-of-type(5) > div:nth-of-type(3)"
                await page.click(timeframe_dropdown_selector)
                await page.wait_for_selector("div.popover-select__settings-time", timeout=5000)
                options = await page.query_selector_all("div.popover-select__settings-time-item")
                for opt in options:
                    label = await opt.inner_text()
                    if label.strip() == timeframe_arg:
                        await opt.click()
                        print(f"✅ Timeframe selected: {label}")
                        break
                await page.wait_for_timeout(1000)
            except Exception as e:
                print(f"⚠️ Could not select timeframe: {e}")
        else:
            print(f"⏳ Unsupported timeframe '{timeframe_arg}'. Aborting.")
            await browser.close()
            return

        print("🖱️ Dragging chart for alignment...")
        await page.mouse.move(600, 300)
        await page.mouse.down()
        await page.mouse.move(400, 300)
        await page.mouse.up()
        await page.wait_for_timeout(1000)

        try:
            print(f"🔁 Selecting asset: {raw_symbol} | Search: {search_symbol} | OTC: {is_otc}")
            await page.click("div.tab__label", timeout=5000)
            await page.wait_for_selector("input.asset-select__search-input", timeout=5000)
            await page.fill("input.asset-select__search-input", search_symbol)
            await page.wait_for_timeout(2000)

            items = await page.query_selector_all("div.assets-table__item")
            found = False
            for item in items:
                name_el = await item.query_selector("div.assets-table__name > span")
                if not name_el:
                    continue
                name = await name_el.inner_text()

                if is_otc and "(OTC)" in name and search_symbol.upper() in name:
                    await item.click()
                    found = True
                    break
                elif not is_otc and "(OTC)" not in name and search_symbol.upper() in name:
                    await item.click()
                    found = True
                    break

            if found:
                print(f"✅ Selected asset: {name}")
            else:
                print(f"❌ Asset not found: {raw_symbol}")
            await page.wait_for_timeout(3000)
        except Exception as e:
            print(f"⚠️ Error selecting asset: {e}")

        canvas = await page.query_selector("canvas.layer.plot")
        if canvas:
            raw_path = os.path.join(output_folder, "temp_chart.png")
            chart_path = os.path.join(output_folder, "chart.png")
            cropped_path = os.path.join(output_folder, "cropped_chart.png")

            await canvas.screenshot(path=raw_path)
            print("✅ Raw screenshot captured")

            image = cv2.imread(raw_path)
            full_img = image[y_full:y_full + height_full, x_full:x_full + width_full]
            cv2.imwrite(chart_path, full_img)
            print("✅ Saved full chart as chart.png")

            crop_x = x_full + left_trim
            crop_y = y_full + top_trim
            crop_w = width_full - left_trim - right_trim
            crop_h = height_full - top_trim - bottom_trim

            cropped_img = image[crop_y:crop_y + crop_h, crop_x:crop_x + crop_w]
            cv2.imwrite(cropped_path, cropped_img)
            print("✅ Saved cropped chart as cropped_chart.png")
        else:
            print("❌ Chart canvas not found!")

        await browser.close()

asyncio.run(capture_chart())
