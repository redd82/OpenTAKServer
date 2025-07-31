import socket
from urllib.parse import urlparse
import re
import socket
from concurrent.futures import ThreadPoolExecutor, Future
import threading
from typing import Optional
import ipaddress

class Util_Sanitize:
    def __init__(self):
        pass
    
    def is_safe_url_component(self, value: str, allow_slash=False) -> bool:
        """
        Sanitizes URL components to ensure no malicious characters.
        """
        pattern = r'^[a-zA-Z0-9.\-]+$' if not allow_slash else r'^[a-zA-Z0-9\-_/]+$'
        return re.match(pattern, value) is not None

    def is_safe_uid(self, value: str) -> bool:
        """
        Validates that a UID contains only safe characters.
        """
        return re.match(r'^[a-zA-Z0-9_\-]+$', value) is not None       

    def is_safe_hostname(self, value: str) -> bool:
        """
        Validates if the given value is a safe hostname, IPv4 or IPv6 address.
        """
        try:
            # Try to parse as IP (both IPv4 and IPv6)
            ipaddress.ip_address(value)
            return True
        except ValueError:
            # If not IP, validate as domain name
            return re.match(r'^[a-zA-Z0-9.\-]+$', value) is not None
    
    def is_valid_protocol(self, value: str, allowed: list[str]) -> bool:
        """
        Checks if the given protocol is within the allowed list.
        """
        return value in allowed
    
    def is_valid_port(self, value: Optional[int]):
        """
        Validates if the given port is an integer between 1 and 65535.
        """
        try: 
            if value > 0 and value <= 65535:
                return value
        except Exception as e:
            return None   # Default port if validation fails
    


class Util_HostnameResolver:
    """
    A thread-safe, non-blocking resolver for external hostname and FQDN from hosts file.

    Usage:
        resolver = HostnameResolver()
        # Asynchronous calls:
        future1 = resolver.get_external_hostname_async()
        future2 = resolver.get_fqdn_from_hosts_async()
        external = future1.result()
        fqdn = future2.result()

        # Synchronous calls:
        external = resolver.get_external_hostname()
        fqdn = resolver.get_fqdn_from_hosts()
    """

    def __init__(self, max_workers: int = 2):
        # ThreadPoolExecutor for non-blocking execution
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        # Lock to ensure thread-safe file reads
        self._lock = threading.Lock()

    def get_external_hostname(self) -> str:
        """
        Synchronously reads the external hostname from /etc/hostname or falls back to socket.gethostname().
        Thread-safe via internal lock.
        """
        with self._lock:
            try:
                with open('/etc/hostname', 'r') as file:
                    external_hostname = file.readline().strip()
                if external_hostname:
                    return external_hostname
            except FileNotFoundError:
                # Fallback if file not present
                return socket.gethostname()

            # In case file exists but is empty
            return socket.gethostname()

    def get_external_hostname_async(self) -> Future:
        """
        Returns a Future that resolves to the external hostname.
        """
        return self._executor.submit(self.get_external_hostname)

    def get_fqdn_from_hosts(self) -> Optional[str]:
        """
        Synchronously reads /etc/hosts and returns the FQDN for 127.0.1.1 if present.
        Thread-safe via internal lock.
        """
        with self._lock:
            try:
                with open("/etc/hosts", "r") as hosts_file:
                    for line in hosts_file:
                        line = line.strip()
                        # Skip comments or empty lines
                        if not line or line.startswith('#'):
                            continue

                        parts = line.split()
                        ip_address = parts[0]
                        if ip_address == "127.0.1.1" and len(parts) > 1:
                            return parts[1]
                return None
            except FileNotFoundError:
                # Hosts file missing
                return None

    def get_fqdn_from_hosts_async(self) -> Future:
        """
        Returns a Future that resolves to the FQDN found in /etc/hosts, or None.
        """
        return self._executor.submit(self.get_fqdn_from_hosts)

    def shutdown(self, wait: bool = True):
        """
        Shuts down the internal ThreadPoolExecutor.
        """
        self._executor.shutdown(wait=wait)

    
    def validate_url(self, url):
        # Parse the URL into its components
        parsed_url = urlparse(url)
        # Extract protocol (scheme), host (hostname), and port
        protocol = parsed_url.scheme
        host = parsed_url.hostname
        port = parsed_url.port
        # Return True if all components are successfully extracted
        return all([protocol, host]) and (port is not None)  

class Util_Safe_Hyperlink:
    DEFAULT_PROTOCOL = "http"
    DEFAULT_HOST = "127.0.0.1"
    DEFAULT_PATH = ""
    ALLOWED_PROTOCOLS = ["http", "https"]
    
    def __init__(self, protocol: str = DEFAULT_PROTOCOL, host: str = DEFAULT_HOST,
                 port: Optional[int] = None, path: str = DEFAULT_PATH, allowed_protocols: Optional[list[str]] = None):
        
        """
        # Test Case 1
            case_1 = {
                "protocol": "http",
                "host": "example.com",
                "port": 80,
                "path": "path/to/resource"
            }

            link = Util_Hyperlink(**case_1)

            # Expected Output:
            # str(link) => "http://example.com:80/path/to/resource"

            # Internal Object State After Initialization:
            # link.Protocol   => "http"
            # link.Host       => "example.com"
            # link.Port       => 80
            # link.Hyperlink  => "http://example.com:80/path/to/resource"
            
        """
        self._sanitize = Util_Sanitize()
        self.allowed_protocols = allowed_protocols or self.ALLOWED_PROTOCOLS
        self.Protocol = protocol if self._sanitize.is_valid_protocol(protocol, self.allowed_protocols) else self.DEFAULT_PROTOCOL
        self.Host = host if self._sanitize.is_safe_hostname(host) else self.DEFAULT_HOST
        self.Port = port if self._sanitize.is_valid_port(port) else None
        self.URL = path or ""
        self._update_hyperlink()
        
    def _update_hyperlink(self):
            protocol_part = self.Protocol + "://"
            port_part = f":{self.Port}" if self.Port is not None else ""
            normalized_url = f"/{self.URL.lstrip('/')}" if self.URL else ""
            is_ipv6 = ':' in self.Host and not self.Host.startswith('[')
            host_part = f"[{self.Host}]" if is_ipv6 else self.Host
            self.Hyperlink = f"{protocol_part}{host_part}{port_part}{normalized_url}"
            
    def Root(self) -> str:
        """
        Returns the root URL of the hyperlink.
        """
        return f"{self.Protocol}://{self.Host}{f':{self.Port}' if self.Port else ''}/"  
    
    def Update(self, protocol: Optional[str] = None, host: Optional[str] = None,
               port: Optional[int] = None, url: Optional[str] = None,
               allowed_protocols: Optional[list[str]] = None):
        # Preserve current state
        new_protocol = self.Protocol
        new_host = self.Host
        new_port = self.Port
        new_url = self.URL

        # Validate and update each field only if valid
        allowed = allowed_protocols or self.allowed_protocols

        if protocol is not None and self._sanitize.is_valid_protocol(protocol, allowed):
            new_protocol = protocol
        if host is not None and self._sanitize.is_safe_hostname(host):
            new_host = host
        if port is not None and self._sanitize.is_valid_port(port):
            new_port = port
        if url is not None:
            new_url = url

        # Apply only if at least one value changed
        if (new_protocol != self.Protocol or new_host != self.Host or
            new_port != self.Port or new_url != self.URL):
            self.Protocol = new_protocol
            self.Host = new_host
            self.Port = new_port
            self.URL = new_url
            self._update_hyperlink()

    def __str__(self):
        return self.Hyperlink