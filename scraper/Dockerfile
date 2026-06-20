FROM python:3.11-slim

# Install Azure Functions deps + Chrome for Selenium in one layer (--no-install-recommends saves ~100–300MB)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl unzip libicu-dev gnupg wget \
    chromium chromium-driver \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Node.js (required for Azure Functions Core Tools)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Azure Functions Core Tools
RUN npm install -g azure-functions-core-tools@4 --unsafe-perm true

# Set environment variables
ENV AzureWebJobsScriptRoot=/app \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true \
    FUNCTIONS_WORKER_RUNTIME=python \
    AzureWebJobsStorage=""

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy function app code
COPY . .

# Pre-download extension bundle during build (when network is available)
# This avoids runtime download failures
RUN mkdir -p /root/.azure-functions-core-tools/Functions/ExtensionBundles/Microsoft.Azure.Functions.ExtensionBundle && \
    cd /root/.azure-functions-core-tools/Functions/ExtensionBundles/Microsoft.Azure.Functions.ExtensionBundle && \
    (curl -fsSL --ipv4 "https://cdn.functions.azure.com/public/ExtensionBundles/Microsoft.Azure.Functions.ExtensionBundle/index.json" -o index.json 2>/dev/null && \
     BUNDLE_VER=$(python3 -c "import json; versions=json.load(open('index.json')); v4=[v for v in versions if v.startswith('4.')]; print(sorted(v4, key=lambda x: [int(i) for i in x.split('.')])[-1] if v4 else '')" 2>/dev/null) && \
     if [ -n "$BUNDLE_VER" ]; then \
       echo "Downloading extension bundle version $BUNDLE_VER..." && \
       mkdir -p "$BUNDLE_VER" && \
       curl -fsSL --ipv4 "https://cdn.functions.azure.com/public/ExtensionBundles/Microsoft.Azure.Functions.ExtensionBundle/$BUNDLE_VER/Microsoft.Azure.Functions.ExtensionBundle.$BUNDLE_VER.zip" -o "$BUNDLE_VER/bundle.zip" && \
       cd "$BUNDLE_VER" && unzip -q bundle.zip && rm bundle.zip && \
       echo "Extension bundle $BUNDLE_VER pre-downloaded successfully"; \
     else \
       echo "Could not determine bundle version, will download at runtime"; \
     fi) || echo "Bundle will be downloaded at runtime if needed"

# Create startup script
RUN echo '#!/bin/bash\n\
echo "Starting Azure Functions..."\n\
if [ -n "$FUNC_APP_FILE" ] && [ -f "$FUNC_APP_FILE" ]; then\n\
    echo "Using function app file: $FUNC_APP_FILE"\n\
    cp "$FUNC_APP_FILE" function_app.py\n\
fi\n\
exec func start --host 0.0.0.0 --port 80 --python\n\
' > /app/start.sh && chmod +x /app/start.sh

EXPOSE 80
ENTRYPOINT ["/app/start.sh"]
