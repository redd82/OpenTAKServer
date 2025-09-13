import json
import random
import string
from typing import Optional, Dict, Any
from flask import jsonify
from enum import IntEnum

import requests
from requests.adapters import HTTPAdapter

from urllib3.util.retry import Retry
from urllib.parse import urlencode

# ─────────────────────────────────────────────────────────────────────────────
# Third‑party / project imports
# ────────────────────────────────────────────────────────────────────────────
from opentakserver.defaultconfig import DefaultConfig  # central config
from opentakserver.blueprints.TakatVideo_api.Mitm import (
    _start_injection,
    _stop_injection,
)

from opentakserver.blueprints.TakatVideo_api.util import Safe_Link as Link
from opentakserver.blueprints.TakatVideo_api.util import Links_Object as Address
from opentakserver.blueprints.TakatVideo_api.util import Resolutions
from opentakserver.blueprints.TakatVideo_api.util import OTP_UID_Manager as SessionCredentials

# If you need sanitising helpers, import them here as well:
# from opentakserver.blueprints.TakatVideo_api.util import Util_Sanitize


# ─────────────────────────────────────────────────────────────────────────────
# MediaMTX API helper
# ─────────────────────────────────────────────────────────────────────────────

class MediaMTX_API_Interface:
    """
    Wrapper for MediaMTX Control-API (v3) using a Safe_Link for host/protocol/port.

    • Operates on a fixed MediaMTX path provided at init
    • Supports optional JWT token
    """

    def __init__(
        self,
        *,
        managed_path: str,         # renamed from 'name'
        link: Link,           # Safe_Link object for host/protocol/port
        jwt_token: Optional[str] = None,
        verify_ssl: bool = False
    ) -> None:

        if not managed_path:
            raise ValueError("The 'managed_path' parameter is required and cannot be empty.")
        if not link:
            raise ValueError("A Safe_Link object must be provided.")

        self._managed_path = managed_path
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

    def _qs(self) -> Dict[str, str]:
        return {"jwt": self._jwt} if self._jwt else {}

    def _call(
        self,
        method: str,
        api_path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        return_full: bool = False,
    ) -> Any:
        url = f"{self._base_url}/{api_path.lstrip('/')}"
        try:
            response = self._sess.request(
                method,
                url,
                headers=self._headers(),
                params=self._qs(),
                json=json,
                timeout=10,
            )
            return response if return_full else response.status_code
        except requests.RequestException:
            return None if return_full else 0

    # ------------------------
    # Path operations
    # ------------------------
    def add_path(self, config: Dict[str, Any]) -> int:
        return self._call("POST", f"/v3/config/paths/add/{self._managed_path}", json=config)

    def patch_path(self, changes: Dict[str, Any]) -> int:
        return self._call("PATCH", f"/v3/config/paths/patch/{self._managed_path}", json=changes)

    def delete_path(self) -> int:
        return self._call("DELETE", f"/v3/config/paths/delete/{self._managed_path}")

    def is_alive(self) -> bool:
        status = self._call("GET", "/v3/config/paths/list")
        return bool(status and 200 <= status < 300)

    def get_path_config(self) -> Optional[Dict[str, Any]]:
        response = self._call("GET", f"/v3/paths/get/{self._managed_path}", return_full=True)
        if not response or response.status_code != 200:
            return None
        try:
            return response.json()
        except Exception:
            return None

    def to_dict(self) -> Dict[str, Any]:
        base = {
            "base_url": self._base_url,
            "jwt_provided": bool(self._jwt),
            "verify_ssl": self._sess.verify,
            "alive": self.alive,
            "managed_path": self._managed_path,
        }
        config = self.get_path_config()
        base["path_config"] = config if config is not None else "Unavailable"
        return base

 
 
 # ─────────────────────────────────────────────────────────────────────────────
