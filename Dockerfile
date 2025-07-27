FROM python:3.11-slim

# Install system dependencies (includes TA-Lib build tools)
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    curl \
    gcc \
    g++ \
    make \
    libffi-dev \
    python3-dev \
    libtool \
    autoconf \
    automake \
    && rm -rf /var/lib/apt/lists/*

# Build and install TA-Lib
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xvzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# Set path for TA-Lib
ENV LD_LIBRARY_PATH="/usr/lib:$LD_LIBRARY_PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir numpy==1.24.3
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Run FastAPI app
CMD ["python", "run.py"]
