#!/bin/sh
set -e

echo "=========================================="
echo "Starting Nuxt Build Process"
echo "=========================================="
echo "Environment: $ENV"
echo "Branch: $CI_COMMIT_REF_NAME"
echo "Commit: $CI_COMMIT_SHORT_SHA"
echo "=========================================="

# Install dependencies
echo "Installing dependencies..."
npm ci --prefer-offline --no-audit

# Build the Nuxt application
echo "Building Nuxt application..."
npm run build

# Verify build output
if [ -d ".output" ]; then
  echo " Build successful! Output directory created."
  echo "Build contents:"
  ls -la .output/
else
  echo "L Build failed! Output directory not found."
  exit 1
fi

echo "=========================================="
echo "Build completed successfully!"
echo "=========================================="
