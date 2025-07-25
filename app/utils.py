import asyncio
import os
import requests
from pyquotex import Quotex


def fetch_crypto_pairs(platform="binance"):
    platform = platform.lower()
    if platform == "binance":
        try:
            res = requests.get("https://api.binance.com/api/v3/exchangeInfo")
            data = res.json()
            symbols = [s["symbol"] for s in data["symbols"] if s["status"] == "TRADING"]
            return symbols
        except Exception as e:
            print(f"[ERROR] Binance pairs fetch failed: {e}")
            return []
    
    elif platform == "quotex":
        email = os.getenv("QX_EMAIL")
        password = os.getenv("QX_PASSWORD")

        if not email or not password:
            print("[ERROR] Quotex credentials missing in environment variables.")
            return []

        try:
            qx = Quotex(email=email, password=password)
            asyncio.run(qx.connect())
            pairs = asyncio.run(qx.get_all_assets())
            asyncio.run(qx.close())
            return pairs
        except Exception as e:
            print(f"[ERROR] Quotex pairs fetch failed: {e}")
            return []

    else:
        print(f"[WARNING] Unsupported platform: {platform}")
        return []


def get_price(pair: str, platform: str = "binance"):
    platform = platform.lower()
    print(f"⏳ Fetching price for {pair} from {platform}...")

    if platform == "quotex":
        email = os.getenv("QX_EMAIL")
        password = os.getenv("QX_PASSWORD")

        if not email or not password:
            print("[ERROR] Quotex credentials missing in environment variables.")
            return "Unavailable"

        try:
            qx = Quotex(email=email, password=password)
            asyncio.run(qx.connect())
            price = 123.456  # Replace with actual fetch logic
            asyncio.run(qx.close())
            return round(float(price), 5)
        except Exception as e:
            print(f"[ERROR] Quotex price fetch failed: {e}")
            return "Unavailable"

    else:  # Binance (via yfinance)
        import yfinance as yf
        try:
            if pair.endswith("USDT"):
                symbol = pair.replace("USDT", "-USD")
            else:
                symbol = pair

            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval="1m")

            if data.empty:
                raise ValueError(f"No data found for {symbol}")

            return round(data['Close'].iloc[-1], 2)
        except Exception as e:
            print(f"[ERROR] Binance price fetch failed: {e}")
            return "Unavailable"