# ✅ ai_analyzer.py (Multi-user Ready)

import logging
from pattern_detector import predict  # ✅ Uses updated predict()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_signal_from_chart(timeframe='1m', expiry='1m', image_dir="."):
    try:
        signal = predict(timeframe=timeframe, image_dir=image_dir)

        confidence = 90 if signal in ["UP", "DOWN"] else 0
        pattern = f"{timeframe.upper()} Chart Signal"

        logger.info(f"🧠 Final Signal: {signal} | Pattern: {pattern} | Confidence: {confidence}%")

        return {
            "direction": signal,
            "pattern": pattern,
            "confidence": confidence,
            "entry_delay": 10,
            "debug": {}
        }

    except Exception as e:
        logger.error(f"Analyzer error: {str(e)}")
        return {
            "direction": "ERROR",
            "confidence": 0,
            "entry_delay": 0,
            "error": str(e),
            "pattern": "Unknown",
            "debug": {}
        }
