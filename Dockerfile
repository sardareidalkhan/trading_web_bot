FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    make \
    wget \
    build-essential \
    libffi-dev \
    python3-dev \
    libz-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    curl \
    libssl-dev \
    zlib1g-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    liblzma-dev \
    --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Build and install TA-Lib from source
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xvzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# Set library path for TA-Lib
ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Default command to run your app
CMD ["python", "run.py"]
