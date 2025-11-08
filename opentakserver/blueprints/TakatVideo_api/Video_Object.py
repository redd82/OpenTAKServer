import json, copy
from enum import Enum

#logger.debug
from opentakserver.extensions import logger

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urlencode
import json
from typing import Any, Dict, Optional, Tuple, List, Union



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

class MediaMTXPathConfigV5:

    def __init__(self, name: str, source: str):
        
        # mandatory fields
        self._name = name
        self._source = source
        
        # optional fields with defaults
        self._sourceFingerprint = ""
        self._sourceOnDemand = False
        self._sourceOnDemandStartTimeout = ""
        self._sourceOnDemandCloseAfter = ""
        self._maxReaders = 0
        self._srtReadPassphrase = ""
        self._fallback = ""
        self._useAbsoluteTimestamp = False
        self._record = False
        self._recordPath = "/home/takusr/ots/mediamtx/recordings/%path/%Y-%m-%d_%H-%M-%S-%f"
        self._recordFormat = "fmp4"
        self._recordPartDuration = "100ms"
        #self._recordMaxPartSize = ""
        self._recordSegmentDuration = "1h0m0s"
        self._recordDeleteAfter = ""
        self._overridePublisher = False
        self._srtPublishPassphrase = ""
        self._rtspTransport = "automatic"
        self._rtspAnyPort = False
        self._rtspRangeType = ""
        self._rtspRangeStart = ""
        self._sourceRedirect = ""
        self._rpiCameraCamID = 0
        self._rpiCameraSecondary = False
        self._rpiCameraWidth = 1024
        self._rpiCameraHeight = 768
        self._rpiCameraHFlip = False
        self._rpiCameraVFlip = False
        self._rpiCameraBrightness = 0
        self._rpiCameraContrast = 0
        self._rpiCameraSaturation = 0
        self._rpiCameraSharpness = 0
        self._rpiCameraExposure = "normal"
        self._rpiCameraAWB = "auto"
        self._rpiCameraAWBGains = [0, 0]
        self._rpiCameraDenoise = "off"
        self._rpiCameraShutter = 0
        self._rpiCameraMetering = "centre"
        self._rpiCameraGain = 0
        self._rpiCameraEV = 0
        self._rpiCameraROI = ""
        self._rpiCameraHDR = False
        self._rpiCameraTuningFile = ""
        self._rpiCameraMode = ""
        self._rpiCameraFPS = 30
        self._rpiCameraAfMode = "continuous"
        self._rpiCameraAfRange = "normal"
        self._rpiCameraAfSpeed = "normal"
        self._rpiCameraLensPosition = 0
        self._rpiCameraAfWindow = ""
        self._rpiCameraFlickerPeriod = 0
        self._rpiCameraTextOverlayEnable = False
        self._rpiCameraTextOverlay = ""
        self._rpiCameraCodec = "auto"
        self._rpiCameraIDRPeriod = 0
        self._rpiCameraBitrate = 0
        self._rpiCameraProfile = "main"
        self._rpiCameraLevel = "4.1"
        self._rpiCameraJPEGQuality = 60
        self._runOnInit = ""
        self._runOnInitRestart = False
        self._runOnDemand = ""
        self._runOnDemandRestart = False
        self._runOnDemandStartTimeout = "10s"
        self._runOnDemandCloseAfter = "10s"
        self._runOnUnDemand = " "
        self._runOnReady = ""
        self._runOnReadyRestart = False
        self._runOnNotReady = ""
        self._runOnRead = ""
        self._runOnReadRestart = False
        self._runOnUnread = ""
        self._runOnRecordSegmentCreate = ""
        self._runOnRecordSegmentComplete = ""
        self._playback = False

                
    # Boolean Helper method
    def _normalize_bool(self, val):
        if isinstance(val, bool):
            return val
        if isinstance(val, int):
            return val != 0
        if isinstance(val, str):
            val_norm = val.strip().lower()
            if val_norm in ("1", "true", "yes", "on"):
                return True
            elif val_norm in ("0", "false", "no", "off", ""):
                return False
        raise ValueError(f"Invalid boolean value: {val!r} (expected bool, int, or 'true/false'-like string)")

    # Boolean fields getters/setters
    def runOnReadRestart(self, value=None):
        if value is None:
            return self._runOnReadRestart
        self._runOnReadRestart = self._normalize_bool(value)
    def runOnReadyRestart(self, value=None):
        if value is None:
            return self._runOnReadyRestart
        self._runOnReadyRestart = self._normalize_bool(value)
    def runOnDemandRestart(self, value=None):
        if value is None:
            return self._runOnDemandRestart
        self._runOnDemandRestart = self._normalize_bool(value)
    def runOnInitRestart(self, value=None):
        if value is None:
            return self._runOnInitRestart
        self._runOnInitRestart = self._normalize_bool(value)
    def rpiCameraTextOverlayEnable(self, value=None):
        if value is None:
            return self._rpiCameraTextOverlayEnable
        self._rpiCameraTextOverlayEnable = self._normalize_bool(value)
    def rpiCameraHDR(self, value=None):
        if value is None:
            return self._rpiCameraHDR
        self._rpiCameraHDR = self._normalize_bool(value)
    def rpiCameraHFlip(self, value=None):
        if value is None:
            return self._rpiCameraHFlip
        self._rpiCameraHFlip = self._normalize_bool(value)
    def rpiCameraVFlip(self, value=None):
        if value is None:
            return self._rpiCameraVFlip
        self._rpiCameraVFlip = self._normalize_bool(value)
    def rpiCameraSecondary(self, value=None):
        if value is None:
            return self._rpiCameraSecondary
        self._rpiCameraSecondary = self._normalize_bool(value)
    def rtspAnyPort(self, value=None):
        if value is None:
            return self._rtspAnyPort
        self._rtspAnyPort = self._normalize_bool(value)
    def SourceOnDemand(self, value=None):
        if value is None:
            return self._sourceOnDemand
        self._sourceOnDemand = self._normalize_bool(value)
    def overridePublisher(self, value=None):
        if value is None:
            return self._overridePublisher
        self._overridePublisher = self._normalize_bool(value)
    def useAbsoluteTimestamp(self, value=None):
        if value is None:
            return self._useAbsoluteTimestamp
        self._useAbsoluteTimestamp = self._normalize_bool(value)
    def record(self, value=None):
        if value is None:
            return self._record
        self._record = self._normalize_bool(value)
    def playback(self, value=None):
        if value is None:
            return self._playback
        self._playback = self._normalize_bool(value)

    
    # int fields getters/setters
    def MaxReaders(self, value=None):
        """Maximum number of clients allowed to read/view this stream. (hardcoded to 1000) 0 = no limit."""
        if value == None: return self._maxReaders
        else: self._range(value, 0, 1000)
    def RpiCameraJPEGQuality(self, value=None):
    #    """MJPEG quality (2–31). 0 = default."""
        if value is None: return self._rpiCameraJPEGQuality
        self._rpiCameraJPEGQuality = self._range(value, 0, 31)
        return self._rpiCameraJPEGQuality
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
            logger.debug("MediaMTXPathConfigV5: AWBGains must be a list or tuple of two numbers [RedGain, BlueGain]")
            raise ValueError("AWBGains must be a list or tuple of two numbers [RedGain, BlueGain]")
        # Clamp each channel gain individually
        self._rpiCameraAWBGains = [
            self._range_float(float(value[0]), 0.0, 8.0),
            self._range_float(float(value[1]), 0.0, 8.0)
        ]
    # mandatory fields getters/setters  
    def Name(self, value=None):
        if value is None: return self._name
        else: self._name = value
    def Source(self, value=None):
        if value is None: return self._source
        else: self._source = value
    # string fields getters/setters
    def SourceFingerprint(self, value=None):
        if value is None: return self._sourceFingerprint
        else: self._sourceFingerprint = value
    def SourceOnDemandStartTimeout(self, value=None):
        if value is None: return self._sourceOnDemandStartTimeout
        else: self._sourceOnDemandStartTimeout = value
    def SourceOnDemandCloseAfter(self, value=None):
        if value is None: return self._sourceOnDemandCloseAfter
        else: self._sourceOnDemandCloseAfter = value
    def SrtReadPassphrase(self, value=None):
        if value is None: return self._srtReadPassphrase
        else: self._srtReadPassphrase = value
    def Fallback(self, value=None):
        if value is None: return self._fallback
        else: self._fallback = value
    def RecordPath(self, value=None):
        if value is None: return self._recordPath
        else: self._recordPath = value
    def RecordFormat(self, value=None):
        if value is None: return self._recordFormat
        else: self._recordFormat = value
    def RecordPartDuration(self, value=None):
        if value is None: return self._recordPartDuration
        else: self._recordPartDuration = value
    #def RecordMaxPartSize(self, value=None):
    #    if value is None: return self._recordMaxPartSize
    #    else: self._recordMaxPartSize = value
    def RecordSegmentDuration(self, value=None):
        if value is None: return self._recordSegmentDuration
        else: self._recordSegmentDuration = value
    def RecordDeleteAfter(self, value=None):
        if value is None: return self._recordDeleteAfter
        else: self._recordDeleteAfter = value
    def SrtPublishPassphrase(self, value=None):
        if value is None: return self._srtPublishPassphrase
        else: self._srtPublishPassphrase = value
    def RtspTransport(self, value=None):
        if value is None: return self._rtspTransport
        else: self._rtspTransport = value
    def RtspRangeType(self, value=None):
        if value is None: return self._rtspRangeType
        else: self._rtspRangeType = value
    def RtspRangeStart(self, value=None):
        if value is None: return self._rtspRangeStart
        else: self._rtspRangeStart = value
    #def RtpSDP(self, value=None):
    #    if value is None: return self._rtpSDP
    #    else: self._rtpSDP = value  
    def SourceRedirect(self, value=None):
        if value is None: return self._sourceRedirect
        else: self._sourceRedirect = value
    def RpiCameraExposure(self, value=None):
        """rpiCameraExposure
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
        """
        if value is None: return self._rpiCameraExposure 
        value = value.lower()
        if value in ("auto", "sun", "cloudy", "shade", "tungsten", "fluorescent", "incandescent", "flash", "horizon"): self._rpiCameraExposure = value
       
        pass
    def RpiCameraAWB(self, value=None):
        """rpiCameraAWB
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
            - Note: "auto" enables automatic white balance adjustment."""
            
        if value is None: return self._rpiCameraAWB  
        value = value.lower() 
        if value in ("auto", "sun", "cloudy", "shade", "tungsten", "fluorescent", "incandescent", "flash", "horizon"): self._rpiCameraAWB = value        
    def RpiCameraDenoise(self, value=None):
        if value is None: return self._rpiCameraDenoise
        else: self._rpiCameraDenoise = value     
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
        if value is None: return self._rpiCameraMetering    
        if value.lower() in ("average", "spot", "backlit", "matrix"): self._rpiCameraMetering = value
        
        pass
    def RpiCameraROI(self, value=None):
        # unused for now; takes a four float input for x/y top left and bottom right corner 
        # but mediamtx api wants this as a string
        return self._rpiCameraROI
    
    def RpiCameraTuningFile(self, value=None):
        if value is None: return self._rpiCameraTuningFile
        else: self._rpiCameraTuningFile = value
    def RpiCameraMode(self, value=None):
        if value is None: return self._rpiCameraMode
        else: self._rpiCameraMode = value
    def RpiCameraAfMode(self, value=None):
        if value is None: return self._rpiCameraAfMode
        else: self._rpiCameraAfMode = value
    def RpiCameraAfRange(self, value=None):
        if value is None: return self._rpiCameraAfRange
        else: self._rpiCameraAfRange = value
    def RpiCameraAfSpeed(self, value=None):
        if value is None: return self._rpiCameraAfSpeed
        else: self._rpiCameraAfSpeed = value    
    def RpiCameraAfWindow(self, value=None):
        if value is None: return self._rpiCameraAfWindow
        else: self._rpiCameraAfWindow = value
    def RpiCameraTextOverlay(self, value=None):
        if value is None: return self._rpiCameraTextOverlay
        else: self._rpiCameraTextOverlay = value
    def RpiCameraCodec(self, value=None):
        if value is None: return self._rpiCameraCodec
        else: self._rpiCameraCodec = value
    def RpiCameraHardwareH264Profile(self, value=None):
        if value is None: return self._rpiCameraHardwareH264Profile
        else: self._rpiCameraHardwareH264Profile = value
    def RpiCameraHardwareH264Level(self, value=None):
        if value is None: return self._rpiCameraHardwareH264Level
        else: self._rpiCameraHardwareH264Level = value
    def RunOnInit(self, value=None):
        if value is None: return self._runOnInit
        else: self._runOnInit = value
    def RunOnDemand(self, value=None):
        if value is None: return self._runOnDemand
        else: self._runOnDemand = value
    def RunOnUnDemand(self, value=None):
        if value is None: return self._runOnUnDemand
        else: self._runOnUnDemand = value
    def RunOnReady(self, value=None):
        if value is None: return self._runOnReady
        else: self._runOnReady = value
    def RunOnNotReady(self, value=None):
        if value is None: return self._runOnNotReady
        else: self._runOnNotReady = value
    def RunOnRead(self, value=None):
        if value is None: return self._runOnRead
        else: self._runOnRead = value
    def RunOnUnread(self, value=None):
        if value is None: return self._runOnUnread
        else: self._runOnUnread = value
    def RunOnRecordSegmentCreate(self, value=None):
        if value is None: return self._runOnRecordSegmentCreate
        else: self._runOnRecordSegmentCreate = value
    def RunOnRecordSegmentComplete(self, value=None):
        if value is None: return self._runOnRecordSegmentComplete
        else: self._runOnRecordSegmentComplete = value
        

    # helper methods
    def _range(self, value: int, minimum: int, maximum: int) -> int: return max(minimum, min(value, maximum))
    def _range_float(self, value: float, minimum: float, maximum: float) -> float: return max(minimum, min(value, maximum))
    
    def PayloadCreatePath(self) -> Dict[str, Any]:
        """
        Create a blankdictionary payload for MediaMTX API path creation.
        """
        payload = {}

        return payload
    
    def PayloadUpdatePath(self) -> Dict[str, Any]:
        """
        Create a dictionary payload for MediaMTX API path creation,
        including all self._ attributes except `_name`.
        """
        payload = {}
        for attr, value in self.__dict__.items():
            if attr.startswith("_") and attr != "_name":
                # Remove leading underscore for the dictionary key
                key = attr[1:]
                payload[key] = value
        return payload
 
    def SyncFromDict(self, data: Dict[str, Any]) -> None:
        """
        Update the object's attributes based on a given dictionary.
        Uses the object's setter methods if they exist, otherwise updates the internal attribute directly.
        This ensures type checking and range validation are applied.
        """
        try:
            for key, value in data.items():
                # Try to get the setter method (same name as key)
                setter = getattr(self, key, None)

                if callable(setter):
                    try:
                        setter(value)  # Use setter for validation
                    except Exception as e:
                        logger.warning(f"MediaMTXPathConfigV5: Warning: could not set {key}={value}: {e}")
                        raise ValueError(f"MediaMTXPathConfigV5: Warning: could not set {key}={value}: {e}")
                else:
                    # Fallback: directly set the _ attribute if it exists
                    attr_name = f"_{key}"
                    if hasattr(self, attr_name):
                        setattr(self, attr_name, value)
                    else:
                        logger.warning(f"MediaMTXPathConfigV5:Warning: attribute {key} does not exist on object")
                        raise ValueError(f"MediaMTXPathConfigV5:Warning: attribute {key} does not exist on object")
        except Exception as e:
            raise ValueError(f"MediaMTXPathConfigV5: Error syncing from dict: {e}")
 
    def SyncFromJson(self, data: dict) -> None:
        """
        Update the config from a JSON/dict returned by MediaMTX API.
        Maps API fields to internal attributes, using existing setters when possible.
        """
        try:
            if not isinstance(data, dict):
                logger.error("MediaMTXPathConfigV5: SyncFromJson expects a dictionary.")
                raise ValueError("MediaMTXPathConfigV5: SyncFromJson expects a dictionary.")

            for key, value in data.items():
                # Skip name (mandatory, shouldn't be overwritten)
                if key == "name":
                    continue
                try:
                    # Use SyncFromDict to handle all other existing attributes
                    self.SyncFromDict({key: value})
                except ValueError:
                    # ignore unknown fields
                    logger.warning(f"MediaMTXPathConfigV5: Warning: attribute {key} does not exist on object")
                    raise Warning(f"MediaMTXPathConfigV5: Warning: attribute {key} does not exist on object")
        except Exception as e:
            logger.warning(f"MediaMTXPathConfigV5: Error syncing from JSON: {e}")
            raise ValueError(f"MediaMTXPathConfigV5: Error syncing from JSON: {e}")
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Return a dictionary representation of the configuration.
        This is similar to PayloadUpdatePath(), but includes the _name field
        and ensures JSON-safe values (e.g., lists, bools, numbers, strings only).
        """
        result: Dict[str, Any] = {}
        for attr, value in self.__dict__.items():
            if attr.startswith("_"):
                key = attr[1:]
                # convert nested objects (if any) into strings for safety
                if isinstance(value, (str, int, float, bool, list, dict)) or value is None:
                    result[key] = value
                else:
                    result[key] = str(value)
        return result


# ─────────────────────────────────────────────────────────────────────────────
# MediaMTX API helper
# ─────────────────────────────────────────────────────────────────────────────
class MediamMTXAPIInterfaceV5:

    class Endpoints(Enum):
        LIST_PATHS = "/v3/config/paths/list"
        ADD_PATH = "/v3/config/paths/add/{uid}"
        PATCH_PATH = "/v3/config/paths/patch/{uid}"
        DELETE_PATH = "/v3/config/paths/delete/{uid}"
        GET_PATH = "/v3/paths/get/{uid}"  

    def __init__(
        self,
        *,     
        link: "Link",
        jwt_token: Optional[str] = None,
        verify_ssl: bool = False
    ) -> None:

        if not link:
            logger.error("MediamMTXAPIInterfaceV5: A Safe_Link object must be provided.")
            raise ValueError("MediamMTXAPIInterfaceV5: A Safe_Link object must be provided.")

        self._link = link
        self._jwt = jwt_token
        self._base_url = self._link.Hyperlink.rstrip("/")

        self._session = requests.Session()
        self._session.verify = verify_ssl

        # Retry strategy
        retries = Retry(
            total=3,
            backoff_factor=3,
            status_forcelist=[502, 503, 504],
            allowed_methods=frozenset(["HEAD", "GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])  # must be a set/frozenset
        )
        adapter = HTTPAdapter(max_retries=retries.total)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

        try:
            self.alive = self.is_alive()
        except Exception:
            self.alive = False

    @property 
    def Hyperlink(self):
        return self._base_url

    def is_alive(self) -> bool:
        """Check if MediaMTX is reachable and responding."""
        status = self._request("GET", self.Endpoints.LIST_PATHS.value)
        return 200 <= status < 300
    
    #path
    def create_path(self, config: "MediaMTXPathConfigV5", path_name: str) -> int: 
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
                    
            
            200	 the request was successful.
            400	 invalid request.
                 {
                    "error": "string"
                }

            500 server error.
                {
                    "error": "string"
                }
        """
        
        """Create a MediaMTX path."""
        try:
            payload = config.PayloadCreatePath()
            response = self._request("POST", self.Endpoints.ADD_PATH.value.format(uid=path_name), json=payload)
            return response
        except Exception as e:
            logger.error(f"MediamMTXAPIInterfaceV5: Error creating path: {e}")
            raise ValueError(f"MediamMTXAPIInterfaceV5: Error creating path: {e}")
    
    def delete_path(self, path_name: str) -> int:
        """Delete a MediaMTX path."""
        try:
            endpoint = self.Endpoints.DELETE_PATH.value.format(uid=path_name)
            status = self._request("DELETE", endpoint)
            return status
        except Exception as e:
            logger.error(f"MediamMTXAPIInterfaceV5: Error deleting path: {e}")
            raise ValueError(f"MediamMTXAPIInterfaceV5: Error deleting path: {e}")
 
    def get_path(self, path_name: str) -> dict:
        """
        Retrieve a MediaMTX path configuration.
        GET /v3/paths/get/{name}

        Returns the JSON response on success.
        Raises ValueError on failure (400, 404, 500, etc.).
        """
        try:
            endpoint = self.Endpoints.GET_PATH.value.format(uid=path_name)
            url = f"{self._base_url}/{endpoint.lstrip('/')}"
            
            response = self._session.get(
                url,
                headers=self._headers(),
                params=self._params(),
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 400:
                logger.error(f"MediamMTXAPIInterfaceV5: Invalid request for path '{path_name}': {response.text}")
                raise ValueError(f"MediamMTXAPIInterfaceV5: Invalid request for path '{path_name}': {response.text}")
            elif response.status_code == 404:
                logger.error(f"MediamMTXAPIInterfaceV5: Path '{path_name}' not found.")
                raise ValueError(f"MediamMTXAPIInterfaceV5: Path '{path_name}' not found.")
            else:
                logger.error(f"MediamMTXAPIInterfaceV5: Server error ({response.status_code}) retrieving path '{path_name}': {response.text}")
                raise ValueError(f"MediamMTXAPIInterfaceV5: Server error ({response.status_code}) retrieving path '{path_name}': {response.text}")
        
        except requests.RequestException as e:
            logger.error(f"MediamMTXAPIInterfaceV5: Network error retrieving path '{path_name}': {e}")
            raise ValueError(f"MediamMTXAPIInterfaceV5: Network error retrieving path '{path_name}': {e}")
    
    def patch_path(self, path_name: str, changes: dict) -> int:
        """Patch a MediaMTX path with the given changes dictionary.
            post:
            summary: adds a path configuration.
            description: all fields are optional.
            parameters:
            - path_name str
            - changes dict
        """
        try:
            endpoint = self.Endpoints.PATCH_PATH.value.format(uid=path_name)
            status = self._request("PATCH", endpoint, json=changes)
            return status
        except Exception as e:
            logger.error(f"MediamMTXAPIInterfaceV5: Error patching path: {e}")  
            raise ValueError(f"MediamMTXAPIInterfaceV5: Error patching path: {e}")  
    
    #def list_paths(self) ->None:       """List all MediaMTX paths."""
        #placeholder_ #TODO Make Functional
    #    pass
    
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
        json: Optional[dict] = None
    ) -> int:

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
            return response

        except requests.RequestException:
            return 500
        except Exception:
            return 500

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
        adapter = HTTPAdapter(max_retries=retries.total)
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

    def disconnect_url(self, otp: Optional[str] = None, as_curl: bool = False) -> str:
        """Return the URL for disconnecting, including uid and otp."""
        url = self.build_url(UnifiedInputs.TakatVideo_Endpoints.DISCONNECT, otp=otp)
        return f"{self._addCurl()}{url}" if as_curl else url

    def add_camera(self, otp: str) -> int:
        """Add a camera for this uid using the given OTP."""
        return self._call(UnifiedInputs.TakatVideo_Endpoints.ADD_CAMERA, otp=otp)

    def add_camera_url(self, otp: Optional[str] = None, as_curl: bool = False) -> str:
        """Return the URL for adding a camera, including uid and otp."""
        url = self.build_url(UnifiedInputs.TakatVideo_Endpoints.ADD_CAMERA, otp=otp)
        return f"{self._addCurl()}{url}" if as_curl else url

    def remove_camera(self, otp: str) -> int:
        """Remove a camera for this uid using the given OTP."""
        return self._call(UnifiedInputs.TakatVideo_Endpoints.REMOVE_CAMERA, otp=otp)

    def remove_camera_url(self, otp: Optional[str] = None, as_curl: bool = False) -> str:
        """Return the URL for removing a camera, including uid and otp."""
        url = self.build_url(UnifiedInputs.TakatVideo_Endpoints.REMOVE_CAMERA, otp=otp)
        return f"{self._addCurl()}{url}" if as_curl else url

    def register(self, otp: str) -> int:
        """Register this uid using the given OTP."""
        return self._call(UnifiedInputs.TakatVideo_Endpoints.REGISTER, otp=otp)

    def register_url(self, otp: Optional[str] = None, as_curl: bool = False) -> str:
        """Return the URL for registering, including uid and otp."""
        url = self.build_url(UnifiedInputs.TakatVideo_Endpoints.REGISTER, otp=otp)
        return f"{self._addCurl()}{url}" if as_curl else url

    def unregister(self, otp: str) -> int:
        """Unregister this uid using the given OTP."""
        return self._call(UnifiedInputs.TakatVideo_Endpoints.UNREGISTER, otp=otp)

    def unregister_url(self, otp: Optional[str] = None, as_curl: bool = False) -> str:
        """Return the URL for unregistering, including uid and otp."""
        url = self.build_url(UnifiedInputs.TakatVideo_Endpoints.UNREGISTER, otp=otp)
        return f"{self._addCurl()}{url}" if as_curl else url
    
    # ------------------------
    # helper function to prefix the curl command
    # ------------------------
    def _addCurl(self) -> str:
        curl = "curl -s -X POST "
        return curl
        

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
        self._metadata = f"-metadata uid='{self._camera_uid}' -metadata linked_device='{self._linked_device}'"

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
        output_url = f"{encoding.value}://127.0.0.1{port_suffix}/{self._camera_uid}"

        # Wrap URLs in quotes for shell safety
        cmd = f"ffmpeg -timeout {timeout} -i '{input_url}' -c copy {self._metadata} -f {encoding.value} '{output_url}'"
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
        output_url = f"{encoding.value}://127.0.0.1{port_suffix}/{self._camera_uid}"

        cmd = f"ffmpeg -re -stream_loop {loop_flag} -i '{input_url}' -c copy {self._metadata} -f {encoding.value} '{output_url}'"
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
        output_url = f"{encoding.value}://127.0.0.1{port_suffix}/{self._camera_uid}"

        cmd = f"ffmpeg -re -stream_loop {loop_flag} -i '{input_url}' -c copy {self._metadata} -f {encoding.value} '{output_url}'"
        return cmd

