import json, copy
from typing import Optional, Dict, Any, Tuple, Union
from enum import Enum
import re

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urlencode
import logging
#from requests.adapters import HTTPAdapter, Retry

# ─────────────────────────────────────────────────────────────────────────────
# Third‑party / project imports
# ────────────────────────────────────────────────────────────────────────────
#from opentakserver.defaultconfig import DefaultConfig  # central config

from opentakserver.blueprints.TakatVideo_api.util import Safe_Link as Link
from opentakserver.blueprints.TakatVideo_api.util import Resolutions as Resolutions
from opentakserver.blueprints.TakatVideo_api.util import HttpCode as HTTPStatusCodes
from opentakserver.blueprints.TakatVideo_api.util import OTP_UID_Manager as SessionCredentials
from opentakserver.blueprints.TakatVideo_api.util import Unified_Enum_Inputs as UnifiedInputs

# If you need sanitising helpers, import them here as well:
# from opentakserver.blueprints.TakatVideo_api.util import Util_Sanitize


# ─────────────────────────────────────────────────────────────────────────────
# Mediamtx API path configuration object
# ─────────────────────────────────────────────────────────────────────────────   
import json
import logging
from typing import Any, Dict, Optional, Tuple, List, Union


class MediaMTXPathConfigV5:

    def __init__(self, name: str, source: str):
        # mandatory fields
        self._name = name
        self._source = source
        
        # boolean fields with default values
        self._runOnReadRestart = False
        self._runOnReadyRestart = False
        self._runOnDemandRestart = False
        self._runOnInitRestart = False
        self._rpiCameraTextOverlayEnable = False
        self._rpiCameraHDR = False
        self._rpiCameraHFlip = False
        self._rpiCameraVFlip = False
        self._rpiCameraSecondary = False
        self._rtspAnyPort = False
        self._overridePublisher = False
        self._useAbsoluteTimestamp = False
        self._record = False
        # int fields with default int values
        self._maxReaders = 0
        self._rpiCameraMJPEGQuality = 0
        self._rpiCameraIDRPeriod = 0
        self._rpiCameraBitrate = 0
        self._rpiCameraFlickerPeriod = 0
        self._rpiCameraLensPosition = 0
        self._rpiCameraFPS = 0
        self._rpiCameraGain = 0
        self._rpiCameraEV = 0
        self._rpiCameraShutter = 0
        self._rpiCameraBrightness = 0
        self._rpiCameraContrast = 0
        self._rpiCameraSaturation = 0
        self._rpiCameraSharpness = 0
        self._rpiCameraCamID = 0
        self._rpiCameraWidth = 0
        self._rpiCameraHeight = 0
        self._rtpUDPReadBufferSize = 0
        self._rtspUDPReadBufferSize = 0
        self._mpegtsUDPReadBufferSize = 0
        # list fields with default list values
        self._rpiCameraAWBGains=[0,0]

    
    # boolean fields getters/setters
    def runOnReadRestart(self, input=None):
        if input == None: return self._runOnReadRestart
        if input in ("1", "true", "yes", "on"): self._runOnReadRestart= True
        elif input in ("0", "false", "no", "off"): self._runOnReadRestart= False
    def runOnReadyRestart(self, input=None):
        if input == None: return self._runOnReadyRestart
        if input in ("1", "true", "yes", "on"): self._runOnReadyRestart= True
        elif input in ("0", "false", "no", "off"): self._runOnReadyRestart= False
    def runOnDemandRestart(self, input=None): 
        if input == None: return self._runOnReadRestart
        if input in ("1", "true", "yes", "on"): self._runOnReadRestart= True
        elif input in ("0", "false", "no", "off"): self._runOnReadRestart= False
    def runOnInitRestart(self, input=None):
        if input == None: return self._runOnInitRestart
        if input in ("1", "true", "yes", "on"): self._runOnInitRestart= True
        elif input in ("0", "false", "no", "off"): self._runOnInitRestart= False
    def rpiCameraTextOverlayEnable(self, input=None):
        if input == None: return self._rpiCameraTextOverlayEnable
        if input in ("1", "true", "yes", "on"): self._rpiCameraTextOverlayEnable= True
        elif input in ("0", "false", "no", "off"): self._rpiCameraTextOverlayEnable= False
    def rpiCameraHDR(self, input=None):
        if input == None: return self._rpiCameraHDR
        if input in ("1", "true", "yes", "on"): self._rpiCameraHDR= True
        elif input in ("0", "false", "no", "off"): self._rpiCameraHDR= False
    def rpiCameraHFlip(self, input=None):
        if input == None: return self._rpiCameraHFlip
        if input in ("1", "true", "yes", "on"): self._rpiCameraHFlip= True
        elif input in ("0", "false", "no", "off"): self._rpiCameraHFlip= False
    def rpiCameraVFlip(self, input=None):
        if input == None: return self._rpiCameraVFlip
        if input in ("1", "true", "yes", "on"): self._rpiCameraVFlip= True
        elif input in ("0", "false", "no", "off"): self._rpiCameraVFlip= False
    def rpiCameraSecondary(self, input=None):
        if input == None: return self._rpiCameraSecondary
        if input in ("1", "true", "yes", "on"): self._rpiCameraSecondary= True
        elif input in ("0", "false", "no", "off"): self._rpiCameraSecondary= False
    def rtspAnyPort(self, input=None):
        if input == None: return self._rtspAnyPort
        if input in ("1", "true", "yes", "on"): self._rtspAnyPort= True
        elif input in ("0", "false", "no", "off"): self._rtspAnyPort= False
    def overridePublisher(self, input=None):
        if input == None: return self._overridePublisher
        if input in ("1", "true", "yes", "on"): self._overridePublisher= True
        elif input in ("0", "false", "no", "off"): self._overridePublisher= False
    def useAbsoluteTimestamp(self, input=None):
        if input == None: return self._useAbsoluteTimestamp
        if input in ("1", "true", "yes", "on"): self._useAbsoluteTimestamp= True
        elif input in ("0", "false", "no", "off"): self._useAbsoluteTimestamp= False
    def record(self, input=None):
        if input == None: return self._record
        if input in ("1", "true", "yes", "on"): self._record= True
        elif input in ("0", "false", "no", "off"): self._record= False
    
        """
            Boolean fields:
            "runOnReadRestart": true,
            "runOnReadyRestart": true,
            "runOnDemandRestart": true,
            "runOnInitRestart": true,
            "rpiCameraTextOverlayEnable": true,
            "rpiCameraHDR": true,             
            "rpiCameraHFlip": true,
            "rpiCameraVFlip": true,            
            "rpiCameraSecondary": true,
            "rtspAnyPort": true,
            "overridePublisher": true,
            "useAbsoluteTimestamp": true,
            "record": true,"sourceOnDemand": true,
        """
    
    
        """
        {
            "name": "string",
            "source": "string",
            "sourceFingerprint": "string",
            "sourceOnDemandStartTimeout": "string",
            "sourceOnDemandCloseAfter": "string",
            "srtReadPassphrase": "string",
            "fallback": "string",
            "recordPath": "string",
            "recordFormat": "string",
            "recordPartDuration": "string",
            "recordMaxPartSize": "string",
            "recordSegmentDuration": "string",
            "recordDeleteAfter": "string",
            "srtPublishPassphrase": "string",
            "rtspTransport": "string",
            "rtspRangeType": "string",
            "rtspRangeStart": "string",
            "rtpSDP": "string",
            "sourceRedirect": "string",
            "rpiCameraExposure": "string",
            "rpiCameraAWB": "string",
            "rpiCameraDenoise": "string",
            "rpiCameraMetering": "string",
            "rpiCameraROI": "string",
            "rpiCameraTuningFile": "string",
            "rpiCameraMode": "string",
            "rpiCameraAfMode": "string",
            "rpiCameraAfRange": "string",
            "rpiCameraAfSpeed": "string",
            "rpiCameraAfWindow": "string",
            "rpiCameraTextOverlay": "string",
            "rpiCameraCodec": "string",
            "rpiCameraHardwareH264Profile": "string",
            "rpiCameraHardwareH264Level": "string",
            "rpiCameraSoftwareH264Profile": "string",
            "rpiCameraSoftwareH264Level": "string",
            "runOnInit": "string",
            "runOnDemand": "string",
            "runOnDemandStartTimeout": "string",
            "runOnDemandCloseAfter": "string",
            "runOnUnDemand": "string",
            "runOnReady": "string",
            "runOnNotReady": "string",
            "runOnRead": "string",
            "runOnUnread": "string",
            "runOnRecordSegmentCreate": "string",
            "runOnRecordSegmentComplete": "string"
            

            
            "rpiCameraAWBGains": [0,0],
            }
        """
    def MaxReaders(self, value=None):
        """Maximum number of clients allowed to read/view this stream. (hardcoded to 1000) 0 = no limit."""
        if value == None: return self._maxReaders
        else: self._range(value, 0, 1000)
    def RpiCameraMJPEGQuality(self, value=None):
        """MJPEG quality (2–31). 0 = default."""
        if value is None: return self._rpiCameraMJPEGQuality
        self._rpiCameraMJPEGQuality = self._range(value, 0, 31)
        return self._rpiCameraMJPEGQuality
    def RpiCameraIDRPeriod(self, value=None):
        """IDR (keyframe) interval in frames (1–300). 0 = default."""
        if value is None: return self._rpiCameraIDRPeriod
        self._rpiCameraIDRPeriod = self._range(value, 0, 300)
        return self._rpiCameraIDRPeriod
    def RpiCameraBitrate(self, value=None):
        """Bitrate in bits per second (10_000–50_000_000). 0 = default (~4Mbps)."""
        if value is None: return self._rpiCameraBitrate
        self._rpiCameraBitrate = self._range(value, 0, 50000000)
        return self._rpiCameraBitrate
    def RpiCameraFlickerPeriod(self, value=None):
        """Anti-flicker frequency: 50 or 60 Hz. 0 = default."""
        if value is None: return self._rpiCameraFlickerPeriod
        self._rpiCameraFlickerPeriod = self._range(value, 50, 60)
        return self._rpiCameraFlickerPeriod
    def RpiCameraLensPosition(self, value=None):
        """Lens position 0–32 (0 = auto)."""
        if value is None: return self._rpiCameraLensPosition
        self._rpiCameraLensPosition = self._range(value, 0, 32)
        return self._rpiCameraLensPosition
    def RpiCameraFPS(self, value=None):
        """Camera FPS (1–120). 0 = default."""
        if value is None: return self._rpiCameraFPS
        self._rpiCameraFPS = self._range(value, 0, 120)
        return self._rpiCameraFPS
    def RpiCameraGain(self, value=None):
        """Analog gain 1–16 (0 = auto)."""
        if value is None: return self._rpiCameraGain
        self._rpiCameraGain = self._range(value, 0, 16)
        return self._rpiCameraGain
    def RpiCameraEV(self, value=None):
        """Exposure compensation (-10 to +10)."""
        if value is None: return self._rpiCameraEV
        self._rpiCameraEV = self._range(value, -10, 10)
        return self._rpiCameraEV
    def RpiCameraShutter(self, value=None):
        """Shutter speed in µs (100–10_000_000). 0 = auto."""
        if value is None: return self._rpiCameraShutter
        self._rpiCameraShutter = self._range(value, 0, 10000000)
        return self._rpiCameraShutter
    def RpiCameraBrightness(self, value=None):
        """Brightness 0–1. 0 = default."""
        if value is None: return self._rpiCameraBrightness
        self._rpiCameraBrightness = self._range(value, 0, 1)
        return self._rpiCameraBrightness
    def RpiCameraContrast(self, value=None):
        """Contrast 0–32."""
        if value is None: return self._rpiCameraContrast
        self._rpiCameraContrast = self._range(value, 0, 32)
        return self._rpiCameraContrast
    def RpiCameraSaturation(self, value=None):
        """Saturation 0–32."""
        if value is None: return self._rpiCameraSaturation
        self._rpiCameraSaturation = self._range(value, 0, 32)
        return self._rpiCameraSaturation
    def RpiCameraSharpness(self, value=None):
        """Sharpness 0–32."""
        if value is None: return self._rpiCameraSharpness
        self._rpiCameraSharpness = self._range(value, 0, 32)
        return self._rpiCameraSharpness
    def RpiCameraCamID(self, value=None):
        """Camera ID (0 or 1)."""
        if value is None: return self._rpiCameraCamID
        self._rpiCameraCamID = self._range(value, 0, 1)
        return self._rpiCameraCamID
    def RpiCameraWidth(self, value=None):
        """Video width in pixels (64–4056). 0 = auto."""
        if value is None: return self._rpiCameraWidth
        self._rpiCameraWidth = self._range(value, 0, 4056)
        return self._rpiCameraWidth
    def RpiCameraHeight(self, value=None):
        """Video height in pixels (64–3040). 0 = auto."""
        if value is None: return self._rpiCameraHeight
        self._rpiCameraHeight = self._range(value, 0, 3040)
        return self._rpiCameraHeight
    # list fields getters/setters    
    def RpiCameraAWBGains(self, value=None):
        if value is None: return self._rpiCameraAWBGains
        if not isinstance(value, (list, tuple)) or len(value) != 2:
            raise ValueError("AWBGains must be a list or tuple of two numbers [RedGain, BlueGain]")
        # Clamp each channel gain individually
        self._rpiCameraAWBGains = [
            self._range_float(float(value[0]), 0.0, 8.0),
            self._range_float(float(value[1]), 0.0, 8.0)
        ]
    
    
    
    """
RPi Camera String Settings with Mandatory Input Values
------------------------------------------------------

1. rpiCameraExposure
   - Description: Camera exposure mode.
   - Mandatory Inputs:
       * "auto"        - Automatic exposure
       * "night"       - Optimized for low-light conditions
       * "nightpreview"- Enhanced preview in low-light
       * "backlight"   - Compensates for strong backlighting
       * "spotlight"   - Adjusts for spotlight conditions
       * "sports"      - For fast-moving subjects
       * "snow"        - Compensates for bright snow scenes
       * "beach"       - Optimized for beach scenes
       * "verylong"    - Extremely long exposures
       * "fixedfps"    - Fixed frame rate exposure
   - Note: "auto" allows the camera to adjust exposure automatically.

2. rpiCameraAWB
   - Description: Auto White Balance mode.
   - Mandatory Inputs:
       * "auto"        - Automatic white balance
       * "sun"         - Daylight
       * "cloudy"      - Overcast
       * "shade"       - Shaded conditions
       * "tungsten"    - Incandescent lighting
       * "fluorescent" - Fluorescent lighting
       * "incandescent"- Incandescent lighting
       * "flash"       - Flash lighting
       * "horizon"     - Horizon lighting
   - Note: "auto" enables automatic white balance adjustment.

3. rpiCameraMetering
   - Description: Exposure metering mode.
   - Mandatory Inputs:
       * "average" - Average light metering
       * "spot"    - Spot metering
       * "backlit" - Backlit metering
       * "matrix"  - Matrix metering
   - Note: "average" uses the average light level across the frame.

References:
- Raspberry Pi Camera Documentation & Forums
- Picamera2 GitHub Issues
"""

    
    def Name(self):
        return self._name
    def Source(self):
        return self._source
    def SourceFingerprint(self, value=None):
        pass
    def SourceOnDemandStartTimeout(self, value=None):
        pass
    def SourceOnDemandCloseAfter(self, value=None):
        pass
    def SrtReadPassphrase(self, value=None):
        pass
    def Fallback(self, value=None):
        pass
    def RecordPath(self, value=None):
        pass
    def RecordFormat(self, value=None):
        pass
    def RecordPartDuration(self, value=None):
        pass
    def RecordMaxPartSize(self, value=None):
        pass
    def RecordSegmentDuration(self, value=None):
        pass
    def RecordDeleteAfter(self, value=None):
        pass
    def SrtPublishPassphrase(self, value=None):
        pass
    def RtspTransport(self, value=None):
        pass
    def RtspRangeType(self, value=None):
        pass
    def RtspRangeStart(self, value=None):
        pass
    def RtpSDP(self, value=None):
        pass
    def SourceRedirect(self, value=None):
        pass
    def RpiCameraExposure(self, value=None):
        pass
    def RpiCameraAWB(self, value=None):
        pass
    def RpiCameraDenoise(self, value=None):
        pass
    def RpiCameraMetering(self, value=None):
        """rpiCameraMetering
            - Description: Exposure metering mode.
            - Mandatory Inputs:
                * "average" - Average light metering
                * "spot"    - Spot metering
                * "backlit" - Backlit metering
                * "matrix"  - Matrix metering
            - Note: "average" uses the average light level across the frame.
        """
        if value in ("1", "true", "yes", "on"): 
        
        pass
    def RpiCameraROI(self, value=None):
        pass
    def RpiCameraTuningFile(self, value=None):
        pass
    def RpiCameraMode(self, value=None):
        pass
    def RpiCameraAfMode(self, value=None):
        pass
    def RpiCameraAfRange(self, value=None):
        pass
    def RpiCameraAfSpeed(self, value=None):
        pass
    def RpiCameraAfWindow(self, value=None):
        pass
    def RpiCameraTextOverlay(self, value=None):
        pass

    def RpiCameraCodec(self, value=None):
        pass

    def RpiCameraHardwareH264Profile(self, value=None):
        pass

    def RpiCameraHardwareH264Level(self, value=None):
        pass

    def RpiCameraSoftwareH264Profile(self, value=None):
        pass

    def RpiCameraSoftwareH264Level(self, value=None):
        pass

    def RunOnInit(self, value=None):
        pass

    def RunOnDemand(self, value=None):
        pass

    def RunOnUnDemand(self, value=None):
        pass

    def RunOnReady(self, value=None):
        pass

    def RunOnNotReady(self, value=None):
        pass

    def RunOnRead(self, value=None):
        pass

    def RunOnUnread(self, value=None):
        pass

    def RunOnRecordSegmentCreate(self, value=None):
        pass

    def RunOnRecordSegmentComplete(self, value=None):
        pass

    # helper methods
    def _range(self, value: int, minimum: int, maximum: int) -> int: return max(minimum, min(value, maximum))
    def _range_float(self, value: float, minimum: float, maximum: float) -> float: return max(minimum, min(value, maximum))
 
 
 
 
 
 
 
 
 
 
    
