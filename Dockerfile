# Use a clean Python image — we'll install browsers ourselves
FROM python:3.11-slim-bookworm

WORKDIR /app

# Install OS dependencies for Chromium + diagnostic tools
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgcc1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    lsb-release \
    xdg-utils \
    libgbm1 \
    libdrm2 \
    libcurl4 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install ONLY patchright's Chromium (not Playwright's)
RUN python -m patchright install chromium

# Verify installation
RUN python -c "import patchright; print('Patchright version:', patchright.__version__)" && \
    ls -la /root/.cache/patchright/ 2>/dev/null || echo "Check patchright path" && \
    which chromium 2>/dev/null || echo "chromium not in PATH" && \
    ls /root/.cache/patchright/chromium-*/chrome-linux/chrome 2>/dev/null || \
    ls /root/.cache/patchright/*/chrome-linux/chrome 2>/dev/null || \
    echo "Searching for chrome binary..." && find /root/.cache -name "chrome" -type f 2>/dev/null | head -5

# Copy application code
COPY . .

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Expose the port
EXPOSE 5075

# Use ENTRYPOINT for base command, CMD for default args
# Railway can override CMD in service settings
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["--browser", "chromium", "--port", "5075", "--headless", "--threads", "2"]
