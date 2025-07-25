import random

# --- Binance Crypto Signal Generator ---
def generate_crypto_signal(pair, timeframe):
    market_condition = random.choice(["Trending", "Ranging", "Volatile"])
    coin_volatility = random.choice(["Low", "Medium", "High"])
    confidence = random.randint(75, 97)

    # Auto-indicator selection based on timeframe & market
    def select_indicators(tf, volatility, condition):
        if tf == "1m" and condition == "Volatile":
            return ["VWAP", "EMA 3", "RSI 2"]
        elif tf == "5m" and condition == "Trending":
            return ["MACD", "Supertrend"]
        elif tf == "1h" and volatility == "Low":
            return ["Ichimoku", "ADX 14"]
        else:
            return ["Bollinger Bands", "Stochastic", "EMA 5"]

    indicators = select_indicators(timeframe, coin_volatility, market_condition)
    direction = random.choice(["UP", "DOWN"])

    return {
        "signal": direction,
        "strategy": f"Using {', '.join(indicators)} optimized for {market_condition.lower()} market",
        "confidence": confidence,
        "entry_delay": "N/A",
        "market_condition": market_condition,
        "volatility": coin_volatility,
        "predicted": round(random.uniform(100, 500), 2),
        "stop_loss": round(random.uniform(80, 99), 2),
        "tp1": round(random.uniform(101, 510), 2),
        "tp2": round(random.uniform(120, 530), 2),
        "tp1_hit": random.randint(65, 85),
        "tp2_hit": random.randint(50, 75),
        "accuracy": random.randint(80, 96),
        "indicators": indicators
    }

# --- Quotex Binary Signal Generator ---
def generate_binary_signal(pair, timeframe, trade_time="1m"):
    """
    Generates a binary-style signal for Quotex.
    Args:
        pair (str): e.g., 'BTCUSDT'
        timeframe (str): e.g., '1m', '5m'
        trade_time (str): Binary trade length, e.g. '30s', '1m'
    Returns:
        dict: signal, reason, confidence, entry_delay
    """
    trend = random.choice(["UP", "DOWN"])
    confidence = random.randint(85, 99)
    entry_delay = random.choice([5, 10, 15, 20, 30])

    indicators = ["Heikin-Ashi", "Stochastic RSI", "EMA 3", "Volume Spikes"]

    return {
        "signal": trend,
        "strategy": f"Scalping with {', '.join(indicators)} for short-term binary setup",
        "confidence": confidence,
        "entry_delay": entry_delay,
        "market_condition": "Short-term momentum",
        "volatility": "High",
        "predicted": "N/A",
        "stop_loss": "N/A",
        "tp1": "N/A",
        "tp2": "N/A",
        "tp1_hit": "N/A",
        "tp2_hit": "N/A",
        "accuracy": random.randint(88, 99),
        "indicators": indicators
    }
