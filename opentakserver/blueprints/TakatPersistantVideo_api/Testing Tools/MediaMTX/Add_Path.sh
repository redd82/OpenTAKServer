#!/bin/bash
# ------------------------------------------------------------
# MediaMTX Path Configuration Utility
# ------------------------------------------------------------
# Supports: get, add, patch, replace, delete
# API spec: https://github.com/bluenviron/mediamtx/blob/v1.15.1/api/openapi.yaml
# ------------------------------------------------------------

HOST="127.0.0.1"
PORT="9997"
BASE_URL="http://${HOST}:${PORT}/v3/config/paths"

# --- Helper: Check dependencies ---
for cmd in curl jq; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Error: $cmd is required but not installed."
    exit 1
  fi
done

# --- Helper: Print usage ---
usage() {
  echo "Usage:"
  echo "  $0 get <name>"
  echo "  $0 add <name> [json-file]"
  echo "  $0 patch <name> [json-file]"
  echo "  $0 replace <name> [json-file]"
  echo "  $0 delete <name>"
  echo
  echo "Examples:"
  echo "  $0 get cam1"
  echo "  $0 add cam1 path.json"
  echo "  $0 patch cam1 patch.json"
  echo "  $0 delete cam1"
  exit 1
}

# --- Parse args ---
ACTION="$1"
NAME="$2"
JSON_FILE="$3"

if [[ -z "$ACTION" || -z "$NAME" ]]; then
  usage
fi

# --- Construct URL based on action ---
case "$ACTION" in
  get)      METHOD="GET";     URL="${BASE_URL}/get/${NAME}" ;;
  add)      METHOD="POST";    URL="${BASE_URL}/add/${NAME}" ;;
  patch)    METHOD="PATCH";   URL="${BASE_URL}/patch/${NAME}" ;;
  replace)  METHOD="POST";    URL="${BASE_URL}/replace/${NAME}" ;;
  delete)   METHOD="DELETE";  URL="${BASE_URL}/delete/${NAME}" ;;
  *) usage ;;
esac

# --- Build curl command ---
if [[ "$METHOD" == "GET" || "$METHOD" == "DELETE" ]]; then
  RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X "$METHOD" "$URL")
else
  if [[ -n "$JSON_FILE" ]]; then
    if [[ ! -f "$JSON_FILE" ]]; then
      echo "Error: JSON file '$JSON_FILE' not found."
      exit 1
    fi
    RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X "$METHOD" \
      -H "Content-Type: application/json" \
      -d @"$JSON_FILE" \
      "$URL")
  else
    # Empty JSON if no file is provided
    RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X "$METHOD" \
      -H "Content-Type: application/json" \
      -d '{}' \
      "$URL")
  fi
fi

# --- Parse response ---
HTTP_BODY=$(echo "$RESPONSE" | sed -e 's/HTTP_STATUS\:.*//g')
HTTP_STATUS=$(echo "$RESPONSE" | tr -d '\n' | sed -e 's/.*HTTP_STATUS://')


# --- Display result ---
echo "------------------------------------------------------------"
echo "HTTP Status: $HTTP_STATUS"
echo "URL: $URL"
echo "------------------------------------------------------------"

if [[ "$HTTP_STATUS" == "200" || "$HTTP_STATUS" == "201" ]]; then
  echo "Success!"
  echo "$HTTP_BODY" | jq
else
  echo "Request failed (HTTP $HTTP_STATUS)"
  echo "$HTTP_BODY" | jq
  exit 1
fi
