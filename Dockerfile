FROM continuumio/miniconda3

WORKDIR /app

# Copy environment setup files
COPY environment.yml .
COPY requirements.txt .

# Create Conda environment
RUN conda env create -f environment.yml

# Activate Conda environment for all next commands
SHELL ["conda", "run", "-n", "tradingbot", "/bin/bash", "-c"]

# 🛠️ Install required system libs for TA-Lib
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    curl \
    libffi-dev \
    libta-lib0 \
    libta-lib-dev

# 🐍 Install Python packages
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m playwright install

# 📁 Copy the entire project and download model folder
COPY . .
RUN pip install gdown
RUN python download_models.py

# 🌐 Expose the port (Render will use it)
EXPOSE 8000

# 🚀 Start the app using run.py with proper dynamic port handling
CMD ["conda", "run", "--no-capture-output", "-n", "tradingbot", "python", "run.py"]
