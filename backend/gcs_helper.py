"""
Google Cloud Storage Helper for Video Persistence
This module handles uploading and downloading videos to/from GCS bucket
"""

import os
import logging
from typing import Optional, Dict, Any
from google.cloud import storage
from pathlib import Path

logger = logging.getLogger(__name__)

class GCSVideoManager:
    """Manages video storage in Google Cloud Storage"""
    
    def __init__(self, bucket_name: str = "wonderkid-demo-videos"):
        self.bucket_name = bucket_name
        self.client = None
        self.bucket = None
        self.initialize_client()
    
    def initialize_client(self) -> bool:
        """Initialize GCS client and bucket"""
        try:
            logger.info(f"☁️ Initializing GCS client for bucket: {self.bucket_name}")
            
            # Use default credentials (from environment or service account)
            self.client = storage.Client()
            
            # Get or create bucket
            try:
                self.bucket = self.client.get_bucket(self.bucket_name)
                logger.info(f"✅ Connected to existing GCS bucket: {self.bucket_name}")
            except Exception as e:
                logger.info(f"📦 Creating new GCS bucket: {self.bucket_name}")
                self.bucket = self.client.create_bucket(
                    self.bucket_name, 
                    location="us-east4"  # Same region as Cloud Run
                )
                logger.info(f"✅ Created new GCS bucket: {self.bucket_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize GCS client: {str(e)}")
            logger.error(f"💡 Make sure GOOGLE_APPLICATION_CREDENTIALS is set or running on GCP")
            return False
    
    def upload_video(self, local_path: str, gcs_filename: Optional[str] = None) -> Optional[str]:
        """
        Upload a video file to GCS bucket
        Returns the GCS public URL if successful
        """
        if not self.bucket:
            logger.error(f"❌ GCS bucket not initialized")
            return None
        
        try:
            # Use original filename if not specified
            if not gcs_filename:
                gcs_filename = os.path.basename(local_path)
            
            logger.info(f"☁️ Uploading video to GCS: {local_path} -> gs://{self.bucket_name}/{gcs_filename}")
            
            # Create blob and upload
            blob = self.bucket.blob(gcs_filename)
            
            # Set metadata for proper content type
            blob.content_type = "video/mp4"
            
            # Upload the file
            with open(local_path, 'rb') as video_file:
                blob.upload_from_file(video_file)
            
            # Make the blob publicly accessible
            blob.make_public()
            
            # Get public URL
            public_url = blob.public_url
            
            logger.info(f"✅ Video uploaded to GCS successfully!")
            logger.info(f"📍 Public URL: {public_url}")
            logger.info(f"📍 GCS Path: gs://{self.bucket_name}/{gcs_filename}")
            
            return public_url
            
        except Exception as e:
            logger.error(f"❌ Failed to upload video to GCS: {str(e)}")
            logger.error(f"📁 Local file: {local_path}, exists: {os.path.exists(local_path)}")
            return None
    
    def download_video(self, gcs_filename: str, local_path: Optional[str] = None) -> Optional[str]:
        """
        Download a video file from GCS bucket
        Returns the local path if successful
        """
        if not self.bucket:
            logger.error(f"❌ GCS bucket not initialized")
            return None
        
        try:
            # Use same filename locally if not specified
            if not local_path:
                local_path = gcs_filename
            
            logger.info(f"☁️ Downloading video from GCS: gs://{self.bucket_name}/{gcs_filename} -> {local_path}")
            
            # Get blob and download
            blob = self.bucket.blob(gcs_filename)
            
            if not blob.exists():
                logger.error(f"❌ Video not found in GCS: {gcs_filename}")
                return None
            
            # Download to local file
            blob.download_to_filename(local_path)
            
            logger.info(f"✅ Video downloaded from GCS successfully!")
            logger.info(f"📁 Local file: {local_path}, size: {os.path.getsize(local_path)} bytes")
            
            return local_path
            
        except Exception as e:
            logger.error(f"❌ Failed to download video from GCS: {str(e)}")
            return None
    
    def get_video_url(self, gcs_filename: str) -> Optional[str]:
        """
        Get the public URL for a video in GCS
        """
        if not self.bucket:
            return None
        
        try:
            blob = self.bucket.blob(gcs_filename)
            if blob.exists():
                # Ensure it's public
                blob.make_public()
                return blob.public_url
            else:
                logger.error(f"❌ Video not found in GCS: {gcs_filename}")
                return None
        except Exception as e:
            logger.error(f"❌ Failed to get video URL from GCS: {str(e)}")
            return None
    
    def video_exists(self, gcs_filename: str) -> bool:
        """Check if a video exists in GCS"""
        if not self.bucket:
            return False
        
        try:
            blob = self.bucket.blob(gcs_filename)
            return blob.exists()
        except Exception as e:
            logger.error(f"❌ Failed to check video existence in GCS: {str(e)}")
            return False

# Global instance for easy access
gcs_manager = None

def get_gcs_manager() -> GCSVideoManager:
    """Get or create the global GCS manager instance"""
    global gcs_manager
    if gcs_manager is None:
        gcs_manager = GCSVideoManager()
    return gcs_manager
