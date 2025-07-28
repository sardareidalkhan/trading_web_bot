FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# System dependencies + TA-Lib
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    curl \
    git \
    gcc \
    libffi-dev \
    libgl1 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    python3-dev \
    unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install TA-Lib C library from source
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xvzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && \
    rm -rf ta-lib*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN pip install playwright==1.27.1 && playwright install --with-deps

# Copy all source code
COPY . .

# Default run command
CMD ["python", "run.py"]
