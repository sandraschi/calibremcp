"""
Custom exceptions for Calibre MCP.
"""

class CalibreError(Exception):
    """Base exception for all Calibre MCP errors"""
    pass

class AuthError(CalibreError):
    """Raised when authentication fails or credentials are invalid"""
    pass

class BookNotFoundError(CalibreError):
    """Raised when a book is not found in the library"""
    pass

class ServerConnectionError(CalibreError):
    """Raised when unable to connect to a Calibre server"""
    pass

class InvalidServerError(CalibreError):
    """Raised when server configuration is invalid"""
    pass

class StorageError(CalibreError):
    """Base class for storage-related errors"""
    pass

class LocalLibraryError(StorageError):
    """Raised for errors specific to local library access"""
    pass

class RemoteServerError(StorageError):
    """Raised for errors specific to remote server access"""
    pass

class ConfigurationError(CalibreError):
    """Raised for configuration-related errors"""
    pass

class ValidationError(CalibreError):
    """Raised when input validation fails"""
    pass
