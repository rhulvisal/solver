FROM python:3.11-slim-bookworm

WORKDIR /app

# Install OS dependencies for Chromium
RUN apt-get update && apt-get install -y \
    wget gnupg ca-certificates fonts-liberation libasound2 \
    libatk-bridge2.0-0 libatk1.0-0 libc6 libcairo2 libcups2 \
    libdbus-1-3 libexpat1 libfontconfig1 libgcc1 libglib2.0-0 \
    libgtk-3-0 libnspr4 libnss3 libpango-1.0-0 libpangocairo-1.0-0 \
    libstdc++6 libx11-6 libx11-xcb1 libxcb1 libxcomposite1 \
    libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 \
    libxrandr2 libxrender1 libxss1 libxtst6 lsb-release \
    xdg-utils libgbm1 libdrm2 libcurl4 curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install patchright chromium
RUN python -m patchright install chromium

# CRITICAL: Find the patchright chromium binary and symlink it to /usr/bin/chromium
# This ensures the binary is in PATH and the stealth patches are applied
RUN echo "=== Finding patchright chromium binary ===" && \
    find /root/.cache/patchright -name "chrome" -type f 2>/dev/null && \
    CHROME_PATH=$(find /root/.cache/patchright -name "chrome" -type f | head -1) && \
    if [ -n "$CHROME_PATH" ]; then \
        echo "Found: $CHROME_PATH" && \
        ln -sf "$CHROME_PATH" /usr/bin/chromium && \
        ln -sf "$CHROME_PATH" /usr/bin/chromium-browser && \
        echo "Symlinked to /usr/bin/chromium"; \
    else \
        echo "ERROR: Could not find patchright chrome binary" && \
        exit 1; \
    fi

# Verify the symlink works
RUN ls -la /usr/bin/chromium && /usr/bin/chromium --version 2>/dev/null || echo "chromium --version failed"

COPY . .
RUN chmod +x /app/entrypoint.sh

EXPOSE 5075

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["--browser", "chromium", "--port", "5075", "--headless", "--threads", "2"]
