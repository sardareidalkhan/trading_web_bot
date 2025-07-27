FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    make \
    wget \
    build-essential \
    libffi-dev \
    python3-dev \
    --no-install-recommends

# Build and install TA-Lib from source
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xvzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your code
COPY . .

# Start command
CMD ["python", "run.py"]
