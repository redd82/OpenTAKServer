#!/bin/bash

# ============================================================================================
# Script: start_ffmpeg.sh
#
# Securely launches an FFmpeg process that copies an input stream to a MediaMTX RTSP endpoint,
# and notifies a callback server once the stream is live.
#
# Dependencies:
# - curl (for HTTP API calls):      sudo apt install curl
# - jq (for safe JSON generation):  sudo apt install jq
#
# --------------------------------------------------------------------------------------------
# USAGE EXAMPLE:
#
# ./start_ffmpeg.sh \
#   5000000 \
#   "http://192.168.1.50/stream" \
#   rtsp \
#   "linked_uid_1234/stream" \
#   "CAM123" \
#   "ABCDEF" \
#   "rtsp" \
#   "mediamtx.local" \
#   "8554" \
#   "https" \
#   "dev-ots.takat.nl" \
#   "8080" \
#   "jwtuser" \
#   "jwttoken"
#
# ARGUMENTS:
#   1.  TIMEOUT               FFmpeg socket timeout (e.g. 5000000)
#   2.  INPUT_URL             Camera or source stream URL
#   3.  FFMPEG_PROTOCOL       Output format for FFmpeg (rtsp, rtmp, etc.)
#   4.  LINKED_PATH           Path portion for MediaMTX (e.g. stream path)
#   5.  CAMERA_UID            Camera identifier
#   6.  OTP                   One-time pass or key
#   7.  MTX_PROTOCOL          MediaMTX protocol (http or rtsp)
#   8.  MTX_HOST              MediaMTX hostname or IP
#   9.  MTX_PORT              MediaMTX port (optional)
#   10. CALLBACK_PROTOCOL     Callback protocol (http or https)
#   11. CALLBACK_HOST         Callback host/domain
#   12. CALLBACK_PORT         Callback port (optional)
#   13. JWT_USER              JWT username (optional)
#   14. JWT_TOKEN             JWT bearer token (optional)
#
# --------------------------------------------------------------------------------------------
# OUTPUT EXAMPLE:
#
# Starting FFmpeg stream...
# Input:  http://192.168.1.50/stream
# Output: rtsp://127.0.0.1:8554/linked_uid_1234/stream
# Virtual Camera URL: rtsp://mediamtx.local:8554/linked_uid_1234/stream
# Callback: https://dev-ots.takat.nl:8080/RunOnReady
# Callback returned HTTP status code: 200
# FFmpeg PID: 12345
# ============================================================================================

# Input arguments
TIMEOUT="$1"
FFMPEG_CAMERA_INPUT_URL="$2"
FFMPEG_PROTOCOL="$3"
LINKED_PATH="$4"
CAMERA_UID="$5"
OTP="$6"
MTX_PROTOCOL="$7"
MTX_HOST="$8"
MTX_PORT="${9:-}"
CALLBACK_PROTOCOL="${10:-}"
CALLBACK_HOST="${11:-}"
CALLBACK_PORT="${12:-}"
JWT_USER="${13:-}"
JWT_TOKEN="${14:-}"

# ===== Input Validation =====
ALLOWED_PROTOCOLS=("http" "https" "rtsp" "rtmp" "srt" "udp" "tcp")

function is_protocol_allowed {
    local proto="$1"
    for allowed in "${ALLOWED_PROTOCOLS[@]}"; do
        if [[ "$proto" == "$allowed" ]]; then
            return 0
        fi
    done
    return 1
}

if ! is_protocol_allowed "$FFMPEG_PROTOCOL"; then
    echo "Error: Unsupported FFMPEG protocol: $FFMPEG_PROTOCOL"
    exit 1
fi

if ! is_protocol_allowed "$MTX_PROTOCOL"; then
    echo "Error: Unsupported MediaMTX protocol: $MTX_PROTOCOL"
    exit 1
fi

if ! is_protocol_allowed "$CALLBACK_PROTOCOL"; then
    echo "Error: Unsupported callback protocol: $CALLBACK_PROTOCOL"
    exit 1
fi

if [[ "$LINKED_PATH" =~ [^a-zA-Z0-9/_-] ]]; then
    echo "Error: LINKED_PATH contains illegal characters."
    exit 1
fi

# ===== URL Construction =====
if [ -n "$MTX_PORT" ]; then
    MTX_BASE_URL="${MTX_PROTOCOL}://${MTX_HOST}:${MTX_PORT}"
    COPIED_STREAM_URL="${FFMPEG_PROTOCOL}://127.0.0.1:${MTX_PORT}/${LINKED_PATH}"
else
    MTX_BASE_URL="${MTX_PROTOCOL}://${MTX_HOST}"
    COPIED_STREAM_URL="${FFMPEG_PROTOCOL}://127.0.0.1/${LINKED_PATH}"
fi

if [ -n "$CALLBACK_PORT" ]; then
    CALLBACK_BASE_URL="${CALLBACK_PROTOCOL}://${CALLBACK_HOST}:${CALLBACK_PORT}"
else
    CALLBACK_BASE_URL="${CALLBACK_PROTOCOL}://${CALLBACK_HOST}"
fi

VIRTUAL_CAMERA_URL="${FFMPEG_PROTOCOL}://${MTX_HOST}:${MTX_PORT}/${LINKED_PATH}"
CALLBACK_URL="${CALLBACK_BASE_URL}/RunOnReady"

# ===== Logging =====
echo "Starting FFmpeg stream..."
echo "Input:  $FFMPEG_CAMERA_INPUT_URL"
echo "Output: $COPIED_STREAM_URL"
echo "Virtual Camera URL: $VIRTUAL_CAMERA_URL"
echo "Callback: $CALLBACK_URL"

# ===== Start FFmpeg =====
ffmpeg -timeout "$TIMEOUT" -i "$FFMPEG_CAMERA_INPUT_URL" -c copy -f "$FFMPEG_PROTOCOL" "$COPIED_STREAM_URL" &
FFMPEG_PID=$!

# ===== Callback Payload =====
json_payload=$(jq -n \
    --arg camera_uid "$CAMERA_UID" \
    --arg otp "$OTP" \
    --arg copied_stream_url "$VIRTUAL_CAMERA_URL" \
    --arg ffmpeg_pid "$FFMPEG_PID" \
    '{camera_uid: $camera_uid, otp: $otp, copied_stream_url: $copied_stream_url, ffmpeg_pid: $ffmpeg_pid}')

# ===== Callback Request =====
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

echo "Callback returned HTTP status code: $response"
echo "FFmpeg PID: $FFMPEG_PID"
