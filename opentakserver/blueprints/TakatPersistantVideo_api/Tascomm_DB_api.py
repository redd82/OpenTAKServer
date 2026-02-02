import json
from enum import Enum
from typing import Any, Dict, Tuple

# Logger
from opentakserver.extensions import logger

# Project imports
from opentakserver.blueprints.TakatPersistantVideo_api.Validation import Validation
from opentakserver.blueprints.TakatInterApi_interface.defaultPluginConfig import DefaultPluginConfig as pluginConfig
from opentakserver.blueprints.TakatPersistantVideo_api.Takat_Logging import TakatLogger, TakatMessages
from opentakserver.blueprints.TakatPersistantVideo_api.RestTakatLan import RestTakatLan


class Tasscom_DB_api:
    """
    Tasscom database API interface using RestTakatLan client.
    Handles JWT tokens, server connections, and video object operations.
    """
    
    class Endpoints(Enum):
        # Video object operations
        CREATE_VIDEOOBJECT = "/mediamtx/createVideoObject"
        CHANGE_VIDEOOBJECT = "/mediamtx/changeVideoObject/{uid}"
        DELETE_VIDEOOBJECT = "/mediamtx/deleteVideoObject/{uid}"
        GET_VIDEOBJECT = "/mediamtx/getVideoObjectByUID/{uid}"
        
        # Video object searches
        GET_ALL_VIDEOOBJECTS = "/mediamtx/getAllVideoObjects"
        GET_VIDEOOBJECT_BY_UID = "/mediamtx/getVideoObjectByUID/{uid}"
        GET_VIDEOOBJECT_BY_LINKEDUID = "/mediamtx/getVideoObjectByLinkedUID/{linkedUid}"
        GET_ALL_VIDEOOBJECT_UIDS = "/mediamtx/getAllVideoObjectUIDsList"
        GET_ALL_VIDEOOBJECT_LINKEDUIDS = "/mediamtx/getAllVideoObjectLinkedUIDsList"
        
        # Utility
        DOES_UID_EXIST = "/mediamtx/doesUIDExist/{uid}"
        ForceKey = "/otsServers/serverCameAlive"

    # ─────────────────────────────────────────────────────────────────────────────
    def __init__(self, retries: int = 3, log: bool = False, debug: bool = False):
        # Logging and validation
        self._caller = "Tasscom_DB_api"
        self._logging = TakatLogger()
        self._messages = TakatMessages()
        self._clamp = Validation()
        
        # Retry settings
        self._maxretries = 5
        self._minretries = 0
        self._retries = self._clamp.Range(retries, self._minretries, self._maxretries)
        
        # Logging and debugging
        self._log = self._clamp.ToBool(log)
        self._debug = self._clamp.ToBool(debug)
        
        # DB connection parameters
        self._db_fqdn = ""
        self._db_jwt = ""
        self._db_port = 0
        self._db_verified_ssl = False
        self._db_prefix = ""
        self._hotswapable = False
        
        # Initialize connection parameters
        self.UpdateDBConnection(UpdateRest=False)
        
        # Instantiate REST client
        self._db_rest = RestTakatLan(
            server=self._db_fqdn,
            port=self._db_port,
            verify_ssl=self._db_verified_ssl,
            auto_update=True,
            log=self._log,
            debug=self._debug
        )
        
        # Set client logging/debugging
        self._db_rest.log = self._log
        self._db_rest.debug = self._debug
        
        # Log initialization
        self._logging.Info(
            caller=self._caller,
            message=(
                f"Initialized Tasscom DB API with FQDN: {self._db_fqdn}, "
                f"Port: {self._db_port}, Verified SSL: {self._db_verified_ssl}, "
                f"Retries: {self._retries}, Logging: {self._log}, Debugging: {self._debug}"
            ),
            log=self._log
        )

    # ─────────────────────────────────────────────────────────────────────────────
    # Getters and setters
    # ─────────────────────────────────────────────────────────────────────────────
    @property
    def Logging(self) -> bool:
        return self._log

    @Logging.setter
    def Logging(self, value: bool):
        self._log = self._clamp.ToBool(value)
        self._db_rest.log = self._log

    @property
    def Debugging(self) -> bool:
        return self._debug

    @Debugging.setter
    def Debugging(self, value: bool):
        self._debug = self._clamp.ToBool(value)
        self._db_rest.debug = self._debug

    @property
    def Retries(self) -> int:
        return self._retries

    @Retries.setter
    def Retries(self, value: int):
        self._retries = self._clamp.Range(value, self._minretries, self._maxretries)

    @property
    def MinRetries(self) -> int:
        return self._minretries

    @MinRetries.setter
    def MinRetries(self, value: int):
        self._minretries = self._clamp.Min(0, value)

    @property
    def MaxRetries(self) -> int:
        return self._maxretries

    @MaxRetries.setter
    def MaxRetries(self, value: int):
        self._maxretries = self._clamp.Max(10, value)

    @property
    def Hotswapable(self) -> bool:
        return self._hotswapable

    @Hotswapable.setter
    def Hotswapable(self, value: bool):
        self._hotswapable = self._clamp.ToBool(value)

    # ─────────────────────────────────────────────────────────────────────────────
    # DB connection updates
    # ─────────────────────────────────────────────────────────────────────────────
    def UpdateDBConnection(self, UpdateRest: bool = True):
        # Update internal variables from pluginConfig
        self._db_fqdn = pluginConfig.TasscommFQDN or "127.0.0.1"
        self._db_jwt = pluginConfig.TascommAccessToken or ""
        self._db_port = pluginConfig.TasscommPort or 443
        self._db_prefix = pluginConfig.Prefix_TascommAPI or ""
        self._db_verified_ssl = pluginConfig.verified_ssl or False

        if UpdateRest:
            self._db_rest._server = self._db_fqdn
            self._db_rest._jwt = self._db_jwt
            self._db_rest._port = self._db_port
            self._db_rest._verify_ssl = self._db_verified_ssl

    def ForceKeyUpdate(self):
        """Force update of server key at startup."""
        ip = pluginConfig.TasscommInternalIP
        port = pluginConfig.TasscommInternalPort
        prefix = pluginConfig.Prefix_TascommAPI
        endpoint = f"{prefix}{Tasscom_DB_api.Endpoints.ForceKey.value}"
        
        tmpRest = RestTakatLan(server=ip, port=port, retry=1, verify_ssl=False, jwt_token="")
        message = tmpRest.GET(endpoint=endpoint, overrideLog=self._log)

        self._logging.Info(
            caller=self._caller,
            message=f"ForceKeyUpdate attempt: {message}",
            log=self._log
        )

        self.UpdateDBConnection(UpdateRest=True)
        return message

    def _updateJWT(self):
        """Update JWT from pluginConfig and refresh REST client if hotswap enabled."""
        self._db_jwt = pluginConfig.TascommAccessToken
        if self._hotswapable:
            self.UpdateDBConnection(UpdateRest=True)
        self._logging.Info(caller=self._caller, message="Updated Tascomm Database access token", log=self._log)

    # ─────────────────────────────────────────────────────────────────────────────
    # Video object operations
    # ─────────────────────────────────────────────────────────────────────────────
    def CreateVideoObject(self, video_object_data: Dict[str, Any]):
        endpoint = f"{self._db_prefix}{Tasscom_DB_api.Endpoints.CREATE_VIDEOOBJECT.value}"
        self._updateJWT()
        return self._db_rest.POST(endpoint=endpoint, payload=video_object_data, overrideLog=self._log)

    def ChangeVideoObject(self, uid: str, video_object_data: Dict[str, Any]):
        endpoint = f"{self._db_prefix}{Tasscom_DB_api.Endpoints.CHANGE_VIDEOOBJECT.value.format(uid=uid)}"
        self._updateJWT()
        return self._db_rest.PATCH(endpoint=endpoint, payload=video_object_data, overrideLog=self._log)

    def DeleteVideoObject(self, uid: str):
        endpoint = f"{self._db_prefix}{Tasscom_DB_api.Endpoints.DELETE_VIDEOOBJECT.value.format(uid=uid)}"
        self._updateJWT()
        return self._db_rest.DELETE(endpoint=endpoint, overrideLog=self._log)

    def GetVideoObject(self, uid: str):
        endpoint = f"{self._db_prefix}{Tasscom_DB_api.Endpoints.GET_VIDEOOBJECT_BY_UID.value.format(uid=uid)}"
        self._updateJWT()
        return self._db_rest.GET(endpoint=endpoint, overrideLog=self._log)

    # ─────────────────────────────────────────────────────────────────────────────
    # Search functions
    # ─────────────────────────────────────────────────────────────────────────────
    def GetAllVideoObjects(self):
        self._updateJWT()
        endpoint = f"{self._db_prefix}{Tasscom_DB_api.Endpoints.GET_ALL_VIDEOOBJECTS.value}"
        return self._db_rest.GET(endpoint=endpoint, overrideLog=True)

    def GetVideoObjectByLinkedUID(self, linked_uid: str):
        self._updateJWT()
        endpoint = f"{self._db_prefix}{Tasscom_DB_api.Endpoints.GET_VIDEOOBJECT_BY_LINKEDUID.value.format(linkedUid=linked_uid)}"
        return self._db_rest.GET(endpoint=endpoint, overrideLog=True)

    def GetAllVideoObjectUIDs(self):
        self._updateJWT()
        endpoint = f"{self._db_prefix}{Tasscom_DB_api.Endpoints.GET_ALL_VIDEOOBJECT_UIDS.value}"
        return self._db_rest.GET(endpoint=endpoint, overrideLog=True)

    def DoesUIDExist(self, uid: str) -> Dict[str, Any]:
        if not uid:
            return self._messages.Error_message(
                caller=self._caller,
                status=400,
                endpoint="",
                error="UID parameter is empty or None",
                log=self._log
            )

        self._updateJWT()
        endpoint = f"{self._db_prefix}{Tasscom_DB_api.Endpoints.DOES_UID_EXIST.value.format(uid=uid)}"
        response = self._db_rest.GET(endpoint=endpoint, overrideLog=self._log)

        result = {
            "uid": uid,
            "exists": False,
            "defaulted_response": True,
            "rest_response": response
        }

        if response.get("status") == 200:
            message = response.get("data", {}).get("message")
            result["exists"] = self._clamp.ToBool(message)
            result["defaulted_response"] = False

        return result