class MediaMTXPathConfigV4:
    """
    Represents a MediaMTX path configuration.
    - Internal attributes store values (prefixed with _)
    - Public properties give controlled access
    - Supports dict ↔ JSON serialization
    
    Example usage of MediaMTXPathConfigV4 with all options:

    config = MediaMTXPathConfigV4(
        name="cam_full",                   # Required: unique path name
        source="rpiCamera",                # Required: source URL or device

        # ── Resolution ──
        resolution=Resolutions.fhd,        # Predefined resolution [1920, 1080]
        # resolution=[1280, 1024],        # Alternatively, custom resolution list

        # ── Override individual width/height if needed
        rpiCameraWidth=1600,               # Optional, overrides resolution width
        rpiCameraHeight=900,               # Optional, overrides resolution height

        # ── Max ranges for width/height/maxReaders
        rpiCameraWidthMax=2000,            # Optional
        rpiCameraHeightMax=1200,           # Optional
        maxReadersMax=500,                 # Optional

        # ── Source / Recording Options
        sourceOnDemand=True,
        sourceOnDemandStartTimeout="15s",
        record=True,
        recordPath="./my_recordings/%path/%Y-%m-%d_%H-%M-%S",
        recordFormat="fmp4",
        maxReaders=100,

        # ── Raspberry Pi Camera settings
        rpiCameraFPS=25,
        rpiCameraBrightness=50,
        rpiCameraContrast=2,
        rpiCameraSaturation=1,
        rpiCameraSharpness=3,
        rpiCameraExposure="long",
        rpiCameraAWB="daylight",
        rpiCameraAWBGains=[1.2, 1.3],
        rpiCameraDenoise="cdn_hq",
        rpiCameraMetering="matrix",
        rpiCameraGain=1.0,
        rpiCameraEV=2,
        rpiCameraHDR=True,
        rpiCameraCodec="hardwareH264",
        rpiCameraIDRPeriod=120,
        rpiCameraBitrate=6000000,
        rpiCameraHardwareH264Profile="high",
        rpiCameraHardwareH264Level="4.2",
        rpiCameraMJPEGQuality=70,

        # ── Hooks / Scripts
        runOnInit="echo 'Starting camera'",
        runOnInitRestart=True,
        runOnReady="echo 'Path ready'",
        runOnRead="echo 'Reader connected'"
    )

    Notes:
    - Any parameter from DEFAULTS can be passed as a keyword argument.
    - Resolution can be passed as a predefined Resolutions attribute or a custom [width, height] list.
    - Max ranges for width, height, and maxReaders can be customized at initialization.
    - Hook commands are optional and can run shell commands on path events.


    
    """

    # ─────────────────────────────
    # Default values (from "all_others") with allowed inputs
    # ─────────────────────────────
    DEFAULTS: Dict[str, Any] = {
        # ───── Source Settings ─────
        "source": "",  # string | source URL or device (e.g. "rtsp://...", "rtsps://...", "srt://...", "rtmp://...", "v4l2:///dev/video0", "rpiCamera", etc.)
        "sourceFingerprint": "",  # string | SHA256 fingerprint of allowed publisher certificate
        "sourceOnDemand": False,  # bool | True to start source only when first reader connects
        "sourceOnDemandStartTimeout": "10s",  # duration | wait time for source to start (e.g. "10s", "1m")
        "sourceOnDemandCloseAfter": "10s",  # duration | time to stop source after last reader disconnects
        "maxReaders": 0,  # int | 0 = unlimited
        "srtReadPassphrase": "",  # string | passphrase for SRT read connections
        "fallback": "",  # string | path or URL to fallback stream if unavailable
        "useAbsoluteTimestamp": False,  # bool | use original timestamps from publisher

        # ───── Recording ─────
        "record": False,  # bool | enable recording for this path
        "recordPath": "./recordings/%path/%Y-%m-%d_%H-%M-%S-%f",  # string | output path (supports time/path vars)
        "recordFormat": "fmp4",  # enum | "fmp4", "mpegts"
        "recordPartDuration": "1s",  # duration | segment part length (e.g. "1s", "5s")
        "recordSegmentDuration": "1h0m0s",  # duration | how long each file lasts before new segment
        "recordDeleteAfter": "1d",  # duration | auto-delete recordings after this time
        "overridePublisher": True,  # bool | allow new publisher to override an active one
        "recordMaxPartSize": 0,  # int | optional, max bytes per part (0 = unlimited)

        # ───── Network / Transport ─────
        "srtPublishPassphrase": "",  # string | passphrase for SRT publishing
        "rtspTransport": "automatic",  # enum | "automatic", "udp", "multicast", "tcp"
        "rtspAnyPort": False,  # bool | use random UDP ports instead of fixed ones
        "rtspRangeType": "",  # string | optional RTSP range type ("clock" or "npt")
        "rtspRangeStart": "",  # string | optional start time (e.g. "now")
        "rtspUDPReadBufferSize": 0,  # int | bytes | 0 = default system buffer
        "mpegtsUDPReadBufferSize": 0,  # int | bytes | 0 = default system buffer
        "rtpSDP": "",  # string | SDP description override
        "rtpUDPReadBufferSize": 0,  # int | bytes | 0 = default system buffer
        "sourceRedirect": "",  # string | optional redirection URL

        # ───── Raspberry Pi Camera Settings ─────
        "rpiCameraCamID": 0,  # int | 0 = default camera
        "rpiCameraSecondary": False,  # bool | secondary stream (MJPEG)
        "rpiCameraWidth": 1920,  # int | output width in pixels
        "rpiCameraHeight": 1080,  # int | output height in pixels
        "rpiCameraHFlip": False,  # bool | horizontal flip
        "rpiCameraVFlip": False,  # bool | vertical flip
        "rpiCameraBrightness": 0,  # int | 0–100
        "rpiCameraContrast": 1,  # int | 0–100
        "rpiCameraSaturation": 1,  # int | 0–100
        "rpiCameraSharpness": 1,  # int | 0–100
        "rpiCameraExposure": "normal",  # enum | "normal", "short", "long", "custom"
        "rpiCameraAWB": "auto",  # enum | "auto", "incandescent", "tungsten", "fluorescent", "indoor", "daylight", "cloudy", "custom"
        "rpiCameraAWBGains": [0.0, 0.0],  # list | e.g. [1.2, 1.5] for manual white balance
        "rpiCameraDenoise": "off",  # enum | "off", "cdn_off", "cdn_fast", "cdn_hq"
        "rpiCameraShutter": 0,  # int | microseconds | 0 = auto
        "rpiCameraMetering": "centre",  # enum | "centre", "spot", "matrix", "custom"
        "rpiCameraGain": 0.0,  # float | 0 = auto
        "rpiCameraEV": 0,  # int | range [-10, 10]
        "rpiCameraROI": "",  # string | "x,y,width,height" (normalized 0–1)
        "rpiCameraHDR": False,  # bool | enable HDR
        "rpiCameraTuningFile": "",  # string | path to custom tuning file
        "rpiCameraMode": "",  # string | advanced mode override
        "rpiCameraFPS": 30,  # int | frames per second
        "rpiCameraAfMode": "continuous",  # enum | "auto", "manual", "continuous"
        "rpiCameraAfRange": "normal",  # enum | "normal", "macro", "full"
        "rpiCameraAfSpeed": "normal",  # enum | "normal", "fast"
        "rpiCameraLensPosition": 0.0,  # float | 0–10 (approx), only used in manual AF
        "rpiCameraAfWindow": "",  # string | ROI for AF (x,y,width,height)
        "rpiCameraFlickerPeriod": 0,  # int | Hz | 0 = auto
        "rpiCameraTextOverlayEnable": False,  # bool | overlay text onto image
        "rpiCameraTextOverlay": "%Y-%m-%d %H:%M:%S - MediaMTX",  # string | text format (strftime-compatible)
        "rpiCameraCodec": "auto",  # enum | "auto", "hardwareH264", "softwareH264", "mjpeg"
        "rpiCameraIDRPeriod": 60,  # int | frames between keyframes
        "rpiCameraBitrate": 5000000,  # int | bits per second
        "rpiCameraHardwareH264Profile": "main",  # enum | "baseline", "main", "high"
        "rpiCameraHardwareH264Level": "4.1",  # string | e.g. "4.0", "4.1"
        "rpiCameraSoftwareH264Profile": "",  # string | optional override
        "rpiCameraSoftwareH264Level": "",  # string | optional override
        "rpiCameraMJPEGQuality": 60,  # int | 0–100

        # ───── Hooks / Scripts ─────
        "runOnInit": "",  # string | command to run on startup
        "runOnInitRestart": False,  # bool | restart if command exits
        "runOnDemand": "",  # string | command to start when first client connects
        "runOnDemandRestart": False,  # bool | restart if script exits
        "runOnDemandStartTimeout": "10s",  # duration | wait for on-demand source readiness
        "runOnDemandCloseAfter": "10s",  # duration | time to stop on-demand source after last reader disconnects
        "runOnUnDemand": "",  # string | command to run after last reader disconnects
        "runOnReady": "",  # string | run when path is ready to serve
        "runOnReadyRestart": False,  # bool | restart if command exits
        "runOnNotReady": "",  # string | run when path becomes unavailable
        "runOnRead": "",  # string | run when a reader connects
        "runOnReadRestart": False,  # bool | restart script on reconnect
        "runOnUnread": "",  # string | run when reader disconnects
        "runOnRecordSegmentCreate": "",  # string | run when a new recording segment starts
        "runOnRecordSegmentComplete": ""  # string | run when a recording segment completes
    }
    # ─────────────────────────────
    # Initialization
    # ─────────────────────────────
    def __init__(self, name: str, source: str, **kwargs):
        self._name = name
        self._source = source

        # ───────── Initialize Resolutions ─────────
        res = Resolutions()

        # Determine target width & height from kwargs
        resolution_value = kwargs.pop("resolution", None)
        
        if isinstance(resolution_value, list) and len(resolution_value) == 2:
            # User passed an actual resolution list, e.g., Resolutions.svga
            width, height = resolution_value
        else:
            # fallback to wxga
            width, height = getattr(res, "wxga")

        # fallback to explicit width/height kwargs if provided
        width = kwargs.get("rpiCameraWidth", width)
        height = kwargs.get("rpiCameraHeight", height)

        # ───────── Max ranges ─────────
        max_width = max(r[0] for r in res._all)
        max_height = max(r[1] for r in res._all)

        self._max_ranges = {
            "maxReaders": kwargs.get("maxReadersMax", 1000),
            "rpiCameraWidth": kwargs.get("rpiCameraWidthMax", max_width),
            "rpiCameraHeight": kwargs.get("rpiCameraHeightMax", max_height),
        }

        # Override width/height in kwargs for initialization
        kwargs.setdefault("rpiCameraWidth", width)
        kwargs.setdefault("rpiCameraHeight", height)

        # ───────── Initialize defaults with validation ─────────
        for key, default_value in self.DEFAULTS.items():
            value = kwargs.get(key, default_value)
            valid, msg, converted_value = self._validate_and_convert(key, value)
            setattr(self, f"_{key}", converted_value)


    # ─────────────────────────────
    # Core Properties
    # ─────────────────────────────
    @property
    def name(self) -> str:
        return self._name

    @property
    def source(self) -> str:
        return self._source

    # ─────────────────────────────
    # Dynamic properties for all default fields
    # ─────────────────────────────
    def __getattr__(self, item):
        if item in self.DEFAULTS:
            return getattr(self, f"_{item}")
        raise AttributeError(f"{item} is not a valid configuration key.")

    def __setattr__(self, key, value):
        if key.startswith("_") or key in ("_name", "_source"):
            super().__setattr__(key, value)
        elif key in self.DEFAULTS:
            valid, msg, converted_value = self._validate_and_convert(key, value)
            if valid:
                super().__setattr__(f"_{key}", converted_value)
            else:
                raise ValueError(f"Invalid value for {key}: {value} ({msg})")
        else:
            raise AttributeError(f"{key} is not a valid configuration key.")

    # ─────────────────────────────
    # Serialization
    # ─────────────────────────────
    def to_dict(self, for_api: bool = False) -> Dict[str, Any]:
        data = {"source": self._source}
        for key in self.DEFAULTS:
            data[key] = getattr(self, f"_{key}")
        if not for_api:
            data["name"] = self._name
        return data

    def to_json(self, indent: int = 2, for_api: bool = False) -> str:
        return json.dumps(self.to_dict(for_api=for_api), indent=indent)

    # ─────────────────────────────
    # Deserialization
    # ─────────────────────────────
    def load_from_dict(self, data: Dict[str, Any]) -> None:
        for key, value in data.items():
            if key == "name":
                self._name = value
            elif key == "source":
                self._source = value
            elif key in self.DEFAULTS:
                valid, msg, converted_value = self._validate_and_convert(key, value)
                if valid:
                    setattr(self, f"_{key}", converted_value)
                else:
                    print(f"Warning: Invalid value for {key}: {value} ({msg})")
            else:
                print(f"Warning: Unknown key '{key}' skipped.")

    def load_from_json(self, json_str: str) -> None:
        data = json.loads(json_str)
        self.load_from_dict(data)

    # ─────────────────────────────
    # Utility
    # ─────────────────────────────
    def __repr__(self) -> str:
        return f"<MediaMTXPathConfigV4 name={self._name!r} source={self._source!r}>"

    def change_param(self, key: str, value: Any) -> bool:
        if key not in self.DEFAULTS:
            raise AttributeError(f"{key} is not a valid configuration key.")
        valid, msg, converted_value = self._validate_and_convert(key, value)
        print(msg)
        if valid:
            setattr(self, f"_{key}", converted_value)
            return True
        print(f"MediaMTXPathConfigV4: Change rejected: {msg}")
        return False

    # ─────────────────────────────
    # Validation & Conversion
    # ─────────────────────────────
    def _validate_and_convert(self, key: str, value: Any) -> tuple[bool, str, Any]:
        """
        Convert a configuration value to the appropriate type and clamp it to allowed ranges.
        - Uses self._max_ranges for max/min of certain keys if defined.
        - Returns: (valid: bool, message: str, converted_value)
        """

        # Use self._max_ranges if it exists; fallback to defaults
        max_ranges = getattr(self, "_max_ranges", {
            "maxReaders": (0, 1000),
            "rpiCameraWidth": (16, 4096),
            "rpiCameraHeight": (16, 2160),
        })

        # ───────── Integer Keys ─────────
        int_keys = {
            "maxReaders", "rpiCameraWidth", "rpiCameraHeight", "rpiCameraBrightness",
            "rpiCameraContrast", "rpiCameraSaturation", "rpiCameraSharpness",
            "rpiCameraFPS", "rpiCameraIDRPeriod", "rpiCameraBitrate", "rpiCameraMJPEGQuality",
            "rpiCameraShutter", "rpiCameraFlickerPeriod", "rtspUDPReadBufferSize",
            "mpegtsUDPReadBufferSize", "rtpUDPReadBufferSize",
        }
        if key in int_keys:
            try:
                value_int = int(value)
            except (ValueError, TypeError):
                value_int = 0
                return False, f"{key}={value} invalid, defaulting to 0", value_int
            # Clamp if key has defined max/min
            if key in max_ranges:
                min_val, max_val = max_ranges[key]
                if value_int < min_val:
                    return False, f"{key}={value_int} below min, clamped to {min_val}", min_val
                if value_int > max_val:
                    return False, f"{key}={value_int} above max, clamped to {max_val}", max_val
            return True, f"{key}={value_int} valid", value_int

        # ───────── Float Keys ─────────
        float_keys = {"rpiCameraLensPosition", "rpiCameraGain", "rpiCameraEV"}
        if key in float_keys:
            try:
                value_float = float(value)
            except (ValueError, TypeError):
                value_float = 0.0
                return False, f"{key}={value} invalid, defaulting to 0.0", value_float
            if key in max_ranges:
                min_val, max_val = max_ranges[key]
                if value_float < min_val:
                    return False, f"{key}={value_float} below min, clamped to {min_val}", min_val
                if value_float > max_val:
                    return False, f"{key}={value_float} above max, clamped to {max_val}", max_val
            return True, f"{key}={value_float} valid", value_float

        # ───────── Boolean Keys ─────────
        bool_keys = [k for k, v in self.DEFAULTS.items() if isinstance(v, bool)]
        if key in bool_keys:
            if isinstance(value, bool):
                return True, f"{key}={value} valid", value
            # Try string conversion
            v_lower = str(value).lower()
            if v_lower in {"true", "false"}:
                return True, f"{key}={v_lower} valid", v_lower == "true"
            return False, f"{key}={value} invalid, defaulting to False", False

        # ───────── Default: return as-is ─────────
        return True, f"{key}={value} accepted", value

