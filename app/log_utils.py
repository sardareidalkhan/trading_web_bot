# ✅ log_utils.py — Phase 3 Logging System for Admin Panel

import os
import json
from datetime import datetime

LOG_PATH = os.path.join("logs", "predictions.json")

# Ensure directory and file exists
os.makedirs("logs", exist_ok=True)
if not os.path.exists(LOG_PATH):
    with open(LOG_PATH, "w") as f:
        json.dump([], f)

def log_prediction(user_email, symbol, platform, timeframe, direction, confidence):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "user": user_email,
        "symbol": symbol,
        "platform": platform,
        "timeframe": timeframe,
        "direction": direction,
        "confidence": confidence
    }

    with open(LOG_PATH, "r+") as f:
        data = json.load(f)
        data.insert(0, entry)  # latest first
        f.seek(0)
        json.dump(data[:100], f, indent=2)  # keep last 100 logs
        f.truncate()

def get_recent_logs(limit=20):
    with open(LOG_PATH, "r") as f:
        data = json.load(f)
    return data[:limit]