# ─────────────────────────────────────────────────────────────────────────────
# Single Camera object
# ───────────────────────────────────────────────────────────────────────────── 
class CameraObjectV4():
                    
    def __init__(
            self,
            *,
            config: MediaMTXPathConfigV5,
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

        # // ...existing code...
        # from typing import Any, Dict, Optional, Tuple, List, Union
        # // ...existing code...
        # from typing import Any, Dict, Optional, Tuple, List, Union, Sequence
        # // ...existing code...
        #             *,
        # -            config: MediaMTXPathConfigV5,
        # +            config: Union[MediaMTXPathConfigV5, Sequence[MediaMTXPathConfigV5]],
        # // ...existing code...
        # -        self._source_config = copy.deepcopy(config)
        # +        configs = (config if isinstance(config, Sequence) else (config,))
        # +        self._source_config = copy.deepcopy(configs[0])
        #         self._source_config.Name(value=source_uid)
                
        #         self._virtual_path_url: Optional[str] = None
        # -        self._virtual_config = copy.deepcopy(config)
        # +        base_virtual = configs[1] if len(configs) > 1 else configs[0]
        # +        self._virtual_config = copy.deepcopy(base_virtual)


        # Core IDs
        self._source_uid = source_uid
        self._virtual_uid = virtual_uid
        
        self._source_path_url: Optional[str] = None
        
        self._source_config= copy.deepcopy(config)              # make a copy of the config
        self._virtual_config= copy.deepcopy(self._source_config)# make a copy of the copy of the config
        
        self._source_config.Name(value=source_uid)      # change the name of the config to the source camera path (do this only BEFORE creating a path)
        
        self._virtual_path_url: Optional[str] = None
        self._virtual_config.Name(value=virtual_uid)    # change the name of the config to the virtual camera path (do this only BEFORE creating a path)
        
        self._api_mediamtx = api_mediamtx_link
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

        # Build FFmpeg helper
        port = self._stream_mediamtx_link.Port or 8554
        self._ffmpeg = FFMPEG_Command_Builder_v4(
            camera_uid=self._source_uid,
            linked_uid=self._virtual_uid,
            mediamtx_streaming_port=port,
            link=self._stream_source_link
        )
        
        # API interface
        self.Media_MTX_API = MediamMTXAPIInterfaceV5(
                            link=api_mediamtx_link,
                            verify_ssl=False,
                            jwt_token=None
                            )
        
        # change the local configs to what we want them to become              
        #source camera
        self._source_config.RunOnReady(value=self._ffmpeg.run_on_init(ingest_type=self._input_type,
                                                                         output_protocol=self._output_protocol,
                                                                         timeout=self._timeout,
                                                                         loop=self._loop))
        self._source_config.SourceOnDemand(value="")
        self._source_config.Source(value="publisher")
        self._source_config.RunOnDemand(value="")    
        self._source_config.RunOnNotReady(value=self._api_takat.disconnect_url(otp=self._otp, as_curl=True)) # TakatVideo disconnect command
        self._source_config.rpiCameraTextOverlayEnable(value=False) # no text overlay on origional
        self._source_config.RpiCameraTextOverlay(value="")          # no text overlay on origional
        self._source_config.rpiCameraHFlip(value=False)             # we do not flip the origional 
        self._source_config.rpiCameraVFlip(value=False)             # we do not flip the origional 
        self._source_config.record(value=False)                     # we do not record the origional
        
        #virtual camera
        self._virtual_config.Source(value=f"{output_protocol.value}://{stream_mediamtx_link.Host}:{stream_mediamtx_link.Port}/{self.source_uid}")
        self._virtual_config.SourceOnDemand(value=True)
        if self._virtual_config.Source() != "publisher": # incase of a non publisher source we must set runondemand and runonundemand to ""
            self._virtual_config.RunOnDemand(value="")
            self._virtual_config.RunOnUnDemand(value="")
        
        # reset the following values because if they are changed from default we only want to apply them in the source camera
        self._virtual_config.RpiCameraBrightness(value=0)
        self._virtual_config.RpiCameraContrast(value=0)
        self._virtual_config.RpiCameraSaturation(value=0)
        self._virtual_config.RpiCameraSharpness(value=0)
        self._virtual_config.RpiCameraExposure(value="normal")
        self._virtual_config.RpiCameraAWB(value="auto")
        self._virtual_config.RpiCameraGain(value=0)
        self._virtual_config.RpiCameraShutter(value=0)
        self._virtual_config.RpiCameraDenoise(value="off")
        self._virtual_config.RpiCameraMetering(value="centre")
        self._virtual_config.RpiCameraROI(value="")
        self._virtual_config.RpiCameraEV(value=0)
        self._virtual_config.RpiCameraAfMode(value="continuous")
        self._virtual_config.RpiCameraAfRange(value="normal")
        self._virtual_config.RpiCameraAfSpeed(value="normal")                
        self._virtual_config.RpiCameraLensPosition(value=0)
        self._virtual_config.RpiCameraAfWindow(value="")
        self._virtual_config.RpiCameraFlickerPeriod(value=0)
        
        # now make thoose paths and set them up
        # Initialize paths only if flag is True
        if create_paths == True: self._initialize_paths()

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
        self._add_source()
        # Step 2: Add Virtual Path
        self._add_virtual()
        # Step 3: Reverse Sync (push local config to server)
        self._sync()
        # Step 4: Update URLs
        self._update_url()
        # All steps succeeded

    def _add_source(self) -> None:
        try:
            status_source_add = self.Media_MTX_API.create_path(path_name=self._source_uid, config=self._source_config)
            if not (200 <= status_source_add < 300):
                self._status_code = status_source_add
                self._status_message = f"CameraObjectV4: Failed to add source path ({self._source_uid}, with code {status_source_add})"
                logger.info(f"CameraObjectV4: Failed to add source path ({self._source_uid}, with code {status_source_add})")
                return
            else:
                #path has been created, now update its settings
                self._status_code = status_source_add
                self._status_message = f"CameraObjectV4: added source path ({self._source_uid}, with code {status_source_add})"
                logger.info(f"CameraObjectV4: added source path ({self._source_uid}, with code {status_source_add})")
                return
                
        except Exception as E:
            # something went catwompus whilest making the path.
            self._status_code = 500
            logger.error(f"CameraObjectV4: Unexpected error when adding source path: {E}")
            return
        
    def _add_virtual(self) -> None:
        # Step 2: Add Virtual Path
        try:
            status_virtual_add = self.Media_MTX_API.create_path(path_name=self._virtual_uid, config=self._virtual_config)
            if not (200 <= status_virtual_add < 300):
                self._status_code = status_virtual_add
                self._status_message = f"CameraObjectV4: Failed to add virtual path ({self._virtual_uid}, with code {status_virtual_add})"
                logger.info(f"CameraObjectV4: Failed to add source path ({self._virtual_uid}, with code {status_virtual_add})")
                return
            else:
                self._status_code = status_virtual_add
                self._status_message = f"CameraObjectV4: added virtual path ({self._virtual_uid}, with code {status_virtual_add})"
                logger.info(f"CameraObjectV4: added virtual path ({self._virtual_uid}, with code {status_virtual_add})")
                return

        except Exception as E:
            self._status_code = 500
            logger.error(f"CameraObjectV4: Unexpected error when adding virtual path: {E}")
            return
            
    def _sync(self) -> None:
        # ------------------------
        # Step 3: Sync (push local config to server)
        # ------------------------
        try:
            # patch source cam
            statusS = self.Media_MTX_API.patch_path(path_name=self._source_uid, changes=self._source_config.to_dict())
            # patch virtual cam
            statusV = self.Media_MTX_API.patch_path(path_name=self._virtual_uid, changes=self._virtual_config.to_dict()) 
            if statusS != 200: 
                logger.warning(f"CameraObjectV4: Unexpected server response whilest patching source path {self._source_uid}")
            if statusV != 200:
                logger.warning(f"CameraObjectV4: Unexpected server response whilest patching virtual path {self._virtual_uid}")
                
        except requests.exceptions.ConnectionError:
            logger.warning(f"CameraObjectV4: connection error whilest connecting to {self._api_mediamtx.Hyperlink} ")
        except Exception:
            logger.warning(f"CameraObjectV4: internal server error whilest connecting to {self._api_mediamtx.Hyperlink} ")
            
    def _update_url(self) -> None:
                # ------------------------
        # Step 4: Update URLs
        # ------------------------
        try:
            self._source_path_url = f"{self._stream_mediamtx_link.Root()}{self._source_uid}"
            self._virtual_path_url = f"{self._stream_mediamtx_link.Root()}{self._virtual_uid}"
        except Exception:
            logger.warning(f"CameraObjectV4: Failed to update source/virtual URLs")
            raise Warning(f"CameraObjectV4: Failed to update source/virtual URLs")

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
            #def delete_path(self, path_name: str) -> int:
            statusS = self.Media_MTX_API.delete_path(path_name=self._source_uid)
            statusV = self.Media_MTX_API.delete_path(path_name=self._virtual_uid)
            
            if statusS != 200: 
                raise Warning(f"CameraObjectV4: Unexpected server response whilest deleting source path {self._source_uid}")
            if statusV != 200:
                raise Warning(f"CameraObjectV4: Unexpected server response whilest deleting irtual path {self._source_uid}")
            
            # TODO: unregister from TakatVideo API when available
        except Exception as e:
            raise Warning(f"CameraObjectV4: Self-destruct cleanup failed: {e}")

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
    # Reverse Sync
    # ------------------------
    def SourceCameraFromServer(self, uid):
        """
            Retrieve and apply source camera configuration from the MediaMTX server.

            Parameters
            ----------
            uid : str or None
                Unique identifier of the source camera on the MediaMTX server.
                If None, the function will not attempt to retrieve any configuration.

            Raises
            ------
            Warning
                If a connection error occurs or if the MediaMTX server responds with an internal error.
            requests.exceptions.ConnectionError
                If the connection to the MediaMTX API fails.

            Notes
            -----
            This method uses the `Media_MTX_API.get_path()` method to fetch the
            configuration for the given `uid`, and applies it to `_source_config`
            using `SyncFromDict()`.
            """
        try:
            if uid != None:
                    self._source_config.SyncFromDict(data=self.Media_MTX_API.get_path(uid)) # try to set the config from what is on the mediamtx server
                    
        except requests.exceptions.ConnectionError: # Errors :/
            logger.error(f"CameraObjectV4: connection error whilest connecting to {self.Media_MTX_API.Hyperlink} whilest attempting to retrieve config from mediamtx server.")
            #raise Warning(f"CameraObjectV4: connection error whilest connecting to {self.Media_MTX_API.Hyperlink} whilest attempting to retrieve config from mediamtx server.")
        except Exception:
            logger.error(f"CameraObjectV4: internal server error whilest connecting to {self._api_mediamtx.Hyperlink} whilest attempting to retrieve config from mediamtx server.")
    
    def VirtualCameraFromServer(self, uid):
        """
            Retrieve and apply virtual camera configuration from the MediaMTX server.

            Parameters
            ----------
            uid : str or None
                Unique identifier of the virtual camera on the MediaMTX server.
                If None, the function will not attempt to retrieve any configuration.

            Raises
            ------
            Warning
                If a connection error occurs or if the MediaMTX server responds with an internal error.
                requests.exceptions.ConnectionError
                 If the connection to the MediaMTX API fails.

            Notes
            -----
            This method uses the `Media_MTX_API.get_path()` method to fetch the
            configuration for the given `uid`, and applies it to `_virtual_config`
            using `SyncFromDict()`.
        """
        try:
            if uid != None:
                    self._virtual_config.SyncFromDict(data=self.Media_MTX_API.get_path(uid)) # try to set the config from what is on the mediamtx server
                    
        except requests.exceptions.ConnectionError: # Errors :/
            logger.error(f"CameraObjectV4: connection error whilest connecting to {self.Media_MTX_API.Hyperlink} whilest attempting to retrieve config from mediamtx server.")
        except Exception:
            logger.error(f"CameraObjectV4: internal server error whilest connecting to {self._api_mediamtx.Hyperlink} whilest attempting to retrieve config from mediamtx server.")
    
    # ------------------------
    # Utility
    # ------------------------
    def UidInUse(self, uid: str) -> bool:
        return uid in (self._source_uid, self._virtual_uid)
   
   # ------------------------
    # Dict Export
    # ------------------------
    def to_dict(self) -> dict[str, Any]:
        """
        Return a dictionary representation of this CameraObjectV4 instance.
        Useful for logging, debugging, or lightweight serialization.
        """
        return {
            "source_uid": self._source_uid,
            "stream_source_link": str(self._stream_source_link),
            "source_config": self._source_config.to_dict(),
            "source_path_url": self._source_path_url,
            "virtual_uid": self._virtual_uid,
            "virtual_config": self._virtual_config.to_dict(),
            "virtual_path_url": self._virtual_path_url,
            "camera_type": getattr(self._camera_type, "name", str(self._camera_type)),
            "otp": self._otp,
            "input_type": getattr(self._input_type, "name", str(self._input_type)),
            "output_protocol": getattr(self._output_protocol, "name", str(self._output_protocol)),
            "timeout": self._timeout,
            "loop": self._loop,
            "api_mediamtx": str(self._api_mediamtx),
            "stream_mediamtx_link": str(self._stream_mediamtx_link),
        } 

    
# ─────────────────────────────────────────────────────────────────────────────
# Video object that glues everything together
# ─────────────────────────────────────────────────────────────────────────────
class Video_Object_v4:
    def __init__(self, 
                  source_camera: Link, mediamtx_server_api: Link, takat_server_api: Link, 
                  mediamtx_server_stream: Link, path_config: MediaMTXPathConfigV5,
                  linked_device: str, virtual_camera_uid: str, source_camera_uid: str, 
                  primary_uid: Optional[str] = None, 
                  ffmpeg_processing_type: Optional[UnifiedInputs.FFMPEG_IngestType] = UnifiedInputs.FFMPEG_IngestType.Default,
                  ffmpeg_output_type:Optional[UnifiedInputs.FFMPEG_Protocol] = UnifiedInputs.FFMPEG_Protocol.DEFAULT,
                  otp: Optional[str] = None): 
        
        self._CAMERAS: list[CameraObjectV4] = [] #this holds all the camera objects
        
        self._primary_uid = primary_uid   #the primary uid of the video object 
        
        if self._IsUnique(linked_device) == True:
            self._link_device = linked_device   # a unique lnked device we add it later in the init
            
        else:
            logger.error(f"Video_Object_v3: Linked Device '{linked_device}' already exists in the global list")
            return

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
                logger.error(f"Video_Object_v3: Primary UID '{primary_uid}' already exists in the global list")
            self._primary_uid = primary_uid
            
        if otp == None: # if otp is not set, set a random one.
            self._otp= SessionCredentials.random_otp(12)
        else: self._otp = otp
        
        self._credentials = SessionCredentials(uid=self._primary_uid, otp=self._otp) #create a credential manger for this session.
        
        self._credentials.add_linked_device(linked_device)  # (finaly) set the linked device
        
        
        
        
        # create a virtal camera based on the primary uid. this is the main channel the takusers look at. 
        # it should be the path of the mediamtx serverstream and the primary uid of this object.
        #self._mediamtx_streaming_server = mediamtx_server_stream
        #self._MYCAM_API_MediamMTX = MediamMTXAPIInterfaceV5(link=mediamtx_server_api,
        #                                                    jwt_token=None,
        #                                                    verify_ssl=False)
        #self._MYCAM_config = copy.deepcopy(path_config)
        #self._MYCAM_config.Source(value="set-to-first-virtual-camera") #OPTIONAL TODO, change to setup so the source points to the first virtual camera in credentials
        #self._MYCAM_config.Name(value=self._primary_uid)
        
        #result = self._MYCAM_API_MediamMTX.create_path(path_name=self._primary_uid, config=self._MYCAM_config)
        
    
            
    @property
    def PrimaryUID(self) -> str:
        return self._credentials.primary_uid
    @property
    def LinkedDevice(self) ->str:
        return self._credentials.linked_device
    @property
    def CameraPath(self):
        pass
    @property
    def Used_UIDs(self) -> list[str]:
        return self._credentials.all_uids
    @property
    def LinkedDevice_CameraPath(self):
        pass
    
    def WallPaper(self) -> None:
        pass

                  
    def Switch_Source(self, up: bool = True) -> None:
        pass
            
    def Add_CameraObject(self,source_uid: str,
                            virtual_uid: str,
                            otp: Optional[str],
                            config: MediaMTXPathConfigV5,
                            api_mediamtx_link: Link,
                            stream_source_link: Link,
                            stream_mediamtx_link: Link,
                            input_type: Optional[UnifiedInputs.FFMPEG_IngestType] = UnifiedInputs.FFMPEG_IngestType.Default,
                            output_protocol: Optional[UnifiedInputs.FFMPEG_Protocol] = UnifiedInputs.FFMPEG_Protocol.DEFAULT,
                            timeout: Optional[int] = 5_000_000,
                            loop: Optional[bool] = True,
                            create_paths: Optional[bool] = True,
                            camera_type: Optional[UnifiedInputs.CameraObjectV4_CameraType] = UnifiedInputs.CameraObjectV4_CameraType.Source,) -> CameraObjectV4:
        
        """
        
        """
        #Mandatory checks
        if self._IsUnique(source_uid) != True: #error not a unique source uid
            logger.error(f"Video_Object_v4: Add_CameraObject: Error, the provided source camera ud is already in use.")
        
        if self._IsUnique(virtual_uid) != True: #error not a unique source uid
            logger.error(f"Video_Object_v4: Add_CameraObject: Error, the provided source camera ud is already in use.")
            
        if otp == None: otp = SessionCredentials.random_otp() # if otp = none create random
        if output_protocol == None: output_protocol = UnifiedInputs.FFMPEG_Protocol.DEFAULT
        if input_type == None: input_type = UnifiedInputs.FFMPEG_IngestType.Default
        if timeout == None: timeout = 5_000_000
        if loop == None: loop = True
        if create_paths == None: create_paths = True
        
        try:
            if self._IsUnique(source_uid) == True and self._IsUnique(virtual_uid) == True: 
                Camera = CameraObjectV4(config=config, 
                                        source_uid=source_uid,
                                        api_mediamtx_link=api_mediamtx_link,
                                        stream_source_link=stream_source_link,
                                        input_type=input_type,
                                        output_protocol=output_protocol,
                                        timeout=timeout,
                                        loop=loop,
                                        create_paths=create_paths,
                                        camera_type=camera_type,
                                        otp=otp,
                                        virtual_uid=virtual_uid,
                                        stream_mediamtx_link=stream_mediamtx_link,
                                        )
                return Camera
        except Exception as E:
            logger.error(f"Video_Object_v4: Add_CameraObject: Error creating camera object")
        
        pass
            
    def Delete_Camera(self, uid: str) -> None:

        pass
                
    def _IsUnique(self, uid) -> bool:
        """
        Returns True if the given UID is *not yet used* in any Video_Object_v4.
        Uses the global VIDEO_OBJECTS registry to verify uniqueness.
        """
        #TODO make functional
        return True

    def _Self_Destruct(self, otp) -> None:

        pass

    def to_dict(self):
        pass

