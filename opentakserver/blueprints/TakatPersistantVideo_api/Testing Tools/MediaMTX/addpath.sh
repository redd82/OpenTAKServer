#!/bin/bash
# ------------------------------------------------------------
# Script to add a new MediaMTX path
# ------------------------------------------------------------

# Configuration
HOST="192.168.18.129"
PORT="9997"                          # MediaMTX API port
BASE_URL="http://${HOST}:${PORT}/v3/config/paths/add"

# Prompt user for path name and source URL
read -rp "Enter the new path name: " PATH_NAME
read -rp "Enter the source URL (e.g., rtsp://... or publisher): " SOURCE_URL

# Validate input
if [[ -z "$PATH_NAME" ]]; then
  echo "Error: path name cannot be empty."
  exit 1
fi
if [[ -z "$SOURCE_URL" ]]; then
  echo "Error: source URL cannot be empty."
  exit 1
fi

# Construct JSON payload
JSON_PAYLOAD=$(jq -n \
  --arg name "$PATH_NAME" \
  --arg source "$SOURCE_URL" \
  --argjson sourceOnDemand true \
  --arg rpiCameraWidth 1920 \
  --arg rpiCameraHeight 1080 \
  --arg rpiCameraFPS 30 \
  --arg rpiCameraCodec "auto" \
  --arg rpiCameraBitrate 5000000 \
  '{
      name: $name,
      source: $source,
      sourceOnDemand: $sourceOnDemand,
      rpiCameraWidth: ($rpiCameraWidth|tonumber),
      rpiCameraHeight: ($rpiCameraHeight|tonumber),
      rpiCameraFPS: ($rpiCameraFPS|tonumber),
      rpiCameraCodec: $rpiCameraCodec,
      rpiCameraBitrate: ($rpiCameraBitrate|tonumber),
      record: false,
      recordPath: "./recordings/%path/%Y-%m-%d_%H-%M-%S-%f",
      recordFormat: "fmp4",
      recordPartDuration: "1s",
      recordSegmentDuration: "1h0m0s",
      recordDeleteAfter: "1d",
      overridePublisher: true,
      maxReaders: 0,
      fallback: "",
      useAbsoluteTimestamp: false
  }'
)

# Confirm before adding
echo "About to add path '$PATH_NAME' with source '$SOURCE_URL'."
read -rp "Proceed? (y/N): " CONFIRM
if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
  echo "Addition cancelled."
  exit 0
fi

# Send POST request
echo "Sending POST request to $BASE_URL ..."
RESPONSE=$(curl -s -X POST "$BASE_URL" \
  -H "Content-Type: application/json" \
  -d "$JSON_PAYLOAD")

# Display full response
echo "Server response:"
echo "$RESPONSE" | jq .

# Done
echo -e "\nRequest completed."
