FROM python:3.11-slim

# Install system dependencies needed by TA-Lib
RUN apt-get update && apt-get install -y gcc make libta-lib0 libta-lib0-dev

# Install Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Start command (optional: if not specified inside your code)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
