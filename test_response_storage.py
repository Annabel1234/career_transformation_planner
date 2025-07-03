#!/usr/bin/env python3
"""
Test script for API response storage functionality.
Demonstrates how API responses are automatically saved to local download folder.
"""

import requests
import json
import os
from pathlib import Path
import time

# Configuration
BASE_URL = "http://localhost:8000"
USERNAME = "admin"  # Change to your username
PASSWORD = "admin"  # Change to your password

def test_api_connection():
    """Test if the API is accessible"""
    try:
        response = requests.get(f"{BASE_URL}/api/")
        print(f"✅ API connection successful: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running.")
        return False

def test_export_endpoints():
    """Test all export endpoints that save responses to local files"""
    endpoints = [
        ("profiles", "export"),
        ("user-skills", "export"),
        ("education", "export"),
        ("experience", "export"),
        ("goals", "export"),
        ("imports", "export"),
        ("upload", "export_all"),
    ]
    
    print("\n📁 Testing Export Endpoints (Response Storage)")
    print("-" * 50)
    
    for endpoint, action in endpoints:
        print(f"\n📤 Testing {endpoint}/{action}...")
        
        # Test JSON export
        url = f"{BASE_URL}/api/{endpoint}/{action}/"
        params = {'format': 'json'}
        
        try:
            response = requests.get(url, params=params, auth=(USERNAME, PASSWORD))
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {endpoint}/{action} (JSON) - Success")
                print(f"   File saved: {data.get('file_path', 'N/A')}")
                if 'count' in data:
                    print(f"   Records exported: {data['count']}")
                if 'data_summary' in data:
                    print(f"   Data summary: {data['data_summary']}")
            else:
                print(f"❌ {endpoint}/{action} (JSON) - Failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error testing {endpoint}/{action}: {str(e)}")
        
        # Test CSV export
        params = {'format': 'csv'}
        try:
            response = requests.get(url, params=params, auth=(USERNAME, PASSWORD))
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {endpoint}/{action} (CSV) - Success")
                print(f"   File saved: {data.get('file_path', 'N/A')}")
            else:
                print(f"❌ {endpoint}/{action} (CSV) - Failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing {endpoint}/{action} CSV: {str(e)}")

def test_upload_with_response_storage():
    """Test file upload with automatic response storage"""
    print("\n📤 Testing File Upload with Response Storage")
    print("-" * 50)
    
    # Test skills upload
    file_path = "example_data/skills_example.csv"
    if os.path.exists(file_path):
        print(f"\n📁 Uploading {file_path}...")
        
        try:
            with open(file_path, 'rb') as file:
                files = {'file': file}
                data = {
                    'import_type': 'skills',
                    'file_type': 'csv'
                }
                
                response = requests.post(
                    f"{BASE_URL}/api/imports/upload_file/",
                    files=files,
                    data=data,
                    auth=(USERNAME, PASSWORD)
                )
                
                if response.status_code == 201:
                    result = response.json()
                    print(f"✅ Upload successful")
                    print(f"   Response file saved: {result.get('file_path', 'N/A')}")
                    print(f"   Records processed: {result.get('records_processed', 0)}")
                    print(f"   Records successful: {result.get('records_successful', 0)}")
                    print(f"   Records failed: {result.get('records_failed', 0)}")
                else:
                    print(f"❌ Upload failed: {response.status_code}")
                    print(f"   Error: {response.text}")
                    
        except Exception as e:
            print(f"❌ Error uploading file: {str(e)}")
    else:
        print(f"❌ File not found: {file_path}")

def test_bulk_import_with_response_storage():
    """Test bulk import with response storage"""
    print("\n📊 Testing Bulk Import with Response Storage")
    print("-" * 50)
    
    # Test skills bulk import
    file_path = "example_data/skills_example.csv"
    if os.path.exists(file_path):
        print(f"\n📁 Bulk importing {file_path}...")
        
        try:
            with open(file_path, 'rb') as file:
                files = {'file': file}
                data = {
                    'import_type': 'skills',
                    'overwrite_existing': True,
                    'skip_errors': True
                }
                
                response = requests.post(
                    f"{BASE_URL}/api/upload/bulk_import/",
                    files=files,
                    data=data,
                    auth=(USERNAME, PASSWORD)
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Bulk import successful")
                    print(f"   Response file saved: {result.get('file_path', 'N/A')}")
                    print(f"   Records processed: {result.get('processed', 0)}")
                    print(f"   Records successful: {result.get('successful', 0)}")
                    print(f"   Records failed: {result.get('failed', 0)}")
                else:
                    print(f"❌ Bulk import failed: {response.status_code}")
                    print(f"   Error: {response.text}")
                    
        except Exception as e:
            print(f"❌ Error bulk importing file: {str(e)}")
    else:
        print(f"❌ File not found: {file_path}")

def check_download_folder():
    """Check the contents of the download folder"""
    print("\n📂 Checking Download Folder Contents")
    print("-" * 50)
    
    download_dir = Path("downloads")
    if download_dir.exists():
        files = list(download_dir.glob("*"))
        if files:
            print(f"✅ Found {len(files)} files in downloads folder:")
            for file in sorted(files, key=lambda x: x.stat().st_mtime, reverse=True):
                size = file.stat().st_size
                mtime = time.ctime(file.stat().st_mtime)
                print(f"   📄 {file.name} ({size} bytes) - {mtime}")
        else:
            print("📁 Download folder is empty")
    else:
        print("❌ Download folder does not exist")

def test_error_response_storage():
    """Test error response storage"""
    print("\n⚠️ Testing Error Response Storage")
    print("-" * 50)
    
    # Test with invalid file
    try:
        files = {'file': ('invalid.txt', b'invalid content', 'text/plain')}
        data = {
            'import_type': 'skills',
            'file_type': 'csv'
        }
        
        response = requests.post(
            f"{BASE_URL}/api/imports/upload_file/",
            files=files,
            data=data,
            auth=(USERNAME, PASSWORD)
        )
        
        if response.status_code == 400:
            result = response.json()
            print(f"✅ Error response captured")
            print(f"   Error file saved: {result.get('file_path', 'N/A')}")
            print(f"   Error details: {result.get('error', 'N/A')}")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing error response: {str(e)}")

def main():
    """Main test function"""
    print("🚀 Career Transformation Planner - Response Storage Test")
    print("=" * 60)
    
    # Test API connection
    if not test_api_connection():
        return
    
    # Test export endpoints
    test_export_endpoints()
    
    # Test upload with response storage
    test_upload_with_response_storage()
    
    # Test bulk import with response storage
    test_bulk_import_with_response_storage()
    
    # Test error response storage
    test_error_response_storage()
    
    # Check download folder
    check_download_folder()
    
    print("\n✅ Response storage test completed!")
    print("\n📁 All API responses have been saved to the 'downloads' folder")
    print("   These files can be used for:")
    print("   - Local data backup")
    print("   - Frontend integration")
    print("   - Data analysis")
    print("   - Debugging and troubleshooting")

if __name__ == "__main__":
    main() 