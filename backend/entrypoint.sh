#!/bin/bash
set -e

echo "Starting entrypoint script..."

# Ensure exists and is writable
mkdir -p /workspace/migrations/versions
chmod -R 777 /workspace/migrations/versions 2>/dev/null || true
DB_FILE="/workspace/dummybank.db"

# Check if database(only alembic_version)
if [ -f "$DB_FILE" ]; then
    TABLE_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name != 'alembic_version';" 2>/dev/null || echo "0")
    if [ "$TABLE_COUNT" -eq 0 ]; then
        echo "Found database with no tables (only alembic tracking). This is corrupted. Removing everything..."
        rm -f "$DB_FILE"
        rm -f /workspace/migrations/versions/*.py
        echo "Cleaned up corrupted state."
    fi
fi

# Check if any migration files exist
MIGRATION_COUNT=$(ls -1 /workspace/migrations/versions/*.py 2>/dev/null | wc -l)

if [ "$MIGRATION_COUNT" -eq 0 ]; then
    echo "No migration files found. Generating initial migration..."
    uv run alembic revision --autogenerate -m "Initial schema $(date +%Y%m%d_%H%M%S)"
    echo "Applying initial migration..."
    uv run alembic upgrade head
    echo "Database initialized successfully!"
else
    echo "Found $MIGRATION_COUNT migration file(s)."

    # Check current database state
    if uv run alembic current 2>/dev/null | grep -q "(head)"; then
        echo "Database is marked as up to date. Verifying tables exist..."
        if [ -f "$DB_FILE" ]; then
            TABLE_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name != 'alembic_version';" 2>/dev/null || echo "0")
            if [ "$TABLE_COUNT" -eq 0 ]; then
                echo "ERROR: Database is marked as migrated but has no tables! Regenerating..."
                rm -f "$DB_FILE"
                rm -f /workspace/migrations/versions/*.py
                uv run alembic revision --autogenerate -m "Initial schema $(date +%Y%m%d_%H%M%S)"
                uv run alembic upgrade head
                echo "Database recreated successfully!"
            else
                echo "Database verification passed. $TABLE_COUNT tables found."
            fi
        fi
    else
        echo "Applying pending migrations..."
        # Check for multiple heads and merge if needed
        HEAD_COUNT=$(uv run alembic heads 2>/dev/null | wc -l)
        if [ "$HEAD_COUNT" -gt 1 ]; then
            echo "Multiple heads detected ($HEAD_COUNT). Merging..."
            uv run alembic merge heads -m "Merge multiple heads $(date +%Y%m%d_%H%M%S)"
        fi
        uv run alembic upgrade head || {
            echo "WARNING: Migration failed. Deleting corrupted database and regenerating..."
            rm -f "$DB_FILE"
            echo "Regenerating migrations from scratch..."
            rm -f /workspace/migrations/versions/*.py
            uv run alembic revision --autogenerate -m "Initial schema $(date +%Y%m%d_%H%M%S)"
            uv run alembic upgrade head
            echo "Database recreated successfully!"
        }
    fi
fi

echo "Database setup completed!"

echo "Starting FastAPI application..."
exec uv run fastapi run main.py --port 8000 --proxy-headers
