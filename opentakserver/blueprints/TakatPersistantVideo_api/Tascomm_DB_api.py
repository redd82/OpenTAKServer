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
from enum import Enum

from opentakserver.models.user import User
from flask import jsonify, request, current_app as app, Blueprint
from flask_login import current_user
# ─────────────────────────────────────────────────────────────────────────────
# Third‑party / project imports
# ────────────────────────────────────────────────────────────────────────────
from opentakserver.blueprints.TakatPersistantVideo_api.Rest import Rest
from opentakserver.blueprints.TakatPersistantVideo_api.Validation import Validation


class Tasscom_DB_api:
    
    #naar dit endpoint: http://192.168.18.120:10301/mediamtx/createMediaMTXPathConfig
    class Endpoints(Enum):
        # record edditing functions
        CREATE_PATH = "/mediamtx/createMediaMTXPathConfig"                                  # (post)    Add specific record
        CHANGE_PATH = "/mediamtx/changeMediaMTXPathConfig/{id}"                             # (patch)   Change specific record
        DELETE_PATH = "/mediamtx/deleteMediaMTXPathConfig/{id}"                             # (delete)  Delete specific record
        # record search functions
        GET_All =     "/mediamtx/getAllMediaMTXPathConfigs"                                  # (get)     Return all records (possibly multiple)
        GET_ALL_BY_PRIMARY= "/mediamtx/getAllMediaMTXPathConfigsByPrimaryUID/{PrimaryID}"   # (get)     Return all configs with this primary uid (possibly multiple)
        GET_ALL_BY_LINKED = "/mediamtx/getAllMediaMTXPathConfigsByLinkedUID/{linkedID}"     # (get)     Return all configs with this linked uid (possibly multiple)
        GET_BY_UID = "/mediamtx/getMediaMTXPathConfigByUID/{uid}"                           # (get)     Return this uid specific config (this should always be one)
    
    
    
    CAMERAOBJECT_DEFAULT_CONFIG = {
        "camera_object_uid": "",
        "camera_object_jwt": "",
        
        "source_cam_uid": "",
        "Source_cam_type": "stream",
        "source_cam_protocol": "http",
        "source_cam_fqdn": "127.0.0.1",
        "source_cam_port":"8554",
        "source_cam_path": "/stream",
        
        "virtual_cam_uid": "",
        "virtual_cam_protocol": "rtsp",
        "virtual_cam_fqdn": "127.0.0.1",
        "virtual_cam_port": "8554",
        
        "mediamtx_api_protocol":"http",
        "mediamtx_api_fqdn": "127.0.0.1",
        "mediamtx_api_port":"9997",
        "mediamtx_api_jwt":"",
    }
    
    MEDIAMTX_DEFAULT_CONFIG = {
            "source": "",
            "name": "",
            "path": "",
            "sourceFingerprint": "",
            "sourceOnDemand": False,
            "sourceOnDemandStartTimeout": "",
            "sourceOnDemandCloseAfter": "",
            "maxReaders": 0,
            "srtReadPassphrase": "",
            "fallback": "",
            "useAbsoluteTimestamp": False,
            "recordEnabled": False,
            "recordPath": "/home/takusr/ots/mediamtx/recordings/%path/%Y-%m-%d%H-%M-%S-%f",
            "recordFormat": "fmp4",
            "recordPartDuration": "100ms",
            "recordMaxPartSize": "",
            "recordSegmentDuration": "1h0m0s",
            "recordDeleteAfter": "",
            "overridePublisher": False,
            "srtPublishPassphrase": "",
            "rtspTransport": "automatic",
            "rtspAnyPort": False,
            "rtspRangeType": "",
            "rtspRangeStart": "",
            "sourceRedirect": "",
            "rpiCameraCamId": 0,
            "rpiCameraSecondary": False,
            "rpiCameraWidth": 1024,
            "rpiCameraHeight": 768,
            "rpiCameraHFlip": False,
            "rpiCameraVFlip": False,
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
            "rpiCameraHdr": False,
            "rpiCameraTuningFile": "",
            "rpiCameraMode": "",
            "rpiCameraFps": 30,
            "rpiCameraAfMode": "continuous",
            "rpiCameraAfRange": "normal",
            "rpiCameraAfSpeed": "normal",
            "rpiCameraLensPosition": 0,
            "rpiCameraAfWindow": "",
            "rpiCameraFlickerPeriod": 0,
            "rpiCameraTextOverlayEnable": False,
            "rpiCameraTextOverlay": "",
            "rpiCameraCodec": "auto",
            "rpiCameraIdrPeriod": 0,
            "rpiCameraBitrate": 0,
            "rpiCameraProfile": "main",
            "rpiCameraLevel": "4.1",
            "rpiCameraJpegQuality": 60,
            "runOnInit": "",
            "runOnInitRestart": False,
            "runOnDemand": "",
            "runOnDemandRestart": False,
            "runOnDemandStartTimeout": "10s",
            "runOnDemandCloseAfter": "10s",
            "runOnUnDemand": " ",
            "runOnReady": "",
            "runOnReadyRestart": False,
            "runOnNotReady": "",
            "runOnRead": "",
            "runOnReadRestart": False,
            "runOnUnread": "",
            "runOnRecordSegmentCreate": "",
            "runOnRecordSegmentComplete": "",
            "playbackEnabled": False
        }
    
    def __init__(self, fqdn: str, port: int, protocol: str, retries: int, verified_ssl: bool, TascommToken: Optional[str]):
        """
        Initialize a DB API call
        
        Args:
            mediaMTXToken (str):the secret token needed to be authorized
            fqdn (str):         the fqdn or ip of where the api lives. ie takat.nl or 8.8.8.8
            port (int):         the port number where the api lives (if you don't know just set it to 80 for http)
            protocol (str):     the protocol we use, http or https. this defaults to http if something weird happens
        """
        self._clamp = Validation()                          # stateless class used to validate inputs   
        self._mediaMTXToken = ""                 # the secret key needed to access the mediamtx server if it has web tokens enables
        self._fqdn = self._clamp.FQDN(fqdn)                 # the fqdn ip4 or ip6 address of the server
        self._port = self._clamp.Port(port)                 # the port where the api lives (if none is used set to 0)
        self._protocol = self._clamp.HttpOrHttps(protocol)  # make sure we have http or https as a protocol.... default to http
        self._retries = self._clamp.Range(value=retries, max_value=3, min_value=0)  #maximum retries if an api call fails
        self._verified_ssl = verified_ssl or False          # verify is the api call uses ssl (we prefer not to)

        self._resolveToken(value=TascommToken)               # the secret key needed to access the tascomm server if it has web tokens enabled, note that "auto" will retrieve the key automatically
        
        self._rest = Rest(server=self._fqdn, verify_ssl=self._verified_ssl, jwt_token=self._tascommToken, retry=self._retries) #create a rest  object to handle api calls 
        
        # internal uid tracker
        self._ExistingUIDs: list[str] = []  # <- initialize empty list for UIDs
        #Call internal function to populate internal uid tracker
        self._UID_RefreshList()
        
        
        
    
    # ─────────────────────────────────────────────────────────────────────────────
    # Getters and Setters
    # ─────────────────────────────────────────────────────────────────────────────
    
    @property
    def FQDN(self): return self._fqdn
    @FQDN.setter
    def FQDN(self, value): self._fqdn = self._clamp.FQDN(value)
        
    @property
    def Port(self): return self._port
    @Port.setter
    def Port(self, value): self._port = self._clamp.Port(value)
        
    @property
    def Protocol(self): return self._protocol
    @Protocol.setter
    def Protocol(self, value): self._protocol = self._clamp.HttpOrHttps(value)
    
    @property
    def TassComToken(self): return "supersecret"
    @TassComToken.setter
    def TassComToken(self, value): self._resolveToken(value=value)
    
    # ─────────────────────────────────────────────────────────────────────────────
    # Internal Functions to make the keep track of UID's so we do not get doubles.
    # ─────────────────────────────────────────────────────────────────────────────
    def _UID_isInList(self, uid: str) -> bool:
        """
        Check if a given UID already exists in the internal _ExistingUIDs list.
        
        Parameters
        ----------
        uid : str
            The UID to check for existence.
        
        Returns
        -------
        bool
            True if the UID is in the list, False otherwise.
        """
        
        return uid in self._ExistingUIDs
    
    def _UID_AddToList(self, uid: str) -> None:
        """
        Add a UID to the internal _ExistingUIDs list if it doesn't already exist.
        Logs whether the UID was added or already present.

        Parameters
        ----------
        uid : str
            The UID to add.
        """
        if self._UID_isInList(uid): logger.info(f"Tasscom_DB_api._UID_AddToList: UID '{uid}' already exists in _ExistingUIDs, no action taken.")
        else:
            self._ExistingUIDs.append(uid)
            logger.info(f"Tasscom_DB_api._UID_AddToList: UID '{uid}' added to _ExistingUIDs.")
    
    def _UID_RemoveFromList(self, uid: str) -> None:
        """
        Remove a UID from the internal _ExistingUIDs list if it exists.
        Logs whether the UID was removed or not found.

        Parameters
        ----------
        uid : str
            The UID to remove.
        """
        if self._UID_isInList(uid):
            self._ExistingUIDs.remove(uid)
            logger.info(f"Tasscom_DB_api._UID_RemoveFromList: '{uid}' removed from _ExistingUIDs.")
        else: logger.info(f"Tasscom_DB_api._UID_RemoveFromList: '{uid}' not found in _ExistingUIDs, no action taken.")

    def _UID_RefreshList(self) -> None:
        #TODO make function. 
        # use getall to get all records, 
        # filter out all uid's 
        # add them to the list.
        pass
    
    # ─────────────────────────────────────────────────────────────────────────────
    # Internal Helper Functions .
    # ─────────────────────────────────────────────────────────────────────────────
        
    def _defaultError(self, status: str, caller:str, endpoint: str, error: str) -> dict:
            err_dict = {
                "status": str(status),
                "caller": str(caller),
                "endpoint": str(endpoint),
                "error": str(error)
            }
            logger.error(f"Tasscom_DB_api._defaultError: {caller} | Endpoint: {endpoint} | Error: {error}")
            return err_dict
    
    def _defaultSuccess(self, caller:str, endpoint: str) -> dict:
        err_dict = {
                "caller": str(caller),
                "endpoint": str(endpoint),
                "response": "ok" 
        }
        logger.info(f"Tasscom_DB_api._defaultSuccess: {caller} | Endpoint: {endpoint} | response: ok")
        return err_dict        

    """
    def _getServerToken(self) -> None:
        with app.app_context():
            security = app.extensions.get("security")
            if not security:
                logger.error("DB_API: Flask-Security is not initialized; TascommToken unset.")
                self._tascommToken = ""
                return

            user = security.datastore.find_user(username="administrator")
            if not user:
                logger.error("DB_API: Administrator user not found; TascommToken unset.")
                self._tascommToken = ""
                return

            self._tascommToken = user.password   
            logger.info(self._tascommToken)
    """
         
    def _resolveToken(self, value) -> None:
        """
        Normalizes user-provided token input.
        - Treats None or empty strings as empty token
        - Accepts "auto" (any case/whitespace) and replaces with server token
        - Strips extra spaces from valid tokens
        - Always updates and returns self._tascommToken
        """

        # Normalize type: only treat actual strings as user tokens
        if isinstance(value, str):
            token = value.strip()
            if not token: self._tascommToken = ""
            elif token.lower() == "auto":
                with app.app_context():
                    security = app.extensions.get("security")
                    if not security:
                        logger.error("Tasscom_DB_api: Flask-Security is not initialized; TascommToken unset.")
                        self._tascommToken = ""
                        return 
                    user = security.datastore.find_user(username="administrator")
                    if not user:
                        logger.error("Tasscom_DB_api: Administrator user not found; TascommToken unset.")
                        self._tascommToken = ""
                        return  
                    self._tascommToken = user.password   
                    logger.debug(f"Tasscom_DB_api: server token set to: {self._tascommToken} ")
            else: self._tascommToken = token  # Cleaned user token
        else: self._tascommToken = ""  # None or non-string → empty token
        return


    def _response_status(self, result:dict ) -> bool:
        """
        Check if the delete operation was successful based on the API response.

        Parameters
        ----------
        result : dict
            Response dictionary from DELETE request.

        Returns
        -------
        bool
            True if delete succeeded, False otherwise.
        """
        return isinstance(result, dict) and result.get("response") == "Ok"
        
        
        
    # ─────────────────────────────────────────────────────────────────────────────
    # Public Functions to make the Change DB records (add, remove change)
    # ─────────────────────────────────────────────────────────────────────────────
    def CreateRecord(self, uid: str, configuration: dict, linked_uid: Optional[str] = None, primary_uid: Optional[str] = None) -> dict:
        """
            Create a MediaMTX path configuration on the server.

            Parameters
            ----------
            uid : str
                Required UID for the path.
            linked_uid : Optional[str]
                Optional linked UID to include in the payload.
            primary_uid : Optional[str]
                Optional primary UID to include in the payload.
            configuration : Optional[dict]
                Optional overrides for the default path configuration.
            Returns
            -------
            dict
                Result from the REST POST request (or error dictionary).
        """
        
        # make sure we have an uid if not, return an error
        if not uid: return self._defaultError(status="error", caller="Tasscom_DB_api.CreatePath", endpoint=self.Endpoints.CREATE_PATH.value, error="uid is required and cannot be empty")
        # and make sure its not already an existing uid, if so, return an error
        if self._UID_isInList(uid=uid) == True: return self._defaultError(status="error", caller="Tasscom_DB_api.CreateRecord", endpoint=self.Endpoints.CREATE_PATH.value, error="uid is an existing record in the database")     

        DEFAULT_CONFIG = self.MEDIAMTX_DEFAULT_CONFIG # Base payload from default configuration

        # Merge default with any user-provided configuration overrides
        payload = dict(DEFAULT_CONFIG)
        if configuration: payload.update(configuration)

        # Inject required fields
        payload["mediaMTXToken"] = self._mediaMTXToken
        payload["uid"] = uid
        
        if primary_uid: payload["primaryUID"] = primary_uid
        if linked_uid:  payload["linkedUid"] = linked_uid

        # POST to REST endpoint
        result = self._rest.POST(endpoint=self.Endpoints.CREATE_PATH.value, payload=payload, log=True)
        
        #TODO on success add uid to internal list

        return result
            
    
    def ChangeRecord(self, uid, configuration: dict, linked_uid: Optional[str] = None, primary_uid: Optional[str] = None) -> dict:
        """
            Change an existing MediaMTX path configuration on the server.

            Parameters
            ----------
            uid : str
                Required UID for the record to update.
            configuration : dict
                Key-value pairs to update in the record.
            linked_uid : Optional[str]
                Optional new linked UID to include.
            primary_uid : Optional[str]
                Optional new primary UID to include.

            Returns
            -------
            dict
                Result from the REST PATCH request or error dictionary.
        """
            
        # Check if UID is valid
        if not uid: return self._defaultError(status="error", caller="Tasscom_DB_api.ChangeRecord", endpoint=self.Endpoints.CHANGE_PATH.value, error="UID is required and cannot be empty")
        # mCheck to see if there is not already a record of the UID.
        if not self._UID_isInList(uid): return self._defaultError(status="error", caller="Tasscom_DB_api.ChangeRecord", endpoint=self.Endpoints.CHANGE_PATH.value, error=f"UID '{uid}' does not exist in the database")

        # Start with the configuration dictionary
        payload = dict(configuration or {})

        # Inject required fields
        payload["mediaMTXToken"] = self._mediaMTXToken
        payload["uid"] = uid

        if primary_uid: payload["primaryUID"] = primary_uid
        if linked_uid:  payload["linkedUid"] = linked_uid
        
        endpoint = self.Endpoints.CHANGE_PATH.value.format(id=uid) # Construct endpoint URL

        result = self._rest.PATCH(endpoint=endpoint, payload=payload, log=True) # Make PATCH request
        logger.debug(f"Tasscom_DB_api.ChangeRecord: changed record {uid}, response:\n{json.dumps(result, indent=2)}")
        logger.info(f"Tasscom_DB_api.ChangeRecord: changed record {uid}")
        return result
        
    
    def DeleteRecord(self, uid):
        """
            Delete an existing MediaMTX path configuration on the server.

            Parameters
            ----------
            uid : str
                The UID of the record to delete.

            Returns
            -------
            dict
                Result from the REST DELETE request or error dictionary.
        """
        # Validate UID
        if not uid: return self._defaultError(status="error", caller="Tasscom_DB_api.DeleteRecord", endpoint=self.Endpoints.DELETE_PATH.value.format(id=uid), error="UID is required and cannot be empty")

        if not self._UID_isInList(uid): return self._defaultError(status="error", caller="Tasscom_DB_api.DeleteRecord", endpoint=self.Endpoints.DELETE_PATH.value.format(id=uid), error=f"UID '{uid}' does not exist in the database")

        endpoint = self.Endpoints.DELETE_PATH.value.format(id=uid)# Build endpoint URL
        result = self._rest.DELETE(endpoint=endpoint, payload={"mediaMTXToken": self._mediaMTXToken}, log=True) # Make REST DELETE request
        
        #check if we deleted it or not.
        if self._response_status(result):
            self._UID_RemoveFromList(uid)
            logger.info(f"Tasscom_DB_api.DeleteRecord: successfully deleted record {uid}")
            return self._defaultSuccess(caller="Tasscom_DB_api.DeleteRecord:", endpoint=self.Endpoints.DELETE_PATH.value.format(id=uid))
        else:
            logger.warning(f"Tasscom_DB_api.DeleteRecord: failed to delete record {uid}. Response: {result.get('response')} - {result.get('message')}" )
            return self._defaultError(status="error", caller="Tasscom_DB_api.DeleteRecord", endpoint=self.Endpoints.DELETE_PATH.value, error=f"failed to delete record {uid}") 


    # ─────────────────────────────────────────────────────────────────────────────
    # Public Functions to make the Search DB records (get all, search by uid, search by primary, search by linked)
    # ─────────────────────────────────────────────────────────────────────────────
    def RetrieveAll(self):
        pass
    
    def RetrieveByUID(self, uid):
        pass
    
    def RetrieveByPrimaryUID(self, primaryuid):
        pass
    
    def RetrieveByLinkedUID(self, linkedUID):
        pass
    
    
    