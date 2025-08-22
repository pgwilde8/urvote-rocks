"""
DigitalOcean Spaces utility functions for file uploads and storage
"""
import boto3
from botocore.exceptions import ClientError
import os
from typing import Optional, BinaryIO
from app.config import settings

class DigitalOceanSpaces:
    def __init__(self):
        self.session = boto3.session.Session()
        self.client = self.session.client(
            's3',
            region_name=settings.spaces_region,
            endpoint_url=f"//{settings.spaces_region}.digitaloceanspaces.com",
            aws_access_key_id=settings.spaces_access_key,
            aws_secret_access_key=settings.spaces_secret_key
        )
        self.bucket = settings.spaces_bucket
        self.cdn_url = f"https://{settings.spaces_region}.digitaloceanspaces.com/{settings.spaces_bucket}"
    
    def upload_file(self, file_path: str, file_data: BinaryIO, content_type: str) -> bool:
        """
        Upload a file to DigitalOcean Spaces
        
        Args:
            file_path: Path where file should be stored in the bucket
            file_data: File data to upload
            content_type: MIME type of the file
            
        Returns:
            bool: True if upload successful, False otherwise
        """
        try:
            self.client.upload_fileobj(
                file_data,
                self.bucket,
                file_path,
                ExtraArgs={
                    'ContentType': content_type,
                    'ACL': 'public-read'  # Make files publicly accessible
                }
            )
            return True
        except ClientError as e:
            print(f"Error uploading to Spaces: {e}")
            return False
    
    def get_file_url(self, file_path: str) -> str:
        """
        Get the public URL for a file
        
        Args:
            file_path: Path of the file in the bucket
            
        Returns:
            str: Public URL for the file
        """
        return f"{self.cdn_url}/{file_path}"
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from DigitalOcean Spaces
        
        Args:
            file_path: Path of the file to delete
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            self.client.delete_object(Bucket=self.bucket, Key=file_path)
            return True
        except ClientError as e:
            print(f"Error deleting from Spaces: {e}")
            return False
    
    def file_exists(self, file_path: str) -> bool:
        """
        Check if a file exists in DigitalOcean Spaces
        
        Args:
            file_path: Path of the file to check
            
        Returns:
            bool: True if file exists, False otherwise
        """
        try:
            self.client.head_object(Bucket=self.bucket, Key=file_path)
            return True
        except ClientError:
            return False

# Global instance
spaces_client = DigitalOceanSpaces()

def upload_to_spaces(file_data: BinaryIO, file_path: str, content_type: str) -> Optional[str]:
    """
    Upload a file to DigitalOcean Spaces and return the public URL
    
    Args:
        file_data: File data to upload
        file_path: Path where file should be stored
        content_type: MIME type of the file
        
    Returns:
        Optional[str]: Public URL if successful, None if failed
    """
    if spaces_client.upload_file(file_path, file_data, content_type):
        return spaces_client.get_file_url(file_path)
    return None

def delete_from_spaces(file_path: str) -> bool:
    """
    Delete a file from DigitalOcean Spaces
    
    Args:
        file_path: Path of the file to delete
        
    Returns:
        bool: True if successful, False otherwise
    """
    return spaces_client.delete_file(file_path)

def get_spaces_url(file_path: str) -> str:
    """
    Get the public URL for a file in DigitalOcean Spaces
    
    Args:
        file_path: Path of the file
        
    Returns:
        str: Public URL for the file
    """
    return spaces_client.get_file_url(file_path)
