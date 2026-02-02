# ─────────────────────────────────────────────────────────────────────────────
# Takat Standardized Logging and Message Functions
# ─────────────────────────────────────────────────────────────────────────────
import logging
import random
import string
from typing import Any, Optional

from opentakserver.extensions import logger  # logger.debug, logger.info, etc.


# ─────────────────────────────────────────────────────────────────────────────
# Logger
# ─────────────────────────────────────────────────────────────────────────────
class TakatLogger:
    """Standardized logging for Takat server."""

    def mask_for_logging(self, token: Optional[str]) -> str:
        """
        Mask a sensitive token for logging purposes.

        - Empty or None -> "Masked <empty>"
        - Short tokens (<4 chars) -> "<....XXXX>" (random 4 chars)
        - Longer tokens -> "<...last4chars>"

        Args:
            token (Optional[str]): Sensitive token to mask.

        Returns:
            str: Masked token for safe logging.
        """
        
        if not token:
            return "Masked <empty>"
        if len(token) < 4:
            random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
            return f"<....{random_chars}>"
        return f"<...{token[-4:]}>"

    def _log(self, level: int, message: str, caller: str, log: bool = True):
        """Internal helper for logging at a specified level."""
        if log:
            logger.log(level, f"[{caller}]: {message}")

    def Debug(self, message: str, caller: str, log: bool = True):
        self._log(logging.DEBUG, message, caller, log)

    def Info(self, message: str, caller: str, log: bool = True):
        self._log(logging.INFO, message, caller, log)

    def Warning(self, message: str, caller: str, log: bool = True):
        self._log(logging.WARNING, message, caller, log)

    def Error(self, message: str, caller: str):
        """Errors always log."""
        logger.error(f"[{caller}]: {message}")


# ─────────────────────────────────────────────────────────────────────────────
# Messages
# ─────────────────────────────────────────────────────────────────────────────
class TakatMessages:
    """Standardized message builder (always returns plain dict messages)."""

    LOGGING = TakatLogger()

    # ─────────────────────────────────────────────────────────────────────────
    # Internal helpers
    # ─────────────────────────────────────────────────────────────────────────
    def _blank_string(self, value: Optional[Any]) -> str:
        """Convert value to string or return 'Not Applicable' if empty/None."""
        return str(value) if value not in (None, "") else "Not Applicable"

    def _blank_int(self, value: Optional[int]) -> int:
        """Return integer value or 0 if None."""
        return value if value is not None else 0

    # ─────────────────────────────────────────────────────────────────────────
    # Default reply message
    # ─────────────────────────────────────────────────────────────────────────
    def default_reply_message(
        self,
        caller: str = "",
        endpoint: str = "",
        status: int = 0,
        msg: str = "",
        uid: str = "",
        log: bool = False,
        error: str = "",
        data: Any = None,
    ) -> dict:
        """
        Build a standardized reply message.

        Args:
            caller (str): Caller identifier.
            endpoint (str): Endpoint name.
            status (int): Status code.
            msg (str): Event message.
            uid (str): User/request ID.
            log (bool): Whether to log the message.
            error (str): Error message if any.
            data (Any): Additional data (dict/list or other).

        Returns:
            dict: Standardized message dictionary.
        """
        if isinstance(data, (dict, list)):
            safe_data = data
        elif data is None:
            safe_data = None
        else:
            safe_data = self._blank_string(data)

        msg_dict = {
            "status": self._blank_int(status),
            "caller": self._blank_string(caller),
            "uid": self._blank_string(uid),
            "error": self._blank_string(error),
            "event": self._blank_string(msg),
            "endpoint": self._blank_string(endpoint),
            "data": safe_data,
        }

        if log:
            log_msg = f"endpoint: {endpoint} | status: {status} | event: {msg}"
            self.LOGGING.Info(caller=caller, message=log_msg, log=log)

        return msg_dict

    # ─────────────────────────────────────────────────────────────────────────
    # Convenience methods
    # ─────────────────────────────────────────────────────────────────────────
    def Error_message(
        self, caller: str = "", status: int = 0, endpoint: str = "", event: str = "", error: str = "", log: bool = False, uid: str = "", data: Any = None
    ) -> dict:
        """Standardized error message."""
        return self.default_reply_message(
            caller=caller,
            endpoint=endpoint,
            status=status,
            msg=event,
            uid=uid,
            log=log,
            error=error,
            data=data,
        )

    def Success_message(
        self, caller: str, status: int = 0, endpoint: str = "", msg: str = "", log: bool = False, uid: str = "", data: Any = None
    ) -> dict:
        """Standardized success message."""
        return self.default_reply_message(caller, endpoint, status, msg, uid, log, data=data)

    def blank_string(self, value: Any) -> str:
        """Convert any input to string or 'Not Applicable'."""
        return self._blank_string(value)
