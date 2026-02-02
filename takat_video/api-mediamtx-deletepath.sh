#!/bin/bash
# ------------------------------------------------------------
# Script to delete a specific MediaMTX path
# ------------------------------------------------------------

# Configuration
HOST="127.0.0.1"
PORT="9997"                      # default MediaMTX API port
BASE_URL="http://${HOST}:${PORT}/v3/config/paths/delete"

# Prompt user for path name
read -rp "Enter the path name to delete: " PATH_NAME

# Validate input
if [[ -z "$PATH_NAME" ]]; then
  echo "Error: path name cannot be empty."
  exit 1
fi

# Construct full URL
URL="${BASE_URL}/${PATH_NAME}"

# Confirm before deleting
read -rp "Are you sure you want to delete path '$PATH_NAME'? (y/N): " CONFIRM
if [[ "$CONFIRM" != "y" && "$CONFIRM" != "Y" ]]; then
  echo "Deletion cancelled."
  exit 0
fi

# Send DELETE request
echo "Sending DELETE request to $URL ..."
RESPONSE=$(curl -s -X DELETE "$URL")

# Display full response
echo "Server response:"
echo "$RESPONSE" | jq .

# Done
echo -e "\nRequest completed."
