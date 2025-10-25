"""Content synchronization for CalibreMCP."""
from typing import Dict, List, Optional, Any
import asyncio
import hashlib
import os
from datetime import datetime

from fastmcp import MCPTool
from pydantic import BaseModel, Field

# Models
class SyncDevice(BaseModel):
    """Represents a device that can sync with the library."""
    id: str
    name: str
    type: str  # 'web', 'mobile', 'desktop', 'ereader', 'other'
    last_sync: Optional[datetime] = None
    sync_settings: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
    
    def update_timestamp(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()

class SyncJob(BaseModel):
    """Represents a synchronization job."""
    id: str
    device_id: str
    status: str  # 'pending', 'in_progress', 'completed', 'failed', 'cancelled'
    progress: float = 0.0  # 0.0 to 1.0
    total_items: int = 0
    processed_items: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
    
    def start(self):
        """Mark the job as started."""
        self.status = "in_progress"
        self.start_time = datetime.utcnow()
    
    def update_progress(self, progress: float, processed: int, total: int):
        """Update the job progress."""
        self.progress = max(0.0, min(1.0, progress))
        self.processed_items = processed
        self.total_items = total
    
    def complete(self):
        """Mark the job as completed."""
        self.status = "completed"
        self.progress = 1.0
        self.processed_items = self.total_items
        self.end_time = datetime.utcnow()
    
    def fail(self, error: str):
        """Mark the job as failed."""
        self.status = "failed"
        self.error = str(error)
        self.end_time = datetime.utcnow()

# Main tool
class ContentSyncTool(MCPTool):
    """Synchronize content across devices and services."""
    
    name = "content_sync"
    description = "Synchronize content across devices and services"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._devices = {}  # In-memory storage (replace with database in production)
        self._jobs = {}     # In-memory storage for sync jobs
        self._sync_queues = {}  # For background sync tasks
    
    async def _run(self, action: str, **kwargs) -> Dict:
        """Route to the appropriate sync handler."""
        handler = getattr(self, f"sync_{action}", None)
        if not handler:
            return {"error": f"Unknown sync action: {action}", "success": False}
        
        try:
            return await handler(**kwargs)
        except Exception as e:
            return {"error": str(e), "success": False}
    
    # Device Management
    async def sync_register_device(self, 
                                 name: str, 
                                 device_type: str,
                                 device_id: Optional[str] = None,
                                 sync_settings: Optional[Dict] = None) -> Dict:
        """Register a new device for synchronization."""
        if not device_id:
            # Generate a device ID if not provided
            device_id = f"dev_{hashlib.sha256(f'{name}{datetime.utcnow().isoformat()}'.encode()).hexdigest()[:16]}"
        
        device = SyncDevice(
            id=device_id,
            name=name,
            type=device_type,
            sync_settings=sync_settings or {}
        )
        
        self._devices[device_id] = device
        return {"success": True, "device": device.dict()}
    
    async def sync_update_device(self, 
                              device_id: str, 
                              updates: Dict[str, Any]) -> Dict:
        """Update device information and settings."""
        if device_id not in self._devices:
            return {"error": f"Device {device_id} not found", "success": False}
        
        device = self._devices[device_id]
        
        # Update fields
        for field, value in updates.items():
            if hasattr(device, field) and field not in ['id', 'created_at']:
                setattr(device, field, value)
        
        device.updated_at = datetime.utcnow()
        
        return {"success": True, "device": device.dict()}
    
    async def sync_get_device(self, device_id: str) -> Dict:
        """Get device information."""
        if device_id not in self._devices:
            return {"error": f"Device {device_id} not found", "success": False}
        
        return {"success": True, "device": self._devices[device_id].dict()}
    
    # Sync Operations
    async def sync_start(self, 
                        device_id: str,
                        sync_type: str = "full",  # 'full', 'incremental', 'metadata_only', 'content_only'
                        library_path: Optional[str] = None) -> Dict:
        """Start a synchronization job for a device."""
        if device_id not in self._devices:
            return {"error": f"Device {device_id} not found", "success": False}
        
        # Create a new job
        job_id = f"job_{len(self._jobs) + 1}"
        job = SyncJob(
            id=job_id,
            device_id=device_id,
            status="pending",
            metadata={"sync_type": sync_type, "library_path": library_path}
        )
        
        self._jobs[job_id] = job
        
        # Start the sync in the background
        asyncio.create_task(self._run_sync_job(job_id))
        
        return {"success": True, "job_id": job_id}
    
    async def sync_status(self, job_id: str) -> Dict:
        """Get the status of a synchronization job."""
        if job_id not in self._jobs:
            return {"error": f"Job {job_id} not found", "success": False}
        
        job = self._jobs[job_id]
        return {"success": True, "job": job.dict()}
    
    async def sync_cancel(self, job_id: str) -> Dict:
        """Cancel a running synchronization job."""
        if job_id not in self._jobs:
            return {"error": f"Job {job_id} not found", "success": False}
        
        job = self._jobs[job_id]
        if job.status in ["completed", "failed", "cancelled"]:
            return {"error": f"Cannot cancel job in {job.status} state", "success": False}
        
        job.status = "cancelled"
        job.end_time = datetime.utcnow()
        job.error = "Cancelled by user"
        
        # Cancel any background task
        if job_id in self._sync_queues:
            self._sync_queues[job_id].cancel()
            del self._sync_queues[job_id]
        
        return {"success": True, "job": job.dict()}
    
    # Cloud Storage Integration
    async def sync_connect_cloud_storage(self, 
                                       provider: str,  # 'dropbox', 'google_drive', 'onedrive', 'webdav', 's3', etc.
                                       credentials: Dict[str, Any]) -> Dict:
        """Connect to a cloud storage provider."""
        # In a real implementation, this would validate the credentials
        # and establish a connection to the cloud storage provider
        
        # For now, just return a success response with a mock connection ID
        connection_id = f"cloud_{provider}_{hashlib.sha256(str(credentials).encode()).hexdigest()[:8]}"
        
        return {
            "success": True,
            "connection_id": connection_id,
            "provider": provider,
            "status": "connected"
        }
    
    async def sync_upload_to_cloud(self, 
                                 connection_id: str,
                                 local_path: str,
                                 remote_path: str) -> Dict:
        """Upload a file to cloud storage."""
        # In a real implementation, this would upload the file to the cloud
        # For now, just simulate the upload
        
        file_size = os.path.getsize(local_path) if os.path.exists(local_path) else 0
        
        return {
            "success": True,
            "connection_id": connection_id,
            "local_path": local_path,
            "remote_path": remote_path,
            "size_bytes": file_size,
            "uploaded_at": datetime.utcnow().isoformat()
        }
    
    async def sync_download_from_cloud(self, 
                                     connection_id: str,
                                     remote_path: str,
                                     local_path: str) -> Dict:
        """Download a file from cloud storage."""
        # In a real implementation, this would download the file from the cloud
        # For now, just simulate the download
        
        return {
            "success": True,
            "connection_id": connection_id,
            "remote_path": remote_path,
            "local_path": local_path,
            "downloaded_at": datetime.utcnow().isoformat()
        }
    
    # E-Reader Integration
    async def sync_connect_ereader(self, 
                                  device_id: str,
                                  device_info: Dict[str, Any]) -> Dict:
        """Connect to an e-reader device."""
        # In a real implementation, this would detect and connect to the e-reader
        # For now, just return a success response
        
        return {
            "success": True,
            "device_id": device_id,
            "device_info": device_info,
            "status": "connected"
        }
    
    async def sync_to_ereader(self, 
                            device_id: str,
                            book_ids: List[str],
                            format: str = "epub") -> Dict:
        """Send books to an e-reader."""
        # In a real implementation, this would transfer the books to the e-reader
        # For now, just return a success response
        
        return {
            "success": True,
            "device_id": device_id,
            "books_synced": len(book_ids),
            "format": format,
            "synced_at": datetime.utcnow().isoformat()
        }
    
    # Background Task
    async def _run_sync_job(self, job_id: str):
        """Run a synchronization job in the background."""
        if job_id not in self._jobs:
            return
        
        job = self._jobs[job_id]
        job.start()
        
        try:
            device_id = job.device_id
            sync_type = job.metadata.get("sync_type", "full")
            library_path = job.metadata.get("library_path")
            
            # Get device info
            if device_id not in self._devices:
                raise ValueError(f"Device {device_id} not found")
            
            device = self._devices[device_id]
            
            # Get list of books to sync
            from calibre_plugins.calibremcp.storage.local import LocalStorage
            storage = LocalStorage(library_path)
            books = await storage.get_all_books()
            
            total_books = len(books)
            job.total_items = total_books
            job.processed_items = 0
            
            # Simulate sync process
            for i, book in enumerate(books):
                if job.status == "cancelled":
                    break
                
                # Simulate work
                await asyncio.sleep(0.1)
                
                # Update progress
                progress = (i + 1) / total_books
                job.update_progress(progress, i + 1, total_books)
                
                # Update progress every 10% or for the last book
                if (i + 1) % max(1, total_books // 10) == 0 or (i + 1) == total_books:
                    self.logger.info(f"Sync progress: {progress:.1%} ({i+1}/{total_books})")
            
            # Mark as completed if not cancelled
            if job.status != "cancelled":
                job.complete()
                device.last_sync = datetime.utcnow()
                device.update_timestamp()
                
        except Exception as e:
            self.logger.error(f"Sync job {job_id} failed: {str(e)}", exc_info=True)
            job.fail(str(e))
            
        finally:
            # Clean up
            if job_id in self._sync_queues:
                del self._sync_queues[job_id]
    
    # Conflict Resolution
    async def sync_resolve_conflict(self, 
                                  conflict_id: str,
                                  resolution: str,  # 'keep_local', 'keep_remote', 'keep_both', 'merge'
                                  options: Optional[Dict] = None) -> Dict:
        """Resolve a synchronization conflict."""
        # In a real implementation, this would handle conflict resolution
        # For now, just return a success response
        
        return {
            "success": True,
            "conflict_id": conflict_id,
            "resolution": resolution,
            "resolved_at": datetime.utcnow().isoformat(),
            "details": options or {}
        }
    
    # Utility Methods
    async def sync_get_changes_since(self, 
                                   device_id: str,
                                   last_sync_time: Optional[datetime] = None) -> Dict:
        """Get changes since the last sync for a device."""
        if device_id not in self._devices:
            return {"error": f"Device {device_id} not found", "success": False}
        
        # In a real implementation, this would query the database for changes
        # For now, return a mock response
        
        return {
            "success": True,
            "device_id": device_id,
            "last_sync_time": last_sync_time.isoformat() if last_sync_time else None,
            "changes": {
                "added": [],
                "modified": [],
                "deleted": []
            },
            "current_time": datetime.utcnow().isoformat()
        }
    
    async def sync_cleanup_orphaned_files(self, 
                                        library_path: str,
                                        dry_run: bool = True) -> Dict:
        """Clean up orphaned files in the library."""
        # In a real implementation, this would scan the library for orphaned files
        # and optionally remove them
        
        return {
            "success": True,
            "dry_run": dry_run,
            "orphaned_files": [],
            "total_size_bytes": 0,
            "cleaned_up": not dry_run
        }
