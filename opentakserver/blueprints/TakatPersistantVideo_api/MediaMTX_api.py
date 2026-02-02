from enum import Enum
from typing import Any, Dict, Optional, Union
from enum import Enum
from contextlib import contextmanager

from opentakserver.extensions import logger     #logger.debug

# ─────────────────────────────────────────────────────────────────────────────
# Third‑party / project imports
# ────────────────────────────────────────────────────────────────────────────
from opentakserver.blueprints.TakatPersistantVideo_api.Rest import Rest
from opentakserver.blueprints.TakatPersistantVideo_api.Validation import Validation
from opentakserver.blueprints.TakatPersistantVideo_api.models.MediaMTXPathConfig import MediaMTXPathConfig as MTXConfig



class MediaMTX_api:    
    
    class Endpoints(Enum):

        # Which api calls are available in this MediaMTX API
        CREATE_PATH = "/v3/config/paths/add/{name}"     # post
        """
            /v3/config/paths/add/{name}:
            post:
            operationId: configPathsAdd
            tags: [Configuration]
            summary: adds a path configuration.
            description: all fields are optional.
            parameters:
            - name: name
                in: path
                required: true
                description: the name of the path.
                schema:
                type: string
            requestBody:
                required: true
                content:
                application/json:
                    schema:
                    $ref: '#/components/schemas/PathConf'
            responses:
                '200':
                description: the request was successful.
                '400':
                description: invalid request.
                content:
                    application/json:
                    schema:
                        $ref: '#/components/schemas/Error'
                '500':
                description: server error.
                content:
                    application/json:
                    schema:
                        $ref: '#/components/schemas/Error'
        """                      
        PATCH_PATH = "/v3/config/paths/patch/{name}"    # patch
        """
            /v3/config/paths/patch/{name}:
            patch:
            operationId: configPathsPatch
            tags: [Configuration]
            summary: patches a path configuration.
            description: all fields are optional.
            parameters:
            - name: name
                in: path
                required: true
                description: the name of the path.
                schema:
                type: string
            requestBody:
                required: true
                content:
                application/json:
                    schema:
                    $ref: '#/components/schemas/PathConf'
            responses:
                '200':
                description: the request was successful.
                '400':
                description: invalid request.
                content:
                    application/json:
                    schema:
                        $ref: '#/components/schemas/Error'
                '404':
                description: path not found.
                content:
                    application/json:
                    schema:
                        $ref: '#/components/schemas/Error'
                '500':
                description: server error.
                content:
                    application/json:
                    schema:
                        $ref: '#/components/schemas/Error'
        """                             
        DELETE_PATH = "/v3/config/paths/delete/{name}"  # delete
        """
            /v3/config/paths/delete/{name}:
            delete:
            operationId: configPathsDelete
            tags: [Configuration]
            summary: removes a path configuration.
            description: ''
            parameters:
            - name: name
                in: path
                required: true
                description: the name of the path.
                schema:
                type: string
            responses:
                '200':
                description: the request was successful.
                '400':
                description: invalid request.
                content:
                    application/json:
                    schema:
                        $ref: '#/components/schemas/Error'
                '404':
                description: path not found.
                content:
                    application/json:
                    schema:
                        $ref: '#/components/schemas/Error'
                '500':
                description: server error.
                content:
                    application/json:
                    schema:
                        $ref: '#/components/schemas/Error'
        """
        GET_PATH = "/v3/config/paths/get/{name}"        # get
        """
            /v3/config/paths/get/{name}:
            get:
            operationId: configPathsGet
            tags: [Configuration]
            summary: returns a path configuration.
            description: ''
            parameters:
            - name: name
                in: path
                required: true
                description: the name of the path.
                schema:
                type: string
            responses:
                '200':
                description: the request was successful.
                content:
                    application/json:
                    schema:
                        $ref: '#/components/schemas/PathConf'
                '400':
                description: invalid request.
                content:
                    application/json:
                    schema:
                        $ref: '#/components/schemas/Error'
                '404':
                description: path not found.
                content:
                    application/json:
                    schema:
                        $ref: '#/components/schemas/Error'
                '500':
                description: server error.
                content:
                    application/json:
                    schema:
                        $ref: '#/components/schemas/Error'
        """ 
        LIST_PATHS = "/v3/config/paths/list"            # get
        """
            /v3/config/paths/list:
            get:
            operationId: configPathsList
            tags: [Configuration]
            summary: returns all path configurations.
            description: ''
            parameters:
            - name: page
                in: query
                description: page number.
                schema:
                type: integer
                default: 0
            - name: itemsPerPage
                in: query
                description: items per page.
                schema:
                type: integer
                default: 100
            responses:
                '200':
                description: the request was successful.
                content:
                    application/json:
                    schema:
                        $ref: '#/components/schemas/PathConfList'
                '400':
                description: invalid request.
                content:
                    application/json:
                    schema:
                        $ref: '#/components/schemas/Error'
                '500':
                description: server error.
                content:
                    application/json:
                    schema:
                        $ref: '#/components/schemas/Error'
            """     
    
    # context manager to allow for calls to other mediamtx servers if needed
    @contextmanager
    def _override_rest(self,
                       fqdn: Optional[str] = None,
                       port: Optional[int] = None,
                       retries: Optional[int] = None,
                       verified_ssl: Optional[bool] = None,
                       Jwt: Optional[str] = None):
        """
        Context manager to temporarily override self._rest parameters.
        Restores original values automatically on exit.
        """
        # Backup current Rest parameters
        orig_params = {
            "server": self._rest.server,
            "port": self._rest.port,
            "retry": self._rest.retry,
            "verify_ssl": self._rest.verify_ssl,
            "jwt_token": self._rest.jwt_token
        }

        # Apply overrides
        if fqdn is not None:
            self._rest.server = self._clamp.FQDN(fqdn)
        if port is not None:
            self._rest.port = self._clamp.Port(port)
        if retries is not None:
            self._rest.retry = self._clamp.Range(value=retries, max_value=self._maxretries, min_value=self._minretries)
        if verified_ssl is not None:
            self._rest.verify_ssl = self._clamp.ToBool(verified_ssl)
        if Jwt is not None:
            self._rest.jwt_token = self._clamp.JsonWebToken(Jwt)

        try:
            yield
        finally:
            # Restore original parameters
            self._rest.server = orig_params["server"]
            self._rest.port = orig_params["port"]
            self._rest.retry = orig_params["retry"]
            self._rest.verify_ssl = orig_params["verify_ssl"]
            self._rest.jwt_token = orig_params["jwt_token"]

       
    def __init__(self, fqdn: str, port: int, retries: int, verified_ssl: bool, Jwt: Optional[str] = None):
        """
        Initialize the MediaMTX_api class.
        
        Args:
            mediaMTXToken (str):the secret token needed to be authorized
            fqdn (str):         the fqdn or ip of where the api lives. ie takat.nl or 8.8.8.8
            port (int):         the port number where the api lives (if you don't know just set it to 80 for http)
            retries (int):      the number of retries if an api call fails (max 3)
            verified_ssl (bool): whether to verify ssl certificates when making api calls
            Jwt (Optional[str]): JWT token for authentication with the MediaMTX API.
        """
        self._clamp = Validation()                          # stateless class used to validate inputs   
        self._fqdn = self._clamp.FQDN(fqdn)                 # the fqdn ip4 or ip6 address of the server
        self._port = self._clamp.Port(port)                 # the port where the api lives (if none is used set to 0)
        
        self._maxretries = 3                                # maximum retries if an api call fails 
        self._minretries = 0                                # minimum retries if an api call fails
        
        self._retries = self._clamp.Range(value=retries, max_value=self._maxretries, min_value=self._minretries)  #maximum retries if an api call fails
        self._verified_ssl = verified_ssl or False          # verify is the api call uses ssl (we prefer not to)

        self._jwt = self._clamp.JsonWebToken(Jwt) if Jwt else ""         
        
        self._rest = Rest(server=self._fqdn, verify_ssl=self._verified_ssl, jwt_token=self._jwt, retry=self._retries, port=self._port) #create a rest  object to handle api calls 
        self._config = MTXConfig()  # initialize empty config object
    
    # ─────────────────────────────────────────────────────────────────────────────
    # Getters and Setters
    # ─────────────────────────────────────────────────────────────────────────────
    
    @property
    def FQDN(self): return self._fqdn
    @FQDN.setter
    def FQDN(self, value): 
        self._fqdn = self._clamp.FQDN(value)        # set the FQDN for the MediaMTX api object (the new default)
        self._rest.server = self._clamp.FQDN(value) # set the FQDN for the Rest object (the new default)
        
    @property
    def Port(self): return self._port
    @Port.setter
    def Port(self, value): 
        self._port = self._clamp.Port(value)
        self._rest.port = self._clamp.Port(value)

    @property
    def Jwt(self): return self._jwt
    @Jwt.setter
    def Jwt(self, value): 
        self._jwt = self._clamp.JsonWebToken(value)
        self._rest.jwt_token = self._clamp.JsonWebToken(value)
    
    @property
    def VerifiedSSL(self): return self._verified_ssl
    @VerifiedSSL.setter
    def VerifiedSSL(self, value): 
        self._verified_ssl = bool(value)
        self._rest.verify_ssl = bool(value)
    
    @property
    def Retries(self): return self._retries
    @Retries.setter
    def Retries(self, value): 
        self._retries = self._clamp.Range(value=value, max_value=self._maxretries, min_value=self._minretries)
        self._rest.retry = self._clamp.Range(value=value, max_value=self._maxretries, min_value=self._minretries)


    def _defaultreply(self, caller:str, endpoint: str, status: int, msg: Optional[str] = "") -> dict:
        msg_dict = {
                "status": str(status),
                "caller": str(caller),
                "endpoint": str(endpoint),
                "message": str(msg),
        }
        logger.info(f"MediaMTX_api: {caller} | Endpoint: {endpoint} | response: {status}, | message: {msg}")
        return msg_dict     


    def _extract_status(self, response: dict) -> int:
        """
        Safely extract numeric status from a REST response.
        Returns 0 if status is missing or response is invalid.
        """
        if not isinstance(response, dict):
            return 0  # completely invalid response
        try:
            return int(response.get("status", 0))
        except (ValueError, TypeError):
            return 0  # status exists but can't convert to int
        
    # ─────────────────────────────────────────────────────────────────────────────
    # defined API calls
    # ─────────────────────────────────────────────────────────────────────────────

    def CreatePath( self, uid: str, fqdn: Optional[str] = None, port: Optional[int] = None, retries: Optional[int] = None, verified_ssl: Optional[bool] = None,
                    Jwt: Optional[str] = None, config: Optional[Dict[str, Any]]= None, log=True ) -> dict:
        """
        Create a new MediaMTX path with the given configuration.
        Temporarily override Rest parameters if provided.
        
        Args:
            fqdn (str, optional): Temporary FQDN for this call.
            port (int, optional): Temporary port for this call.
            retries (int, optional): Temporary retry count.
            verified_ssl (bool, optional): Temporary SSL verification.
            Jwt (str, optional): Temporary JWT token.
            config (MediaMTXPathConfig, optional): Configuration for the new path.
        
        Returns:
            dict: The created path or the error
        """
        
        
            # Convert dict to MTXConfig if needed, otherwise fallback to default
        if isinstance(config, dict):
            config_obj = MTXConfig.from_dict(config)
        elif isinstance(config, MTXConfig):
            config_obj = config
        else:
            config_obj = self._config  # fallback to default

        # Serialize to dict suitable for MediaMTX API
        payload = config_obj.to_mediamtx_dict()

        endpoint = MediaMTX_api.Endpoints.CREATE_PATH.value.format(name=uid) # Format endpoint

        #make the api call with temporary overrides if set
        #with self._override_rest(fqdn, port, retries, verified_ssl, Jwt): response = self._rest.POST(endpoint, payload=payload, log=True)
        with self._override_rest(fqdn, port, retries, verified_ssl, Jwt): 
            
            response = self._rest.POST(endpoint, payload=payload, log=True)     # create a path with a setup
            
            # Example outputs: 
            # Sending AddPath request to MediaMTX... reply successful
            #       {"Status":{"caller":"rest._call","endpoint":"http://127.0.0.1:9997/v3/config/paths/add/123","event":"successful POST call","status":200}}
            #       HTTP status: 200
            # Sending AddPath request to MediaMTX... reply error
            #       {"Status":{"caller":"rest._call","endpoint":"http://127.0.0.1:9997/v3/config/paths/add/123","event":"400: {'error': 'path already exists'}","status":400}}
            #       HTTP status: 200
            
            # Note the HTTP status is always 200 as long as the api call was received,
            # the actual success or failure is in the returned json 'status' field.
            
            status_code = self._extract_status(response) # extract status code safely
            if status_code == 200:
                if log == True: logger.info(f"MediaMTX_api CreatePath: API call successful: {response}")
            else:
                if log == True: logger.error(f"MediaMTX_api CreatePath: API call failed with status {status_code}: {response}")

            return response 


    def PatchPath(  self, uid: str, fqdn: Optional[str] = None, port: Optional[int] = None, retries: Optional[int] = None, verified_ssl: Optional[bool] = None,
                    Jwt: Optional[str] = None, updates: Optional[Dict[str, Any]] = None, log: bool = False) -> dict:
        """
        Patch an existing MediaMTX path with the given updates.
        Temporarily override Rest parameters if provided.
        
        Args:
            uid (str): The name/UID of the path to patch.
            fqdn (str, optional): Temporary FQDN for this call.
            port (int, optional): Temporary port for this call.
            retries (int, optional): Temporary retry count.
            verified_ssl (bool, optional): Temporary SSL verification.
            Jwt (str, optional): Temporary JWT token.
            updates (dict, optional): Fields to update. Falls back to self._config if not provided.
        
        Returns:
            dict: The patched path or the error
        """
        
        # Use the passed updates or fallback to self._config
        if updates is None:
            config_to_use = self._config
            payload = dict(config_to_use.to_mediamtx_dict())
            
        else:
            data = MTXConfig.from_dict(updates)    # try and load the config into a config object
            payload = data.to_mediamtx_dict()   # convert back to a dict suitable for mediamtx api
        


        # Format endpoint
        endpoint = MediaMTX_api.Endpoints.PATCH_PATH.value.format(name=uid)
        #make the api call with temporary overrides if set  
        with self._override_rest(fqdn, port, retries, verified_ssl, Jwt): response = self._rest.PATCH(endpoint, payload=payload, log=log)
        
        # Handle response
        status_code = self._extract_status(response) # extract status code safely
        
        if status_code == 200:
            if log == True: logger.info(f"MediaMTX_api PatchPath: API call successful: {response}")
        else:
            if log == True: logger.error(f"MediaMTX_api PatchPath: API call failed with status {status_code}: {response}")
            
        return response 
   
    def DeletePath(self, uid: str, fqdn: Optional[str] = None, port: Optional[int] = None, retries: Optional[int] = None, verified_ssl: Optional[bool] = None, 
                   Jwt: Optional[str] = None, log: bool = False)  -> dict:
        """
        Delete a MediaMTX path by UID.
        Temporarily override Rest parameters if provided.
        
        Args:
            uid (str): The unique identifier of the path to delete.
            fqdn (str, optional): Temporary FQDN for this call.
            port (int, optional): Temporary port for this call.
            retries (int, optional): Temporary retry count.
            verified_ssl (bool, optional): Temporary SSL verification.
            Jwt (str, optional): Temporary JWT token.

        Returns:
            dict: The result of the deletion or an error.
        """

        endpoint = MediaMTX_api.Endpoints.DELETE_PATH.value.format(name=uid)

        with self._override_rest(fqdn, port, retries, verified_ssl, Jwt): response = self._rest.DELETE(endpoint, log=log)
        
        status_code = self._extract_status(response) # extract status code safely
        if status_code == 200:
            if log == True: logger.info(f"MediaMTX_api PatchPath: API call successful: {response}")
        else:
            if log == True: logger.error(f"MediaMTX_api PatchPath: API call failed with status {status_code}: {response}")
            
        return response 
   

    def GetPath(self, uid: str, fqdn: Optional[str] = None, port: Optional[int] = None,retries: Optional[int] = None, 
                verified_ssl: Optional[bool] = None, Jwt: Optional[str] = None, log: bool = False) -> dict:
        """
        Retrieve a MediaMTX path configuration by UID.
        Temporarily override Rest parameters if provided.

        Args:
            uid (str): The unique identifier of the path to retrieve.
            fqdn (str, optional): Temporary FQDN for this call.
            port (int, optional): Temporary port for this call.
            retries (int, optional): Temporary retry count.
            verified_ssl (bool, optional): Temporary SSL verification.
            Jwt (str, optional): Temporary JWT token.

        Returns:
            dict: The retrieved path configuration or an error dictionary.
        """
        

        endpoint = MediaMTX_api.Endpoints.GET_PATH.value.format(name=uid)
        with self._override_rest(fqdn, port, retries, verified_ssl, Jwt): response = self._rest.GET(endpoint, log=log)

        # Handle response
        status_code = self._extract_status(response) # extract status code safely
        if status_code == 200:
            if log == True: logger.info(f"MediaMTX_api GetPath: API call successful: {response}")
        else:
            if log == True: logger.error(f"MediaMTX_api GetPath: API call failed with status {status_code}: {response}")
            
        return response 

    def ListPaths( self, fqdn: Optional[str] = None, port: Optional[int] = None, retries: Optional[int] = None, 
                  verified_ssl: Optional[bool] = None, Jwt: Optional[str] = None, log: bool = False) -> Union[list[dict], dict]:
        """
        Retrieve all MediaMTX paths with optional temporary REST overrides.

        Returns:
            list[dict]: On success.
            dict: _defaultreply() on error or unexpected format.
        """

        endpoint = MediaMTX_api.Endpoints.LIST_PATHS.value
        with self._override_rest(fqdn, port, retries, verified_ssl, Jwt): response = self._rest.GET(endpoint, log=log)
        #with self._override_rest(fqdn, port, retries, verified_ssl, Jwt): response = self._rest.GET(endpoint, log=log)

        # Handle response
        status_code = self._extract_status(response) # extract status code safely
        if status_code == 200:
            if log == True: logger.info(f"MediaMTX_api GetPath: API call successful: {response}")
        else:
            if log == True: logger.error(f"MediaMTX_api GetPath: API call failed with status {status_code}: {response}")

        # Expecting a list of path configurations
        return response 
    
    def PathExists( self, uid: str, fqdn: Optional[str] = None,
                    port: Optional[int] = None, retries: Optional[int] = None,
                    verified_ssl: Optional[bool] = None, Jwt: Optional[str] = None,
                    log: bool = False) -> bool:
        """
        Check whether a MediaMTX path exists.

        Calls ListPaths() and searches for a path with the given name.

        Args:
            name (str): Path name to check.
            fqdn (str, optional): Temporary FQDN override.
            port (int, optional): Temporary port override.
            retries (int, optional): Temporary retry override.
            verified_ssl (bool, optional): Temporary SSL verification override.
            Jwt (str, optional): Temporary JWT override.
            log (bool): Enable logging.

        Returns:
            bool: True if the path exists, False otherwise.
        """

        # grab all apths on the server
        response = self.ListPaths(fqdn=fqdn, port=port, retries=retries, verified_ssl=verified_ssl, Jwt=Jwt, log=log)

        # ListPaths should return a list on success
        if not isinstance(response, list):
            if log:
                logger.error(f"PathExists: unexpected response format: {response}")
            return False

        # Check for matching path name
        return any(
            isinstance(path, dict) and path.get("name") == uid
            for path in response
        )