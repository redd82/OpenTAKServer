import json, copy, re
from enum import Enum

#logger.debug
from opentakserver.extensions import logger

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urlencode
import json
from typing import Any, Dict, Optional, Tuple, List, Union


# ─────────────────────────────────────────────────────────────────────────────
# Third‑party / project imports
# ────────────────────────────────────────────────────────────────────────────
from opentakserver.blueprints.TakatPersistantVideo_api.support import Rest

class DB_API:
    
    #naar dit endpoint: http://192.168.18.120:10301/mediamtx/createMediaMTXPathConfig
    class Endpoints(Enum):
        CREATE_PATH = "/mediamtx/createMediaMTXPathConfig"                                  # (post)    Add specific record
        CHANGE_PATH = "/mediamtx/changeMediaMTXPathConfig/{id}"                             # (patch)   Change specific record
        DELETE_PATH = "/mediamtx/deleteMediaMTXPathConfig/{id}"                             # (delete)  Delete specific record
        GET_All =     "/mediamtx/getAllMediaMTXPathConfig"                                  # (get)     Return all records
        GET_ALL_BY_PRIMARY= "/mediamtx/getAllMediaMTXPathConfigsByPrimaryUID/{PrimaryID}"   # (get)     Return all configs with this primary uid (possibly multiple)
        GET_ALL_BY_LINKED = "/mediamtx/getAllMediaMTXPathConfigsByLinkedUID/{linkedID}"     # (get)     Return all configs with this linked uid (possibly multiple)
        GET_BY_UID = "/mediamtx/getMediaMTXPathConfigByUID/{uid}"                            # (get)     Return this uid specific config (this should always be one)
    
    def __init__(self, mediaMTXToken, fqdn: str, port: int, protocol: str):
        """
        Initialize a DB API call
        
        Args:
            mediaMTXToken (_type_): the secret token needed to be authorized
            fqdn (str): the fqdn or ip of where the api lives. ie takat.nl or 8.8.8.8
            port (int): the port number where the api lives (if you don't know just set it to 80 forr http)
            protocol (str): the protocol we use, http or https. this defaults to http if something weird happens
        """
        self._mediaMTXToken = mediaMTXToken                 # the secret key needed to access the tascomm api
        self._fqdn = self._clamp_fqdn(fqdn)                 # make sure we have no funny characters/number/letters etc in the fqdn (ip also allowed)
        self._port = self._clamp_port(port)                 # make sure we have a valid port
        self._protocol = self._clamp_protocol(protocol)     # make sure we have http or https as a protol.. default to http
        
        #url: str ="http://127.0.0.1", verify_ssl: bool = False,jwt_token: Optional[str] = None, retry: Optional[int] =3,
        
        
        self._rest = Rest(url="", verify_ssl=False)
    
    @property
    def FQDN(self, value=None):
        if value is None: return self._fqdn
        else: self._fqdn =  self._clamp_fqdn(value)
    @property
    def Port(self, value=None):
        if value is None: return self._port
        else: self._port = self._clamp_port(value)
    @property
    def Protocol(self, value=None):
        if value is None: return self._protocol
        else: self._protocol = self._clamp_protocol(value)
        
    # ─────────────────────────────────────────────────────────────────────────────
    # Helper functions Normalize input from __init__ and @property
    # ─────────────────────────────────────────────────────────────────────────────
    def _clamp_fqdn(self, fqdn: str) -> str:
        """
        Clamp a fully qualified domain name (FQDN) or IP address to valid characters.

        Args:
            fqdn (str): The input FQDN or IP address.

        Returns:
            str: A sanitized, lowercase FQDN or IP address containing only letters, numbers, and periods.
        """
        if fqdn is None:
            return "127.0.0.1"  # edge case, if the @property is set to none we basically reset it to 127.0.0.1)
        
        if not isinstance(fqdn, str):
            logger.error(f"DB_API: _clamp_fqdn: fqdn {fqdn} is not of type str.")
            raise TypeError("DB_API: _clamp_fqdn: FQDN must be a string")
        
        # Remove everything except letters, numbers, and periods
        clean_fqdn = re.sub(r'[^a-zA-Z0-9\.]', '', fqdn).lower()

        if not clean_fqdn:
            logger.warning(f"DB_API: _clamp_fqdn: input {fqdn} became empty after cleaning. Defaulting to '127.0.0.1'.")
            return "127.0.0.1"

        return clean_fqdn
    
    def _clamp_port(self, port: int) -> int:
        """
        Clamp a port number to the valid range (0–65535).

        Args:
            port (int): The port number to clamp.

        Returns:
            int: A valid port number between 0 and 65535.
        """
        if port is None:
            return 80   #edge case, the @property setter was deliberatly set to None, default to 80
        if not isinstance(port, int):
            logger.error(f"DB_API: _clamp_port: port {port} is not of type int.")
            raise TypeError("Port must be an integer")
        return max(0, min(65535, abs(port)))
        
    def _clamp_protocol(self, protocol: str) -> str:
        """
        Clamp protocol to the valid string of http or https.

        Args:
            protocol (str): The protocol to clamp.

        Returns:
            str: either http or https. defaulting to http if the input was invalid.
        """
        default="http"
        
        if protocol is None:
            return default.lower()   # edge case if the @property is set to None, we default back to http
        if not isinstance(protocol, str):
            logger.error(f"DB_API: _clamp_protocol: protocol {protocol} is not of type str.")
            raise TypeError("Protocol must be an string")
        if protocol.lower() in ("http", "https"): return protocol.lower()
        else: 
            logger.warning(f"DB_API: _clamp_protocol: invalid protocol '{protocol}', defaulting to 'http'.")
            return default.lower()
        
    

    # ─────────────────────────────────────────────────────────────────────────────
    # Public Functions to make the actual api calls.
    # ─────────────────────────────────────────────────────────────────────────────
    def CreatePath(self, uid, inputs):
        
        """
            naar dit endpoint: http://192.168.18.120:10301/mediamtx/createMediaMTXPathConfig
            deze json
            {
                "mediaMTXToken": "23432wefasfa3rawfsfsrf3r",
                "primaryUID": "asdfjsdi3jksjdksjdku839",
                "uid": "po908938edlskdlskd93eu9jdlsdk",
                "linkedUid": "podjud09wd09jddmedj0ejde8j",
                "source": "",
                "name": "",
                "path": "",
                "sourceFingerprint": "",
                "sourceOnDemand": false,
                "sourceOnDemandStartTimeout": "",
                "sourceOnDemandCloseAfter": "",
                "maxReaders": 0,
                "srtReadPassphrase": "",
                "fallback": "",
                "useAbsoluteTimestamp": false,
                "recordEnabled": false,
                "recordPath": "/home/takusr/ots/mediamtx/recordings/%path/%Y-%m-%d%H-%M-%S-%f",
                "recordFormat": "fmp4",
                "recordPartDuration": "100ms",
                "recordMaxPartSize": "",
                "recordSegmentDuration": "1h0m0s",
                "recordDeleteAfter": "",
                "overridePublisher": false,
                "srtPublishPassphrase": "",
                "rtspTransport": "automatic",
                "rtspAnyPort": false,
                "rtspRangeType": "",
                "rtspRangeStart": "",
                "sourceRedirect": "",
                "rpiCameraCamId": 0,
                "rpiCameraSecondary": false,
                "rpiCameraWidth": 1024,
                "rpiCameraHeight": 768,
                "rpiCameraHFlip": false,
                "rpiCameraVFlip": false,
                "rpiCameraBrightness": 0,
                "rpiCameraContrast": 0,
                "rpiCameraSaturation": 0,
                "rpiCameraSharpness": 0,
                "rpiCameraExposure": "normal",
                "rpiCameraAwb": "auto",
                "rpiCameraAwbGains": "0,0",
                "rpiCameraDenoise": "off",
                "rpiCameraShutter": 0,
                "rpiCameraMetering": "centre",
                "rpiCameraGain": 0,
                "rpiCameraEv": 0,
                "rpiCameraRoi": "",
                "rpiCameraHdr": false,
                "rpiCameraTuningFile": "",
                "rpiCameraMode": "",
                "rpiCameraFps": 30,
                "rpiCameraAfMode": "continuous",
                "rpiCameraAfRange": "normal",
                "rpiCameraAfSpeed": "normal",
                "rpiCameraLensPosition": 0,
                "rpiCameraAfWindow": "",
                "rpiCameraFlickerPeriod": 0,
                "rpiCameraTextOverlayEnable": false,
                "rpiCameraTextOverlay": "",
                "rpiCameraCodec": "auto",
                "rpiCameraIdrPeriod": 0,
                "rpiCameraBitrate": 0,
                "rpiCameraProfile": "main",
                "rpiCameraLevel": "4.1",
                "rpiCameraJpegQuality": 60,
                "runOnInit": "",
                "runOnInitRestart": false,
                "runOnDemand": "",
                "runOnDemandRestart": false,
                "runOnDemandStartTimeout": "10s",
                "runOnDemandCloseAfter": "10s",
                "runOnUnDemand": " ",
                "runOnReady": "",
                "runOnReadyRestart": false,
                "runOnNotReady": "",
                "runOnRead": "",
                "runOnReadRestart": false,
                "runOnUnread": "",
                "runOnRecordSegmentCreate": "",
                "runOnRecordSegmentComplete": "",
                "playbackEnabled": false
                }
            """
        pass
    
    def ChangePAth(self, uid, inputs):
        pass
    
    def DeletePath(self, uid):
        pass

    def GetAll(self):
        pass