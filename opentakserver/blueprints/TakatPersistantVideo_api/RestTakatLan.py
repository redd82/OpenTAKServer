import requests
import ipaddress
from requests.adapters import HTTPAdapter
from typing import Optional, Dict, Any

from opentakserver.extensions import logger
from opentakserver.blueprints.TakatPersistantVideo_api.Validation import Validation
from opentakserver.blueprints.TakatInterApi_interface.defaultPluginConfig import DefaultPluginConfig as pluginConfig
from opentakserver.blueprints.TakatPersistantVideo_api.Takat_Logging import TakatLogger, TakatMessages


class RestTakatLan:
    """
    Robust REST client with:
    - JWT auth
    - retry and error handling
    - optional JWT/settings auto-refresh
    - debug and info logging
    """

    def __init__(
        self,
        server: str = "127.0.0.1",
        port: int = 0,
        verify_ssl: bool = False,
        jwt_token: Optional[str] = None,
        retry: int = 6,
        timeout: int = 5,
        auto_update: bool = True,
        log: bool = False,
        debug: bool = False,
    ):
        self._clamp = Validation()
        self._logging = TakatLogger()
        self._messages = TakatMessages()
        self._caller = "Takat Rest Client"

        self._maxretries = 10
        self._minretries = 1
        self._max_timeout = 30
        self._min_timeout = 1
        self._auto_update = auto_update

        self._sess = requests.Session()
        self._server = self._clamp.FQDN(server)
        self._port = self._clamp.Port(port)
        self._verify_ssl = verify_ssl
        self._jwt = jwt_token or ""
        self._timeout = self._clamp.Range(timeout, self._min_timeout, self._max_timeout)
        self._retry = self._clamp.Range(retry, self._minretries, self._maxretries)
        self._log = log
        self._debug = debug

        self._configure_session()

    # ------------------------
    # Session configuration
    # ------------------------
    def _configure_session(self):
        adapter = HTTPAdapter(max_retries=self._retry)
        self._sess.mount("http://", adapter)
        self._sess.mount("https://", adapter)
        self._logging.Debug(f"Session configured with {self._retry} retries.", self._caller, self._debug)

    # ------------------------
    # Properties
    # ------------------------
    @property
    def log(self) -> bool:
        return self._log

    @log.setter
    def log(self, value: bool):
        self._log = self._clamp.ToBool(value)
        self._logging.Info(f"Logging set to: {self._log}", self._caller, self._log)

    @property
    def debug(self) -> bool:
        return self._debug

    @debug.setter
    def debug(self, value: bool):
        self._debug = self._clamp.ToBool(value)
        self._logging.Debug(f"Debug set to: {self._debug}", self._caller, self._debug)

    @property
    def timeout(self) -> int:
        return self._timeout

    @timeout.setter
    def timeout(self, value: int):
        self._timeout = self._clamp.Range(value, self._min_timeout, self._max_timeout)
        self._logging.Debug(f"Timeout updated to {self._timeout} seconds", self._caller, self._debug)

    @property
    def jwt_token(self) -> str:
        return self._jwt

    @jwt_token.setter
    def jwt_token(self, value: str):
        self._jwt = value or ""
        masked = self._logging.mask_for_logging(self._jwt)
        self._logging.Info(f"JWT updated to: {masked}", self._caller, self._log)

    @property
    def retry(self) -> int:
        return self._retry

    @retry.setter
    def retry(self, value: int):
        self._retry = self._clamp.Range(value, self._minretries, self._maxretries)
        self._configure_session()
        self._logging.Debug(f"Retry count updated to {self._retry}", self._caller, self._debug)

    @property
    def auto_update(self) -> bool:
        return self._auto_update

    @auto_update.setter
    def auto_update(self, value: bool):
        self._auto_update = bool(value)
        self._logging.Debug(f"Auto-update set to {self._auto_update}", self._caller, self._debug)

    # ------------------------
    # Internal helpers
    # ------------------------
    def _build_url(self, endpoint: str) -> str:
        host = self._server.rstrip('/')
        if not host.startswith(("http://", "https://")):
            scheme = "https" if self._verify_ssl else "http"
            try:
                ip = ipaddress.ip_address(host)
                if ip.version == 6:
                    host = f"[{host}]"
            except ValueError:
                pass
            host = f"{scheme}://{host}"

        if self._port and self._port != 0:
            host = f"{host}:{self._port}"

        return f"{host}/{endpoint.lstrip('/')}"

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self._jwt:
            headers["Authorization"] = f"Bearer {self._jwt}"
        return headers

    def _refresh_plugin_settings(self, update_jwt_only: bool = False):
        if update_jwt_only:
            self.jwt_token = pluginConfig.TascommAccessToken or self._jwt
            self._logging.Info("JWT token refreshed from pluginConfig", self._caller, self._log)
            return

        self._server = self._clamp.FQDN(getattr(pluginConfig, "Server", self._server))
        self._port = self._clamp.Port(getattr(pluginConfig, "Port", self._port))
        self._verify_ssl = bool(getattr(pluginConfig, "VerifySSL", self._verify_ssl))
        self.jwt_token = pluginConfig.TascommAccessToken or self._jwt
        self._logging.Info(f"PluginConfig fully refreshed: server={self._server}, port={self._port}, SSL={self._verify_ssl}, JWT updated", self._caller, self._log)

    # ------------------------
    # Core HTTP call
    # ------------------------
    def _call(
        self,
        method: str,
        endpoint: str,
        payload: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None,
        log: Optional[bool] = None,
        forceUpdateOnFail: Optional[bool] = None,
    ) -> dict:
        timeout = timeout or self._timeout
        attempt = 0
        full_url = self._build_url(endpoint)
        log = log if log is not None else self._log
        force_update_on_fail = self._auto_update if forceUpdateOnFail is None else forceUpdateOnFail

        while attempt < self._retry:
            attempt += 1
            try:
                headers = self._headers()
                self._debug_log(f"Preparing {method} request", full_url, headers, payload)
                self._log_action(f"{method} {full_url} with payload {payload}")

                # Execute request
                response = getattr(self._sess, method.lower())(
                    full_url,
                    headers=headers,
                    json=payload if method.upper() in ("POST", "PATCH", "DELETE") else None,
                    params=payload if method.upper() == "GET" else None,
                    timeout=timeout,
                )

                try:
                    data_parsed = response.json()
                except ValueError:
                    self._logging.Error(f"Response not JSON: {response.text}", self._caller)
                    data_parsed = {"raw_response": response.text}

                data_to_send = data_parsed if data_parsed is not None else self._messages.blank_string(None)

                if response.ok:
                    return self._messages.Success_message(
                        caller=self._caller,
                        status=response.status_code,
                        endpoint=full_url,
                        msg=f"{method} call successful",
                        log=log,
                        data=data_to_send
                    )

                if response.status_code in (401, 403) and attempt == 1 and force_update_on_fail:
                    self._refresh_plugin_settings(update_jwt_only=True)
                    self._logging.Info(f"JWT refreshed on first failure, retrying attempt {attempt}", self._caller, log)
                    continue

                return self._messages.Error_message(
                    caller=self._caller,
                    status=response.status_code,
                    endpoint=full_url,
                    error=str(data_parsed),
                    log=log,
                    data=data_to_send
                )

            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, Exception) as e:
                if attempt == 1 and force_update_on_fail:
                    self._refresh_plugin_settings(update_jwt_only=True)
                if attempt == self._retry - 1:
                    self._refresh_plugin_settings(update_jwt_only=False)
                    self._logging.Info("Full pluginConfig refresh applied before last attempt", self._caller, log=log)
                if attempt < self._retry:
                    self._logging.Warning(f"{type(e).__name__} on {method} {endpoint}: {e}, retrying attempt {attempt}", self._caller, log=log)
                    continue
                self._logging.Error(f"All attempts failed: {type(e).__name__}: {e}", self._caller)
                return self._messages.Error_message(
                    caller=self._caller,
                    endpoint=full_url,
                    error=f"{type(e).__name__}: {e}",
                    log=log,
                    data=self._messages.blank_string(None)
                )

        return self._messages.Error_message(
            caller=self._caller,
            endpoint=full_url,
            error=f"{method} {endpoint} failed after {self._retry} attempts",
            log=log,
            data=self._messages.blank_string(None)
        )

    # ------------------------
    # Logging helpers
    # ------------------------
    def _debug_log(self, message: str, endpoint: str, headers: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None):
        if not self._debug:
            return
        masked_headers = headers.copy() if headers else {}
        if "Authorization" in masked_headers:
            masked_headers["Authorization"] = self._logging.mask_for_logging(masked_headers["Authorization"])
        self._logging.Debug(f"{message}, endpoint: {endpoint}, headers: {masked_headers}, params: {params}", self._caller, self._debug)

    def _log_action(self, message: str):
        if self._log:
            self._logging.Info(f"Log: {message}", self._caller, self._log)

    # ------------------------
    # Convenience HTTP methods
    # ------------------------
    def GET(self, endpoint, payload=None, forceUpdate: bool = False, overrideLog: Optional[bool] = None):
        return self._call("GET", endpoint, payload=payload, forceUpdateOnFail=forceUpdate, log=overrideLog)

    def POST(self, endpoint, payload=None, forceUpdate: bool = False, overrideLog: Optional[bool] = None):
        return self._call("POST", endpoint, payload=payload, forceUpdateOnFail=forceUpdate, log=overrideLog)

    def PATCH(self, endpoint, payload=None, forceUpdate: bool = False, overrideLog: Optional[bool] = None):
        return self._call("PATCH", endpoint, payload=payload, forceUpdateOnFail=forceUpdate, log=overrideLog)

    def DELETE(self, endpoint, payload=None, forceUpdate: bool = False, overrideLog: Optional[bool] = None):
        return self._call("DELETE", endpoint, payload=payload, forceUpdateOnFail=forceUpdate, log=overrideLog)
