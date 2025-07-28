FROM python:3.11-slim

# Install system-level dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    wget \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && apt-get clean

# Fix pip and install precompiled wheels
RUN pip install --upgrade pip wheel

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install --with-deps

# Copy app code
COPY . .

# Start command
CMD ["python", "run.py"]
