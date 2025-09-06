import json
import random
import string
from typing import Optional, Dict, Any
from flask import jsonify

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
from opentakserver.blueprints.TakatVideo_api.util import OTP as SessionCredentials

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
        retries = Retry(total=3, backoff_factor=0.3, status_forcelist=[502, 503, 504])
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
        "disconnect": "TakatVideo/StopInjection"
        # Add more endpoints here in the future
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
    def __init__(self, UID: str, Linked_Device: str, OTP: str, timeout: int = 5000000):
        self.UID = UID
        self.Linked_Device = Linked_Device
        self.OTP = OTP
        self.timeout = timeout
        self.metadata_template = f'-metadata uid="{self.UID}" -metadata linked_device="{self.Linked_Device}" -metadata otp="{self.OTP}"'

    # Enum-style type handling
    def _enum(self, input_type: int) -> int:
        camera = 0
        networked_mp4 = 1
        local_mp4 = 2
        yolo = 3
        
        if input_type not in (camera, networked_mp4, local_mp4, yolo):
            return camera
        return input_type

    @property
    def Enum(self) -> dict:
        return {
            "camera": 0,
            "networked_mp4": 1,
            "local_mp4": 2,
            "yolo": 3
        }
    def ChangeTimeout(self, timeout: int =0, uid: str = "", otp:str = "") -> None:  #change timeout, uid, otp
        if timeout > 0:
            self.timeout = timeout
        if uid != "":
            self.UID = uid
        if otp != "":
            self.OTP = otp
        self.metadata_template = f'-metadata uid="{self.UID}" -metadata linked_device="{self.Linked_Device}" -metadata otp="{self.OTP}"'       
        
    
    def RunOnReady(self, type_int: int, Source: Link, MediaMTX_Streaming_Port: int) -> str:
        return self._ingest(type_int, Source, MediaMTX_Streaming_Port)

    # Unified ingest function
    def _ingest(self, type_int: int, Source: Link, MediaMTX_Streaming_Port: int) -> str:
        type_int = self._enum(type_int)  # sanitize input

        # Determine input path based on type
        if type_int == 0:  # camera
            input_path = Source.Hyperlink
        elif type_int == 1:  # networked mp4
            input_path = f"{Source.Root}{Source.URL}"
        elif type_int == 2:  # local mp4
            input_path = Source.URL
        elif type_int == 3:  # YOLO / future type
            return "echo 'YOLO ingestion not yet implemented'"
        else:
            return "echo 'Unsupported type'"

        command = (
            f'ffmpeg -timeout {self.timeout} '
            f'-re -stream_loop -1 -i "{input_path}" '
            f'-c copy {self.metadata_template} '
            f'-f rtsp "rtsp://127.0.0.1:{MediaMTX_Streaming_Port}/{self.UID}/stream"'
        )
        return command
# ─────────────────────────────────────────────────────────────────────────────
# Single Camera object
# ─────────────────────────────────────────────────────────────────────────────      
class Camera_Object():
    def __init__(self, Camera_UID: str, OTP: str, config: MediaMTX_Path_Config, Camera_Address: Link, Mediamtx_Server: Link, Takat_Server: Link):
        
        self._ready = False
        self._statuscode = 0
        self._otp = OTP
        
        self._camera_UID = Camera_UID
        self._config = config
        self._address = Camera_Address
        self._MediamtxAPI = MediaMTX_API_Interface(managed_path=Camera_UID, link=Mediamtx_Server, verify_ssl=False, jwt_token=None)
        
        self.TakatVideoAPi = TakatVideo_API_Interface(fqdn=Takat_Server.Host, port=Takat_Server.Port, protocol=Takat_Server.Protocol)

        # Initial setup
        status = self.Add_Path()
        if status != 200:
            print(f"Failed to initialize camera {Camera_UID}. Status code: {status}")
            self._ready = False
        else:
            print(f"Camera {Camera_UID} initialized successfully.")
            self._ready = True
            
    @property
    def OTP(self) -> str:
        return self._otp        
    @property
    def MediamtxAPI(self) -> MediaMTX_API_Interface:
        return self._MediamtxAPI
    @property
    def Address(self) -> Link:
        return self._address
    @property   
    def Ready(self) -> bool:
        return self._ready
    @property
    def Camera_UID(self) -> str:
        return self._camera_UID
    @property
    def Statuscode(self) -> int:
        return self._statuscode
    
    def Add_Path(self) -> int:
        """Create the path on the MediaMTX server. Returns HTTP status code."""
        try:
            self._ready = True  # Mark as ready before attempting setup
            return self._MediamtxAPI.add_path(self._config.to_dict())
        except Exception as e:
            print(f"Error adding path: {e}")
            return 0

    def Remove_Path(self) -> int:
        """Delete the path on the MediaMTX server."""
        try:
            self._ready = False  # Mark as not ready before deletion
            return self.MediamtxAPI.delete_path()
        except Exception as e:
            print(f"Error deleting path: {e}")
            return 0

    def Alive(self) -> bool:
        """Check if the MediaMTX server is alive and reachable."""
        try:
            return self.MediamtxAPI.is_alive()
        except Exception as e:
            self._ready = False # Mark as not ready if an error occurs
            print(f"Error checking server status: {e}")
            return False


