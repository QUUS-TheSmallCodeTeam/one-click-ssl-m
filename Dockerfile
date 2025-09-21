# Simple dual server setup for Next.js + FastAPI on Hugging Face Spaces

# Use full Node.js image (includes npm, unlike slim version)
FROM node:22

# Set working directory
WORKDIR /app

# Install system dependencies including Python
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    git \
    fonts-liberation \
    fonts-noto-cjk \
    fonts-noto-color-emoji \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*


# Copy all application files
COPY . .

# Install Python dependencies
RUN cd securecheck-pro/backend && pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Install Node.js dependencies and build frontend
# Use dummy values for build (real values are set at runtime)
ENV NEXT_PUBLIC_SUPABASE_URL=https://placeholder.supabase.co
ENV NEXT_PUBLIC_SUPABASE_ANON_KEY=placeholder_key
RUN cd securecheck-pro/frontend && npm install && npm run build

# Create simple entrypoint script
RUN echo '#!/bin/bash\n\
set -e\n\
echo "Starting 원클릭SSL services..."\n\
\n\
# Override environment variables if provided at runtime\n\
if [ ! -z "$NEXT_PUBLIC_SUPABASE_URL" ] && [ "$NEXT_PUBLIC_SUPABASE_URL" != "https://placeholder.supabase.co" ]; then\n\
    echo "Using runtime Supabase URL: $NEXT_PUBLIC_SUPABASE_URL"\n\
    export NEXT_PUBLIC_SUPABASE_URL="$NEXT_PUBLIC_SUPABASE_URL"\n\
fi\n\
\n\
if [ ! -z "$NEXT_PUBLIC_SUPABASE_ANON_KEY" ] && [ "$NEXT_PUBLIC_SUPABASE_ANON_KEY" != "placeholder_key" ]; then\n\
    echo "Using runtime Supabase key (exists: true)"\n\
    export NEXT_PUBLIC_SUPABASE_ANON_KEY="$NEXT_PUBLIC_SUPABASE_ANON_KEY"\n\
fi\n\
\n\
# Start FastAPI backend in background\n\
echo "Starting FastAPI backend on port 8000..."\n\
cd /app/securecheck-pro/backend\n\
export PYTHONPATH=/app/securecheck-pro/backend\n\
python3 main.py &\n\
FASTAPI_PID=$!\n\
\n\
# Wait a moment for backend to start\n\
sleep 3\n\
\n\
# Start Next.js frontend in foreground\n\
echo "Starting Next.js frontend on port 7860..."\n\
cd /app/securecheck-pro/frontend\n\
export PORT=7860\n\
export NODE_ENV=production\n\
npm start &\n\
NEXTJS_PID=$!\n\
\n\
# Function to handle shutdown\n\
cleanup() {\n\
    echo "Shutting down services..."\n\
    kill $FASTAPI_PID $NEXTJS_PID 2>/dev/null || true\n\
    exit 0\n\
}\n\
\n\
# Handle signals\n\
trap cleanup SIGTERM SIGINT\n\
\n\
# Wait for both processes\n\
wait $NEXTJS_PID\n' > /app/start.sh

# Make entrypoint executable
RUN chmod +x /app/start.sh

# Create temp directories
RUN mkdir -p /tmp/reports /tmp/screenshots && chmod 777 /tmp/reports /tmp/screenshots

# Expose port (Hugging Face Spaces uses 7860)
EXPOSE 7860

# Set environment variables
ENV PORT=7860
ENV NODE_ENV=production
ENV NODE_OPTIONS="--dns-result-order=ipv4first"

# Run the simple entrypoint script
CMD ["/app/start.sh"]