
#!/bin/sh
set -euo pipefail
LAST_COMMIT=$(git rev-parse HEAD^)
CURRENT_COMMIT=$(git rev-parse HEAD)
# Check if Dockerfile or requirements.txt have changed
if git diff --name-only $LAST_COMMIT $CURRENT_COMMIT | grep -qE "Dockerfile|requirements.txt"; then
    echo "REBUILD_NEEDED=true" >> build.env
    echo "Changes detected in Dockerfile or requirements.txt. Rebuild is needed."
else
    echo "REBUILD_NEEDED=false" >> build.env
    echo "No changes detected in Dockerfile or requirements.txt. Skipping rebuild."
fi