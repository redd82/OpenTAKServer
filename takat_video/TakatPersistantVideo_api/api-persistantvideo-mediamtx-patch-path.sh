#!/bin/bash
# ------------------------------------------------------------------
# Script to call MediaMTX_PatchPath via TakatVideo API (with login)
# ------------------------------------------------------------------

# Configuration
HOST="192.168.18.129"
PORT="8081"
LOGIN_ENDPOINT="/api/login?include_auth_token"
PATCH_PATH_ENDPOINT="/api/persistantvideo/MediaMTX/PatchPath"

LOGIN_URL="http://${HOST}:${PORT}${LOGIN_ENDPOINT}"
PATCH_PATH_URL="http://${HOST}:${PORT}${PATCH_PATH_ENDPOINT}"

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
  echo "$LOGIN_RESPONSE"
  exit 1
fi

echo "Got auth token."
echo

# ------------------------------------------------------------
# 2. Prompt for PatchPath parameters
# ------------------------------------------------------------

read -r -p "Enter uid (required): " PATH_UID
[ -z "$PATH_UID" ] && echo "Error: uid is required." && exit 1

read -r -p "Enter fqdn (optional, press Enter to skip): " FQDN
read -r -p "Enter MediaMTX port (default 9997): " PORT_MMTX
read -r -p "Enter number of retries (default 0): " RETRIES
read -r -p "Enable verified SSL? (y/n, default n): " SSL_INPUT
read -r -p "Enter Jwt (optional, press Enter to skip): " JWT_TOKEN

# Custom config
read -r -p "Enter rpiCameraWidth (optional, press Enter to skip): " RPI_WIDTH
read -r -p "Enter rpiCameraHeight (optional, press Enter to skip): " RPI_HEIGHT

# Defaults (MATCH BACKEND)
PORT_MMTX=${PORT_MMTX:-9997}
RETRIES=${RETRIES:-0}

if [[ "$SSL_INPUT" =~ ^[Yy]$ ]]; then
    VERIFIED_SSL=true
else
    VERIFIED_SSL=false
fi

# ------------------------------------------------------------
# 3. Build JSON payload
# ------------------------------------------------------------

PAYLOAD="{\"uid\":\"$PATH_UID\",\"port\":$PORT_MMTX,\"retries\":$RETRIES,\"verified_ssl\":$VERIFIED_SSL"

if [ -n "$FQDN" ]; then
  PAYLOAD="${PAYLOAD},\"fqdn\":\"$FQDN\""
fi

if [ -n "$JWT_TOKEN" ]; then
  PAYLOAD="${PAYLOAD},\"Jwt\":\"$JWT_TOKEN\""
fi

# Custom config updates
if [ -n "$RPI_WIDTH" ]; then
  PAYLOAD="${PAYLOAD},\"rpiCameraWidth\":$RPI_WIDTH"
fi

if [ -n "$RPI_HEIGHT" ]; then
  PAYLOAD="${PAYLOAD},\"rpiCameraHeight\":$RPI_HEIGHT"
fi

PAYLOAD="${PAYLOAD}}"

echo
echo "Payload to send:"
echo "$PAYLOAD"
echo

# ------------------------------------------------------------
# 4. Send PatchPath request
# ------------------------------------------------------------

echo "Sending PatchPath request to MediaMTX..."
RESPONSE=$(curl -s -X PATCH "$PATCH_PATH_URL" \
  -H "Content-Type: application/json" \
  -H "Authentication-Token: $AUTH_TOKEN" \
  -d "$PAYLOAD" \
  -w "\nHTTP status: %{http_code}\n")

echo "$RESPONSE"
echo -e "\nRequest completed."
