# Use the official Playwright image which comes with all OS dependencies pre-installed
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Set work directory
WORKDIR /app

# Copy your requirements and install them
# We use --no-cache-dir to keep the image size smaller
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Install the Patchright browser specifically
# (The base image has playwright browsers, but patchright needs its own)
RUN python -m patchright install chromium

# Expose the port your script uses
EXPOSE 5075

# Run the application
# We use 0.0.0.0 to ensure it's accessible externally
CMD ["python", "main.py", "--port", "5075"]
