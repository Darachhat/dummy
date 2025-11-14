
#!/bin/sh
set -euo pipefail
LAST_COMMIT=$(git rev-parse HEAD^)
CURRENT_COMMIT=$(git rev-parse HEAD)
# Check if Dockerfile or pyproject.toml have changed
if git diff --name-only $LAST_COMMIT $CURRENT_COMMIT | grep -qE "Dockerfile|pyproject.toml"; then
    echo "REBUILD_NEEDED=true" >> build.env
    echo "Changes detected in Dockerfile or pyproject.toml. Rebuild is needed."
else
    echo "REBUILD_NEEDED=false" >> build.env
    echo "No changes detected in Dockerfile or pyproject.toml. Skipping rebuild."
fi