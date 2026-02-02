#!/bin/bash
# ------------------------------------------------------------
# Script
# ------------------------------------------------------------

# Configuration
HOST="192.168.18.120"
PORT="10301"
ENDPOINT="/devapi/mediamtx/getAllMediaMTXPathConfigs"
URL="http://${HOST}:${PORT}${ENDPOINT}"

# JSON payload (if the endpoint requires one; using empty JSON as default)
DATA='{}'

# Optional headers
CONTENT_TYPE="Content-Type: application/json"

# Send GET request
echo "Sending GET to $URL ..."
curl -X GET "$URL" \
     -H "$CONTENT_TYPE" \
     #-d "$DATA" \


# Done
echo -e "\nRequest completed."
