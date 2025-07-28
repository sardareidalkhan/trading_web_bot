FROM continuumio/miniconda3

WORKDIR /app

# Copy Conda and pip requirements
COPY environment.yml .
COPY requirements.txt .

# Create Conda environment
RUN conda env create -f environment.yml

# Activate Conda environment
SHELL ["conda", "run", "-n", "tradingbot", "/bin/bash", "-c"]

# ✅ Install system packages and build TA-Lib from source
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    curl \
    libffi-dev \
    python3-dev \
    && wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz \
    && tar -xvzf ta-lib-0.4.0-src.tar.gz \
    && cd ta-lib && ./configure --prefix=/usr && make && make install \
    && cd .. && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# ✅ Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m playwright install

# ✅ Copy project files and download models
COPY . .
RUN pip install gdown
RUN python download_models.py

# ✅ Expose FastAPI port
EXPOSE 8000

# ✅ Start app
CMD ["conda", "run", "--no-capture-output", "-n", "tradingbot", "python", "run.py"]
