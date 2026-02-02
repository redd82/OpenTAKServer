#!/bin/bash

# ------------------------------------------------------------
# Script to query all active MediaMTX paths
# ------------------------------------------------------------

# Configuration
HOST="127.0.0.1"
PORT="9997"                       # default MediaMTX API port
ENDPOINT="/v3/config/paths/list"
URL="http://${HOST}:${PORT}${ENDPOINT}"

# Send GET request
echo "Fetching active MediaMTX paths from $URL ..."
RESPONSE=$(curl -s "$URL")

# Display full JSON
echo "Full response:"
echo "$RESPONSE" | jq .

# Optionally extract just the path names
echo
echo "Active paths:"
echo "$RESPONSE" | jq -r '.items[].name'

# Done
echo -e "\nRequest completed."
