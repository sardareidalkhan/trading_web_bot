import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context("quotex_user_data", headless=False)
        page = browser.pages[0] if browser.pages else await browser.new_page()

        print("🌐 Opening Quotex page for click inspection...")
        await page.goto("https://market-qx.pro/en/demo-trade", wait_until="load")

        # 🛑 Wait until user logs in
        if "login" in page.url or "sign-in" in page.url:
            print("🔐 Waiting for you to log in manually...")
            for i in range(60):
                await asyncio.sleep(1)
                if "trade" in page.url:
                    print("✅ Login successful.")
                    break
            else:
                print("❌ Login not detected after 60 seconds. Exiting.")
                await browser.close()
                return
            await page.goto("https://market-qx.pro/en/demo-trade", wait_until="networkidle")
            await page.wait_for_timeout(3000)

        print("⏳ Waiting for you to click on the timeframe dropdown (like 1m)...")
        await page.evaluate("""
            () => {
                window.clickedElement = null;
                document.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    window.clickedElement = e.target;
                }, { once: true });
            }
        """)

        for _ in range(40):
            result = await page.evaluate("window.clickedElement !== null")
            if result:
                break
            await asyncio.sleep(0.5)

        if not await page.evaluate("window.clickedElement !== null"):
            print("❌ No click detected. Please try again.")
            await browser.close()
            return

        # Get outer HTML
        html = await page.evaluate("window.clickedElement.outerHTML")

        # Inject CSS path function
        await page.add_script_tag(content="""
            window.getElementSelector = function(el) {
                if (!(el instanceof Element)) return '';
                const path = [];
                while (el.nodeType === Node.ELEMENT_NODE) {
                    let selector = el.nodeName.toLowerCase();
                    if (el.id) {
                        selector += '#' + el.id;
                        path.unshift(selector);
                        break;
                    } else {
                        let sib = el, nth = 1;
                        while (sib = sib.previousElementSibling) {
                            if (sib.nodeName.toLowerCase() == selector)
                                nth++;
                        }
                        selector += `:nth-of-type(${nth})`;
                    }
                    path.unshift(selector);
                    el = el.parentNode;
                }
                return path.join(" > ");
            };
        """)
        selector = await page.evaluate("getElementSelector(window.clickedElement)")

        print("\n✅ Inspector finished. Here is the clicked element info:\n")
        print("🔽 HTML:\n", html)
        print("\n🔽 Selector:\n", selector)
        print("\n📋 Copy both and send them to ChatGPT.")

        await asyncio.sleep(3)
        await browser.close()

asyncio.run(run())