# Mediamtx API path configuration object
# ─────────────────────────────────────────────────────────────────────────────   
class MediaMTX_Path_Config:
    """
    Holds the configuration for a MediaMTX path.
    This is a simplified version of the MediaMTX API path configuration.

    """

    def __init__( self, name: str,                      source: str,                    sourceFingerprint: str = "",        sourceOnDemand: bool = False,      
                sourceOnDemandCloseAfter: str = "",     maxReaders: int = 0,            srtReadPassphrase: str = "",        fallback: str = "",
                useAbsoluteTimestamp: bool = False,     record: bool = False,           recordPath: str = "",               recordFormat: str = "",
                recordPartDuration: str = "",           recordMaxPartSize: str = "",    recordSegmentDuration: str = "",    recordDeleteAfter: str = "",
                overridePublisher: bool = False,        srtPublishPassphrase: str = "", rtspTransport: str = "",            rtspAnyPort: bool = False,
                rtspRangeType: str = "",                rtspRangeStart: str = "",       rtspUDPReadBufferSize: int = 0,     mpegtsUDPReadBufferSize: int = 0,
                rtpSDP: str = "",                       rtpUDPReadBufferSize: int = 0,  sourceRedirect: str = "",           rpiCameraCamID: int = 0,
                rpiCameraSecondary: bool = False,       rpiCameraWidth: int = 0,        rpiCameraHeight: int = 0,           rpiCameraHFlip: bool = False,
                rpiCameraVFlip: bool = False,           rpiCameraBrightness: int = 0,   rpiCameraContrast: int = 0,         rpiCameraSaturation: int = 0,
                rpiCameraSharpness: int = 0,            rpiCameraExposure: str = "",    rpiCameraAWB: str = "",             rpiCameraAWBGains: list[int] | None = None,
                rpiCameraDenoise: str = "",             rpiCameraShutter: int = 0,      rpiCameraMetering: str = "",        rpiCameraGain: int = 0,
                rpiCameraEV: int = 0,                   rpiCameraROI: str = "",         rpiCameraHDR: bool = False,         rpiCameraTuningFile: str = "",
                rpiCameraMode: str = "",                rpiCameraFPS: int = 0,          rpiCameraAfMode: str = "",          rpiCameraAfRange: str = "",
                rpiCameraAfSpeed: str = "",             rpiCameraLensPosition: int = 0, rpiCameraAfWindow: str = "",        rpiCameraFlickerPeriod: int = 0,
                rpiCameraTextOverlayEnable: bool=False, rpiCameraTextOverlay: str = "", rpiCameraCodec: str = "",           rpiCameraIDRPeriod: int = 0,
                rpiCameraBitrate: int = 0,              rpiCameraHardwareH264Profile: str = "",                             sourceOnDemandStartTimeout: str = "",
                rpiCameraHardwareH264Level: str = "",   rpiCameraSoftwareH264Profile: str = "",                             runOnRecordSegmentComplete: str = "",
                rpiCameraSoftwareH264Level: str = "",   rpiCameraMJPEGQuality: int = 0, runOnInit: str = "",                runOnInitRestart: bool = False,
                runOnDemand: str = "",                  runOnDemandRestart: bool = False,runOnDemandStartTimeout: str = "", runOnDemandCloseAfter: str = "",
                runOnUnDemand: str = "",                runOnReady: str = "",           runOnReadyRestart: bool = False,    runOnNotReady: str = "",
                runOnRead: str = "",                    runOnReadRestart: bool = False, runOnUnread: str = "",              runOnRecordSegmentCreate: str = "",
                
            ) -> None:


        self.name = name
        self.source = source
        self.sourceFingerprint = sourceFingerprint
        self.sourceOnDemand = sourceOnDemand
        self.sourceOnDemandStartTimeout = sourceOnDemandStartTimeout
        self.sourceOnDemandCloseAfter = sourceOnDemandCloseAfter
        self.maxReaders = maxReaders
        self.srtReadPassphrase = srtReadPassphrase
        self.fallback = fallback
        self.useAbsoluteTimestamp = useAbsoluteTimestamp
        self.record = record
        self.recordPath = recordPath
        self.recordFormat = recordFormat
        self.recordPartDuration = recordPartDuration
        self.recordMaxPartSize = recordMaxPartSize
        self.recordSegmentDuration = recordSegmentDuration
        self.recordDeleteAfter = recordDeleteAfter
        self.overridePublisher = overridePublisher
        self.srtPublishPassphrase = srtPublishPassphrase
        self.rtspTransport = rtspTransport
        self.rtspAnyPort = rtspAnyPort
        self.rtspRangeType = rtspRangeType
        self.rtspRangeStart = rtspRangeStart
        self.rtspUDPReadBufferSize = rtspUDPReadBufferSize
        self.mpegtsUDPReadBufferSize = mpegtsUDPReadBufferSize
        self.rtpSDP = rtpSDP
        self.rtpUDPReadBufferSize = rtpUDPReadBufferSize
        self.sourceRedirect = sourceRedirect
        self.rpiCameraCamID = rpiCameraCamID
        self.rpiCameraSecondary = rpiCameraSecondary
        self.rpiCameraWidth = rpiCameraWidth
        self.rpiCameraHeight = rpiCameraHeight
        self.rpiCameraHFlip = rpiCameraHFlip
        self.rpiCameraVFlip = rpiCameraVFlip
        self.rpiCameraBrightness = rpiCameraBrightness
        self.rpiCameraContrast = rpiCameraContrast
        self.rpiCameraSaturation = rpiCameraSaturation
        self.rpiCameraSharpness = rpiCameraSharpness
        self.rpiCameraExposure = rpiCameraExposure
        self.rpiCameraAWB = rpiCameraAWB
        self.rpiCameraAWBGains = rpiCameraAWBGains
        self.rpiCameraDenoise = rpiCameraDenoise
        self.rpiCameraShutter = rpiCameraShutter
        self.rpiCameraMetering = rpiCameraMetering
        self.rpiCameraGain = rpiCameraGain
        self.rpiCameraEV = rpiCameraEV
        self.rpiCameraROI = rpiCameraROI
        self.rpiCameraHDR = rpiCameraHDR
        self.rpiCameraTuningFile = rpiCameraTuningFile
        self.rpiCameraMode = rpiCameraMode
        self.rpiCameraFPS = rpiCameraFPS
        self.rpiCameraAfMode = rpiCameraAfMode
        self.rpiCameraAfRange = rpiCameraAfRange
        self.rpiCameraAfSpeed = rpiCameraAfSpeed
        self.rpiCameraLensPosition = rpiCameraLensPosition
        self.rpiCameraAfWindow = rpiCameraAfWindow
        self.rpiCameraFlickerPeriod = rpiCameraFlickerPeriod
        self.rpiCameraTextOverlayEnable = rpiCameraTextOverlayEnable
        self.rpiCameraTextOverlay = rpiCameraTextOverlay
        self.rpiCameraCodec = rpiCameraCodec
        self.rpiCameraIDRPeriod = rpiCameraIDRPeriod
        self.rpiCameraBitrate = rpiCameraBitrate
        self.rpiCameraHardwareH264Profile = rpiCameraHardwareH264Profile
        self.rpiCameraHardwareH264Level = rpiCameraHardwareH264Level
        self.rpiCameraSoftwareH264Profile = rpiCameraSoftwareH264Profile
        self.rpiCameraSoftwareH264Level = rpiCameraSoftwareH264Level
        self.rpiCameraMJPEGQuality = rpiCameraMJPEGQuality
        self.runOnInit = runOnInit
        self.runOnInitRestart = runOnInitRestart
        self.runOnDemand = runOnDemand
        self.runOnDemandRestart = runOnDemandRestart
        self.runOnDemandStartTimeout = runOnDemandStartTimeout
        self.runOnDemandCloseAfter = runOnDemandCloseAfter
        self.runOnUnDemand = runOnUnDemand
        self.runOnReady = runOnReady
        self.runOnReadyRestart = runOnReadyRestart
        self.runOnNotReady = runOnNotReady
        self.runOnRead = runOnRead
        self.runOnReadRestart = runOnReadRestart
        self.runOnUnread = runOnUnread
        self.runOnRecordSegmentCreate = runOnRecordSegmentCreate
        self.runOnRecordSegmentComplete = runOnRecordSegmentComplete
    
    def to_dict(self) -> dict:
        """Return all attributes as a dictionary."""
        return self.__dict__.copy()

    def to_json(self, indent: int = 2) -> str:
        """Return all attributes as a JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    def update_value(self, key: str, value) -> None:
        """Update a single attribute if it exists."""
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            print(f"Warning: '{key}' is not a valid attribute.")
    
    def load_from_dict(self, data: dict) -> None:
        """
        Load values from a dictionary into this config.
        Silently ignores keys that don't exist in the class.
        """
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                print(f"Warning: '{key}' is not a valid attribute, skipping.")
    
    def load_from_json(self, json_str: str) -> None:
        data = json.loads(json_str)
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                print(f"Warning: '{key}' is not a valid attribute, skipping.")
  
# ─────────────────────────────────────────────────────────────────────────────
# TAKAT API helper
# ─────────────────────────────────────────────────────────────────────────────
class TakatVideo_API_Interface:
    # Class-level endpoints dictionary
    ENDPOINTS = {
        "start_injection": "TakatVideo/StartInjection",
        "stop_injection": "TakatVideo/StopInjection",
        "disconnect": "TakatVideo/Disconnect"
        # Add more endpoints here in the future
        #Unregister
        #Reset
        
    }
    
    
    def __init__(self, fqdn: str = "127.0.0.1", port: Optional[int] = 80, protocol: str = "https"):
        if protocol not in ("http", "https"):
            raise ValueError("Protocol must be 'http' or 'https'.")
        
        self._fqdn = fqdn
        self._port = port
        self._protocol = protocol

    # Read-only properties
    @property
    def fqdn(self) -> str:
        return self._fqdn

    @property
    def port(self):
        if self._port is None:
            if self.protocol == "https":
                return 443
            elif self.protocol == "http":
                return 80
        else:
            return self._port

    @property
    def protocol(self) -> str:
        return self._protocol

    # Internal helper to build full URL
    def _build_url(self, endpoint_key: str, **params) -> str:
        if endpoint_key not in self.ENDPOINTS:
            raise ValueError(f"Unknown endpoint: {endpoint_key}")
        endpoint_path = self.ENDPOINTS[endpoint_key]
        query = urlencode(params)
        default_port = 443 if self.protocol == "https" else 80
        port_part = f":{self.port}" if self.port != default_port else ""
        return f"{self.protocol}://{self.fqdn}{port_part}/{endpoint_path}?{query}"

    # API URL generators
    def start_injection_url(self, uid: str, otp: str) -> str:
        return self._build_url("start_injection", uid=uid, otp=otp)

    def stop_injection_url(self, uid: str, otp: str) -> str:
        return self._build_url("stop_injection", uid=uid, otp=otp)

    def disconnect(self, uid: str, otp: str, ip:str) -> str:
        return self._build_url("disconnect", uid=uid, otp=otp)

    # Optional request methods
    def start_injection_request(self, uid: str, otp: str, jwt: Optional[str] = None) -> int:
        try:
            url = self.start_injection_url(uid, otp)
            headers = {"Authorization": f"Bearer {jwt}"} if jwt else {}
            response = requests.get(url, headers=headers)
            return response.status_code
        except requests.RequestException as e:
            print(f"Error in start_injection_request: {e}")
            return 0

    def stop_injection_request(self, uid: str, otp: str, jwt: Optional[str] = None) -> int:
        try:
            url = self.stop_injection_url(uid, otp)
            headers = {"Authorization": f"Bearer {jwt}"} if jwt else {}
            response = requests.get(url, headers=headers)
            return response.status_code
        except requests.RequestException as e:
            print(f"Error in stop_injection_request: {e}")
            return 0
        
  
class FFMPEG_Command_Builder:
    class IngestType(IntEnum):
        CAMERA = 0
        NETWORKED_MP4 = 1
        LOCAL_MP4 = 2
        YOLO = 3

    def __init__(
        self,
        uid: str,
        linked_device: str,
        otp: str,
        timeout: int = 5_000_000,
        input_type: "FFMPEG_Command_Builder.IngestType" = IngestType.CAMERA,
    ):
        self.UID = uid
        self.Linked_Device = linked_device
        self.OTP = otp
        self.timeout = timeout
        self._input_type: FFMPEG_Command_Builder.IngestType = input_type
        self._last_type: Optional[FFMPEG_Command_Builder.IngestType] = None

    @property
    def metadata_template(self) -> str:
        return (
            f'-metadata uid="{self.UID}" '
            f'-metadata linked_device="{self.Linked_Device}" '
            f'-metadata otp="{self.OTP}"'
        )

    @classmethod
    def allowed_types(cls) -> list["FFMPEG_Command_Builder.IngestType"]:
        return list(cls.IngestType)

    @property
    def last_type_used(self) -> Optional["FFMPEG_Command_Builder.IngestType"]:
        return self._last_type

    def update_metadata(
        self,
        *,
        timeout: Optional[int] = None,
        uid: Optional[str] = None,
        otp: Optional[str] = None,
    ) -> None:
        if timeout and timeout > 0:
            self.timeout = timeout
        if uid:
            self.UID = uid
        if otp:
            self.OTP = otp

    def run_on_ready(
        self,
        source: "Link",
        input_type: Optional["FFMPEG_Command_Builder.IngestType"] = None,
        port: int = 8554,
    ) -> str:
        return self._ingest(input_type or self._input_type, source, port)

    def _ingest(
        self,
        type_: "FFMPEG_Command_Builder.IngestType",
        source: "Link",
        port: int,
    ) -> str:
        self._last_type = type_

        if type_ == self.IngestType.CAMERA:
            input_path = source.Hyperlink
        elif type_ == self.IngestType.NETWORKED_MP4:
            input_path = f"{source.Root}{source.URL}"
        elif type_ == self.IngestType.LOCAL_MP4:
            input_path = source.URL
        elif type_ == self.IngestType.YOLO:
            raise NotImplementedError("YOLO ingestion not yet implemented")
        else:
            raise ValueError(f"Unsupported type: {type_}")

        return (
            f'ffmpeg -timeout {self.timeout} '
            f'-re -stream_loop -1 -i "{input_path}" '
            f'-c copy {self.metadata_template} '
            f'-f rtsp "rtsp://127.0.0.1:{port}/{self.UID}/stream"'
        )

    def to_dict(self) -> dict:
        return {
            "UID": self.UID,
            "Linked_Device": self.Linked_Device,
            "OTP": self.OTP,
            "Timeout": self.timeout,
            "MetadataTemplate": self.metadata_template,
            "InputType": self._input_type.name,
            "LastTypeUsed": self._last_type.name if self._last_type else None,
            "Enum": {t.name: t.value for t in self.IngestType},
        }


    
# ─────────────────────────────────────────────────────────────────────────────
# Single Camera object
# ─────────────────────────────────────────────────────────────────────────────      
class Camera_Object():
    Address_ENUM = {
        "camera": 0,
        "MediaMTX": 1,
        "Takat": 2,
    }
    
    def __init__(self, Camera_UID: str, OTP: str, config: MediaMTX_Path_Config, Camera_Address: Link, Mediamtx_Server: Link, Takat_Server: Link, StreamingPort: Optional[int] = 8554, Input_Type: Optional[int]=0):
        # basic paramaters
        self._statuscode = 0
        self._status_message = ""
        self._otp = OTP
        self._streamingport = StreamingPort
        
        #an elegent way to make sure the input type is in the FFMPEG builder enum.
        if Input_Type not in FFMPEG_Command_Builder.ingest_types():
            self._input_type = 0
        else: self._input_type = Input_Type
        # inputs from user
        self._camera_UID = Camera_UID
        self._config = config
        #links
        self._camera_address = Camera_Address
        self._mediamtx_address = Mediamtx_Server
        self._takat_address = Takat_Server  
        
        #connect to mediamtx api
        self._MediamtxAPI = MediaMTX_API_Interface(managed_path=Camera_UID, link=Mediamtx_Server, verify_ssl=False, jwt_token=None)
        #connect to takat api
        self._TakatVideoAPi = TakatVideo_API_Interface(fqdn=Takat_Server.Host, port=Takat_Server.Port, protocol=Takat_Server.Protocol)
        #ffmpeg command builder to alter config runonready command
        self._ffmpeg_command = FFMPEG_Command_Builder(UID=Camera_UID, Linked_Device=Camera_UID, OTP=OTP, input_type=self._input_type)

        # Initial setup
        status = self.Add_Path()
        if status != 200:
            self._status_message = f"Failed to initialize camera {Camera_UID}. Status code: {status}"
            self._statuscode = status
        else:
            self._status_message = f"Camera {Camera_UID} initialized successfully."
            self._statuscode = 200
    
    # Enum-style type handling
    def _enum(self, address_type: int) -> int:
        if address_type not in self.Address_ENUM.values():
            return 0  # default to 'camera'
        return address_type
    
    #elegant way to allow for listing allowed types from outsode the class
    @classmethod
    def address_types(cls) -> list[int]:
        return list(cls.Address_ENUM.values())
    
    @property
    def FFMPEG_RunOnReady(self) -> str:
        return self._ffmpeg_command.RunOnReady(Source=self._camera_address,MediaMTX_Streaming_Port=self._streamingport)
        
    @property
    def OTP(self) -> str:
        return self._otp        
    @property
    def MediamtxAPI(self) -> MediaMTX_API_Interface:
        return self._MediamtxAPI

    @property   
    def Ready(self) -> bool:
        return self._statuscode in (200, 201)
    
    @property
    def StatusMessage(self) -> str:
        return self._status_message

    @property
    def Camera_UID(self) -> str:
        return self._camera_UID
    @property
    def Statuscode(self) -> int:
        return self._statuscode
    @property
    def MediaMTXPathConfiguration(self) -> MediaMTX_Path_Config:
        return self._config
    
    def get_address(self, device: int | str = "camera") -> Link:
        """
        Return the address based on enum value or key.
        - device can be int (0, 1, 2) or str ("camera", "MediaMTX", "Takat").
        """
        if isinstance(device, str):
            device = self.Address_ENUM.get(device, 0)

        match device:
            case 0:
                return self._camera_address
            case 1:
                return self._mediamtx_address
            case 2:
                return self._takat_address
            case _:
                return self._camera_address
    
    
    def Add_Path(self) -> int:
        """Create the path on the MediaMTX server. Returns HTTP status code."""
        try:
            status = self._MediamtxAPI.add_path(self._config.to_dict())
            self._status_message = "MediaMTX server added path"
            self._statuscode = status
            return status
        except requests.exceptions.ConnectionError:
            self._status_message = "MediaMTX server unreachable"
            self._statuscode = 503
            return 503
        except Exception as e:
            self._status_message = f"MediaMTX server Unexpected error adding path: {e}"
            self._statuscode = 500
            return 500
    
    #change a single config value
    def Update_Path_Single_Value(self, Key: str, Value: str) -> int:
        """Update a single config value on the MediaMTX server."""
        try:
            # Update local config
            self._config.update_value(key=Key, value=Value)
            # Call API
            status = self._MediamtxAPI.patch_path(self._config.to_dict())
            # set status codes
            self._status_message = f"MediaMTX path patched: {Key}={Value}"
            self._statuscode = status
            return status

        except requests.exceptions.ConnectionError:
            self._status_message = "MediaMTX server unreachable during single-value update"
            self._statuscode = 503
            return 503

        except Exception as e:
            self._status_message = f"Unexpected error patching single value: {e}"
            self._statuscode = 500
            return 500
        
        
    # change a number of config values
    def Update_Path_List_Values(self, updates: dict[str, str]) -> int:
        """
        Update multiple key/value pairs in the config and patch once.
        Example: 
                obj.Update_Path_List_Values({"timeout": "5000", "uid": "newUID"})
        """
        try:
            # Apply all updates locally
            for key, value in updates.items():
                self._config.update_value(key=key, value=value)
            
            # Call API once with full config
            status = self._MediamtxAPI.patch_path(self._config.to_dict())
            
            self._status_message = f"MediaMTX path patched with {len(updates)} values"
            self._statuscode = status
            return status
        except requests.exceptions.ConnectionError:
            self._status_message = "MediaMTX server unreachable during multi-value update"
            self._statuscode = 503
            return 503
        except Exception as e:
            self._status_message = f"Unexpected error patching multiple values: {e}"
            self._statuscode = 500
        return 500
        
        
    #remove the path.
    def Remove_Path(self) -> int:
        """Delete the path on the MediaMTX server."""
        try:
            status = self.MediamtxAPI.delete_path()
            self._status_message = "MediaMTX server path deleted"
            self._statuscode = status
            return status
        except requests.exceptions.ConnectionError:
            self._status_message = "MediaMTX server unreachable during delete"
            self._statuscode = 503
            return 503
        except Exception as e:
            self._status_message = f"Unexpected error deleting path: {e}"
            self._statuscode = 500
            return 500
       
     
    def Change_OTP(self, new_otp: str) -> int:
        """Change the OTP for the camera."""
        try: 
            self._otp = new_otp
            #update ffmpeg command builder
            self._ffmpeg_command.ChangeMetaData(otp=new_otp)
            self._status_message = "OTP changed."
            self._statuscode = 200
            return 200  # status code of ok
        except Exception as e:
            self._statuscode = 500
            self._status_message = f"Error changing OTP: {e}"
            return 500  # status code of internal server error
        
    def Alive(self) -> bool:
        """Check if the MediaMTX server is alive and reachable."""
        try:
            alive = self.MediamtxAPI.is_alive()
            self._status_message = "MediaMTX server status checked"
            self._statuscode = 200 if alive else 503
            return alive
        except Exception as e:
            self._status_message = f"Error checking server status: {e}"
            self._statuscode = 503
            return False

    def to_dict(self) -> dict:
        """
        Returns a dictionary representation of the camera object,
        including nested objects.
        """
        return {
            "Camera_UID": self.Camera_UID,
            "OTP": self.OTP,
            "StreamingPort": self._streamingport,
            "InputType": self._input_type,
            "StatusCode": self.Statuscode,
            
            # Addresses (converted to dict if possible)
            "CameraAddress": self._camera_address.to_dict() if hasattr(self._camera_address, "to_dict") else str(self._camera_address),
            "MediamtxAddress": self._mediamtx_address.to_dict() if hasattr(self._mediamtx_address, "to_dict") else str(self._mediamtx_address),
            "TakatAddress": self._takat_address.to_dict() if hasattr(self._takat_address, "to_dict") else str(self._takat_address),

            # Config
            "MediaMTXPathConfiguration": self._config.to_dict() if hasattr(self._config, "to_dict") else str(self._config),
            
            # FFmpeg command builder
            "FFMPEG_RunOnReady": self.FFMPEG_RunOnReady,
            "FFMPEG_CommandBuilder": self._ffmpeg_command.__dict__,  # or a to_dict if implemented

            # Mediamtx / Takat APIs
            "MediamtxAPI": str(self._MediamtxAPI),
            "TakatVideoAPI": str(self._TakatVideoAPi)
        }



# ─────────────────────────────────────────────────────────────────────────────
# Video object that glues everything together
# ─────────────────────────────────────────────────────────────────────────────
class Video_Object:
    """
    Holds all metadata for a single camera / virtual feed pair and
    embeds a MediaMTX_API_Interface to manage paths on the fly.
    """

    
    def __init__(self, uid: str, source_camera: Link, mediamtx_server: Link, takat_server: Link, streaming_port: int, camera_config: MediaMTX_Path_Config,
                 virtual_camera_uid: Optional[str] = None,source_camera_uid: Optional[str] = None, linked_device: Optional[str] = None, 
                 processing_type: Optional[int] = 0):

        # keep track of the status of the video object
        self._statuscode = 503
        self._status_message = f"Object {uid}: Not initialized"
        
        
        #note the addresses, the streaming port, and the type (is it a regular cam, a networked mp4 a local one etc etc, check the ffmpeg class enum for more info)
        self._streamingport = streaming_port
        self._processing_type = processing_type
        #the links
        self._source_camera_address = source_camera
        self._mediamtx_server_address = mediamtx_server
        self._takat_server_address = takat_server
        #do we have a linked device?
        if linked_device == None:
            self._linked_device = "None"
        else: self._linked_device = linked_device
        # main camera config
        self._main_Config = camera_config
        
        
        #credentials list
        # Unique identifiers (we use the source camera as a base)
        self._credentials = SessionCredentials(uid=uid)    #create a new set of credentials
        self._uid = self._credentials.find_uid_by_name("primary_key")
        self._otp = self._credentials.otp
        
        #set the camera uid and add it to the credentials list
        if source_camera_uid == None:
            self._credentials.add_uid(self._credentials.random_uid(), "source_camera")
        else: self._credentials.add_uid(source_camera_uid, "source_camera")
        
        # set the virtual camera and add it to the credentials list.
        if virtual_camera_uid == None:
            self._credentials.add_uid(self._credentials.random_uid(), "virtual_camera")
            #update the linked device to be the virtual camera (if it was none)
            if self._linked_device == "None":
                self._linked_device = self._credentials.find_uid_by_name("virtual_camera")[0]
        else: self._credentials.add_uid(virtual_camera_uid, "virtual_camera")
        
        
        #create the source camera (object)
        scuid= self._credentials.find_uid_by_name("source_camera")[0]
        self.Source_Camera = Camera_Object(Camera_UID=scuid, OTP=self._credentials.otp,
                                           config=self._main_Config,
                                           Camera_Address=self._source_camera_address,
                                           Mediamtx_Server=self._mediamtx_server_address,
                                           Takat_Server=self._takat_server_address,
                                           StreamingPort=self._streamingport)
        
        #make changes to the source camera config to set the  correct hooks
        self.Source_Camera.Update_Path_Single_Value("RunOnReady", self.Source_Camera.FFMPEG_RunOnReady) #add the ffmpeg run on ready command
        #TODO create the runonnotread command
        self.Source_Camera.Update_Path_Single_Value("RunOnNotReady", "takat api, unregister camera and remove path") #add the ffmpeg run on ready command
        
        #create the virtual camera (object)
        vcuid= self._credentials.find_uid_by_name("virtual_camera")[0]
        #create virtual camera address
        self._virtual_camera_address = Link(host=self._mediamtx_server_address.Host, protocol="rtsp",
                                            port=self._streamingport, path=f"{vcuid}/stream" , allowed_protocols=self._mediamtx_server_address.ALLOWED_PROTOCOLS
                                            )
        self.Virtual_Camera = Camera_Object(Camera_UID=vcuid, OTP=self._credentials.otp,
                                           config=self._main_Config,
                                           Camera_Address=self._virtual_camera_address,
                                           Mediamtx_Server=self._mediamtx_server_address,
                                           Takat_Server=self._takat_server_address,
                                           StreamingPort=self._streamingport)
        # make changes to the virtual camera to set the corect hooks AND input
       
        #TODO create the rononready command
        self.Virtual_Camera.Update_Path_Single_Value("RunOnReady", "takat api start injection") #add the ffmpeg run on ready command
        #TODO create the runonnotready
        self.Virtual_Camera.Update_Path_Single_Value("RunOnNotReady", "takat api, stop injection and remove path") #add the ffmpeg run on ready command
        
        #set the source for this camera to http://127.0.0.1/virtualcamera_uid/stream, this allows us to duplicate the stream
        # and let the server handle the many clients on the virtual stream
        self.Virtual_Camera.Update_Path_Single_Value("source", f"{self._virtual_camera_address.Protocol}://127.0.0.1:{self._virtual_camera_address.Port}/{vcuid}/stream")
        
        
        
        #TODO
        # try catch to check if all paths are there.
        
    @property
    def UID(self) -> str:
        return self._uid[0]
    @property
    def OTP(self) -> str:
        return self._otp
    
    # Read-only properties for status
    @property
    def CheckCamerasStatus(self) -> int:
        """
        Check if both Source_Camera and Virtual_Camera are ready.
        Sets self._status based on the camera objects' status codes.
        Returns the overall status code.
        """
        source_status = self.Source_Camera.Statuscode
        virtual_status = self.Virtual_Camera.Statuscode

        # Both cameras OK
        if source_status in (200, 201) and virtual_status in (200, 201):
            self._status = 200
            self._status_message = "Both cameras are ready."
        else:
            self._status = 500
            messages = []
            if source_status not in (200, 201):
                messages.append(f"Source camera error ({source_status}): {self.Source_Camera.StatusMessage}")
            if virtual_status not in (200, 201):
                messages.append(f"Virtual camera error ({virtual_status}): {self.Virtual_Camera.StatusMessage}")
            self._status_message = "; ".join(messages)

        return self._status

    # Remove both paths
    def RemoveAllPaths(self) -> int:
        """
        Remove both the source and virtual camera paths on the MediaMTX server.
        Updates self._status and self._status_message.
        Returns the combined status code:
            - 200 if both paths removed successfully
            - 500 if one or both failed
        """
        source_status = self.Source_Camera.Remove_Path()
        virtual_status = self.Virtual_Camera.Remove_Path()

        if source_status == 200 and virtual_status == 200:
            self._status = 200
            self._status_message = "Both camera paths removed successfully."
        else:
            self._status = 500
            messages = []
            if source_status != 200:
                messages.append(f"Source camera removal failed ({source_status}): {self.Source_Camera.StatusMessage}")
            if virtual_status != 200:
                messages.append(f"Virtual camera removal failed ({virtual_status}): {self.Virtual_Camera.StatusMessage}")
            self._status_message = "; ".join(messages)

        return self._status

    def ValidCredentials(self, otp:str, uid: str) -> bool:
        if self._credentials.valid(otp=otp, uid=uid) == True: return True
        else: return False 
    
    def to_dict(self) -> dict:
        """
        Returns all relevant settings of this Video_Object as a dictionary,
        including nested objects.
        """
        return {
            "UID": self.UID,
            "OTP": self.OTP,
            "StreamingPort": self._streamingport,
            "ProcessingType": self._processing_type,
            "LinkedDevice": self._linked_device,
            "SourceCameraAddress": self._source_camera_address.to_dict() if hasattr(self._source_camera_address, "to_dict") else str(self._source_camera_address),
            "MediamtxServerAddress": self._mediamtx_server_address.to_dict() if hasattr(self._mediamtx_server_address, "to_dict") else str(self._mediamtx_server_address),
            "TakatServerAddress": self._takat_server_address.to_dict() if hasattr(self._takat_server_address, "to_dict") else str(self._takat_server_address),
            "Credentials": {
                "primary_uid": self._credentials.primary_uid,
                "uids": self._credentials.uids,
                "otp": self._credentials.otp
            },
            "SourceCamera": self.Source_Camera.to_dict() if hasattr(self.Source_Camera, "to_dict") else str(self.Source_Camera),
            "VirtualCamera": self.Virtual_Camera.to_dict() if hasattr(self.Virtual_Camera, "to_dict") else str(self.Virtual_Camera),
            "VirtualCameraAddress": self._virtual_camera_address.to_dict() if hasattr(self._virtual_camera_address, "to_dict") else str(self._virtual_camera_address)
        }
        