#!/bin/bash
# ------------------------------------------------------------
# Script to get all videoObjects via TakatVideo API (with authentication)
# ------------------------------------------------------------

# Configuration
HOST="tascomm.takat.nl"
PORT="443"
LOGIN_ENDPOINT="/devapi/authorization/login"
RESTART_ENDPOINT="/api/persistantvideo/TascommDB/GetAllVideoObjects"

LOGIN_URL="https://${HOST}${LOGIN_ENDPOINT}"
RESTART_URL="http://${HOST}:${PORT}${RESTART_ENDPOINT}"

USERNAME="mediamtx"
PASSWORD="k9i#v0A1x@kmEbbz"

# ------------------------------------------------------------
# 0. Prompt for password
# ------------------------------------------------------------
#IFS= read -r -p "Enter password for ${USERNAME}: " PASSWORD
#echo

# ------------------------------------------------------------
# 1. Get authentication token
# ------------------------------------------------------------
echo "Logging in to get token..."
#LOGIN_RESPONSE=$(curl -s -X POST "$LOGIN_URL" \
#  -H "Content-Type: application/json" \
#  -d "{\"userId\": \"${USERNAME}\", \"password\": \"${PASSWORD}\"}")

LOGIN_RESPONSE=$(curl -s -X POST "$LOGIN_URL" \
  --json "{\"userId\": \"${USERNAME}\", \"password\": \"${PASSWORD}\"}")

AUTH_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.webToken')

if [ -z "$AUTH_TOKEN" ] || [ "$AUTH_TOKEN" = "null" ]; then
  echo "Failed to get webToken"
  echo "$LOGIN_RESPONSE"
  exit 1
fi

echo "$AUTH_TOKEN"

# ------------------------------------------------------------
# 2. Send restart request with token
# ------------------------------------------------------------
#echo "Sending restart command to $RESTART_URL ..."
#RESPONSE=$(curl -s -X POST "$RESTART_URL" \
#  -H "Content-Type: application/json" \
#  -H "Authentication-Token: $AUTH_TOKEN" \
#  -w "\nHTTP status: %{http_code}\n")

#echo "$RESPONSE"

# Done
echo -e "\nRequest completed."
