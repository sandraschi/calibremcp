"""
Authentication and credential management for Calibre MCP.

Handles secure storage and retrieval of credentials using the system keyring.
"""
import logging
from typing import Optional, Dict, Tuple
import keyring

logger = logging.getLogger(__name__)

class AuthManager:
    """Manages authentication for Calibre content servers"""
    
    def __init__(self, service_name: str = "calibre_mcp"):
        """Initialize with a service name for keyring storage"""
        self.service_name = service_name
    
    def save_credentials(self, server_name: str, username: str, password: str) -> None:
        """
        Securely store credentials in the system keyring.
        
        Args:
            server_name: Unique identifier for the server
            username: Username for authentication
            password: Password for authentication
        """
        try:
            keyring.set_password(
                service_name=self.service_name,
                username=f"{server_name}_username",
                password=username
            )
            keyring.set_password(
                service_name=self.service_name,
                username=f"{server_name}_password",
                password=password
            )
            logger.debug(f"Saved credentials for server: {server_name}")
        except Exception as e:
            logger.error(f"Failed to save credentials for {server_name}: {e}")
            raise
    
    def get_credentials(self, server_name: str) -> Optional[Tuple[str, str]]:
        """
        Retrieve stored credentials from the system keyring.
        
        Args:
            server_name: Unique identifier for the server
            
        Returns:
            Tuple of (username, password) if found, None otherwise
        """
        try:
            username = keyring.get_password(
                service_name=self.service_name,
                username=f"{server_name}_username"
            )
            password = keyring.get_password(
                service_name=self.service_name,
                username=f"{server_name}_password"
            )
            
            if username and password:
                return username, password
            return None
        except Exception as e:
            logger.error(f"Failed to get credentials for {server_name}: {e}")
            return None
    
    def delete_credentials(self, server_name: str) -> bool:
        """
        Remove stored credentials for a server.
        
        Args:
            server_name: Unique identifier for the server
            
        Returns:
            True if credentials were deleted, False otherwise
        """
        try:
            keyring.delete_password(
                service_name=self.service_name,
                username=f"{server_name}_username"
            )
            keyring.delete_password(
                service_name=self.service_name,
                username=f"{server_name}_password"
            )
            logger.debug(f"Deleted credentials for server: {server_name}")
            return True
        except keyring.errors.PasswordDeleteError:
            logger.debug(f"No credentials found for server: {server_name}")
            return False
        except Exception as e:
            logger.error(f"Failed to delete credentials for {server_name}: {e}")
            return False
