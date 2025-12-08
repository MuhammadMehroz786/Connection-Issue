#!/bin/bash

# Railway startup script for Shopify Automation

echo "🚀 Starting Shopify Automation..."

# Set default port if not provided
export PORT=${PORT:-5000}

echo "📦 Environment:"
echo "   - Port: $PORT"
echo "   - Python: $(python --version)"
echo "   - Workers: 4"

# Run database migrations (if any)
echo "🗄️  Checking database..."
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('✅ Database ready')"

# Start gunicorn with production settings
echo "🌐 Starting Gunicorn server..."
exec gunicorn app:app \
    --bind 0.0.0.0:$PORT \
    --workers 4 \
    --threads 2 \
    --timeout 300 \
    --keep-alive 5 \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    --preload
