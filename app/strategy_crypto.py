import ccxt
import pandas as pd
import pandas_ta as ta
import requests
import os
from datetime import datetime
from textblob import TextBlob
from dotenv import load_dotenv

load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

STABLE_COINS = ["BTC/USDT", "ETH/USDT", "BNB/USDT"]

# Fetch OHLCV
def fetch_ohlcv(symbol, timeframe="1m", limit=150):
    if "/" not in symbol and "USDT" in symbol:
        symbol = symbol.replace("USDT", "/USDT")
    binance = ccxt.binance()
    ohlcv = binance.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df

# Detect market condition
def classify_market(df):
    df["ema"] = ta.ema(df["close"], length=20)
    volatility = df["close"].std()
    trend_strength = abs(df["close"].iloc[-1] - df["ema"].iloc[-1])
    if trend_strength > volatility:
        return "trending"
    elif volatility > 1.5:
        return "volatile"
    else:
        return "ranging"

# Sentiment score from news
def get_sentiment_score(symbol):
    try:
        query = symbol.replace("/", "").replace("USDT", "")
        url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&pageSize=5&apiKey={NEWS_API_KEY}"
        articles = requests.get(url).json().get("articles", [])
        text = " ".join([a["title"] + a.get("description", "") for a in articles])
        polarity = TextBlob(text).sentiment.polarity
        return round((polarity + 1) * 50, 2)  # Scale 0-100
    except:
        return 50.0

# Choose indicators based on context
def select_indicators(symbol, timeframe, market_type):
    stable = symbol.upper() in STABLE_COINS
    tf = timeframe.lower()
    if tf == "1m":
        return ["ema_9", "rsi_5", "vwap"]
    elif tf in ["3m", "5m"]:
        return ["macd", "supertrend"] if market_type == "trending" else ["rsi", "bollinger"]
    elif tf in ["15m", "30m"]:
        return ["adx", "ichimoku"] if stable else ["stoch", "cci"]
    elif tf in ["1h", "2h"]:
        return ["ema_20", "macd"] if market_type == "trending" else ["rsi", "sma"]
    elif tf in ["4h", "1d", "1w"]:
        return ["sar", "ema_50"] if stable else ["stoch", "adx"]
    return ["rsi"]

# Smart indicator agreement logic
def evaluate_agreement(indicators):
    agreed = 0
    if "rsi" in indicators or "rsi_5" in indicators:
        agreed += 1
    if "macd" in indicators or "ema_9" in indicators or "ema_20" in indicators or "ema_50" in indicators:
        agreed += 1
    if "bollinger" in indicators or "vwap" in indicators:
        agreed += 1
    return agreed >= 2

# Final Signal Generator
def generate_signal(symbol, timeframe="1m"):
    df = fetch_ohlcv(symbol, timeframe)
    market_type = classify_market(df)
    sentiment = get_sentiment_score(symbol)
    indicators = select_indicators(symbol, timeframe, market_type)
    close = df["close"].iloc[-1]

    # TP multipliers per timeframe
    tp_multipliers = {
        "1m": 1.001,
        "3m": 1.0015,
        "5m": 1.002,
        "15m": 1.004,
        "30m": 1.006,
        "1h": 1.01,
        "2h": 1.015,
        "4h": 1.02,
        "1d": 1.03,
        "1w": 1.05
    }
    multiplier = tp_multipliers.get(timeframe, 1.005)
    tp = round(close * multiplier, 5)

    # Accuracy Calculation
    agreement = evaluate_agreement(indicators)
    accuracy = 50
    if agreement:
        accuracy += 10
    else:
        accuracy -= 15  # Penalize for no strong agreement
    if market_type == "trending":
        accuracy += 10
    if sentiment >= 60 or sentiment <= 40:
        accuracy += 10
    if market_type == "volatile":
        accuracy -= 5
    accuracy = max(20, min(accuracy, 99))

    # Always return UP/DOWN based on sentiment
    direction = "UP" if sentiment >= 50 else "DOWN"

    print(f"[DEBUG] {symbol} | TF: {timeframe} | Price: {close} | TP: {tp} | Dir: {direction} | Accuracy: {accuracy}%")

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "trend": market_type,
        "price": close,
        "direction": direction,
        "indicators": indicators,
        "tp": tp,
        "accuracy": f"{accuracy}%"
    }

# Manual test
if __name__ == "__main__":
    s = generate_signal("BTC/USDT", "1m")
    for k, v in s.items():
        print(f"{k.upper()}: {v}")
