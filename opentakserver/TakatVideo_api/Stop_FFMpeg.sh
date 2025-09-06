#!/bin/bash

# stop_ffmpeg.sh
# Securely stops a running FFmpeg process and notifies a callback URL with the camera's status.
#
# Usage:
#   ./stop_ffmpeg.sh <camera_uid> <otp> <pid> <callback_url> [jwt_user] [jwt_token]
#
# Example:
#   ./stop_ffmpeg.sh CAM123-uid ABCDEF-otp 12345 "https://dev-ots.takat.nl/RunOnNotReady" myuser mytoken
#
# Dependencies:
#   - jq (for JSON handling): sudo apt-get install jq
#   - curl (for HTTP requests): sudo apt-get install curl
#
# Security Enhancements:
#   - Input validation to prevent command injection.
#   - Usage of 'set -euo pipefail' for strict error handling.
#   - Secure handling of JWT tokens with optional authentication.

set -euo pipefail

# Validate and sanitize inputs
if [ $# -lt 4 ]; then
    echo "Usage: $0 <camera_uid> <otp> <pid> <callback_url> [jwt_user] [jwt_token]"
    exit 1
fi

# Assign input arguments to variables
readonly CAMERA_UID="$1"
readonly OTP="$2"
readonly PID="$3"
readonly CALLBACK_URL="$4"
readonly JWT_USER="${5:-}"
readonly JWT_TOKEN="${6:-}"

# Validate that PID is a positive integer
if ! [[ "$PID" =~ ^[0-9]+$ ]]; then
    echo "Error: PID must be a positive integer."
    exit 1
fi

# Terminate the FFmpeg process
if kill "$PID" > /dev/null 2>&1; then
    echo "FFmpeg process with PID $PID terminated."
else
    echo "Failed to terminate FFmpeg process with PID $PID or it was already stopped."
fi

# Prepare JSON payload for callback
json_payload=$(jq -n \
    --arg camera_uid "$CAMERA_UID" \
    --arg otp "$OTP" \
    --arg pid "$PID" \
    --arg virtual_camera_url "rtsp://127.0.0.1/$CAMERA_UID" \
    '{camera_uid: $camera_uid, otp: $otp, pid: $pid, virtual_camera_url: $virtual_camera_url}')

# Send callback notification
if [ -n "$JWT_USER" ] && [ -n "$JWT_TOKEN" ]; then
    response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$CALLBACK_URL" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $JWT_TOKEN" \
        -d "$json_payload")
else
    response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$CALLBACK_URL" \
        -H "Content-Type: application/json" \
        -d "$json_payload")
fi

# Output the result of the callback request
echo "Callback returned HTTP status code: $response"
