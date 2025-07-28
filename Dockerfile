FROM continuumio/miniconda3

WORKDIR /app

# Copy environment definition
COPY environment.yml .
COPY requirements.txt .

# Create the Conda environment
RUN conda env create -f environment.yml

# Activate environment for subsequent RUN commands
SHELL ["conda", "run", "-n", "tradingbot", "/bin/bash", "-c"]

# ✅ Install Python packages with pip
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Install Playwright browsers
RUN python -m playwright install

# Copy all source files
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run the app
CMD ["conda", "run", "--no-capture-output", "-n", "tradingbot", "python", "app/main.py"]
