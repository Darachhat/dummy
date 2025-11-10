#!/bin/sh
set -e

echo "Preparing notification for $CI_COMMIT_REF_NAME environment of $APPLICATION..."

if [ -f job_status.env ]; then
    . ./job_status.env
else
    BUILD_JOB_STATUS="failed"
    DEPLOY_JOB_STATUS="failed"
    DEPLOY_MANUALLY_RERUN="false"
fi

echo "BUILD_JOB_STATUS: $BUILD_JOB_STATUS"
echo "DEPLOY_JOB_STATUS: $DEPLOY_JOB_STATUS"
echo "DEPLOY_MANUALLY_RERUN: $DEPLOY_MANUALLY_RERUN"
echo "Application: $APPLICATION"


escape_html() {
  echo "$1" | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g; s/"/\&quot;/g; s/'"'"'/\&#39;/g'
}

format_commit_message() {
    echo "$1" | sed '/^$/d' | while IFS= read -r line; do
        trimmed_line=$(echo "$line" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
        echo "• $(escape_html "$trimmed_line")"
    done | paste -sd $'\n' -
}

# Function to parse ISO 8601 timestamp and return Unix timestamp
parse_iso8601() {
  local iso_date="$1"
  local year=$(echo "$iso_date" | cut -d'T' -f1 | cut -d'-' -f1)
  local month=$(echo "$iso_date" | cut -d'T' -f1 | cut -d'-' -f2)
  local day=$(echo "$iso_date" | cut -d'T' -f1 | cut -d'-' -f3)
  local time=$(echo "$iso_date" | cut -d'T' -f2 | cut -d'Z' -f1)
  local hour=$(echo "$time" | cut -d':' -f1)
  local minute=$(echo "$time" | cut -d':' -f2)
  local second=$(echo "$time" | cut -d':' -f3)

  date -u -d "$year-$month-$day $hour:$minute:$second" +%s
}

# Function to format duration
format_duration() {
  local seconds=$1
  local minutes=$((seconds / 60))
  local remaining_seconds=$((seconds % 60))
  printf "%02d:%02d" $minutes $remaining_seconds
}

# Function to get status emoji
get_status_emoji() {
  case "$1" in
    "success") echo "✅";;
    "failed") echo "❌";;
    "running") echo "🏃";;
    "canceled") echo "🚫";;
    "skipped") echo "⏭️";;
    "pending") echo "⏳";;
    *) echo "❓";;
  esac
}

echo "Constructing message..."

# Debug: Print CI variables
echo "CI_PIPELINE_SOURCE: $CI_PIPELINE_SOURCE"
echo "CI_PIPELINE_CREATED_AT: $CI_PIPELINE_CREATED_AT"
echo "CI_COMMIT_SHA: $CI_COMMIT_SHA"
echo "CI_COMMIT_SHORT_SHA: $CI_COMMIT_SHORT_SHA"
echo "CI_COMMIT_BRANCH: $CI_COMMIT_BRANCH"
echo "CI_COMMIT_TAG: $CI_COMMIT_TAG"
echo "CI_COMMIT_MESSAGE: $CI_COMMIT_MESSAGE"
echo "CI_JOB_STATUS: $CI_JOB_STATUS"

parse_timestamp() {
    local timestamp="$1"
    # Extract date and time parts
    local date_part=$(echo "$timestamp" | cut -d'T' -f1)
    local time_part=$(echo "$timestamp" | cut -d'T' -f2 | cut -d'+' -f1)
    local timezone_part=$(echo "$timestamp" | grep -o '[+-][0-9:]\+$')

    # Split time into hours, minutes, and seconds
    local hours=$(echo "$time_part" | cut -d':' -f1)
    local minutes=$(echo "$time_part" | cut -d':' -f2)
    local seconds=$(echo "$time_part" | cut -d':' -f3)

    # Format the date and time
    echo "${date_part} ${hours}:${minutes}:${seconds} UTC"
}

# Parse duration in minutes and seconds
parse_duration() {
    local duration="$1"
    local minutes=$((duration / 60))
    local seconds=$((duration % 60))
    echo "${minutes}m ${seconds}s"
}

commit_date=$(parse_timestamp "$CI_COMMIT_TIMESTAMP")

# Calculate pipeline duration
current_timestamp=$(date +%s)
if [ -n "$CI_PIPELINE_CREATED_AT" ]; then
  start_timestamp=$(parse_iso8601 "$CI_PIPELINE_CREATED_AT")
  if [ $? -eq 0 ]; then
    pipeline_duration=$(parse_duration $((current_timestamp - start_timestamp)))
    start_time="$CI_PIPELINE_CREATED_AT"
  else
    echo "Warning: Failed to parse CI_PIPELINE_CREATED_AT. Using placeholder values."
    pipeline_duration="N/A"
    start_time="N/A"
  fi
else
  echo "Warning: CI_PIPELINE_CREATED_AT is not set. Using placeholder values."
  pipeline_duration="N/A"
  start_time="N/A"
