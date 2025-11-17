#!/bin/bash
set -e

echo "Starting entrypoint script..."

# Ensure migrations directory exists and is writable
mkdir -p /workspace/migrations/versions
chmod -R 777 /workspace/migrations/versions 2>/dev/null || true

# Auto-generate migration if there are model changes
echo "Checking for database schema changes..."
MIGRATION_FILE=$(alembic revision --autogenerate -m "Auto-migration: $(date +%Y%m%d_%H%M%S)" 2>&1 | grep -oP 'Generating \K[^ ]+' | head -1)

if [ -n "$MIGRATION_FILE" ] && [ -f "$MIGRATION_FILE" ]; then
    echo "New migration generated: $MIGRATION_FILE"
    echo "Fixing NOT NULL constraints for SQLite compatibility..."

    # Fix NOT NULL columns by adding server_default for new columns
    # This makes them nullable temporarily or adds defaults
    sed -i "s/sa.Column('\([^']*\)', \([^,]*\), nullable=False)/sa.Column('\1', \2, nullable=True)/g" "$MIGRATION_FILE"

    echo "Migration file updated to be SQLite compatible"
fi

# Apply all pending migrations
echo "Applying database migrations..."
alembic upgrade head

echo "Migrations applied successfully!"

# Start the application
echo "Starting FastAPI application..."
exec fastapi run main.py --port 8000 --proxy-headers
