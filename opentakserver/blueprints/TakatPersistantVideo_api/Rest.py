#logger.debug
from opentakserver.extensions import logger
from opentakserver.blueprints.TakatPersistantVideo_api.Validation import Validation

import requests
import ipaddress
from requests.adapters import HTTPAdapter

from typing import Dict, Optional

class Rest:
    
    def __init__(self,
                 server: str = "127.0.0.1",
                 port: int = 0,
                 verify_ssl: bool = False,
                 jwt_token: Optional[str] = None,
                 retry: Optional[int] = 3,
                 timeout: Optional[int] = 5,
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

        #------------------------
        # Initialization
        #------------------------
        self._clamp = Validation()
        self._sess = requests.Session()
        
        self._verify_ssl = verify_ssl
        self._sess.verify = verify_ssl
        self._jwt = jwt_token
        
        self._timeout = self._clamp.Range(value=timeout or 5, min_value=1, max_value=30)
        self._server = self._clamp.FQDN(server)
        self._port = self._clamp.Port(port)
        self._retry = self._clamp.Range(max_value=3, min_value=0, value=retry or 3)

        self._log = False            
        self._debug = False            
        
        self._configure_session()   #default configuration of the session retries

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
    def log(self) -> bool:
        return self._log
    @log.setter
    def log(self, value: bool):
        data = self._clamp.ToBool(value=value)
        self._log = data
        self._infologger(f"Updating logging to: {data}")
        self._debuglogger(f"Updating logging to: {data}")
    
    @property
    def debug(self) -> bool:
        return self._debug
    @debug.setter
    def debug(self, value: bool):
        data = self._clamp.ToBool(value=value)
        self._debug = data
        self._infologger(f"Updating debugging to: {data}")
        self._debuglogger(f"Updating debugging to: {data}")
    
    @property
    def timeout(self) -> int: return self._timeout
    @timeout.setter
    def timeout(self, value: int):
        data = self._clamp.Range(value=value, min_value=1, max_value=30)
        self._debuglogger(f"{self._timeout}: Updating timeout to: {data}")
        self._infologger(f"{self._timeout}: Updating timeout to: {data}")
        self._timeout = data
    
    @property
    def server(self) -> str:
        return self._server
    @server.setter
    def server(self, value: str):
        data =self._clamp.FQDN(fqdn=value)
        self._debuglogger(f"{self._server}: Updating server to: {data}")
        self._infologger(f"{self._server}: Updating server to: {data}")
        self._server = data

    @property
    def port(self) -> int: return self._port
    @port.setter
    def port(self, value: int):
        data = self._clamp.Port(value)
        self._debuglogger(f"{self._server}:Updating port to: {data}")
        self._infologger(f"{self._server}:Updating port to: {data}")
        self._port = data

    @property
    def verify_ssl(self) -> bool:
        return self._verify_ssl
    @verify_ssl.setter
    def verify_ssl(self, value: bool):
        data = self._clamp.ToBool(value=value)
        self._debuglogger(f"{self._server}:Updating SSL verification to: {data}")
        self._infologger(f"{self._server}:Updating SSL verification to: {data}")
        self._verify_ssl = data
        self._sess.verify = data

    @property
    def jwt_token(self) -> Optional[str]:
        return self._jwt
    @jwt_token.setter
    def jwt_token(self, value: str):
        data = value if value is not None else ""
        self._infologger(f"{self._server}:Updating JWT token to: {data}")
        self._debuglogger(f"{self._server}:Updating JWT token to: {data}")
        self._jwt = data # data or value?

    @property
    def retry(self) -> int:
        return self._retry
    @retry.setter
    def retry(self, value: int):
        data = self._clamp.Range(value=value, min_value=0, max_value=3)
        self._debuglogger(f"Updating retry count to: {data}")
        self._infologger(f"Updating retry count to: {data}")
        self._retry =  data
        self._configure_session()   # reconfigure session with new retry count
        
    # ------------------------
    # Internal helpers for creating api calls
    # ------------------------
    
    def _build_url(self, endpoint: str) -> str:
        host = self._server.rstrip('/')

        if not host.startswith(("http://", "https://")):
            scheme = "https" if self._verify_ssl else "http"

            # Wrap IPv6 literals in brackets (NO mutation)
            try:
                ip = ipaddress.ip_address(host)
                if ip.version == 6:
                    host = f"[{host}]"
            except ValueError:
                pass  # not an IP address

            base = f"{scheme}://{host}"
        else:
            base = host

        if self._port and self._port != 0:
            base = f"{base}:{self._port}"

        return f"{base}/{endpoint.lstrip('/')}"
    
    def _headers(self) -> Dict[str, str]:
            headers = {"Content-Type": "application/json"}
            if self._jwt: headers["Authorization"] = f"Bearer {self._jwt}"
            return headers
    
    def _call(self, method, endpoint, payload, timeout, log=False) -> dict:
        """        
        """
        full_url = None
        try:
            full_url = self._build_url(endpoint)
            headers = self._headers()
            
            if method == "GET":       response = self._sess.get(full_url, headers=headers, params=payload or {}, timeout=timeout) 
            elif method== "POST":     response = self._sess.post(full_url, headers=headers, json=payload, timeout=timeout)
            elif method == "PATCH":   response = self._sess.patch(full_url, headers=headers, json=payload, timeout=timeout)
            elif method == "DELETE":  response = self._sess.delete(full_url, headers=headers, json=payload, timeout=timeout)
            else: return self._defaultError(caller="rest._call", endpoint=full_url, error="an unknown error has occured", log=log)  
            
            try: data = response.json()
            except ValueError: data = {"raw_response": response.text}
            
            # Handle success and error responses
            if response.ok:
                return self._defaultSuccess(    caller="rest._call",
                                                endpoint=full_url,
                                                event=f"successful {method} call",
                                                log=log,
                                                status=response.status_code,
                                                data=data)
            # Handle non-2xx responses
            if not response.ok:
                return self._defaultError(  caller="rest._call",
                                            endpoint=full_url,
                                            error=f"{response.status_code}: {data}",
                                            log=log,
                                            status=response.status_code,
                                            data=data)
            # Catch HTTP errors explicitly
            return self._defaultError(  caller="rest._call",
                                            endpoint=full_url,
                                            error=f"{500}: {data}",
                                            log=log,
                                            status=500)
            
        
        # Catch timeout explicitly
        except requests.exceptions.Timeout:
            return self._defaultError(
                caller="rest._call",
                endpoint=full_url,
                error=f"Request timed out after {timeout} seconds", 
                log=log,
                status=504  # Gateway Timeout
            )

        # Catch connection errors explicitly
        except requests.exceptions.ConnectionError as e:
            return self._defaultError(
                caller="rest._call",
                endpoint=full_url,
                error=f"Connection error: {e}",
                log=log,
                status=503  # Service Unavailable
            )

        # Catch all other exceptions
        except Exception as e:
            return self._defaultError(
                caller="rest._call",
                endpoint=full_url,
                error=str(e),
                log=log,
                status=500
            )
    
    def _defaultError(self, caller, endpoint, error, log=True, status=500, data=None) ->dict:
    #def _defaultError(self, caller, endpoint, data: None, log:bool=True, status: Optional[int] =500, error: Optional[str] = "an unknown error has occured") -> dict:
        """
        """
        # Return data directly if provided
        if data not in (None, "", {}, []):
            return data
        
        # Otherwise return wrapper
        if log == True: logger.error(f"rest class: api call made by:{caller} to endpoint:{endpoint} encountered error:{error}")
        error_dict= {   "status": status,
                        "caller": caller,
                        "endpoint": endpoint,
                        "event": error,
                    }
        return error_dict
    
    def _defaultSuccess(self, caller, endpoint, event, log=False, status=200, data=None):
    #def _defaultSuccess(self, caller, endpoint, event, data: None, log:bool=False, status: Optional[int] =200) -> dict:
        # Return data directly if provided
        if data not in (None, "", {}, []):
            return data

        # Otherwise return wrapper
        
        if log == True: logger.info(f"rest class: api call made by:{caller} to endpoint:{endpoint} status:{status}")
        message_dict= { "status": status,
                        "caller": caller,
                        "endpoint": endpoint,
                        "event": str(event),
                    }
        return message_dict

    # ------------------------
    # rest messages Convenience
    # ------------------------
    def MessageStatus(self, response: dict) -> int:
        """
        Safely extract a numeric status code from a REST response dictionary.
        Returns 0 if status is missing, invalid, or the response is not a dict.
        
        Parameters
        ----------
        response : dict
            The response dict returned by a GET/POST/PATCH/DELETE call.
        
        Returns
        -------
        int
            The HTTP/API status code, or 0 if unknown.
        """
        if not isinstance(response, dict):
            return 0  # invalid response, can't extract status
        try:
            # Look for common keys in your _defaultError/_defaultSuccess wrappers
            return int(response.get("status", 0))
        except (ValueError, TypeError):
            return 0  # can't convert to int


    # ------------------------
    # API Calls
    # ------------------------
    def GET(self, endpoint, payload=None, log=False):    return self._call(method="GET",    endpoint=endpoint, payload=payload, timeout=self._timeout, log=log)
    def POST(self, endpoint, payload=None, log=False):   return self._call(method="POST",   endpoint=endpoint, payload=payload, timeout=self._timeout, log=log)
    def PATCH(self, endpoint, payload=None, log=False):  return self._call(method="PATCH",  endpoint=endpoint, payload=payload, timeout=self._timeout, log=log)
    def DELETE(self, endpoint, payload=None, log=False): return self._call(method="DELETE", endpoint=endpoint, payload=payload, timeout=self._timeout, log=log)
        

    def _debuglogger(self, message: str):
        if self._debug: logger.debug(f"[Rest API Client] {message}")
        return

    def _infologger(self, message: str):
        if self._log: logger.info(f"[Rest API Client] {message}")
        return
    
    