FROM continuumio/miniconda3

# Set working directory
WORKDIR /app

# Copy environment config and requirements
COPY environment.yml .
COPY requirements.txt .  # ✅ This line is essential!

# Create Conda environment (includes TA-Lib prebuilt)
RUN conda env create -f environment.yml

# Use the new environment from now on
SHELL ["conda", "run", "-n", "tradingbot", "/bin/bash", "-c"]

# Copy all project files
COPY . .

# Install Playwright browsers
RUN python -m playwright install

# Expose port
EXPOSE 8000

# Start app
CMD ["python", "run.py"]
