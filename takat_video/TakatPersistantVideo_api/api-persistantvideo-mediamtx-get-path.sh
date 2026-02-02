#!/bin/bash
# ------------------------------------------------------------------
# Script to call MediaMTX_GetPath via TakatVideo API (with login)
# ------------------------------------------------------------------

# Configuration
HOST="192.168.18.129"
PORT="8081"
LOGIN_ENDPOINT="/api/login?include_auth_token"
ADD_PATH_ENDPOINT="/api/persistantvideo/MediaMTX/GetPath"

LOGIN_URL="http://${HOST}:${PORT}${LOGIN_ENDPOINT}"
ADD_PATH_URL="http://${HOST}:${PORT}${ADD_PATH_ENDPOINT}"

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

AUTH_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.response.user.authentication_token')

if [ "$AUTH_TOKEN" == "null" ] || [ -z "$AUTH_TOKEN" ]; then
  echo "Failed to get authentication token."
  echo "Response was:"
  echo "$LOGIN_RESPONSE"
  exit 1
fi

echo "Got auth token: $AUTH_TOKEN"
echo


# ------------------------------------------------------------
# 2. Prompt for GetPath parameters
# ------------------------------------------------------------

read -r -p "Enter uid (required): " PATH_UID
if [ -z "$PATH_UID" ]; then
  echo "Error: uid is required."
  exit 1
fi


read -r -p "Enter fqdn (optional, press Enter to skip): " FQDN
read -r -p "Enter MediaMTX port (default 9997): " PORT_MMTX
read -r -p "Enter number of retries (default 0): " RETRIES
read -r -p "Enable verified SSL? (y/n, default n): " SSL_INPUT
read -r -p "Enter Jwt (optional, press Enter to skip): " JWT_TOKEN

# Defaults
PORT_MMTX=${PORT_MMTX:-9997}
RETRIES=${RETRIES:-0}

# SSL boolean
if [[ "$SSL_INPUT" =~ ^[Yy]$ ]]; then
    VERIFIED_SSL=true
else
    VERIFIED_SSL=false
fi


# ------------------------------------------------------------
# 3. Build dynamic JSON payload
# ------------------------------------------------------------
# Start base JSON
PAYLOAD="{\"uid\":\"$PATH_UID\",\"port\":$PORT_MMTX,\"retries\":$RETRIES,\"verified_ssl\":$VERIFIED_SSL"


# Add optional fields if provided
if [ -n "$FQDN" ]; then
  PAYLOAD="${PAYLOAD},\"fqdn\":\"$FQDN\""
fi

if [ -n "$JWT_TOKEN" ]; then
  PAYLOAD="${PAYLOAD},\"Jwt\":\"$JWT_TOKEN\""
fi

# Close JSON
PAYLOAD="${PAYLOAD}}"

echo "Payload to send:"
echo "$PAYLOAD"
echo


# ------------------------------------------------------------
# 4. Send GetPath request
# ------------------------------------------------------------
echo "Sending request to MediaMTX..."
RESPONSE=$(curl -s -X POST "$ADD_PATH_URL" \
  -H "Content-Type: application/json" \
  -H "Authentication-Token: $AUTH_TOKEN" \
  -d "$PAYLOAD" \
  -w "\nHTTP status: %{http_code}\n")

echo "$RESPONSE"

echo -e "\nRequest completed."
