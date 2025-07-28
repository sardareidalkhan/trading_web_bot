FROM continuumio/miniconda3

WORKDIR /app

# Copy environment files
COPY environment.yml .
COPY requirements.txt .

# Create Conda environment (this installs everything in env + pip packages)
RUN conda env create -f environment.yml

# Use Conda environment for the rest of the steps
SHELL ["conda", "run", "-n", "tradingbot", "/bin/bash", "-c"]

# Copy entire project into the image
COPY . .

# Install Playwright browsers
RUN python -m playwright install

# Expose port (if using FastAPI or Flask)
EXPOSE 8000

# Run the app
CMD ["python", "app/main.py"]
