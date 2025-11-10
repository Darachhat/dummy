#!/bin/sh
set -euo pipefail

LAST_COMMIT=$(git rev-parse HEAD^)
CURRENT_COMMIT=$(git rev-parse HEAD)

echo "Checking for changes between commits..."
echo "Last commit: $LAST_COMMIT"
echo "Current commit: $CURRENT_COMMIT"

# Check if package files or source code have changed
if git diff --name-only $LAST_COMMIT $CURRENT_COMMIT | grep -qE "package\.json|package-lock\.json|pages/|components/|layouts/|composables/|assets/|public/|nuxt\.config\.ts|app\.vue"; then
    echo "REBUILD_NEEDED=true" >> build.env
    echo "✅ Changes detected in package files or source code. Rebuild is needed."
    echo "Changed files:"
    git diff --name-only $LAST_COMMIT $CURRENT_COMMIT | grep -E "package\.json|package-lock\.json|pages/|components/|layouts/|composables/|assets/|public/|nuxt\.config\.ts|app\.vue" || true
else
    echo "REBUILD_NEEDED=false" >> build.env
    echo "⏭️  No changes detected in package files or source code. Skipping rebuild."
fi