#!/bin/sh
set -e

if [ -f "$CI_PROJECT_DIR/build.env" ]; then
  . "$CI_PROJECT_DIR/build.env"
fi

# Set environment-specific variables
if [ "$CI_COMMIT_REF_NAME" = "uat" ]; then
  DEPLOY_SERVER=$DEPLOY_UAT_SERVER
  DEPLOY_USER=$UAT_USER
  DEPLOY_PATH=$UAT_DEPLOY_PATH
  API_BASE_URL=$UAT_API_BASE_URL
  ENV="uat"
  URL=$UAT_URL

elif [ "$CI_COMMIT_REF_NAME" = "staging" ]; then
  DEPLOY_SERVER=$DEPLOY_STAGING_SERVER
  DEPLOY_USER=$STAGING_USER
  DEPLOY_PATH=$STAGING_DEPLOY_PATH
  API_BASE_URL=$STAGING_API_BASE_URL
  ENV="staging"
  URL=$STAGING_URL

elif [ "$CI_COMMIT_REF_NAME" = "prod" ]; then
  DEPLOY_SERVER=$DEPLOY_PROD_SERVER
  DEPLOY_USER=$PROD_USER
  DEPLOY_PATH=$PROD_DEPLOY_PATH
  API_BASE_URL=$PROD_API_BASE_URL
  ENV="prod"
  URL=$PROD_URL

else
  echo "Unsupported branch for deployment: $CI_COMMIT_REF_NAME"
  exit 1
fi

echo "=========================================="
echo "Deployment Configuration"
echo "=========================================="
echo "Environment: $ENV"
echo "Deploy Server: $DEPLOY_SERVER"
echo "Deploy User: $DEPLOY_USER"
echo "Deploy Path: $DEPLOY_PATH"
echo "API Base URL: $API_BASE_URL"
echo "Application URL: $URL"
echo "=========================================="

# Verify SSH connection
echo "Verifying SSH connection to $DEPLOY_SERVER..."
timeout 10s ssh -o StrictHostKeyChecking=no $DEPLOY_USER@$DEPLOY_SERVER "echo 'SSH connection successful'" || (echo "SSH connection failed" && exit 1)
echo "✅ SSH connection verified."

# Create deployment directory if it doesn't exist
echo "Creating deployment directory on remote server..."
ssh $DEPLOY_USER@$DEPLOY_SERVER "mkdir -p $DEPLOY_PATH"

# Sync build artifacts to remote server
echo "Syncing build artifacts to remote server..."
rsync -avz --delete \
  --exclude='.git' \
  --exclude='node_modules/.cache' \
  .output/ \
  ecosystem.config.js \
  package.json \
  package-lock.json \
  nuxt.config.ts \
  $DEPLOY_USER@$DEPLOY_SERVER:$DEPLOY_PATH/

# Create .env file on remote server
echo "Creating .env file on remote server..."
ssh $DEPLOY_USER@$DEPLOY_SERVER "cat > $DEPLOY_PATH/.env" <<EOF
NUXT_PUBLIC_API_BASE=$API_BASE_URL
NODE_ENV=production
EOF

# Install/Update PM2 and dependencies on remote server
echo "Setting up PM2 on remote server..."
ssh $DEPLOY_USER@$DEPLOY_SERVER << 'ENDSSH'
# Install Node.js and PM2 if not already installed
if ! command -v node &> /dev/null; then
    echo "Node.js not found. Please install Node.js on the server."
    exit 1
fi

if ! command -v pm2 &> /dev/null; then
    echo "PM2 not found. Installing PM2 globally..."
    npm install -g pm2
fi

echo "✅ PM2 is installed"
pm2 --version
ENDSSH

# Deploy with PM2
echo "Deploying application with PM2..."
ssh $DEPLOY_USER@$DEPLOY_SERVER << ENDSSH
cd $DEPLOY_PATH

# Update ecosystem.config.js with environment-specific values
cat > ecosystem.config.js <<'EOFCONFIG'
module.exports = {
  apps: [{
    name: '${PM2_APP_NAME:-nuxt-app}-${ENV}',
    port: '${PM2_PORT:-3000}',
    exec_mode: 'cluster',
    instances: '${PM2_INSTANCES:-2}',
    script: './.output/server/index.mjs',
    env: {
      NODE_ENV: 'production',
      NUXT_PUBLIC_API_BASE: '$API_BASE_URL',
      PORT: '${PM2_PORT:-3000}'
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_file: './logs/combined.log',
    time: true,
    max_memory_restart: '1G',
    exp_backoff_restart_delay: 100,
    autorestart: true
  }]
}
EOFCONFIG

# Create logs directory
mkdir -p logs

# Start or reload the application with PM2
if pm2 describe ${PM2_APP_NAME:-nuxt-app}-${ENV} > /dev/null 2>&1; then
  echo "Application found. Reloading..."
  pm2 reload ecosystem.config.js --env production
else
  echo "Application not found. Starting..."
  pm2 start ecosystem.config.js --env production
fi

# Save PM2 configuration
pm2 save

# Setup PM2 startup script (only needed once, won't hurt to run again)
pm2 startup systemd -u $DEPLOY_USER --hp /home/$DEPLOY_USER > /dev/null 2>&1 || true

# Show PM2 status
pm2 list
pm2 info ${PM2_APP_NAME:-nuxt-app}-${ENV}

echo "✅ Deployment completed successfully!"
ENDSSH

echo "=========================================="
echo "Deployment Summary"
echo "=========================================="
echo "Environment: $ENV"
echo "Application URL: $URL"
echo "PM2 App Name: ${PM2_APP_NAME:-nuxt-app}-${ENV}"
echo "=========================================="
echo "✅ Deployment completed for $ENV environment!"
