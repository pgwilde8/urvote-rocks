#!/usr/bin/env python3
"""
Test script for Google OAuth configuration
"""
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, '/opt/urvote')

def test_google_oauth_config():
    try:
        from app.config import settings
        print("✅ Successfully imported settings")
        
        # Test Google OAuth configuration
        print(f"Google Client ID: {settings.google_client_id}")
        print(f"Google Client Secret: {settings.google_client_secret}")
        print(f"Google Redirect URI: {settings.google_redirect_uri}")
        
        # Check if credentials are set
        if settings.google_client_id and settings.google_client_secret:
            print("✅ Google OAuth credentials are configured")
        else:
            print("❌ Google OAuth credentials are missing")
            
        # Test Google OAuth imports
        try:
            from google.auth.transport import requests
            from google.oauth2 import id_token
            from google_auth_oauthlib.flow import Flow
            print("✅ Google OAuth libraries imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import Google OAuth libraries: {e}")
            print("Run: pip install google-auth google-auth-oauthlib google-auth-httplib2")
            
        # Test OAuth flow creation
        try:
            from app.routers.auth_google import get_google_flow
            flow = get_google_flow()
            print("✅ Google OAuth flow created successfully")
        except Exception as e:
            print(f"❌ Failed to create Google OAuth flow: {e}")
            
    except Exception as e:
        print(f"❌ Error testing Google OAuth: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_google_oauth_config()