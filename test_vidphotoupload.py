#!/usr/bin/env python3
"""
Test script for video/photo upload functionality
"""
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, '/opt/urvote')

def test_upload_functionality():
    try:
        from app.routers.boards import upload_video, upload_visuals
        print("✅ Video and photo upload functions imported successfully")
        
        # Test file size limits
        from app.routers.boards import MAX_VIDEO_SIZE, MAX_VISUAL_SIZE
        print(f"✅ Video max size: {MAX_VIDEO_SIZE / (1024*1024):.1f}MB")
        print(f"✅ Photo max size: {MAX_VISUAL_SIZE / (1024*1024):.1f}MB")
        
        # Test utility imports
        try:
            from app.utils import create_upload_directory_structure, get_upload_file_path
            print("✅ Upload utility functions imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import upload utilities: {e}")
            
    except Exception as e:
        print(f"❌ Error testing upload functionality: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_upload_functionality()