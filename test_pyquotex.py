# test_pyquotex.py
import subprocess
from ai_analyzer import get_signal_from_chart

print("🚀 Running Quotex Signal Bot")

# Step 1: Capture chart
print("📸 Capturing chart from Quotex...")
subprocess.run(["python", "chart_capture.py"])

# Step 2: Analyze chart image
print("🧠 Analyzing chart...")
signal, expiry = get_signal_from_chart()

print(f"\n✅ Final Signal: {signal}")
print(f"⌛ Recommended Expiry Time: {expiry}")