# ─────────────────────────────────────────────────────────────────────────────
# MediaMTX API helper
# ─────────────────────────────────────────────────────────────────────────────
class MediaMTXAPIInterfaceV4:
    """
    Wrapper for MediaMTX Control-API (v4) using a Safe_Link for host/protocol/port.
    All methods now return a tuple (HTTPStatusCodes, Optional[data]).
    """

    class Endpoints(Enum):
        LIST_PATHS = "/v3/config/paths/list"
        ADD_PATH = "/v3/config/paths/add/{uid}"
        PATCH_PATH = "/v3/config/paths/patch/{uid}"
        DELETE_PATH = "/v3/config/paths/delete/{uid}"
        GET_PATH = "/v3/paths/get/{uid}"

    def __init__(
        self,
        *,
        path_uid: str,
        link: "Link",
        jwt_token: Optional[str] = None,
        verify_ssl: bool = False
    ) -> None:

        if not path_uid:
            raise ValueError("The 'path_uid' parameter is required and cannot be empty.")
        if not link:
            raise ValueError("A Safe_Link object must be provided.")

        self._path_uid = path_uid
        self._link = link
        self._jwt = jwt_token
        self._base_url = self._link.Hyperlink.rstrip("/")

        self._session = requests.Session()
        self._session.verify = verify_ssl

        # Retry strategy
        retries = Retry(total=3, backoff_factor=3, status_forcelist=[502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

        try:
            self.alive = self.is_alive()
        except Exception:
            self.alive = False

    # ------------------------
    # Internal helpers
    # ------------------------
    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self._jwt:
            headers["Authorization"] = f"Bearer {self._jwt}"
        return headers

    def _params(self) -> dict[str, str]:
        return {"jwt": self._jwt} if self._jwt else {}

    def _request(
        self,
        method: str,
        endpoint: str,
        *,
        json: Optional[dict] = None,
        return_full: bool = False
    ) -> tuple[HTTPStatusCodes, Optional[Any]]:
        """
        Make an HTTP request to the MediaMTX API.

        Returns:
            tuple(HttpCode, response_data_or_None)
        """
        url = f"{self._base_url}/{endpoint.lstrip('/')}"
        try:
            response = self._session.request(
                method,
                url,
                headers=self._headers(),
                params=self._params(),
                json=json,
                timeout=10
            )

            # Map numeric status code to HttpCode enum safely
            status_code = next(
                (code for code in HTTPStatusCodes if code.code == response.status_code),
                HTTPStatusCodes.INTERNAL_SERVER_ERROR
            )

            if return_full:
                return status_code, response

            return status_code, None

        except requests.RequestException:
            return HTTPStatusCodes.NETWORK_CONNECT_TIMEOUT_ERROR, None
        except Exception:
            return HTTPStatusCodes.INTERNAL_SERVER_ERROR, None


    # ------------------------
    # Path operations
    # ------------------------
    def create_path(self, config: "MediaMTXPathConfigV4") -> tuple[HTTPStatusCodes, None]:
        """
        /v3/config/paths/add/{name}:
        post:
            summary: adds a path configuration.
            description: all fields are optional.
            parameters:
            - name: name
                in: path
                required: true
            requestBody:
            required: true
            content:
                application/json:
                schema:
                    $ref: '#/components/schemas/PathConf'        
        """
        
        """Create a MediaMTX path."""
        payload = config.to_dict(for_api=True)
        status, _ = self._request(
            "POST", self.Endpoints.ADD_PATH.value.format(uid=self._path_uid), json=payload
        )
        return status, None

    def patch_path(self, changes: dict[str, Any]) -> tuple[HTTPStatusCodes, None]:
        """Patch a MediaMTX path."""
        endpoint = self.Endpoints.PATCH_PATH.value.format(uid=self._path_uid)
        status, _ = self._request("PATCH", endpoint, json=changes)
        return status, None

    def delete_path(self) -> tuple[HTTPStatusCodes, None]:
        """Delete a MediaMTX path."""
        endpoint = self.Endpoints.DELETE_PATH.value.format(uid=self._path_uid)
        status, _ = self._request("DELETE", endpoint)
        return status, None

    def get_path_config(self) -> tuple[HTTPStatusCodes, Optional[dict]]:
        """Retrieve current configuration of the path."""
        endpoint = self.Endpoints.GET_PATH.value.format(uid=self._path_uid)
        status, response = self._request("GET", endpoint, return_full=True)
        if status != HTTPStatusCodes.OK or response is None:
            return status, None
        try:
            return status, response.json()
        except Exception:
            return HTTPStatusCodes.INTERNAL_SERVER_ERROR, None

    def is_alive(self) -> bool:
        """Check if MediaMTX is reachable and responding."""
        status, _ = self._request("GET", self.Endpoints.LIST_PATHS.value)
        return 200 <= status.code < 300



# TakatVideo API helper (v3)
# ─────────────────────────────────────────────────────────────────────────────

class TakatVideo_API_Interface_v3:
    """
    Wrapper for the TakatVideo API using a Safe_Link for host/protocol/port.

    • Operates on a fixed uid provided at init
    • Supports optional JWT token
    • Provides Start/Stop/Disconnect injection operations
    """
    def __init__(
        self,
        *,
        uid: str,
        link: Link,  # Safe_Link object for host/protocol/port
        jwt_token: Optional[str] = None,
        verify_ssl: bool = False,
    ) -> None:

        if not uid:
            raise ValueError("The 'uid' parameter is required and cannot be empty. - Takat API")
        if not link:
            raise ValueError("A Safe_Link object must be provided.")

        self._uid = uid
        self._link = link
        self._jwt = jwt_token

        # Use the Safe_Link's hyperlink as base
        self._base_url = self._link.Hyperlink.rstrip("/")

        self._sess = requests.Session()
        self._sess.verify = verify_ssl

        # Set retries
        retries = Retry(total=3, backoff_factor=3, status_forcelist=[502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries)
        self._sess.mount("http://", adapter)
        self._sess.mount("https://", adapter)

        try:
            self.alive = self.is_alive()
        except Exception:
            self.alive = False

    # ------------------------
    # Internal helpers
    # ------------------------
    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self._jwt:
            headers["Authorization"] = f"Bearer {self._jwt}"
        return headers

    def _qs(self, otp: Optional[str] = None) -> Dict[str, str]:
        qs = {"uid": self._uid}
        if otp:
            qs["otp"] = otp
        if self._jwt:
            qs["jwt"] = self._jwt
        return qs

    def _call(
        self,
        endpoint: UnifiedInputs.TakatVideo_Endpoints,
        *,
        otp: Optional[str] = None,
        return_full: bool = False,
    ) -> Any:
        url = f"{self._base_url}/{endpoint.value}"
        try:
            response = self._sess.get(
                url,
                headers=self._headers(),
                params=self._qs(otp),
                timeout=10, #TODO make this variable
            )
            return response if return_full else response.status_code
        except requests.RequestException:
            return None if return_full else 0

    # ------------------------
    # API operation methods
    # ------------------------
    def start_injection(self, otp: str) -> int:
        """Start injection for this uid using the given OTP."""
        return self._call(UnifiedInputs.TakatVideo_Endpoints.START_INJECTION, otp=otp)

    def start_injection_url(self, otp: Optional[str] = None) -> str:
        """Return the URL for starting injection, including uid and otp."""
        return self.build_url(UnifiedInputs.TakatVideo_Endpoints.START_INJECTION, otp=otp)

    def stop_injection(self, otp: str) -> int:
        """Stop injection for this uid using the given OTP."""
        return self._call(UnifiedInputs.TakatVideo_Endpoints.STOP_INJECTION, otp=otp)

    def stop_injection_url(self, otp: Optional[str] = None) -> str:
        """Return the URL for stopping injection, including uid and otp."""
        return self.build_url(UnifiedInputs.TakatVideo_Endpoints.STOP_INJECTION, otp=otp)

    def disconnect(self, otp: str) -> int:
        """Disconnect this uid using the given OTP."""
        return self._call(UnifiedInputs.TakatVideo_Endpoints.DISCONNECT, otp=otp)

    def disconnect_url(self, otp: Optional[str] = None) -> str:
        """Return the URL for disconnecting, including uid and otp."""
        return self.build_url(UnifiedInputs.TakatVideo_Endpoints.DISCONNECT, otp=otp)

    def add_camera(self, otp: str) -> int:
        """Add a camera for this uid using the given OTP."""
        return self._call(UnifiedInputs.TakatVideo_Endpoints.ADD_CAMERA, otp=otp)

    def add_camera_url(self, otp: Optional[str] = None) -> str:
        """Return the URL for adding a camera, including uid and otp."""
        return self.build_url(UnifiedInputs.TakatVideo_Endpoints.ADD_CAMERA, otp=otp)

    def remove_camera(self, otp: str) -> int:
        """Remove a camera for this uid using the given OTP."""
        return self._call(UnifiedInputs.TakatVideo_Endpoints.REMOVE_CAMERA, otp=otp)

    def remove_camera_url(self, otp: Optional[str] = None) -> str:
        """Return the URL for removing a camera, including uid and otp."""
        return self.build_url(UnifiedInputs.TakatVideo_Endpoints.REMOVE_CAMERA, otp=otp)

    def register(self, otp: str) -> int:
        """Register this uid using the given OTP."""
        return self._call(UnifiedInputs.TakatVideo_Endpoints.REGISTER, otp=otp)

    def register_url(self, otp: Optional[str] = None) -> str:
        """Return the URL for registering, including uid and otp."""
        return self.build_url(UnifiedInputs.TakatVideo_Endpoints.REGISTER, otp=otp)

    def unregister(self, otp: str) -> int:
        """Unregister this uid using the given OTP."""
        return self._call(UnifiedInputs.TakatVideo_Endpoints.UNREGISTER, otp=otp)

    def unregister_url(self, otp: Optional[str] = None) -> str:
        """Return the URL for unregistering, including uid and otp."""
        return self.build_url(UnifiedInputs.TakatVideo_Endpoints.UNREGISTER, otp=otp)

    # ------------------------
    # State / Info
    # ------------------------
    def is_alive(self) -> bool:
        """Simple health check: try disconnect without OTP."""
        status = self._call(UnifiedInputs.TakatVideo_Endpoints.DISCONNECT)
        return bool(status and 200 <= status < 300)
    
    def build_url(
        self,
        endpoint: UnifiedInputs.TakatVideo_Endpoints,
        *,
        otp: Optional[str] = None,
    ) -> str:
        """
        Return the full request URL for the given endpoint.
        Always includes uid, and otp/jwt if provided.
        """
        if not isinstance(endpoint, UnifiedInputs.TakatVideo_Endpoints):
            raise ValueError(f"Invalid endpoint: {endpoint}")

        url = f"{self._base_url}/{endpoint.value}"
        qs = urlencode(self._qs(otp))
        return f"{url}?{qs}"
    

    def to_dict(self) -> Dict[str, Any]:
        return {
            "base_url": self._base_url,
            "jwt_provided": bool(self._jwt),
            "verify_ssl": self._sess.verify,
            "alive": self.alive,
            "uid": self._uid,
        }
  
# ─────────────────────────────────────────────────────────────────────────────
# FFmpeg Command Builder v4
# ─────────────────────────────────────────────────────────────────────────────

class FFMPEG_Command_Builder_v4:
    """
    FFmpeg command builder for different ingest types, with proper quoting for metadata and URLs.
    """

    def __init__(
        self,
        *,
        camera_uid: str,
        linked_uid: str,
        mediamtx_streaming_port: int = 8554,
        link: "Link",  # Safe_Link or equivalent
    ):
        self._camera_uid = camera_uid
        self._linked_device = linked_uid
        self._link = link
        self._streaming_port = mediamtx_streaming_port

        # Metadata with proper quoting
        self._metadata = f'-metadata uid="{self._camera_uid}" -metadata linked_device="{self._linked_device}"'

    def run_on_init(
        self,
        ingest_type: "UnifiedInputs.FFMPEG_IngestType",
        output_protocol: "UnifiedInputs.FFMPEG_Protocol",
        timeout: int = 5000000,
        loop: bool = True
    ) -> str:
        match ingest_type:
            case UnifiedInputs.FFMPEG_IngestType.CAMERA:
                return self._ffmpeg_esp32cam(timeout=timeout, encoding=output_protocol)
            case UnifiedInputs.FFMPEG_IngestType.NETWORKED_MP4:
                return self._ingest_networked_mp4(loop=loop, encoding=output_protocol)
            case UnifiedInputs.FFMPEG_IngestType.LOCAL_MP4:
                return self._ingest_local_mp4(loop=loop, encoding=output_protocol)
            case _:
                return ""

    def _ffmpeg_esp32cam(self, timeout: int = 5000000, encoding: "UnifiedInputs.FFMPEG_Protocol" = UnifiedInputs.FFMPEG_Protocol.DEFAULT) -> str:
        """Build FFmpeg command for live RTSP camera feed."""
        port_suffix = f":{self._streaming_port}" if self._streaming_port else ""
        input_url = self._link.Hyperlink  # no extra quotes
        output_url = f"{encoding.value}://127.0.0.1{port_suffix}/{self._camera_uid}/stream"

        # Wrap URLs in quotes for shell safety
        cmd = f'ffmpeg -timeout {timeout} -i "{input_url}" -c copy {self._metadata} -f {encoding.value} "{output_url}"'
        return cmd

    def _ingest_local_mp4(
        self,
        loop: bool = True,
        encoding: "UnifiedInputs.FFMPEG_Protocol" = UnifiedInputs.FFMPEG_Protocol.DEFAULT
    ) -> str:
        """Build FFmpeg command for local MP4 files."""
        loop_flag = "-1" if loop else "0"
        port_suffix = f":{self._streaming_port}" if self._streaming_port else ""
        input_url = self._link.Payload  # local file path
        output_url = f"{encoding.value}://127.0.0.1{port_suffix}/{self._camera_uid}/stream"

        cmd = f'ffmpeg -re -stream_loop {loop_flag} -i "{input_url}" -c copy {self._metadata} -f {encoding.value} "{output_url}"'
        return cmd

    def _ingest_networked_mp4(
        self,
        loop: bool = True,
        encoding: "UnifiedInputs.FFMPEG_Protocol" = UnifiedInputs.FFMPEG_Protocol.DEFAULT
    ) -> str:
        """Build FFmpeg command for networked MP4 (HTTP/HTTPS)."""
        loop_flag = "-1" if loop else "0"
        port_suffix = f":{self._streaming_port}" if self._streaming_port else ""
        input_url = self._link.Hyperlink  # HTTP/HTTPS URL
        output_url = f"{encoding.value}://127.0.0.1{port_suffix}/{self._camera_uid}/stream"

        cmd = f'ffmpeg -re -stream_loop {loop_flag} -i "{input_url}" -c copy {self._metadata} -f {encoding.value} "{output_url}"'
        return cmd

# ─────────────────────────────────────────────────────────────────────────────
# Single Camera object
# ───────────────────────────────────────────────────────────────────────────── 
class CameraObjectV4():
    """ Represents a single camera instance managed through MediaMTX, composed of a 
            source path (the ingest stream) and a virtual path (the public stream).

            This class encapsulates configuration management, path creation, syncing,
            and patching of both source and virtual MediaMTX paths. It serves as the 
            logical bridge between local configuration objects and the MediaMTX server API.

            Main Responsibilities:
            -----------------------
            • Create, patch, and destroy MediaMTX source and virtual paths.
            • Maintain local (internal) MediaMTXPathConfigV4 configurations that can 
            be synchronized with the server in both directions.
            • Generate and manage FFmpeg run commands used during path initialization.
            • Provide utilities for updating individual path parameters dynamically.
            • Optionally perform automatic path creation and reverse synchronization 
            during initialization.

            Attributes:
            -----------
            _source_uid : str
                Unique identifier for the source path.
            _virtual_uid : str
                Unique identifier for the virtual path.
            _source_config : MediaMTXPathConfigV4
                Local configuration object representing the source path state.
            _virtual_config : MediaMTXPathConfigV4
                Local configuration object representing the virtual path state.
            _source_path_url : Optional[str]
                Complete URL to the MediaMTX source stream endpoint.
            _virtual_path_url : Optional[str]
                Complete URL to the MediaMTX virtual stream endpoint.
            _api_source : MediaMTXAPIInterfaceV4
                API interface instance used for manipulating the source path.
            _api_virtual : MediaMTXAPIInterfaceV4
                API interface instance used for manipulating the virtual path.
            _ffmpeg : FFMPEG_Command_Builder_v3
                Helper object responsible for generating FFmpeg run-on-init commands.
            _status_code : HTTPStatusCodes
                Latest operation status code (e.g., from path creation or sync).
            _status_message : str
                Descriptive message of the latest operation result.
            _camera_type : UnifiedInputs.CameraObjectV4_CameraType
                Type of camera instance (source or virtual).
            _timeout : int
                Timeout (in microseconds) used in path configuration.
            _loop : bool
                Whether FFmpeg streams should loop on completion.

            Methods:
            --------
            _initialize_paths() -> None
                Creates source and virtual paths on the MediaMTX server, performs a 
                reverse sync to push local configs, and updates internal URLs.
            sync(to_server: bool = False) -> Tuple[HTTPStatusCodes, HTTPStatusCodes]
                Synchronizes configuration either from the MediaMTX server (pull) 
                or to the server (push), updating both local and remote states.
            update_source_parameter(key: str, value: Any) -> Tuple[HTTPStatusCodes, str]
                Patches a single parameter on the source path; updates internal config 
                on success and returns status/message.
            update_virtual_parameter(key: str, value: Any) -> Tuple[HTTPStatusCodes, str]
                Patches a single parameter on the virtual path; updates internal config 
                on success and returns status/message.
            self_destruct(otp: Optional[str] = None) -> None
                Removes source and virtual paths from the MediaMTX server and clears
                all internal references. Optionally performs OTP-based validation
                for secure teardown.
            its_me(uid: str) -> bool
                Returns True if the provided UID matches either the source or virtual path.
            to_dict() -> dict
                Serializes the camera object and its configs into a dictionary for persistence.

            Typical Usage:
            --------------
                 cam = CameraObjectV4(
                     config=MediaMTXPathConfigV4(name="camera1", source="rtsp://..."),
                     source_uid="src_cam_01",
                     virtual_uid="virt_cam_01",
                     api_mediamtx_link=Link(...),
                     stream_source_link=Link(...),
                     stream_mediamtx_link=Link(...),
                     create_paths=True
                 )
                 cam.update_virtual_parameter("timeout", 8000000)
                 cam.sync(to_server=True)
                 cam.self_destruct()

            Notes:
            ------
            - The class assumes MediaMTX is reachable via the provided link interfaces.
            - The FFmpeg run-on-init command is automatically generated for the source path.
            - Both paths are always created and patched sequentially for reliability.
            """
                    
    def __init__(
            self,
            *,
            config: MediaMTXPathConfigV4,
            source_uid: str,
            virtual_uid: str,
            otp:str,
            api_mediamtx_link: Link,
            stream_source_link: Link,
            stream_mediamtx_link: Link,
            input_type: UnifiedInputs.FFMPEG_IngestType = UnifiedInputs.FFMPEG_IngestType.Default,
            output_protocol: UnifiedInputs.FFMPEG_Protocol = UnifiedInputs.FFMPEG_Protocol.DEFAULT,
            timeout: int = 5_000_000,
            loop: bool = True,
            create_paths: bool = True,
            camera_type: Optional[UnifiedInputs.CameraObjectV4_CameraType] = UnifiedInputs.CameraObjectV4_CameraType.Source,
        ) -> None:

        # Core IDs
        self._source_uid = source_uid
        self._virtual_uid = virtual_uid
        
        self._source_path_url: Optional[str] = None
        self._source_config = copy.deepcopy(config)
        
        self._virtual_path_url: Optional[str] = None
        self._virtual_config = copy.deepcopy(config)
        
        self._api_takat = TakatVideo_API_Interface_v3(  uid=self._source_uid,
                                                        link=api_mediamtx_link,
                                                        verify_ssl=False,
                                                        jwt_token=None
                                                    )
        self._camera_type = camera_type or UnifiedInputs.CameraObjectV4_CameraType.Source
        self._otp = otp
        

        # Streaming & FFmpeg
        self._stream_source_link = stream_source_link
        self._stream_mediamtx_link = stream_mediamtx_link
        self._input_type = input_type
        self._output_protocol = output_protocol
        self._timeout = timeout
        self._loop = loop

        # Status
        self._status_code = HTTPStatusCodes.CONFLICT
        self._status_message = f"Camera {self._source_uid} not initialized"

        # Build FFmpeg helper
        port = self._stream_mediamtx_link.Port or 8554
        self._ffmpeg = FFMPEG_Command_Builder_v4(
            camera_uid=self._source_uid,
            linked_uid=self._virtual_uid,
            mediamtx_streaming_port=port,
            link=self._stream_source_link
        )
        
        # API interfaces
        self._api_source =  MediaMTXAPIInterfaceV4(path_uid=self._source_config.name, link=api_mediamtx_link)
        self._api_virtual = MediaMTXAPIInterfaceV4(path_uid=self._virtual_config.name, link=api_mediamtx_link)

        # Initialize paths only if flag is True
        if create_paths:
            # change the local configs to what we want them to become
            
            # source camera config changes
            #self._source_config.change_param("runOnInit", self._ffmpeg.run_on_init(    ingest_type=self._input_type,
            #                                                                            output_protocol=self._output_protocol,
            #                                                                            timeout=self._timeout,
            #                                                                            loop=self._loop
            #                                                                        ))
            self._source_config.change_param("sourceOnDemand", False)
            #self._source_config.change_param("name", self._source_uid)
            self._source_config.change_param("runOnNotReady", self._api_takat.disconnect_url(self._otp))  # TakatVideo disconnect command
            
            #virtual camera config changes
            #self._virtual_config.change_param("name", self._virtual_uid)
            self._virtual_config.change_param("source", f"{output_protocol.value}://127.0.0.1:{stream_mediamtx_link.Port}/{self.source_uid}/stream")
            #self._virtual_config.change_param("timeout", self._timeout)
            self._virtual_config.change_param("sourceOnDemand", False)
            

            # now make thoose paths and set them up
            self._initialize_paths()

    # ------------------------
    # Internal path initialization
    # ------------------------
    def _initialize_paths(self) -> None:
        """
        Sequentially create source and virtual paths on MediaMTX and sync configs.
        Steps:
        1. Create source path
        2. Create virtual path
        3. Push local configs to server (reverse sync)
        4. Update internal URLs
        """

        # Step 1: Add Source Path
        try:
            status_source_add = self._api_source.create_path(self._source_config)
            if not (200 <= status_source_add.code < 300):
                self._status_code = status_source_add
                self._status_message = f"CameraObjectV4: Failed to add source path ({status_source_add})"
                return
        except requests.exceptions.ConnectionError:
            self._status_code = HTTPStatusCodes.NETWORK_CONNECT_TIMEOUT_ERROR
            self._status_message = "CameraObjectV4: Connection error when adding source path"
            return
        except Exception:
            self._status_code = HTTPStatusCodes.INTERNAL_SERVER_ERROR
            self._status_message = "CameraObjectV4: Unexpected error when adding source path"
            return

        # Step 2: Add Virtual Path
        try:
            status_virtual_add = self._api_virtual.create_path(self._virtual_config)
            if not (200 <= status_virtual_add.code < 300):
                self._status_code = status_virtual_add
                self._status_message = f"CameraObjectV4: Failed to add virtual path ({status_virtual_add})"
                return
        except requests.exceptions.ConnectionError:
            self._status_code = HTTPStatusCodes.NETWORK_CONNECT_TIMEOUT_ERROR
            self._status_message = "CameraObjectV4: Connection error when adding virtual path"
            return
        except Exception:
            self._status_code = HTTPStatusCodes.INTERNAL_SERVER_ERROR
            self._status_message = "CameraObjectV4: Unexpected error when adding virtual path"
            return
        # ------------------------
        # Step 3: Reverse Sync (push local config to server)
        # ------------------------
        try:          
                
            src_status, virt_status = self.sync(to_server=True)  # push local configs
            if src_status != HTTPStatusCodes.OK or virt_status != HTTPStatusCodes.OK:
                self._status_code = HTTPStatusCodes.FAILED_DEPENDENCY
                self._status_message = f"CameraObjectV4: Failed reverse sync (source: {src_status}, virtual: {virt_status})"
                return
        except requests.exceptions.ConnectionError:
            self._status_code = HTTPStatusCodes.NETWORK_CONNECT_TIMEOUT_ERROR
            self._status_message = "CameraObjectV4: Connection error during reverse sync"
            return
        except Exception:
            self._status_code = HTTPStatusCodes.INTERNAL_SERVER_ERROR
            self._status_message = "CameraObjectV4: Unexpected error during reverse sync"
            return

        # ------------------------
        # Step 4: Update URLs
        # ------------------------
        try:
            self._source_path_url = f"{self._stream_mediamtx_link.Root()}{self._source_uid}/stream"
            self._virtual_path_url = f"{self._stream_mediamtx_link.Root()}{self._virtual_uid}/stream"
        except Exception:
            self._status_code = HTTPStatusCodes.INTERNAL_SERVER_ERROR
            self._status_message = "CameraObjectV4: Failed to update source/virtual URLs"
            return

        # ------------------------
        # All steps succeeded
        # ------------------------
        self._status_code = HTTPStatusCodes.OK
        self._status_message = HTTPStatusCodes.OK.status

    # ------------------------
    # Sync method - updates the settings to and from what is on the mediamtx server
    # ------------------------
    def sync(self, to_server: bool = False) -> tuple[HTTPStatusCodes, HTTPStatusCodes]:
        """
        Sync internal config with MediaMTX server.

        If to_server=False (default), pull server state into internal config.
        If to_server=True, push internal config to server so server matches local state.

        Returns (source_status, virtual_status)
        """
        source_status, virtual_status = HTTPStatusCodes.INTERNAL_SERVER_ERROR, HTTPStatusCodes.INTERNAL_SERVER_ERROR

        # ------------------------
        # Source Path
        # ------------------------
        try:
            if to_server:
                # Push internal config to server
                patch_dict = {k: v for k, v in self._source_config.to_dict().items() if k != "name"}
                status_patch = self._api_source.patch_path(patch_dict, return_full=True)  # returns int
                source_status = HTTPStatusCodes.OK if 200 <= status_patch < 300 else HTTPStatusCodes.FAILED_DEPENDENCY
            else:
                # Pull server state into internal config
                status_get, data = self._api_source.get_path_config()
                if status_get == HTTPStatusCodes.OK and data:
                    self._source_config.load_from_dict(data)
                    self._source_path_url = f"{self._stream_mediamtx_link.Root()}{self._source_uid}/stream"
                source_status = status_get
        except requests.exceptions.ConnectionError:
            source_status = HTTPStatusCodes.NETWORK_CONNECT_TIMEOUT_ERROR
        except Exception:
            source_status = HTTPStatusCodes.INTERNAL_SERVER_ERROR

        # ------------------------
        # Virtual Path
        # ------------------------
        try:
            if to_server:
                patch_dict = {k: v for k, v in self._virtual_config.to_dict().items() if k != "name"}
                status_patch = self._api_virtual.patch_path(patch_dict, return_full=True)  # returns int
                virtual_status = HTTPStatusCodes.OK if 200 <= status_patch < 300 else HTTPStatusCodes.FAILED_DEPENDENCY
            else:
                status_get, data = self._api_virtual.get_path_config()
                if status_get == HTTPStatusCodes.OK and data:
                    self._virtual_config.load_from_dict(data)
                    self._virtual_path_url = f"{self._stream_mediamtx_link.Root()}{self._virtual_uid}/stream"
                virtual_status = status_get
        except requests.exceptions.ConnectionError:
            virtual_status = HTTPStatusCodes.NETWORK_CONNECT_TIMEOUT_ERROR
        except Exception:
            virtual_status = HTTPStatusCodes.INTERNAL_SERVER_ERROR

        return source_status, virtual_status

    # ------------------------
    # Update a single parameter for source camera
    # ------------------------
    def update_source_parameter(self, key: str, value: Any) -> Tuple[HTTPStatusCodes, str]:
        try:
            patch_dict = {key: value}
            status, _ = self._api_source.patch_path(patch_dict, return_full=True)
            if 200 <= status.code < 300:
                self._source_config.change_param(key=key, value=value)
                return HTTPStatusCodes.OK, f"CameraObjectV4: Source parameter '{key}' updated successfully."
            else:
                return HTTPStatusCodes.FAILED_DEPENDENCY, f"CameraObjectV4: Failed to update source parameter '{key}'."
        except requests.exceptions.ConnectionError:
            return HTTPStatusCodes.NETWORK_CONNECT_TIMEOUT_ERROR, f"CameraObjectV4: Connection error when updating source parameter '{key}'."
        except Exception as e:
            return HTTPStatusCodes.INTERNAL_SERVER_ERROR, f"CameraObjectV4: Unexpected error when updating source parameter '{key}': {e}"

    # ------------------------
    # Update a single parameter for virtual camera
    # ------------------------
    def update_virtual_parameter(self, key: str, value: Any) -> Tuple[HTTPStatusCodes, str]:
        try:
            patch_dict = {key: value}
            status, _ = self._api_virtual.patch_path(patch_dict, return_full=True)
            if 200 <= status.code < 300:
                self._virtual_config.change_param(key=key, value=value)
                return HTTPStatusCodes.OK, f"CameraObjectV4: Virtual parameter '{key}' updated successfully."
            else:
                return HTTPStatusCodes.FAILED_DEPENDENCY, f"CameraObjectV4: Failed to update virtual parameter '{key}'."
        except requests.exceptions.ConnectionError:
            return HTTPStatusCodes.NETWORK_CONNECT_TIMEOUT_ERROR, f"CameraObjectV4: Connection error when updating virtual parameter '{key}'."
        except Exception as e:
            return HTTPStatusCodes.INTERNAL_SERVER_ERROR, f"CameraObjectV4: Unexpected error when updating virtual parameter '{key}': {e}"



    # ------------------------
    # Self-destruct
    # ------------------------
    def self_destruct(self, otp: Optional[str] = None) -> None:
        """
        Remove MediaMTX paths and clean up internal state.
        Optionally unregister from TakatVideo API if otp is provided.
        """
        #TODO add OTP challange to see if we have the right to destroy the object.
        try:
            self._api_source.delete_path()
            self._api_virtual.delete_path()
            # TODO: unregister from TakatVideo API when available
        except Exception as e:
            print(f"CameraObjectV4: Self-destruct cleanup failed: {e}")

        # Clear internal references
        for attr in list(vars(self).keys()):
            setattr(self, attr, None)

    # ------------------------
    # Properties
    # ------------------------
    @property
    def source_uid(self) -> str:
        return self._source_uid

    @property
    def virtual_uid(self) -> str:
        return self._virtual_uid

    @property
    def source_path(self) -> Optional[str]:
        return self._source_path_url

    @property
    def virtual_path(self) -> Optional[str]:
        return self._virtual_path_url

    @property
    def camera_type(self) -> UnifiedInputs.CameraObjectV4_CameraType:
        return self._camera_type

    # ------------------------
    # Utility
    # ------------------------
    def its_me(self, uid: str) -> bool:
        return uid in (self._source_uid, self._virtual_uid)

    def to_dict(self) -> dict:
        return {
            "status_code": int(self._status_code.code),
            "status_message": self._status_code.status,
            "source_uid": self._source_uid,
            "virtual_uid": self._virtual_uid,
            "source_path": self._source_path_url,
            "virtual_path": self._virtual_path_url,
            "camera_type": int(self._camera_type),
            "source config": self._source_config.to_dict() if self._source_config else None,
            "virtual config": self._virtual_config.to_dict() if self._virtual_config else None,
            "timeout": self._timeout,
            "loop": self._loop,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Video object that glues everything together
# ─────────────────────────────────────────────────────────────────────────────
"""class Video_Object_v3:
    def __init__(self, 
                  source_camera: Link, mediamtx_server_api: Link, takat_server_api: Link, 
                  mediamtx_server_stream: Link, path_config: MediaMTX_Path_Config_v3,
                  linked_device: str, virtual_camera_uid: str, source_camera_uid: str, 
                  primary_uid: Optional[str] = None, 
                  ffmpeg_processing_type: Optional[UnifiedInputs.FFMPEG_IngestType] = UnifiedInputs.FFMPEG_IngestType.Default,
                  ffmpeg_output_type:Optional[UnifiedInputs.FFMPEG_Protocol] = UnifiedInputs.FFMPEG_Protocol.DEFAULT,
                  otp: Optional[str] = None): 
        
        self._CAMERAS: list[Camera_Object_V3] = [] #this holds all the camera objects
        
        self._primary_uid = primary_uid   #the primary uid of the video object 
        
        if self._IsUnique(linked_device) == True:
            self._link_device = linked_device   #a unique lnked device we add it later in the init
            
        else:
            raise ValueError(f"Linked Device '{linked_device}' already exists in the global list")

        
        #make sure the primary uid is setup and unique 
        if primary_uid is None or primary_uid == "":
            while True:
                candidate_uid = SessionCredentials.random_uid()  # generate a random UID
                if self._IsUnique(uid=candidate_uid):      # check if it already exists
                    primary_uid = candidate_uid                  # accept it if unique
                    self._primary_uid = candidate_uid
                    break                                       # exit the loop
                # otherwise, loop again and generate a new random UID
        else:
            # test if provided primary UID already exists
            if not self._IsUnique(primary_uid):
                raise ValueError(f"Primary UID '{primary_uid}' already exists in the global list")
            self._primary_uid = primary_uid
        
        
        if otp == None: # if otp is not set, set a random one.
            self._otp= SessionCredentials.random_otp(12)
        else: self._otp = otp
        
        self._credentials = SessionCredentials(uid=self._primary_uid, otp=self._otp) #create a credential manger for this session.
        
        self._credentials.add_linked_device(linked_device)  # (finaly) set the linked device
        
        # create a virtal camera based on the primary uid. this is the main channel the takusers look at. 
        # it should be the path of the mediamtx serverstream and the primary uid of this object.
        self._mediamtx_streaming_server = mediamtx_server_stream
        self._MYCAM_API_MediamMTX = MediaMTX_API_Interface_v3(uid=self._primary_uid,
                                                            link=mediamtx_server_api,
                                                            jwt_token=None,
                                                            verify_ssl=False)
        self._MYCAM_config = path_config
        self._MYCAM_config.source = f"{self._mediamtx_streaming_server.Root()}{self._primary_uid}" #OPTIONAL TODO, change to setup so the source points to the first virtual camera in credentials
        self._MYCAM_config.name = self._primary_uid
        
        result = self._MYCAM_API_MediamMTX.Create_Path()
        if result == 200: pass #TODO, add status update or exit here
        else: raise RuntimeError(f"Error failed creating main virtual camera")
            
        
        self._MYCAM_virtual_camera_path = f"{self._mediamtx_streaming_server.Root()}{self._primary_uid}" # the path to the main virual camera
        #We now have an object that has a primary and linked uid, an otp its own virtual camera path, now lets add its first camera object (it should have atleast one)
        try:
        #make sure we have have a camera type set.
            if ffmpeg_processing_type == None: ffmpeg_processing_type = UnifiedInputs.FFMPEG_IngestType.Default
            self._processing_type = ffmpeg_processing_type
            if ffmpeg_output_type == None: ffmpeg_output_type = UnifiedInputs.FFMPEG_Protocol.DEFAULT
            self._ffmpeg_output_type = ffmpeg_output_type
            
            #create a camera for the main user.
            self.Add_Camera(Config=self._MYCAM_config, Source_UID=source_camera_uid, Virtual_UID=virtual_camera_uid, 
                            Mediamtx_API=mediamtx_server_api, Takat_API=takat_server_api,
                            Source_Camera=source_camera, MediaMTX_Stream=mediamtx_server_stream, Source_Type=self._processing_type, 
                            OutputProtocol=self._ffmpeg_output_type)
            #update MYCAM source path to the virtual camera of the camera object
            change= {"source": f"{self._mediamtx_streaming_server.Root()}{virtual_camera_uid}",
                    "name": f"{self._primary_uid} streaming: {virtual_camera_uid}",
                    }
            self._MYCAM_API_MediamMTX.patch_path(changes=change) #patch the main virtual cam to the firts virtual camera.
            #self._MYCAM_API_MediamMTX.patch_path(changes=change.__dict__) #patch the main virtual cam to the firts virtual camera.
            self._current = virtual_camera_uid  #this is the channel we are currently watching.      
            
            # Self-register to global lists this also updates the global linked uid / virtual path
            #Add_Video_Object(self)
            
        except Exception as e:
            raise RuntimeError(f"Error while registering camera path: {e}") from e
            
        # if all went wel, we now hav a video object with its own rtsp://mediamtx.com:8554/primary_uid  path, of which the source points to
        # the camera object virtual camera that has path rtsp://mediamtx.com:8554/virtual_camera
        # whilest the source camera lives at path rtsp://mediamtx.com:8554/source_camera
        
        # in the _CAMERAS is a complete collection of all camera objects. using the "Switch_Channel" functions we can change
        # the source path of the rtsp://mediamtx.com:8554/primary_uid
            
    @property
    def PrimaryUID(self) -> str:
        return self._credentials.primary_uid
    @property
    def LinkedDevice(self) ->str:
        return self._credentials.linked_device
    @property
    def CameraPath(self) -> str:
        return self._MYCAM_virtual_camera_path   
    @property
    def Used_UIDs(self) -> list[str]:
        return self._credentials.all_uids
    @property
    def LinkedDevice_CameraPath(self) -> tuple:
        return (self._credentials.linked_device, self._MYCAM_virtual_camera_path)
    
    def WallPaper(self) -> list[str]:

        Iterate through all cameras and return a list of their VirtualCamera_Path strings.
        
        Returns:
            List of VirtualCamera_Path for all cameras in _CAMERAS.

        output_paths: list[str] = []

        # Iterate over a copy of the camera list to be safe
        for camera in self._CAMERAS[:]:
            try:
                # Get the virtual camera path
                path = camera.VirtualCamera_Path
                output_paths.append(path)
            except AttributeError:
                # Camera object may not have the expected attribute
                raise ValueError(f"Camera '{camera.VirtualCamera_UID}' does not have the right attibutes")
            except Exception as e:
                # Catch any unexpected errors and continue
                raise ValueError(f"Camera '{camera.VirtualCamera_UID}' has had an unkown error")
        return output_paths
                  
    def Switch_Source(self, up: bool = True) -> None:

        Args:
            up (bool, optional): _description_. Defaults to True.
            this makes the function to select the next one in the list,
            if set to false it selects the previous in the list.
            the function "loops" through the end/beginning of the list if it gets to the end

        Raises:
            ValueError: _description_
            ValueError: _description_

        if not self._CAMERAS:
            raise ValueError("No cameras available")

        found = False
        for idx, camera in enumerate(self._CAMERAS):
            if camera.VirtualCamera_UID == self._current:
                found = True
                
                # calculate next index based on direction
                if up:
                    next_idx = (idx + 1) % len(self._CAMERAS)
                else:
                    next_idx = (idx - 1) % len(self._CAMERAS)
                
                # get the next camera object
                next_camera = self._CAMERAS[next_idx]
                
                # update virtual camera path
                change = {
                    "source": f"{next_camera.VirtualCamera_Path}",  
                    "name": f"{self._primary_uid} streaming: {next_camera.VirtualCamera_UID}",
                }
                
                self._MYCAM_API_MediamMTX.patch_path(changes=change.__dict__)
                self._current = next_camera.VirtualCamera_UID
                break

        if not found:
            raise ValueError(f"Current UID '{self._current}' not found in camera list")
            
    def Add_Camera(self, Config, Source_UID: str, Virtual_UID: str,Mediamtx_API: Link, Takat_API: Link, Source_Camera: Link, MediaMTX_Stream: Link,
                   Source_Type: UnifiedInputs.FFMPEG_IngestType = UnifiedInputs.FFMPEG_IngestType.Default,
                   OutputProtocol: UnifiedInputs.FFMPEG_Protocol = UnifiedInputs.FFMPEG_Protocol.DEFAULT, Timeout: int | None = 5000000,
                   Loop: bool | None = False) -> None:
        
        # check if uid of source and virtual are not already in a video object in the global list
        if self._IsUnique(Source_UID) == True and self._IsUnique(Virtual_UID) == True:
            #its safe to create this object and its paths
            camera = Camera_Object_V3(Config=Config,Source_Camera_UID=Source_UID,Virtual_Camera_UID=Virtual_UID, API_mediamtx=Mediamtx_API,
                                API_takat=Takat_API, Stream_Mediamtx=MediaMTX_Stream, Stream_SourceCamera=Source_Camera, Stream_SourceCameraInputType=Source_Type,
                                Output_Protocol=OutputProtocol, Timeout=Timeout, Loop=Loop)
            
            
            # add the source uid to the credentials
            self._credentials.add_source_camera(Source_UID)
            # add the virtual uid to the credentials
            self._credentials.add_virtual_camera(Virtual_UID)
            # add the camera to the array.
            self._CAMERAS.append(camera)
            
    def Delete_Camera(self, uid: str) -> None:

        Deletes a camera from this Video_Object_v3 by UID (source or virtual).

        Steps:
        1. Find the camera matching the UID.
        2. Remove its paths / call self_destruct.
        3. Remove its UIDs from credentials.
        4. Remove the camera object from the _CAMERAS list.

        for i, camera in enumerate(self._CAMERAS):
            if camera.ItsMe(uid):  # check if this camera matches the UID
                # store UIDs for credential removal
                source_uid = camera.SourceCamera_UID
                virtual_uid = camera.VirtualCamera_UID

                # call the camera's self-destruct routine
                camera.self_destruct(self._otp)

                # remove the UIDs from the credentials
                self._credentials.remove_uid(uid=source_uid, uid_type=SessionCredentials.UIDType.SOURCE_CAMERA )
                self._credentials.remove_uid(uid=virtual_uid, uid_type=SessionCredentials.UIDType.VIRTUAL_CAMERA)

                # remove the camera object from the list
                del self._CAMERAS[i]
       
                # if no cameras remain, trigger self destruct
                if not self._CAMERAS:
                    self._Self_Destruct(self._otp)

                # exit after deleting one camera
                return

        # If we reach here, the UID was not found
        raise ValueError(f"No camera found with UID '{uid}'")
                
    def _IsUnique(self, uid) -> bool:

        Returns True if the given UID is *not yet used* in any Video_Object_v3.
        Uses the global VIDEO_OBJECTS registry to verify uniqueness.

        #TODO make functional
        return True

    def _Self_Destruct(self, otp) -> None:

        Fully destroys this Video_Object_v3:
        - Safely destroys all camera objects and their credentials.
        - Deletes the main virtual camera path.
        - Removes itself from the global registry if applicable.
        
        Can be called multiple times safely; exceptions are caught and logged.

        if otp != self._credentials.otp:
            raise ValueError("Wrong otp provided")

        # Use logging instead of print for better control
        logger = logging.getLogger(__name__)
        
        # Iterate over a copy of the camera list to safely delete items while looping
        for camera in self._CAMERAS[:]:
            # Step 1: self-destruct the camera
            try:
                camera.self_destruct(self._otp)
                logger.info(f"Camera {camera.VirtualCamera_UID} destroyed successfully.")
            except Exception as e:
                logger.warning(f"Failed to self-destruct camera {camera.VirtualCamera_UID}: {e}")

            # Step 2: remove credentials
            try:
                self._credentials.remove_uid(uid=camera.SourceCamera_UID, uid_type=SessionCredentials.UIDType.SOURCE_CAMERA)
                self._credentials.remove_uid(uid=camera.VirtualCamera_UID, uid_type=SessionCredentials.UIDType.VIRTUAL_CAMERA)
                logger.info(f"Credentials for camera {camera.VirtualCamera_UID} removed successfully.")
            except Exception as e:
                logger.warning(f"Failed to remove credentials for camera {camera.VirtualCamera_UID}: {e}")

            # Step 3: remove from _CAMERAS list
            if camera in self._CAMERAS:
                self._CAMERAS.remove(camera)

        # Step 4: delete main virtual camera path
        try:
            self._MYCAM_API_MediamMTX.delete_path()
            logger.info(f"Main virtual camera path {self._primary_uid} deleted successfully.")
        except Exception as e:
            logger.warning(f"Failed to delete main virtual camera path {self._primary_uid}: {e}")

        # Step 5: remove from global registry if exists
        try:
            #TODO
            #Remove_Video_Object(self)
            # if "GLOBAL_VIDEO_OBJECTS" in globals() and self in GLOBAL_VIDEO_OBJECTS:
            #    GLOBAL_VIDEO_OBJECTS.remove(self)
            logger.info(f"Video object {self._primary_uid} removed from global registry.")
        except Exception as e:
            logger.warning(f"Failed to remove video object {self._primary_uid} from global registry: {e}")

        logger.info(f"Video object {self._primary_uid} fully self-destructed.")
  

    def to_dict(self) -> dict:
        return {
            "primary_uid": self._primary_uid,
            "otp_manager": self._credentials.to_dict(),  # <— simplified
            "linked_device": self._link_device,
            "mediamtx_streaming_server": self._mediamtx_streaming_server.to_dict(),
            "MYCAM_config": self._MYCAM_config.to_dict(),
            "MYCAM_virtual_camera_path": self._MYCAM_virtual_camera_path,
            "cameras": [cam.to_dict() for cam in self._CAMERAS],
            "current_channel": self._current,
            "processing_type": self._processing_type.name if hasattr(self, "_processing_type") else None,
            "ffmpeg_output_type": self._ffmpeg_output_type.name if hasattr(self, "_ffmpeg_output_type") else None,
        }

"""