fi

# Determine pipeline status
if [ "$BUILD_JOB_STATUS" = "success" ] && [ "$DEPLOY_JOB_STATUS" = "success" ]; then
  pipeline_status="success"
elif [ "$BUILD_JOB_STATUS" = "failed" ] || [ "$DEPLOY_JOB_STATUS" = "failed" ]; then
  pipeline_status="failed"
else
  pipeline_status="failed"
fi

# Get commit ref name
if [ -n "$CI_COMMIT_TAG" ]; then
  commit_ref="$CI_COMMIT_TAG"
elif [ -n "$CI_COMMIT_BRANCH" ]; then
  commit_ref="$CI_COMMIT_BRANCH"
else
  commit_ref="$CI_COMMIT_REF_NAME"
fi

# GET Server IP and Service URL
if [ "$CI_COMMIT_REF_NAME" = "dev" ]; then
  SERVER_IP="$DEPLOY_DEV_SERVER"
  SERVICE_URL="$DEV_URL"
elif [ "$CI_COMMIT_REF_NAME" = "uat" ]; then
  SERVER_IP="$DEPLOY_UAT_SERVER"
  SERVICE_URL="$UAT_URL"
elif [ "$CI_COMMIT_REF_NAME" = "staging" ]; then
  SERVER_IP="$DEPLOY_STAGING_SERVER"
  SERVICE_URL="$STAING_URL"
elif [ "$CI_COMMIT_REF_NAME" = "prod" ]; then
  SERVER_IP="$DEPLOY_PROD_SERVER"
  SERVICE_URL="$PROD_URL"
else
  SERVER_IP="Unknown"
  SERVICE_URL=""
fi

# Construct the message
MESSAGE="<code>
$(get_status_emoji "$pipeline_status") $(escape_html "$APPLICATION"), $(escape_html "$CI_COMMIT_REF_NAME"), $(escape_html "$GITLAB_USER_NAME"), $(escape_html "$commit_date")
-----------------------------
Pipeline Overview
ID          : <a href=\"$(escape_html "$CI_PIPELINE_URL")\">$(escape_html "$CI_PIPELINE_ID")</a>
ENVIRONMENT : <b>$(escape_html "$CI_COMMIT_REF_NAME")</b>
APPLICATION : <b>$(escape_html "$APPLICATION")</b>
DATE        : $(escape_html "$commit_date")
DURATION    : $(escape_html "$pipeline_duration")
STATUS      : $(get_status_emoji "$pipeline_status") $(escape_html "$pipeline_status")
-----------------------------
Commit Details
HASH        : $(escape_html "$CI_COMMIT_SHORT_SHA")
COMMITER    : $(escape_html "$GITLAB_USER_NAME")
MESSAGE     :
$(format_commit_message "$CI_COMMIT_MESSAGE")
-----------------------------
Quick Links
VIEW COMMIT : <a href=\"$(escape_html "$CI_PROJECT_URL/-/commit/$CI_COMMIT_SHA")\">Link</a>
VIEW PIPELINE: <a href=\"$(escape_html "$CI_PIPELINE_URL")\">Link</a>
IP          : $(escape_html "$SERVER_IP")
VIEW PROJECT: <a href=\"$(escape_html "$CI_PROJECT_URL")\">$(escape_html "$CI_PROJECT_URL")</a>
SERVICE URL : <a href=\"$(escape_html "$SERVICE_URL")\">$(escape_html "$SERVICE_URL")</a>
-----------------------------
</code>"

# Determine the correct Telegram token and chat ID based on the environment
if [ "$CI_COMMIT_REF_NAME" = "dev" ]; then
  TELEGRAM_BOT_TOKEN="$DEV_TELEGRAM_BOT_TOKEN"
  TELEGRAM_CHAT_ID="$DEV_TELEGRAM_CHAT_ID"
elif [ "$CI_COMMIT_REF_NAME" = "uat" ]; then
  TELEGRAM_BOT_TOKEN="$UAT_TELEGRAM_BOT_TOKEN"
  TELEGRAM_CHAT_ID="$UAT_TELEGRAM_CHAT_ID"
elif [ "$CI_COMMIT_REF_NAME" = "staging" ]; then
  TELEGRAM_BOT_TOKEN="$STAGING_TELEGRAM_BOT_TOKEN"
  TELEGRAM_CHAT_ID="$STAGING_TELEGRAM_CHAT_ID"
elif [ "$CI_COMMIT_REF_NAME" = "prod" ]; then
  TELEGRAM_BOT_TOKEN="$PROD_TELEGRAM_BOT_TOKEN"
  TELEGRAM_CHAT_ID="$PROD_TELEGRAM_CHAT_ID"
else
  echo "⚠️ Unknown environment: $CI_COMMIT_REF_NAME. Cannot determine Telegram credentials."
  exit 1
fi

echo "$MESSAGE" > "$CI_PROJECT_DIR/notification_message.txt"
