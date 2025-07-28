# Use official Python image with Anaconda (includes TA-Lib)
FROM continuumio/miniconda3:latest

# Set working directory
WORKDIR /app

# Install TA-Lib C library and other dependencies
RUN apt-get update && \
    apt-get install -y wget build-essential && \
    wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xvzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib && \
    ./configure --prefix=/usr && make && make install && \
    cd .. && rm -rf ta-lib*

# Install Python packages using conda (faster + prebuilt TA-Lib)
COPY environment.yml .
RUN conda env create -f environment.yml
SHELL ["conda", "run", "-n", "tradingbot", "/bin/bash", "-c"]

# Copy app files
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
