FROM continuumio/miniconda3

WORKDIR /app

# Copy environment setup files
COPY environment.yml .
COPY requirements.txt .

# Create Conda environment
RUN conda env create -f environment.yml
SHELL ["conda", "run", "-n", "tradingbot", "/bin/bash", "-c"]

# Install required Python packages
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m playwright install

# Copy full project files
COPY . .

# ✅ Download models from Google Drive (entire folder)
RUN pip install gdown
RUN python download_models.py

# Expose port for FastAPI
EXPOSE 8000

# Start your FastAPI app
CMD ["conda", "run", "--no-capture-output", "-n", "tradingbot", "python", "run.py"]
