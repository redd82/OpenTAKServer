#logger.debug
from opentakserver.extensions import logger
import re
import ipaddress
import random
import string

class Validation:
    def __init__(self):
        self._caller = "Validation"
        pass
    
    
    # ─────────────────────────────────────────────────────────────────────────────
    # Helper functions Normalize input from __init__ and @property
    # ─────────────────────────────────────────────────────────────────────────────
    def FQDN(self, fqdn: str, log=False) -> str:
        """
        Validate and sanitize a fully qualified domain name (FQDN) or IP address.
        
        Accepts:
            - IPv4 addresses
            - IPv6 addresses
            - Standard domains and subdomains
            - Domains with trailing dot
            - IDNs in Punycode (xn--)
        
        If the input is invalid, returns "127.0.0.1".

        Args:
            fqdn (str): The input FQDN, IP, or domain name.

        Returns:
            str: A sanitized, validated FQDN, IP address, or default "127.0.0.1".
        """
        if fqdn is None:
            if log == True: logger.info("Validation.FQDN: fqdn is None, defaulting to 127.0.0.1")
            return "127.0.0.1"

        if not isinstance(fqdn, str):
            logger.error(f"Validation.FQDN: fqdn {fqdn} is not a string.")
            raise TypeError("Validation.FQDN: FQDN must be a string")

        fqdn = fqdn.strip().lower()

        # --- Check if it's a valid IP address ---
        try:
            ip = ipaddress.ip_address(fqdn)
            if log == True: logger.info(f"Validation.FQDN: interpreted valid IP address '{ip}' from input '{fqdn}'.")
            return str(ip)
        except ValueError:
            pass

        # --- Regex for valid domain names ---
        # Domain labels: letters, numbers, hyphens; no leading/trailing hyphen; 1-63 chars
        # Full domain: labels separated by dots, optional trailing dot
        domain_regex = re.compile(
            r'^(?=.{1,253}\.?$)'                   # total length limit
            r'((?!-)[A-Za-z0-9-]{1,63}(?<!-)\.)*'  # subdomains
            r'((?!-)[A-Za-z0-9-]{1,63}(?<!-))'     # top-level domain
            r'\.?$'                                # optional trailing dot
        )

        if domain_regex.fullmatch(fqdn):
            return fqdn

        else: 
            if log == True: logger.warning(f"Validation.FQDN: invalid FQDN '{fqdn}', defaulting to 127.0.0.1")
            return "127.0.0.1"
         
    def Port(self, port: int, log=False) -> int:
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
        
    def HttpOrHttps(self, protocol: str, log=False) -> str:
        """
        Clamp protocol to the valid string of http or https.

        Args:
            protocol (str): The protocol to clamp.

        Returns:
            str: either http or https. defaulting to http if the input was invalid.
        """
        default="http"
        
        if protocol is None:
            return default  # edge case if the protocol is set to None, we default back to http (note we expect all lower case)
        if not isinstance(protocol, str):
            logger.error(f"Validation.HttpOrHttps: protocol {protocol} is not of type str.")
            raise TypeError("Validation.HttpOrHttps: Protocol must be an string")
        if protocol.lower() in ("http", "https"): return protocol.lower()
        else: 
            if log == True: logger.warning(f"Validation.HttpOrHttps: invalid protocol '{protocol}', defaulting to 'http'.")
            return default.lower()
        
    def Range(self, value: int, min_value: int, max_value: int) -> int:
        """
        Clamp a numeric value to stay within a defined range.

        Automatically swaps min_value and max_value if min_value > max_value.
        If min_value == max_value, returns that value.

        Parameters:
            value (int): The value to be constrained.
            min_value (int): The minimum allowed value.
            max_value (int): The maximum allowed value.

        Returns:
            int: The clamped value within the specified range.

        Examples:
            Range(12, 0, 10) -> 10
            Range(-3, 0, 10) -> 0
            Range(7, 0, 10)  -> 7
            Range(5, 5, 5)   -> 5
            Range(7, 10, 3)  -> 7  # min/max swapped internally to 3/10
        """
        # Swap if min_value > max_value
        if min_value > max_value: min_value, max_value = max_value, min_value
        # Clamp the value within the range
        return max(min_value, min(max_value, value))
    
    def Min(self, value: int, Compare_value: int) -> int:
        """
        Clamp value to be no greater than Compare_value and at least 0.
        Safely bounded even if Compare_value is out of range.
        """
        upper = max(0, Compare_value)
        return self.Range(value, 0, upper)

    def Max(self, value: int, Compare_value: int) -> int:
        """
        Clamp value to be no smaller than Compare_value and at most 10.
        Safely bounded even if Compare_value is out of range.
        """
        lower = min(10, Compare_value)
        return self.Range(value, lower, 10)

    def ToBool(self, value, log=False) -> bool:
        """
        Convert input into a strict Python boolean.

        Accepts common truthy/falsey representations:
          - Truthy: True, 1, "true", "on", "yes", "y"
          - Falsey: False, 0, "false", "off", "no", "n"

        Parameters:
            value: Any type representing a boolean-like state.

        Returns:
            bool: True or False based on input interpretation.

        Default: returns False if the value cannot be interpreted.
        """
        # Handle boolean input directly
        if isinstance(value, bool):
            if log == True: logger.info(f"Validation.ToBool: interpreted boolean {value} from bool: {value}")
            return value

        # Handle integer (0 or 1 only)
        if isinstance(value, int):
            if value in (0, 1):
                result = bool(value)
                if log == True:
                    logger.info(f"Validation.ToBool: interpreted boolean {result} from int: {value}")
                    return result
            else:
                if log == True:
                    logger.warning(f"Validation.ToBool: integer {value} not 0/1, defaulting to False")
                    return False

        # Handle string representations
        if isinstance(value, str):
            val = value.strip().lower()
            truthy = {"true", "on", "yes", "y", "1"}
            falsey = {"false", "off", "no", "n", "0"}
            if val in truthy:
                if log == True: logger.info(f"Validation.ToBool: interpreted boolean True from string: {value!r}")
                return True
            if val in falsey:
                if log == True: logger.info(f"Validation.ToBool: interpreted boolean False from string: {value!r}")
                return False

        if log == True: logger.warning(f"Validation.ToBool: unable to interpret boolean from: {value!r}, defaulting to False")
        return False

    def ToBoolStr(self, value, log=False) -> str:
        """
        Convert input into a 'true'/'false' string using ToBool logic.

        Parameters:
            value: Any type representing a boolean-like state.

        Returns:
            str: "true" or "false"
        """
        result = self.ToBool(value)
        str_result = "true" if result else "false"
        if log == True: logger.info(f"Validation.ToBoolStr: interpreted '{str_result}' from input: {value!r}")
        return str_result

    def ToBoolCanonical(self, value, log=False) -> str:
        """
        Convert input into a canonical truthy/falsey string.

        Returns one of the canonical representations:
          - Truthy: "true", "on", "yes", "y", "1"
          - Falsey: "false", "off", "no", "n", "0"

        Parameters:
            value: Any type representing a boolean-like state.

        Returns:
            str: canonical string representing truthiness.

        Default: returns "false" if value cannot be interpreted.
        """
        truthy = {"true", "on", "yes", "y", "1"}
        falsey = {"false", "off", "no", "n", "0"}

        if isinstance(value, bool):
            result = "true" if value else "false"
            if log == True: logger.info(f"Validation.ToBoolCanonical: interpreted '{result}' from bool: {value}")
            return result

        if isinstance(value, int) and value in (0, 1):
            result = "true" if value == 1 else "false"
            if log == True: logger.info(f"Validation.ToBoolCanonical: interpreted '{result}' from int: {value}")
            return result

        if isinstance(value, str):
            val = value.strip().lower()
            if val in truthy:
                if log == True: logger.info(f"Validation.ToBoolCanonical: interpreted canonical truthy '{val}' from string: {value!r}")
                return val
            if val in falsey:
                if log == True: logger.info(f"Validation.ToBoolCanonical: interpreted canonical falsey '{val}' from string: {value!r}")
                return val

        if log == True: logger.warning(f"Validation.ToBoolCanonical: unable to interpret boolean from: {value!r}, defaulting to 'false'")
        return "false"

    def JsonWebToken(self, value: str, log=False) -> str:
        """
        Sanitize a string to only include characters valid in a JWT.
        Allowed characters: A-Z, a-z, 0-9, dash (-), underscore (_).

        Args:
            value (str): Input string to sanitize.

        Returns:
            str: Sanitized string containing only valid JWT characters.
        """
        if not isinstance(value, str): 
            if log == True: logger.warning(f"Validation.Jwt: failed to interpreted from unkown data type: {value}, converting it to string")
            value = str(value)
        # Keep only valid JWT characters
        return re.sub(r"[^A-Za-z0-9\-_]", "", value)
    
    def SplitBoolTuple(self, index: int, value: tuple) -> bool:
        """
            Safely retrieve an element from a tuple by index.

            Args:
                index (int): The index of the element to retrieve.
                value (tuple): The tuple from which to retrieve the element.
            Returns:
                bool: The element at the specified index if valid.
            Raises:
                ValueError: If the index is not 0 or 1.
        """
        output = False
        if index in (0, 1):
             output =value[index]
        else:
            raise ValueError(f"{self._caller}: SplitBoolTuple Invalid index {index}: must be 0 or 1")
    
        return output

    def RandomString(self, length:int = 1) ->str:
        """
        Generate a random alphanumeric string of a given length.

        Args:
            length (int): Desired length of the string.

        Returns:
            str: Random alphanumeric string.
        """
        length = self.Range(length, min_value=1, max_value= 256) # fix the range between 1 and 256 characters
        chars = string.ascii_letters + string.digits    # what characters to choose from
        return ''.join(random.choices(chars, k=length)) 
        
        
        