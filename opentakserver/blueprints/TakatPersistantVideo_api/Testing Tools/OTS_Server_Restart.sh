#!/bin/bash
# ------------------------------------------------------------
# Script to restart OTS via Takat Persistant Video API (with authentication)
# ------------------------------------------------------------

# Configuration
HOST="192.168.18.129"
PORT="8081"
LOGIN_ENDPOINT="/api/login?include_auth_token"
RESTART_ENDPOINT="/api/system/restartots"

LOGIN_URL="http://${HOST}:${PORT}${LOGIN_ENDPOINT}"
RESTART_URL="http://${HOST}:${PORT}${RESTART_ENDPOINT}"

USERNAME="administrator"

# ------------------------------------------------------------
# 0. Prompt for password
# ------------------------------------------------------------
IFS= read -r -p "Enter password for ${USERNAME}: " PASSWORD
echo

# ------------------------------------------------------------
# 1. Get authentication token
# ------------------------------------------------------------
echo "Logging in to get token..."
LOGIN_RESPONSE=$(curl -s -X POST "$LOGIN_URL" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"${USERNAME}\", \"password\": \"${PASSWORD}\"}")

# Extract token using jq (make sure jq is installed)
AUTH_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.response.user.authentication_token')


if [ "$AUTH_TOKEN" == "null" ] || [ -z "$AUTH_TOKEN" ]; then
  echo "Failed to get authentication token."
  echo "Response was:"
  echo "$LOGIN_RESPONSE"
  exit 1
fi

echo "Got auth token: $AUTH_TOKEN"

# ------------------------------------------------------------
# 2. Send restart request with token
# ------------------------------------------------------------
echo "Sending restart command to $RESTART_URL ..."
RESPONSE=$(curl -s -X GET "$RESTART_URL" \
  -H "Content-Type: application/json" \
  -H "Authentication-Token: $AUTH_TOKEN" \
  -w "\nHTTP status: %{http_code}\n")

echo "$RESPONSE"

# Done
echo -e "\nRequest completed."
