#logger.debug
from opentakserver.extensions import logger
from opentakserver.blueprints.TakatPersistantVideo_api.Validation import Validation

import requests
from requests.adapters import HTTPAdapter

from typing import Dict, Optional

class Rest:
    
    def __init__(self,
                 server: str = "127.0.0.1",
                 port: int = 0,
                 verify_ssl: bool = False,
                 jwt_token: Optional[str] = None,
                 retry: Optional[int] = 3,
                 ) -> None:
        
        """
            Initialize a reusable REST API client with optional authentication, SSL verification, and retry logic.

            This constructor creates a `requests.Session` for efficient connection reuse and mounts
            HTTP adapters with configurable retry behavior. It also allows optional JWT-based
            authentication and SSL verification control.

            Parameters
            ----------
            server : str, optional
                The server hostname, IPv4, or IPv6 address to connect to.
                Defaults to "127.0.0.1". IPv6 addresses should be enclosed in square brackets if a port is used.
            port : Optional[int], optional
                The TCP port of the server. Defaults to 0 (no port specified).
            verify_ssl : bool, optional
                If True, SSL certificates are verified for HTTPS requests.
                Set to False for self-signed certificates or local development.
            jwt_token : Optional[str], optional
                JSON Web Token for authenticated requests. If provided, it is included
                in the Authorization header of each request.
            retry : Optional[int], optional
                The number of automatic retry attempts for transient network or server errors
                (e.g., 502, 503, 504). Defaults to 3.

            Notes
            -----
            - The session is reused for multiple API calls to improve performance.
            - Retry logic uses an exponential backoff factor and is configurable via the `retry` parameter.
            - The server and port can be updated after initialization using the corresponding properties.
        """
        
        self._sess = requests.Session()
        self._verify_ssl = verify_ssl
        self._sess.verify = verify_ssl
        
        self._clamp = Validation()

        self._jwt = jwt_token
        self._server = self._clamp.FQDN(server)
        self._port = self._clamp.Port(port)
        self._retry = self._clamp.Range(max_value=3, min_value=0, value=retry)

        self._configure_session()

    # ------------------------
    # Session configuration
    # ------------------------
    def _configure_session(self):
        """(Re)configure the session retry behavior."""
        #   retries = Retry(total=self._retry, backoff_factor=3, status_forcelist=[502, 503, 504])
        #   adapter = HTTPAdapter(max_retries=retries)
        
        adapter = HTTPAdapter(max_retries=self._retry)
        self._sess.mount("http://", adapter)
        self._sess.mount("https://", adapter)

    # ------------------------
    # Properties (stateless reconfiguration)
    # ------------------------
    @property
    def server(self) -> str:
        return self._server
    @server.setter
    def server(self, value: str):
        logger.debug(f"{self._server}: Updating server to: {self._clamp.FQDN(fqdn=value)}")
        self._server = self._clamp.FQDN(fqdn=value)

    @property
    def port(self) -> int: return self._port
    @port.setter
    def port(self, value: int):
        logger.debug(f"{self._server}:Updating port to: {self._clamp.Port(value)}")
        self._port = self._clamp.Port(value)

    @property
    def verify_ssl(self) -> bool:
        return self._verify_ssl
    @verify_ssl.setter
    def verify_ssl(self, value: bool):
        logger.debug(f"{self._server}:Updating SSL verification to: {self._clamp.Bool(value=value)}")
        self._verify_ssl = self._clamp.Bool(value=value)
        self._sess.verify = self._clamp.Bool(value=value)

    @property
    def jwt_token(self) -> Optional[str]:
        return self._jwt
    @jwt_token.setter
    def jwt_token(self, value: Optional[str]):
        logger.debug(f"{self._server}:Updating JWT token to: SuperSecret")
        self._jwt = value

    @property
    def retry(self) -> int:
        return self._retry
    @retry.setter
    def retry(self, value: int):
        logger.debug(f"Updating retry count to: {self._clamp.Range(value=value, min_value=0, max_value=3)}")
        self._retry =  self._clamp.Range(value=value, min_value=0, max_value=3)
        self._configure_session()
          

    # ------------------------
    # Internal helpers for creating api calls
    # ------------------------
    def _build_url(self, endpoint: str) -> str:
        base = self._server.rstrip('/')
        if self._port and self._port != 0: base = f"{base}:{self._port}"
        return f"{base}/{endpoint.lstrip('/')}"
    
    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self._jwt: headers["Authorization"] = f"Bearer {self._jwt}"
        return headers
    
    def _call(self, method, endpoint, payload, logbook) -> dict:
        """        
        """
        full_url = None
        try:
            full_url = self._build_url(endpoint)
            headers = self._headers()
            
            if method == "GET":       response = self._sess.get(full_url, headers=headers, params=payload) 
            elif method== "POST":     response = self._sess.post(full_url, headers=headers, json=payload)
            elif method == "PATCH":   response = self._sess.patch(full_url, headers=headers, json=payload)
            elif method == "DELETE":  response = self._sess.delete(full_url, headers=headers, json=payload)
            else: return self._defaultError(caller="rest._call", endpoint=full_url, error="an unknown error has occured", log=True)  
            
            try: data = response.json()
            except ValueError: data = {"raw_text": response.text}

            if not response.ok:
                return self._defaultError(  caller="rest._call",
                                            endpoint=full_url,
                                            error=f"HTTP {response.status_code}: {data}",
                                            log=logbook)
                
            return {"status": response.status_code, "data": data}
            
        except Exception as e: return self._defaultError(caller="rest._call", endpoint=full_url, error=e, log=logbook)
        
    def _defaultError(self, caller, endpoint, error, log:bool=True) -> dict:
        """
            Builds a standardized error dictionary for API call failures.
            
            Args:
                caller: str — the method/class that initiated the API call
                endpoint: str — the URL of the API call
                error: str — the error message or exception
                log: bool — whether to log the error (default: True)
            
            Returns:
                dict — a structured dictionary describing the error
        """
        if log == True: logger.error(f"rest class: api call made by:{caller} to endpoint:{endpoint} encountered error:{error}")
        error_dict= {  "status": "error",
                        "caller": caller,
                        "endpoint": endpoint,
                        "error": str(error),
                    }
        return error_dict

    # ------------------------
    # API Calls
    # ------------------------
    def GET(self, endpoint, payload=None, log=True):     
        return self._call(method="GET",    endpoint=endpoint, payload=payload, logbook=log)
    
    def POST(self, endpoint, payload=None, log=True):  
        return self._call(method="POST",   endpoint=endpoint, payload=payload, logbook=log)
    
    def PATCH(self, endpoint, payload=None, log=True):   
        return self._call(method="PATCH",  endpoint=endpoint, payload=payload, logbook=log)
    
    def DELETE(self, endpoint, payload=None, log=True):  
        return self._call(method="DELETE", endpoint=endpoint, payload=payload, logbook=log)
        
