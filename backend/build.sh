#!/bin/sh
set -euo pipefail

git clone http://oauth2:${PERSONAL_ACCESS_TOKEN}@${CI_SERVER_HOST}/${GIT_REPO}.git $APPLICATION

cd $APPLICATION

git checkout $CI_COMMIT_REF_NAME

if [[ $CI_COMMIT_BRANCH == "uat" ]]; then
  cat <<EOF > .env
DATABASE_URL=${UAT_DATABASE_URL}
SECRET_KEY=${UAT_SECRET_KEY}
ACCESS_TOKEN_EXPIRE_MINUTES=${UAT_ACCESS_TOKEN_EXPIRE_MINUTES}
CORS_ORIGINS="${UAT_CORS_ORIGINS}"
DEBUG=${UAT_DEBUG}
USE_MOCK_OSP=${UAT_USE_MOCK_OSP}
OSP_BASE_URL=${UAT_OSP_BASE_URL}
OSP_AUTH=${UAT_OSP_AUTH}
OSP_PARTNER=${UAT_OSP_PARTNER}
OSP_TIMEOUT=${UAT_OSP_TIMEOUT}
FEE_AMOUNT=${UAT_FEE_AMOUNT}
USD_TO_KHR_RATE=${UAT_USD_TO_KHR_RATE}
EOF
elif [[ $CI_COMMIT_BRANCH == "staging" ]]; then
  cat <<EOF > .env
DATABASE_URL=${STAGING_DATABASE_URL}
SECRET_KEY=${STAGING_SECRET_KEY}
ACCESS_TOKEN_EXPIRE_MINUTES=${STAGING_ACCESS_TOKEN_EXPIRE_MINUTES}
CORS_ORIGINS="${STAGING_CORS_ORIGINS}"
DEBUG=${STAGING_DEBUG}
USE_MOCK_OSP=${STAGING_USE_MOCK_OSP}
OSP_BASE_URL=${STAGING_OSP_BASE_URL}
OSP_AUTH=${STAGING_OSP_AUTH}
OSP_PARTNER=${STAGING_OSP_PARTNER}
OSP_TIMEOUT=${STAGING_OSP_TIMEOUT}
FEE_AMOUNT=${STAGING_FEE_AMOUNT}
USD_TO_KHR_RATE=${STAGING_USD_TO_KHR_RATE}
EOF
elif [[ $CI_COMMIT_BRANCH == "prod" ]]; then
  cat <<EOF > .env
DATABASE_URL=${PROD_DATABASE_URL}
SECRET_KEY=${PROD_SECRET_KEY}
ACCESS_TOKEN_EXPIRE_MINUTES=${PROD_ACCESS_TOKEN_EXPIRE_MINUTES}
CORS_ORIGINS="${PROD_CORS_ORIGINS}"
DEBUG=${PROD_DEBUG}
USE_MOCK_OSP=${PROD_USE_MOCK_OSP}
OSP_BASE_URL=${PROD_OSP_BASE_URL}
OSP_AUTH=${PROD_OSP_AUTH}
OSP_PARTNER=${PROD_OSP_PARTNER}
OSP_TIMEOUT=${PROD_OSP_TIMEOUT}
FEE_AMOUNT=${PROD_FEE_AMOUNT}
USD_TO_KHR_RATE=${PROD_USD_TO_KHR_RATE}
EOF
else
  echo "Invalid branch. Please use 'uat', 'staging' or 'prod' branch."
  exit 1
fi

NAMESPACE=$CI_COMMIT_REF_NAME
COMMIT_TAG=$DOCKER_REGISTRY/$NAMESPACE/$DOCKER_FOLDER/$DOCKER_IMAGE:$CI_COMMIT_SHORT_SHA
LATEST_TAG=$DOCKER_REGISTRY/$NAMESPACE/$DOCKER_FOLDER/$DOCKER_IMAGE:latest

LAST_COMMIT=$(git rev-parse HEAD^)
CURRENT_COMMIT=$(git rev-parse HEAD)

if git diff --name-only $LAST_COMMIT $CURRENT_COMMIT | grep -qE "Dockerfile|requirements.txt"; then
    REBUILD_NEEDED=true
    echo "Changes detected in Dockerfile or requirements.txt. Rebuild is needed."
else
    REBUILD_NEEDED=false
    echo "No changes detected in Dockerfile or requirements.txt. Skipping rebuild."
fi

if [ "$REBUILD_NEEDED" = true ]; then
    echo "Building image..."
    docker build -t $COMMIT_TAG .

    echo "Image size:"
    docker image inspect $COMMIT_TAG --format='{{.Size}}' |
      awk '{ split( "B KB MB GB TB PB" , v ); s=1; while( $1>1024 ){ $1/=1024; s++ } printf "%.2f %s", $1, v[s] }'

    echo "Tagging and pushing images..."
    docker tag $COMMIT_TAG $LATEST_TAG

    push_image() {
        local tag=$1
        local log_file=$2
        docker push $tag 2>&1 | tee $log_file
        if grep -q "error" $log_file; then
            echo "Error detected during push of $tag:"
            cat $log_file
            return 1
        fi
        echo "Layers pushed ($tag):"
        grep -E "Pushed|Layer already exists|Mounted from" $log_file | sort | uniq -c
    }

    push_image $COMMIT_TAG push_output_commit.log
    push_image $LATEST_TAG push_output_latest.log

    echo "Push complete."
else
    echo "Skipping build and push as no changes detected in Dockerfile or requirements.txt"
    # Retrieve the last successful build SHA
    LAST_SUCCESSFUL_SHA=$(git rev-parse --short HEAD)
    CI_COMMIT_SHORT_SHA=$LAST_SUCCESSFUL_SHA
    echo "Using last successful build: $LAST_SUCCESSFUL_SHA"
fi

# Store env vars for next jobs
echo "NAMESPACE=$NAMESPACE" > "$CI_PROJECT_DIR/build.env"
echo "VERSION_TAG=$CI_COMMIT_SHORT_SHA" >> "$CI_PROJECT_DIR/build.env"
echo "REBUILD_NEEDED=$REBUILD_NEEDED" >> "$CI_PROJECT_DIR/build.env"

echo "Current directory: $(pwd)"
echo "Files in current directory:"
ls -la

echo "Files in \$CI_PROJECT_DIR:"
ls -la $CI_PROJECT_DIR
