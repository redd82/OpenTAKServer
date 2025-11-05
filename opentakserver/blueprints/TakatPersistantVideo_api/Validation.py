#logger.debug
from opentakserver.extensions import logger
import re

class Validation:
    def __init__(self):
        pass
    
    
    # ─────────────────────────────────────────────────────────────────────────────
    # Helper functions Normalize input from __init__ and @property
    # ─────────────────────────────────────────────────────────────────────────────
    def FQDN(self, fqdn: str) -> str:
        """
        Clamp a fully qualified domain name (FQDN) or IP address to valid characters.

        Args:
            fqdn (str): The input FQDN or IP address.

        Returns:
            str: A sanitized, lowercase FQDN or IP address containing only letters, numbers, and periods.
        """
        if fqdn is None:
            return "127.0.0.1"  # edge case, if the string is set to none we basically reset it to 127.0.0.1)
        
        if not isinstance(fqdn, str):
            logger.error(f"DB_API: _clamp_fqdn: fqdn {fqdn} is not of type str.")
            raise TypeError("DB_API: _clamp_fqdn: FQDN must be a string")
        
        # Remove everything except letters, numbers, and periods
        clean_fqdn = re.sub(r'[^a-zA-Z0-9\.]', '', fqdn).lower()

        if not clean_fqdn:
            logger.info(f"Validation.FQDN:: input {fqdn} became empty after cleaning. Defaulting to '127.0.0.1'.")
            return "127.0.0.1"

        return clean_fqdn
    
    def Port(self, port: int) -> int:
        """
        Clamp a port number to the valid range (0–65535).

        Args:
            port (int): The port number to clamp.

        Returns:
            int: A valid port number between 0 and 65535.
        """
        if port is None:
            return 0   #edge case, the port setter was deliberatly set to None, default to 0
        if not isinstance(port, int):
            logger.error(f"Validation.Port: port {port} is not of type int.")
            raise TypeError("Validation.Port: Port must be an integer")
        return max(0, min(65535, abs(port)))
        
    def HttpOrHttps(self, protocol: str) -> str:
        """
        Clamp protocol to the valid string of http or https.

        Args:
            protocol (str): The protocol to clamp.

        Returns:
            str: either http or https. defaulting to http if the input was invalid.
        """
        default="http"
        
        if protocol is None:
            return default.lower()   # edge case if the protocol is set to None, we default back to http
        if not isinstance(protocol, str):
            logger.error(f"Validation.HttpOrHttps: protocol {protocol} is not of type str.")
            raise TypeError("Validation.HttpOrHttps: Protocol must be an string")
        if protocol.lower() in ("http", "https"): return protocol.lower()
        else: 
            logger.warning(f"Validation.HttpOrHttps: invalid protocol '{protocol}', defaulting to 'http'.")
            return default.lower()
        
    def Range(self, max_value, min_value, value) -> int:
        """
            Clamp a numeric value to stay within a defined range.

            Ensures that `value` does not go below `min_value` or above `max_value`.
            Returns the nearest boundary if it exceeds either limit.

            Parameters:
                min_value (int): The minimum allowed value.
                max_value (int): The maximum allowed value.
                value (int): The value to be constrained.

            Returns:
                int: The clamped value within the specified range.

            Example:
                Range(0, 10, 12) -> 10
                Range(0, 10, -3) -> 0
                Range(0, 10, 7)  -> 7
            """
        return max(min_value, min(max_value, value))

    def Bool(self, value) -> bool:
        """
            Convert various input types into a strict boolean value.
            Accepts common representations of truthy and falsey states.

            Truthy examples:
                True, 1, "true", "True", "on", "On", "yes", "y"
            Falsey examples:
                False, 0, "false", "False", "off", "Off", "no", "n"

            Parameters:
                value: Any type representing a boolean-like state.

            Returns:
                bool: The interpreted boolean value.

            Raises:
                ValueError: If the value cannot be interpreted as a boolean.
        """
        
        if isinstance(value, bool):
            if value == False: logger.info(f"Validation.Bool: interpreted boolean False from bool: {value}")
            if value == True: logger.info(f"Validation.Bool: interpreted boolean True from bool: {value}")
            return value

        if isinstance(value, int):
            if value in (0, 1):
                if value == 0: logger.info(f"Validation.Bool: interpreted boolean false from int: {value}")
                if value == 1: logger.info(f"Validation.Bool: interpreted boolean true from int: {value}")
                return bool(value)

        if isinstance(value, str):
            truthy = {"true", "on", "yes", "y", "1"}
            falsey = {"false", "off", "no", "n", "0"}

            val = value.strip().lower()
            if val in truthy:
                logger.info(f"Validation.Bool: interpreted boolean true from string: {value}")
                return True
            if val in falsey:
                logger.info(f"Validation.Bool: interpreted boolean false from string: {value}")
                return False
            
        logger.error(f"Validation.Bool: Unable to interpret boolean from: {value!r}")
        return False    # default to false
        
    