# ─────────────────────────────────────────────────────────────────────────────
# Video object that glues everything together
# ─────────────────────────────────────────────────────────────────────────────
class Video_Object:
    """
    Holds all metadata for a single camera / virtual feed pair and
    embeds a MediaMTX_API_Interface to manage paths on the fly.
    """

    
    def __init__(self, source_camera: Camera_Object, mediamtx_server: Link, takat_server: Link, linked_device: Optional[str] = None):

        # Unique identifiers (we use the source camera as a base)
        self._credentials = SessionCredentials()    #create a new set of credentials
        self._uid = self._credentials.find_uid_by_name("primary_key")
        self._otp = self._credentials.otp
        
        self._credentials.add_uid(source_camera.Camera_UID, "source_camera")
        _random_uid = self._credentials.random_uid()
        self._credentials.add_uid(_random_uid, name="virtual_camera")

        if linked_device is None:
            try:
                self._virtual_camera_uid = self._credentials.random_uid()
                self._credentials.add_uid(self._virtual_camera_uid, "virtual_camera")
            except Exception as e:
                print(f"Error generating random UID: {e}")
        else:
            self._credentials.add_uid(linked_device, "virtual_camera")
                 
        self._source_camera_uid = self._credentials.find_uid_by_name("source_camera")
        self._virtual_camera_uid = self._credentials.find_uid_by_name("virtual_camera")
        

        self._statuscode = (0, "not initialized")  # (code, message) tuple[int, str]:
        # build the objects we need
        #self, UID: str, Linked_Device: str, OTP: str, timeout: int = 5000000):
        self._FFMPEG = FFMPEG_Command_Builder(source_camera.Camera_UID, "12" , self._otp, timeout=5000000)
        self._takat_server_api = TakatVideo_API_Interface(takat_server.Host, takat_server.Port, takat_server.Protocol)
        self._mediamtx_server_api = MediaMTX_API_Interface(managed_path=source_camera.Camera_UID, link=mediamtx_server, verify_ssl=False, jwt_token=None)
        
        #create the camera's
        
        self._source_camera = None # Placeholder for source camera object
        self.Virtual_Camera = None  # Placeholder for virtual camera object
        
        # create the source camera path on the mediamtx server
        

        
        #
     
    @property
    def uid(self) -> str:
        return self._uid[0]
    
    @property
    def statuscode(self) -> tuple[int, str]:
        return self._statuscode
    @property
    def uids(self) -> list[tuple[str, str]]:
        return self._credentials.uids
    @property
    def primary_uid(self) -> str:
        # find the uid whose name is "primary_uid"
        return next((uid for uid, name in self._credentials.uids if name == "primary_uid"), "")
    @property
    def source_camera__uid(self) -> str:
        # find the uid whose name is "source_camera"
        return next((uid for uid, name in self._credentials.uids if name == "source_camera"), "")
    @property
    def virtual_camera_uid(self) -> str:
        # find the uid whose name is "virtul_camera"
        return next((uid for uid, name in self._credentials.uids if name == "virtual_camera"), "")
    
    @property
    def OTP(self) -> str:
        return self._otp
    
    def _create_source_camera(self, Source_Camera: Camera_Object, Mediamtx_Server: Link, Takat_Server: Link,
                              Camera_Config: MediaMTX_Path_Config, type: int) -> tuple:
        
        output = (0,"unknown error creating source camera")
        # is the mediamtx server alive?
        try:
            alive = self._mediamtx_server_api.alive
            if not alive:   
                output = (0, "mediamtx server is not reachable")    #yes
                self._statuscode = output
            if alive:       
                output = (200, "mediamtx server is reachable")      #no
                self._statuscode = output
        except Exception as e:
            output = (0, f"error checking mediamtx server status: {e}")         #error
            self._statuscode = output
            return output
            
        # Create a source camera object based on the source camera details
        try:
            source_camera = Camera_Object(Camera_UID=Source_Camera.Camera_UID,
                                         OTP=Source_Camera.OTP,
                                         config=Camera_Config,
                                         Camera_Address=Source_Camera.Address,
                                         Mediamtx_Server=Mediamtx_Server,
                                         Takat_Server=Takat_Server)
            self._source_camera = source_camera
            output = (200, "source camera object created successfully")
            self._statuscode = output
        except Exception as e:
            output = (0, f"error creating source camera object: {e}")
            self._statuscode = output
            return output
        
        # create the path on the mediamtx server
        try:
            code = source_camera.Add_Path()
            if code == 200:
                output = (200, "source camera path created successfully")
                self._statuscode = output
            else:
                output = (code, f"error creating source camera path: status code {code}")
                self._statuscode = output
        except Exception as e:
            output = (0, f"error creating source camera path: {e}")
            return output
        
        # runonread/runonnotready commands to trigger ffmpeg to ingest the feed or to have takat api  "callback" to camera for new connection
        #
        try:
     
            output = (200, "source camera runOnReady and runOnNotReady commands set successfully")
            self._statuscode = output
        except Exception as e:
            output = (0, f"error setting source camera runOnReady and runOnNotReady commands: {e}")
            self._statuscode = output
            return output
    
        
        
        
        self._statuscode = output
        return output
        pass    
    
    
    def _create_vritual_camera(self):
        # Create a virtual camera object based on the source camera

        # create blank object
        #        virtual_camera uid = linked uid (or generate random one)
        #        add uid to the session credentials
        #        set the camera otp to that of the session credentials
        
        # create the config for the virtual camera based on the source camera config
        #        change config source to 127.0.0.1/source_camera_uid/stream (to copy the stream from the source camera)
        #        change config name to linked uid
        #        change config RunOnReady takat api start injection command
        #        change config RunOnUnReady takat api stop injection command
        
        # create paths on mediamtx for the virtual camera
        
        
        pass
        
    
    def _setup(self):
        
        pass
    

    pass
