#!/bin/sh
set -e

if [ -f "$CI_PROJECT_DIR/build.env" ]; then
  . "$CI_PROJECT_DIR/build.env"
fi

if [ "$CI_COMMIT_REF_NAME" = "uat" ]; then
  DEPLOY_SERVER=$DEPLOY_UAT_SERVER
  ENVIRONMENT="uat"
  NAMESPACE="uat"
  HOST_USER=$UAT_USER
  ANSIBLE_INVENTORY=$UAT_ANSIBLE_INVENTORY
  ENV="uat"
  URL=$UAT_URL

  DATABASE_URL=${UAT_DATABASE_URL}
  SECRET_KEY=${UAT_SECRET_KEY}
  ACCESS_TOKEN_EXPIRE_MINUTES=${UAT_ACCESS_TOKEN_EXPIRE_MINUTES}
  CORS_ORIGINS=${UAT_CORS_ORIGINS}
  DEBUG=${UAT_DEBUG}
  USE_MOCK_OSP=${UAT_USE_MOCK_OSP}
  OSP_BASE_URL=${UAT_OSP_BASE_URL}
  OSP_AUTH=${UAT_OSP_AUTH}
  OSP_PARTNER=${UAT_OSP_PARTNER}
  OSP_TIMEOUT=${UAT_OSP_TIMEOUT}
  FEE_AMOUNT=${UAT_FEE_AMOUNT}
  USD_TO_KHR_RATE=${UAT_USD_TO_KHR_RATE}

elif [ "$CI_COMMIT_REF_NAME" = "staging" ]; then
  DEPLOY_SERVER=$DEPLOY_STAGING_SERVER
  ENVIRONMENT="staging"
  NAMESPACE="staging"
  HOST_USER=$STAGING_USER
  ANSIBLE_INVENTORY=$STAGING_ANSIBLE_INVENTORY
  ENV="staging"
  URL=$STAGING_URL

  DATABASE_URL=${STAGING_DATABASE_URL}
  SECRET_KEY=${STAGING_SECRET_KEY}
  ACCESS_TOKEN_EXPIRE_MINUTES=${STAGING_ACCESS_TOKEN_EXPIRE_MINUTES}
  CORS_ORIGINS=${STAGING_CORS_ORIGINS}
  DEBUG=${STAGING_DEBUG}
  USE_MOCK_OSP=${STAGING_USE_MOCK_OSP}
  OSP_BASE_URL=${STAGING_OSP_BASE_URL}
  OSP_AUTH=${STAGING_OSP_AUTH}
  OSP_PARTNER=${STAGING_OSP_PARTNER}
  OSP_TIMEOUT=${STAGING_OSP_TIMEOUT}
  FEE_AMOUNT=${STAGING_FEE_AMOUNT}
  USD_TO_KHR_RATE=${STAGING_USD_TO_KHR_RATE}

elif [ "$CI_COMMIT_REF_NAME" = "prod" ]; then
  DEPLOY_SERVER=$DEPLOY_PROD_SERVER
  ENVIRONMENT="prod"
  NAMESPACE="prod"
  HOST_USER=$PROD_USER
  ANSIBLE_INVENTORY=$PROD_ANSIBLE_INVENTORY
  ENV="prod"
  URL=$PROD_URL

  DATABASE_URL=${PROD_DATABASE_URL}
  SECRET_KEY=${PROD_SECRET_KEY}
  ACCESS_TOKEN_EXPIRE_MINUTES=${PROD_ACCESS_TOKEN_EXPIRE_MINUTES}
  CORS_ORIGINS=${PROD_CORS_ORIGINS}
  DEBUG=${PROD_DEBUG}
  USE_MOCK_OSP=${PROD_USE_MOCK_OSP}
  OSP_BASE_URL=${PROD_OSP_BASE_URL}
  OSP_AUTH=${PROD_OSP_AUTH}
  OSP_PARTNER=${PROD_OSP_PARTNER}
  OSP_TIMEOUT=${PROD_OSP_TIMEOUT}
  FEE_AMOUNT=${PROD_FEE_AMOUNT}
  USD_TO_KHR_RATE=${PROD_USD_TO_KHR_RATE}

else
  echo "Unsupported branch for deployment: $CI_COMMIT_REF_NAME"
  exit 1
fi

echo "Verifying SSH connection to $DEPLOY_SERVER..."
timeout 10s ssh -o StrictHostKeyChecking=no $HOST_USER@$DEPLOY_SERVER "echo 'SSH connection successful'" || (echo "SSH connection failed" && exit 1)
echo "SSH connection verified. Proceeding with Ansible deployment..."

git clone http://oauth2:${PERSONAL_ACCESS_TOKEN}@${CI_SERVER_HOST}/${ANSIBLE_REPO_PATH}.git ansible-repo
cd ansible-repo
git checkout $ANSIBLE_BRANCH

echo "Listing ansible-repo directory structure:"
find . -type d
echo "Listing ansible-repo/templates directory:"
ls -la templates

DOCKER_TAG=${VERSION_TAG:-$CI_COMMIT_SHA}

ansible-playbook -i $ANSIBLE_INVENTORY $ANSIBLE_PLAYBOOK -vv \
  -e "application=$APPLICATION" \
  -e "docker_registry=$DOCKER_REGISTRY" \
  -e "docker_tag=$DOCKER_TAG" \
  -e "docker_folder=$DOCKER_FOLDER" \
  -e "docker_image=$DOCKER_IMAGE" \
  -e "docker_namespace=$NAMESPACE" \
  -e "docker_registry_user=$DOCKER_REGISTRY_USER" \
  -e "docker_registry_password=$DOCKER_REGISTRY_PASSWORD" \
  -e "env=$ENV" \
  -e "url=$URL" \
  -e "host_user=$HOST_USER" \
  -e "git_url=$CI_PROJECT_URL" \
  -e "git_branch=$CI_COMMIT_REF_NAME" \
  -e "database_url=$DATABASE_URL" \
  -e "secret_key=$SECRET_KEY" \
  -e "access_token_expire_minutes=$ACCESS_TOKEN_EXPIRE_MINUTES" \
  -e "cors_origins=$CORS_ORIGINS" \
  -e "debug=$DEBUG" \
  -e "use_mock_osp=$USE_MOCK_OSP" \
  -e "osp_base_url=$OSP_BASE_URL" \
  -e "osp_auth=$OSP_AUTH" \
  -e "osp_partner=$OSP_PARTNER" \
  -e "osp_timeout=$OSP_TIMEOUT" \
  -e "fee_amount=$FEE_AMOUNT" \
  -e "usd_to_khr_rate=$USD_TO_KHR_RATE" \
  -e "api_replicas=$SERVICE_REPLICAS"

echo "Ansible deployment completed for $ENV environment."
