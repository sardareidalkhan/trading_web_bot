FROM continuumio/miniconda3

WORKDIR /app

# Copy environment setup files
COPY environment.yml .
COPY requirements.txt .

# Create Conda environment
RUN conda env create -f environment.yml

# Activate Conda env for following commands
SHELL ["conda", "run", "-n", "tradingbot", "/bin/bash", "-c"]

# Install required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright
RUN python -m playwright install

# Copy full project
COPY . .

# ✅ Download models from Google Drive folder
RUN pip install gdown
RUN python download_models.py

# Expose the FastAPI port
EXPOSE 8000

# Start your app (uses updated run.py with dynamic port)
CMD ["conda", "run", "--no-capture-output", "-n", "tradingbot", "python", "run.py"]
