"""
CalibreMCP Configuration Management

Handles configuration from JSON files and environment variables
for Calibre server connection settings.
"""

import json
import os
from typing import Optional, Dict, Any
from pathlib import Path

from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv


class CalibreConfig(BaseModel):
    """Configuration for Calibre server connection"""
    
    # Server connection
    server_url: str = Field(default="http://localhost:8080", description="Calibre server URL")
    username: Optional[str] = Field(default=None, description="Calibre username (if auth enabled)")
    password: Optional[str] = Field(default=None, description="Calibre password (if auth enabled)")
    
    # Request settings
    timeout: int = Field(default=30, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum number of request retries")
    
    # Search settings
    default_limit: int = Field(default=50, description="Default search result limit")
    max_limit: int = Field(default=200, description="Maximum search result limit")
    
    # Library settings
    library_name: str = Field(default="Default Library", description="Primary library name")
    
    @validator('server_url')
    def validate_server_url(cls, v):
        """Ensure server URL has proper format"""
        if not v.startswith(('http://', 'https://')):
            return f"http://{v}"
        return v.rstrip('/')
    
    @validator('timeout')
    def validate_timeout(cls, v):
        """Ensure timeout is reasonable"""
        return max(5, min(300, v))  # 5-300 seconds
    
    @validator('default_limit', 'max_limit')
    def validate_limits(cls, v):
        """Ensure limits are reasonable"""
        return max(1, min(1000, v))
    
    @classmethod
    def load_config(cls, config_file: Optional[str] = None) -> 'CalibreConfig':
        """
        Load configuration from file and environment variables.
        
        Priority order:
        1. Environment variables (highest priority)
        2. JSON configuration file  
        3. Default values (lowest priority)
        
        Args:
            config_file: Optional path to JSON config file
            
        Returns:
            Initialized CalibreConfig instance
        """
        # Load environment variables
        load_dotenv()
        
        # Start with default config
        config_data = {}
        
        # Load from JSON file if provided
        if config_file:
            config_path = Path(config_file)
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        file_data = json.load(f)
                        config_data.update(file_data)
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Warning: Could not load config file {config_file}: {e}")
        
        # Override with environment variables
        env_mappings = {
            'CALIBRE_SERVER_URL': 'server_url',
            'CALIBRE_USERNAME': 'username', 
            'CALIBRE_PASSWORD': 'password',
            'CALIBRE_TIMEOUT': 'timeout',
            'CALIBRE_MAX_RETRIES': 'max_retries',
            'CALIBRE_DEFAULT_LIMIT': 'default_limit',
            'CALIBRE_MAX_LIMIT': 'max_limit',
            'CALIBRE_LIBRARY_NAME': 'library_name'
        }
        
        for env_var, config_key in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # Convert to appropriate type
                if config_key in ['timeout', 'max_retries', 'default_limit', 'max_limit']:
                    try:
                        config_data[config_key] = int(env_value)
                    except ValueError:
                        print(f"Warning: Invalid integer value for {env_var}: {env_value}")
                else:
                    config_data[config_key] = env_value
        
        return cls(**config_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return self.dict()
    
    def save_config(self, config_file: str) -> bool:
        """
        Save current configuration to JSON file.
        
        Args:
            config_file: Path to save config file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            config_path = Path(config_file)
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            config_dict = self.to_dict()
            # Remove sensitive data from saved config
            config_dict.pop('password', None)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error saving config file {config_file}: {e}")
            return False
    
    @property
    def has_auth(self) -> bool:
        """Check if authentication is configured"""
        return bool(self.username and self.password)
    
    @property  
    def base_url(self) -> str:
        """Get base API URL for Calibre server"""
        return f"{self.server_url}/ajax"
    
    def get_auth(self) -> Optional[tuple]:
        """Get authentication tuple for requests"""
        if self.has_auth:
            return (self.username, self.password)
        return None
