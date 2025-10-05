import json
import random
import string
import os
from typing import Optional, Dict, Any
from enum import Enum
from flask import jsonify
from enum import IntEnum

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urlencode
import logging


# ─────────────────────────────────────────────────────────────────────────────
# Third‑party / project imports
# ────────────────────────────────────────────────────────────────────────────
from opentakserver.defaultconfig import DefaultConfig  # central config
from opentakserver.blueprints.TakatVideo_api.Mitm import (
    _start_injection,
    _stop_injection,
)

from opentakserver.blueprints.TakatVideo_api.util import Safe_Link as Link
from opentakserver.blueprints.TakatVideo_api.util import Resolutions
from opentakserver.blueprints.TakatVideo_api.util import HttpCode as HTTPStatusCodes
from opentakserver.blueprints.TakatVideo_api.util import OTP_UID_Manager as SessionCredentials

# If you need sanitising helpers, import them here as well:
# from opentakserver.blueprints.TakatVideo_api.util import Util_Sanitize


# ─────────────────────────────────────────────────────────────────────────────
# MediaMTX API helper
# ─────────────────────────────────────────────────────────────────────────────

class MediaMTX_API_Interface_v3:
    """
    Wrapper for MediaMTX Control-API (v3) using a Safe_Link for host/protocol/port.

    • Operates on a fixed MediaMTX path provided at init
    • Supports optional JWT token
    """

    def __init__(
        self,
        *,
        uid: str,         # renamed from 'name'
        link: Link,           # Safe_Link object for host/protocol/port
        jwt_token: Optional[str] = None,
        verify_ssl: bool = False
    ) -> None:

        if not uid:
            raise ValueError("The 'managed_path' parameter is required and cannot be empty.")
        if not link:
            raise ValueError("A Safe_Link object must be provided.")

        self._managed_path = uid
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
        """_summary_

        Args:
            config (Dict[str, Any]): _description_

        Returns:
            int: _description_
        """
        return self._call("POST", f"/v3/config/paths/add/{self._managed_path}", json=config)

    def patch_path(self, changes: Dict[str, Any]) -> int:
        """_summary_

        Args:
            changes (Dict[str, Any]): _description_

        Returns:
            int: _description_
            
        Example:
            # Define the changes you want to apply
                changes = {
                    "source": "rtsp://192.168.0.50:554/live",
                    "loop": True,
                    "name": "Camera Stream Updated"
                }

                # Send the patch request
                status = mtx.patch_path(changes)
        """
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
class MediaMTX_Path_Config_v3:
    """
    Holds the configuration for a MediaMTX path.
    This is a simplified version of the MediaMTX API path configuration.
    """

    def __init__(self, name: str, source: str, **kwargs) -> None:
        # Initialize all attributes with defaults
        self.name = name
        self.source = source
        
        # Set defaults for all other attributes
        defaults = {
            "sourceFingerprint": "",
            "sourceOnDemand": False,
            "sourceOnDemandCloseAfter": "",
            "maxReaders": 0,
            "srtReadPassphrase": "",
            "fallback": "",
            "useAbsoluteTimestamp": False,
            "record": False,
            "recordPath": "",
            "recordFormat": "",
            "recordPartDuration": "",
            "recordMaxPartSize": "",
            "recordSegmentDuration": "",
            "recordDeleteAfter": "",
            "overridePublisher": False,
            "srtPublishPassphrase": "",
            "rtspTransport": "",
            "rtspAnyPort": False,
            "rtspRangeType": "",
            "rtspRangeStart": "",
            "rtspUDPReadBufferSize": 0,
            "mpegtsUDPReadBufferSize": 0,
            "rtpSDP": "",
            "rtpUDPReadBufferSize": 0,
            "sourceRedirect": "",
            "rpiCameraCamID": 0,
            "rpiCameraSecondary": False,
            "rpiCameraWidth": 0,
            "rpiCameraHeight": 0,
            "rpiCameraHFlip": False,
            "rpiCameraVFlip": False,
            "rpiCameraBrightness": 0,
            "rpiCameraContrast": 0,
            "rpiCameraSaturation": 0,
            "rpiCameraSharpness": 0,
            "rpiCameraExposure": "",
            "rpiCameraAWB": "",
            "rpiCameraAWBGains": None,
            "rpiCameraDenoise": "",
            "rpiCameraShutter": 0,
            "rpiCameraMetering": "",
            "rpiCameraGain": 0,
            "rpiCameraEV": 0,
            "rpiCameraROI": "",
            "rpiCameraHDR": False,
            "rpiCameraTuningFile": "",
            "rpiCameraMode": "",
            "rpiCameraFPS": 0,
            "rpiCameraAfMode": "",
            "rpiCameraAfRange": "",
            "rpiCameraAfSpeed": "",
            "rpiCameraLensPosition": 0,
            "rpiCameraAfWindow": "",
            "rpiCameraFlickerPeriod": 0,
            "rpiCameraTextOverlayEnable": False,
            "rpiCameraTextOverlay": "",
            "rpiCameraCodec": "",
            "rpiCameraIDRPeriod": 0,
            "rpiCameraBitrate": 0,
            "rpiCameraHardwareH264Profile": "",
            "rpiCameraHardwareH264Level": "",
            "rpiCameraSoftwareH264Profile": "",
            "rpiCameraSoftwareH264Level": "",
            "rpiCameraMJPEGQuality": 0,
            "runOnInit": "",
            "runOnInitRestart": False,
            "runOnDemand": "",
            "runOnDemandRestart": False,
            "runOnDemandStartTimeout": "",
            "runOnDemandCloseAfter": "",
            "runOnUnDemand": "",
            "runOnReady": "",
            "runOnReadyRestart": False,
            "runOnNotReady": "",
            "runOnRead": "",
            "runOnReadRestart": False,
            "runOnUnread": "",
            "runOnRecordSegmentCreate": "",
            "runOnRecordSegmentComplete": ""
        }

        # Update defaults with any provided values
        defaults.update(kwargs)

        # Assign them all to self
        for k, v in defaults.items():
            setattr(self, k, v)

    def to_dict(self) -> dict:
        """Return all attributes as a dictionary."""
        return self.__dict__.copy()

    def to_json(self, indent: int = 2) -> str:
        """Return all attributes as a JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def load_from_dict(self, data: dict) -> None:
        """Load values from a dictionary into this config."""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                print(f"Warning: '{key}' is not a valid attribute, skipping.")

    def load_from_json(self, json_str: str) -> None:
        data = json.loads(json_str)
        self.load_from_dict(data)

    @classmethod
    def from_dict(cls, data: dict) -> "MediaMTX_Path_Config_v3":
        """
        Create a new instance from a dictionary.
        Ignores unknown keys.
        """
        # Extract known parameters
        valid_keys = cls.__init__.__code__.co_varnames
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)
  

# ─────────────────────────────────────────────────────────────────────────────
# TakatVideo API helper (v3)
# ─────────────────────────────────────────────────────────────────────────────

class TakatVideo_API_Interface_v3:
    """
    Wrapper for the TakatVideo API using a Safe_Link for host/protocol/port.

    • Operates on a fixed uid provided at init
    • Supports optional JWT token
    • Provides Start/Stop/Disconnect injection operations
    """

    class Endpoint(str, Enum):
        START_INJECTION = "TakatVideo/StartInjection"   # all endpoints have an otp and uid input
        STOP_INJECTION = "TakatVideo/StopInjection"
        DISCONNECT = "TakatVideo/Disconnect"
        ADD_CAMERA = "TakatVideo/AddCamera"
        REMOVE_CAMERA ="TakatVideo/RemoveCamera"
        REGISTER = "TakatVideo/Register"
        UNREGISTER = "TakatVideo/Unregister"
        

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
        endpoint: "TakatVideo_API_Interface_v3.Endpoint",
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
        return self._call(self.Endpoint.START_INJECTION, otp=otp)

    def start_injection_url(self, otp: Optional[str] = None) -> str:
        """Return the URL for starting injection, including uid and otp."""
        return self.build_url(self.Endpoint.START_INJECTION, otp=otp)

    def stop_injection(self, otp: str) -> int:
        """Stop injection for this uid using the given OTP."""
        return self._call(self.Endpoint.STOP_INJECTION, otp=otp)

    def stop_injection_url(self, otp: Optional[str] = None) -> str:
        """Return the URL for stopping injection, including uid and otp."""
        return self.build_url(self.Endpoint.STOP_INJECTION, otp=otp)

    def disconnect(self, otp: str) -> int:
        """Disconnect this uid using the given OTP."""
        return self._call(self.Endpoint.DISCONNECT, otp=otp)

    def disconnect_url(self, otp: Optional[str] = None) -> str:
        """Return the URL for disconnecting, including uid and otp."""
        return self.build_url(self.Endpoint.DISCONNECT, otp=otp)

    def add_camera(self, otp: str) -> int:
        """Add a camera for this uid using the given OTP."""
        return self._call(self.Endpoint.ADD_CAMERA, otp=otp)

    def add_camera_url(self, otp: Optional[str] = None) -> str:
        """Return the URL for adding a camera, including uid and otp."""
        return self.build_url(self.Endpoint.ADD_CAMERA, otp=otp)

    def remove_camera(self, otp: str) -> int:
        """Remove a camera for this uid using the given OTP."""
        return self._call(self.Endpoint.REMOVE_CAMERA, otp=otp)

    def remove_camera_url(self, otp: Optional[str] = None) -> str:
        """Return the URL for removing a camera, including uid and otp."""
        return self.build_url(self.Endpoint.REMOVE_CAMERA, otp=otp)

    def register(self, otp: str) -> int:
        """Register this uid using the given OTP."""
        return self._call(self.Endpoint.REGISTER, otp=otp)

    def register_url(self, otp: Optional[str] = None) -> str:
        """Return the URL for registering, including uid and otp."""
        return self.build_url(self.Endpoint.REGISTER, otp=otp)

    def unregister(self, otp: str) -> int:
        """Unregister this uid using the given OTP."""
        return self._call(self.Endpoint.UNREGISTER, otp=otp)

    def unregister_url(self, otp: Optional[str] = None) -> str:
        """Return the URL for unregistering, including uid and otp."""
        return self.build_url(self.Endpoint.UNREGISTER, otp=otp)

    # ------------------------
    # State / Info
    # ------------------------
    def is_alive(self) -> bool:
        """Simple health check: try disconnect without OTP."""
        status = self._call(self.Endpoint.DISCONNECT)
        return bool(status and 200 <= status < 300)
    
    def build_url(
        self,
        endpoint: "TakatVideo_API_Interface_v3.Endpoint",
        *,
        otp: Optional[str] = None,
    ) -> str:
        """
        Return the full request URL for the given endpoint.
        Always includes uid, and otp/jwt if provided.
        """
        if not isinstance(endpoint, self.Endpoint):
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
  

class FFMPEG_Command_Builder_v3:
    """
    FFMPEG command builder for different ingest types, initialized like TakatVideo_API_Interface_v3.
    """

    class IngestType(IntEnum):
        Default = 0         #change this value to match one of the other settings so we can easily change the default behaviour
        Unknown = -1
        CAMERA = 0
        NETWORKED_MP4 = 1
        LOCAL_MP4 = 2
        #Yolo = 3

    class Protocol(str, Enum):
            # Standard FFmpeg streaming protocols
            DEFAULT = "rtsp" # a nice way to make the default easily changable
            
            RTSP = "rtsp"
            RTMP = "rtmp"
            SRT = "srt"
            HLS = "hls"
            #MPEGTS = "mpegts"        # Transport Stream over UDP
            HTTP = "http"
            HTTPS = "https"
            MMS = "mms"

            # ATAK-compatible / common tactical streaming protocols
            #UDP = "udp"
            #TCP = "tcp"
            #FILE = "file"            # Local file output
            #MPEGTS_UDP = "mpegts+udp"
            #MPEGTS_TCP = "mpegts+tcp"

    def __init__(
        self,
        *,
        camera_uid: str,
        linked_uid: str,
        mediamtx_streaming_port: int = 8554,
        link: Link,  # Safe_Link or equivalent for destination
    ):


        self._camera_uid = camera_uid
        self._linked_device = linked_uid
        self._link = link
        self._validate_protocol(self._link.Protocol)
        self._streaming_port = mediamtx_streaming_port
 
        self._metadata = f"-metadata uid='{self._camera_uid}' -metadata linked_device='{self._linked_device}'"
    
    ## helper function
    def _validate_protocol(self, protocol) -> None:
        """
        Raise ValueError if protocol is not in the allowed FFMPEG_Command_Builder_v3.Protocol enum.
        Accepts any enum with a `.value` matching the allowed protocol strings.
        """
        # get list of allowed values
        allowed = [p.value for p in self.Protocol]

        # convert protocol to string if it’s an Enum
        proto_value = protocol.value if isinstance(protocol, Enum) else str(protocol)

        if proto_value not in allowed:
            raise ValueError(
                f"Invalid protocol: {proto_value}. Must be one of {allowed}"
            )

    def run_on_innit(
        self,
        ingest_type: 'FFMPEG_Command_Builder_v3.IngestType' = IngestType.Unknown,
        output_protocol: 'FFMPEG_Command_Builder_v3.Protocol' = Protocol.DEFAULT,
        timeout: int = 5000000,
        loop: bool = True
    ) -> str:
        match ingest_type: 
            case FFMPEG_Command_Builder_v3.IngestType.CAMERA:
                #NOTE  we expect the link to be something like this: "rtsp://192.168.0.50:554/live"
                return self._ffmpeg_esp32cam(timeout=timeout, encoding=output_protocol)
            case FFMPEG_Command_Builder_v3.IngestType.NETWORKED_MP4:
                #NOTE we expect the link to be set up to something like this: "https://example.com/video.mp4"
                return self._ingest_networked_mp4(loop=loop, encoding=output_protocol)
                
            case FFMPEG_Command_Builder_v3.IngestType.LOCAL_MP4:
                # NOTE we expect the payload of the link to point to a local linux file path like:  /home/clips/nevergonnagiveyouup.mp4
                # NOTE the port also has to be set to the streaming port of the mediamtx server
                return self._ingest_local_mp4(loop=loop, encoding=output_protocol)
            
            case _ :
                return ""
              
    def _ffmpeg_esp32cam(self, timeout: int = 50000, encoding: 'FFMPEG_Command_Builder_v3.Protocol' = Protocol.RTSP ) -> str:
        """Ingest a live RTSP camera feed.
        Eaxmple output: ffmpeg -timeout 5000000 -i "rtsp://192.168.0.50:554/live" -c copy -metadata uid="stream123" -metadata linked_device="cam01" -f rtsp "rtsp://127.0.0.1:9000/stream123/stream"

        """
        Port = ""
        if self._streaming_port != None: Port = f":{self._streaming_port}"
        
        output = f"ffmpeg -timeout {timeout} -i '{self._link.Hyperlink} -c copy {self._metadata} -f {encoding.value} '{encoding.value}'://127.0.0.1{Port}/{self._camera_uid}/stream" 
        return output
     
    def _ingest_local_mp4(self,
                        encoding: "FFMPEG_Command_Builder_v3.Protocol" = Protocol.RTSP,
                        loop: bool = True) -> str:
        """_summary_

        Args:
            encoding (FFMPEG_Command_Builder.Protocol, optional): _description_. Defaults to Protocol.RTSP.
            loop (bool, optional): _description_. Defaults to True.
        Returns:
            str: _description_
        """
        
        l="0"
        if loop == True: l = "-1"
        Port = ""
        if self._streaming_port != None: Port = f":{self._streaming_port}"
        
        
        return f"ffmpeg -re -stream_loop {l} -i '{self._link.Payload}' -c copy {self._metadata} -f {encoding.value} '{encoding.value}'://127.0.0.1{Port}/{self._camera_uid}/stream"

    def _ingest_networked_mp4(self,
                            loop: bool = True,
                            encoding: "FFMPEG_Command_Builder_v3.Protocol" = Protocol.RTSP) -> str:
        """
        Ingest an MP4 file over the network (HTTP/HTTPS).

        Args:
            uid: Unique identifier for the stream.
            url: HTTP/HTTPS URL pointing to an MP4 file.
            linked_device: Device name to tag in metadata.
            otp: One-time password or key to tag in metadata.
            port: Destination port (default: 8554).
            protocol: Streaming protocol (default: RTSP).
            loop: Whether to loop the MP4 indefinitely (default: True).
            reencode: If True, re-encode to H.264/AAC (ensures compatibility).
                      
            example output:
            ffmpeg -re -stream_loop -1 -i "https://example.com/video.mp4" -c copy -metadata uid="stream123" -metadata linked_device="cam01" -metadata otp="secretOTP" 
            -f rtsp "rtsp://127.0.0.1:9000/stream123/stream"
            
            
        """
                
        l="0"
        if loop == True: l = "-1"
        Port = ""
        if self._streaming_port != None: Port = f":{self._streaming_port}"
        
        return f"ffmpeg -re -stream_loop {l} -i '{self._link.Hyperlink}' -c copy {self._metadata} -f {encoding.value} '{encoding.value}://127.0.0.1{Port}/{self._camera_uid}/stream'"

# ─────────────────────────────────────────────────────────────────────────────
# Single Camera object
# ───────────────────────────────────────────────────────────────────────────── 
class Camera_Object_V3():
    class CameraType(IntEnum):
        Default = 0 # Elegant way of making the default easily changable
        Unknown = -1
        Source = 0
        Virtual = 1
    
    
    def __init__(self, Config: MediaMTX_Path_Config_v3, Source_Camera_UID: str, Virtual_Camera_UID: str, API_mediamtx: Link, API_takat: Link, Stream_Mediamtx: Link, 
                 Stream_SourceCamera: Link, Stream_SourceCameraInputType: FFMPEG_Command_Builder_v3.IngestType = FFMPEG_Command_Builder_v3.IngestType.CAMERA,
                 Output_Protocol: FFMPEG_Command_Builder_v3.Protocol = FFMPEG_Command_Builder_v3.Protocol.RTSP, Timeout: Optional[int] = 5000000, Loop: Optional[bool] = True) -> None:
        
        # NOTE, we assume the user has made sure the uid's do not already exist.
        
        # uid's for this camera object, both a source and virtual camera
        self._source_camera_UID = Source_Camera_UID
        self._virtual_camera_UID = Virtual_Camera_UID
                
        # the (inet) path to the source camera (on the streamig mediamtx server, not directly back to the camera)
        self._source_camera_inet = f""
        # the (inet) path to the virtual camera
        self._virtual_camera_inet = f""
        
        # camera input type
        self._camera_type = Camera_Object_V3.CameraType.Source
        # config
        self._config = Config
        
        # object status code
        self._statuscode = HTTPStatusCodes.CONFLICT.code
        self._status_message = f"camera {self._source_camera_UID}: {HTTPStatusCodes.CONFLICT.status}, not initialized"
        
        # adresses
        self._api_mediamtx = API_mediamtx   # path to the mediamtx api, can be lan or inet
        self._api_takat = API_takat         # path to takat api,        can be lan or inet
        #source camera address
        self._stream_source_camera = Stream_SourceCamera    #path to source camera, can be la and inet; most likely inet tho
        self._stream_source_camera_inputtype = Stream_SourceCameraInputType # what type of camera is it? (stream, local mp4, networked mp4)
        self._stream_source_camera_output_protocol = Output_Protocol    # as what type of stream shoud we present it? (rtsp being the default)
        self._timeout = Timeout or 50000
        if Loop == None: Loop = False
        self._loop = Loop
        
        #streaming address
        self._stream_mediamtx = Stream_Mediamtx  # exteral path where clients can find mediamtx path's (in most cases inet)
        
        #ffmpeg commands for the source camera
        port = self._stream_mediamtx.Port or 8554 # try and set the prot
        self._ffmpeg = FFMPEG_Command_Builder_v3(camera_uid=self._source_camera_UID,
                                                 linked_uid= self._virtual_camera_UID, 
                                                 mediamtx_streaming_port=port, 
                                                 link=self._stream_source_camera)

        
        #api interfaces
        _interface_api_mediamtx_source = MediaMTX_API_Interface_v3  (uid=self._source_camera_UID, link=self._api_mediamtx, verify_ssl=False, jwt_token=None)
        _interface_api_mediamtx_virtual= MediaMTX_API_Interface_v3  (uid=self._virtual_camera_UID, link=self._api_mediamtx, verify_ssl=False, jwt_token=None)
        _interface_api_takat_source = TakatVideo_API_Interface_v3   (uid=self._source_camera_UID, link=self._api_takat   , verify_ssl=False, jwt_token=None)
        _interface_api_takat_virtual =TakatVideo_API_Interface_v3   (uid=self._virtual_camera_UID, link=self._api_takat   , verify_ssl=False, jwt_token=None)
        
        #try and create the path for the source and virtual camera
        try:
            #try to create the source camera path
            status = _interface_api_mediamtx_source.add_path(self._config.__dict__)
            #tweak the path config settings so that:
            # runoninit -> ffmpeg to ingest stream
            # runonnotready -> api call to takat to remove the camera from the register and remove the source and virtual cam path from mediamtx
            # sourceondemand = false
            
            runoninit = self._ffmpeg.run_on_innit(ingest_type=self._stream_source_camera_inputtype, output_protocol=self._stream_source_camera_output_protocol,
                                                  timeout=self._timeout, loop=self._loop)
            #TODO fix the takat video api endpoint call to remove the camera path, the virtual camera path and the video object.
            runonnotready = _interface_api_takat_source.disconnect
            
            patch = {"runOnInit": runoninit,
                     "runOnNotReady": runonnotready, 
                     "sourceOnDemand": False,
                     "name": self._source_camera_UID
                     }
            
            # patch the path            
            status_p = _interface_api_mediamtx_source.patch_path(patch)
            # update the source camera (inet) url.
            self._source_camera_inet = f"{self._stream_mediamtx.Root()}{self._source_camera_UID}/stream"
            
            # we have a good status and a status_p(atch), so the path is created
            if 200 <= status < 300 and 200 <= status_p < 300:
                # try to add the virtual path
                status = _interface_api_mediamtx_virtual.add_path(self._config.__dict__)
                # tweak the config settings for the virtual path     
                # sourceondemand = true
                # source = 127.0.0.1:port/source camera uid/stream
                # source on demand timeout = 30
                
                Uid =self._source_camera_UID
                Port = f":{self._stream_mediamtx.Port}"
                Protocol = f"{self._stream_mediamtx.Protocol}://"
                
                patch = {"source": f"{Protocol}://127.0.0.1{Port}/{Uid}/stream",
                         "timeout": self._timeout,
                         "sourceOnDemand": True,
                         "name": self._virtual_camera_UID}
                    
                status_p = _interface_api_mediamtx_virtual.patch_path(patch)
                
                #update the source camera (inet) url.
                self._virtual_camera_inet = f"{self._stream_mediamtx.Root()}{self._virtual_camera_UID}/stream"
                
                if 200 <= status < 300 and 200 <= status_p < 300:
                    #we created the virtual path!!
                    self._statuscode = HTTPStatusCodes.OK.code
                    self._status_message = HTTPStatusCodes.OK.status
                    
                else:
                    #we did not create the virtual path.
                    self._statuscode = HTTPStatusCodes.FAILED_DEPENDENCY.code
                    self._status_message = HTTPStatusCodes.FAILED_DEPENDENCY.status

            else:
                #we did not create the source camera path
                self._statuscode = HTTPStatusCodes.FAILED_DEPENDENCY.code
                self._status_message = HTTPStatusCodes.FAILED_DEPENDENCY.status                    
                     
        except requests.exceptions.ConnectionError:
            #mediamtx server (api) not reachable
            self._statuscode = HTTPStatusCodes.NETWORK_CONNECT_TIMEOUT_ERROR.code
            self._status_message = HTTPStatusCodes.NETWORK_CONNECT_TIMEOUT_ERROR.status
            #call self destruct
            
        except Exception as e:
            # something unknown has gone wrong 
            self._statuscode = HTTPStatusCodes.INTERNAL_SERVER_ERROR.code
            self._status_message = HTTPStatusCodes.INTERNAL_SERVER_ERROR.status
            # call self destruct
            
    @property
    def SourceCamera_UID(self) -> str:
        return self._source_camera_UID
    @property
    def VirtualCamera_UID(self) -> str:
        return self._virtual_camera_UID
    @property
    def SourceCamera_Path(self) -> str:
        return self._source_camera_inet
    @property
    def VirtualCamera_Path(self) -> str:
        return self._virtual_camera_inet
    @property
    def SourceCamera_Type(self) -> CameraType:
        return self._camera_type
    
    def ItsMe(self, uid) -> bool:
        if self.SourceCamera_UID == uid or self.VirtualCamera_UID == uid: return True
        else: return False

    def self_destruct(self, otp):
        """
        Remove MediaMTX paths for source and virtual cameras,
        disconnect from TakatVideo API, and clean up internal state.
        """
        
        #TODO this function can only be finnished once the takat api calls are done.
        try:
            # Initialize API interfaces again (or reuse stored ones)
            api_source = MediaMTX_API_Interface_v3(uid=self._source_camera_UID, link=self._api_mediamtx)
            api_virtual = MediaMTX_API_Interface_v3(uid=self._virtual_camera_UID, link=self._api_mediamtx)

            # Delete the paths
            status_source = api_source.delete_path()
            status_virtual = api_virtual.delete_path()
            

            # Optionally, disconnect TakatVideo cameras
            takat_source = TakatVideo_API_Interface_v3(uid=self._source_camera_UID, link=self._api_takat)
            takat_source.unregister(otp) #unregister this camera (remove it from the video object)

        except Exception as e:
            print(f"Self-destruct cleanup failed: {e}")

        # Clear all internal references
        for attr in list(vars(self).keys()):
            setattr(self, attr, None)
            

    def to_dict(self) -> dict:
        """
        Serialize this camera object into a dictionary.
        """
        return {
            "source_camera_uid": self._source_camera_UID,
            "virtual_camera_uid": self._virtual_camera_UID,
            "source_camera_path": self._source_camera_inet,
            "virtual_camera_path": self._virtual_camera_inet,
            "camera_type": int(self._camera_type),
            "config": self._config.to_dict(),
            "status_code": self._statuscode,
            "status_message": self._status_message,
            "stream_source_camera": self._stream_source_camera.to_dict() if hasattr(self._stream_source_camera, "to_dict") else str(self._stream_source_camera),
            "stream_source_camera_inputtype": int(self._stream_source_camera_inputtype),
            "stream_source_camera_output_protocol": int(self._stream_source_camera_output_protocol),
            "timeout": self._timeout,
            "loop": self._loop,
            "stream_mediamtx": self._stream_mediamtx.to_dict() if hasattr(self._stream_mediamtx, "to_dict") else str(self._stream_mediamtx),
        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
        api_mediamtx: Link,
        api_takat: Link,
        stream_mediamtx: Link
    ) -> "Camera_Object_V3":
        """
        Rebuild a Camera_Object_V3 from serialized data.
        NOTE: This will call MediaMTX/Takat APIs again (just like __init__).
        """
        config = MediaMTX_Path_Config_v3.from_dict(data["config"])

        return cls(
            Config=config,
            Source_Camera_UID=data["source_camera_uid"],
            Virtual_Camera_UID=data["virtual_camera_uid"],
            API_mediamtx=api_mediamtx,
            API_takat=api_takat,
            Stream_Mediamtx=stream_mediamtx,
            Stream_SourceCamera=data["stream_source_camera"],
            Stream_SourceCameraInputType=FFMPEG_Command_Builder_v3.IngestType(data["stream_source_camera_inputtype"]),
            Output_Protocol=FFMPEG_Command_Builder_v3.Protocol(data["stream_source_camera_output_protocol"]),
            Timeout=data.get("timeout", 5000000),
            Loop=data.get("loop", True),
        )
    

# ─────────────────────────────────────────────────────────────────────────────
# Video object that glues everything together
# ─────────────────────────────────────────────────────────────────────────────
class Video_Object_v3:
    def __init__(self, 
                  source_camera: Link, mediamtx_server_api: Link, takat_server_api: Link, 
                  mediamtx_server_stream: Link, path_config: MediaMTX_Path_Config_v3,
                  linked_device: str, virtual_camera_uid: str, source_camera_uid: str, 
                  primary_uid: Optional[str] = None, 
                  ffmpeg_processing_type: Optional[FFMPEG_Command_Builder_v3.IngestType] = FFMPEG_Command_Builder_v3.IngestType.Unknown,
                  ffmpeg_output_type:Optional[FFMPEG_Command_Builder_v3.Protocol] = FFMPEG_Command_Builder_v3.Protocol.DEFAULT,
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
        
        result = self._MYCAM_API_MediamMTX.add_path(self._MYCAM_config.__dict__)
        if result == 200: pass #TODO, add status update or exit here
        
        self._MYCAM_virtual_camera_path = f"{self._mediamtx_streaming_server.Root()}{self._primary_uid}" # the path to the main virual camera
        #We now have an object that has a primary and linked uid, an otp its own virtual camera path, now lets add its first camera object (it should have atleast one)
        try:
        #make sure we have have a camera type set.
            if ffmpeg_processing_type == None: ffmpeg_processing_type = FFMPEG_Command_Builder_v3.IngestType.Default
            self._processing_type = ffmpeg_processing_type
            if ffmpeg_output_type == None: ffmpeg_output_type = FFMPEG_Command_Builder_v3.Protocol.DEFAULT
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
        """
        Iterate through all cameras and return a list of their VirtualCamera_Path strings.
        
        Returns:
            List of VirtualCamera_Path for all cameras in _CAMERAS.
        """
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
        """_summary_

        Args:
            up (bool, optional): _description_. Defaults to True.
            this makes the function to select the next one in the list,
            if set to false it selects the previous in the list.
            the function "loops" through the end/beginning of the list if it gets to the end

        Raises:
            ValueError: _description_
            ValueError: _description_
        """
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
                   Source_Type: FFMPEG_Command_Builder_v3.IngestType = FFMPEG_Command_Builder_v3.IngestType.Default,
                   OutputProtocol: FFMPEG_Command_Builder_v3.Protocol = FFMPEG_Command_Builder_v3.Protocol.DEFAULT, Timeout: int | None = 5000000,
                   Loop: bool | None = False) -> None:
        
        # check if uid of source and virtual are not already in a video object in the global list
        if self._IsUnique(Source_UID) == True and self._IsUnique(Virtual_UID) == True:
            #its safe to create this object and its paths
            camera = Camera_Object_V3(Config=Config,Source_Camera_UID=Source_UID,Virtual_Camera_UID=Virtual_UID, API_mediamtx=Mediamtx_API,
                                API_takat=Takat_API, Stream_Mediamtx=MediaMTX_Stream, Stream_SourceCamera=Source_Camera ,Stream_SourceCameraInputType=Source_Type,
                                Output_Protocol=OutputProtocol, Timeout=Timeout, Loop=Loop)
            
            
            # add the source uid to the credentials
            self._credentials.add_source_camera(Source_UID)
            # add the virtual uid to the credentials
            self._credentials.add_virtual_camera(Virtual_UID)
            # add the camera to the array.
            self._CAMERAS.append(camera)
            
    def Delete_Camera(self, uid: str) -> None:
        """
        Deletes a camera from this Video_Object_v3 by UID (source or virtual).

        Steps:
        1. Find the camera matching the UID.
        2. Remove its paths / call self_destruct.
        3. Remove its UIDs from credentials.
        4. Remove the camera object from the _CAMERAS list.
        """
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
        """
        Returns True if the given UID is *not yet used* in any Video_Object_v3.
        Uses the global VIDEO_OBJECTS registry to verify uniqueness.
        """
        #TODO make functional
        return True

    def _Self_Destruct(self, otp) -> None:
        """
        Fully destroys this Video_Object_v3:
        - Safely destroys all camera objects and their credentials.
        - Deletes the main virtual camera path.
        - Removes itself from the global registry if applicable.
        
        Can be called multiple times safely; exceptions are caught and logged.
        """
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