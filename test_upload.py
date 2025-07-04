#!/usr/bin/env python3
"""
Test script for uploading user information from local files
to the Career Transformation Planner API.
"""

import requests
import json
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000/planner"  # Updated to include /planner prefix
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

def upload_file(file_path, import_type, file_type="csv"):
    """Upload a file to the API"""
    url = f"{BASE_URL}/api/imports/upload_file/"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'rb') as file:
            files = {'file': file}
            data = {
                'import_type': import_type,
                'file_type': file_type
            }
            
            response = requests.post(
                url, 
                files=files, 
                data=data, 
                auth=(USERNAME, PASSWORD)
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ Successfully uploaded {file_path}")
                print(f"   Records processed: {result.get('records_processed', 0)}")
                print(f"   Records successful: {result.get('records_successful', 0)}")
                print(f"   Records failed: {result.get('records_failed', 0)}")
                return True
            else:
                print(f"❌ Upload failed for {file_path}: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error uploading {file_path}: {str(e)}")
        return False

def bulk_import(file_path, import_type, overwrite_existing=False, skip_errors=True):
    """Perform bulk import with options"""
    url = f"{BASE_URL}/api/upload/bulk_import/"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'rb') as file:
            files = {'file': file}
            data = {
                'import_type': import_type,
                'overwrite_existing': overwrite_existing,
                'skip_errors': skip_errors
            }
            
            response = requests.post(
                url, 
                files=files, 
                data=data, 
                auth=(USERNAME, PASSWORD)
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Successfully bulk imported {file_path}")
                print(f"   Records processed: {result.get('processed', 0)}")
                print(f"   Records successful: {result.get('successful', 0)}")
                print(f"   Records failed: {result.get('failed', 0)}")
                if result.get('errors'):
                    print(f"   Errors: {len(result['errors'])}")
                return True
            else:
                print(f"❌ Bulk import failed for {file_path}: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error bulk importing {file_path}: {str(e)}")
        return False

def get_user_data(endpoint):
    """Retrieve user data from API"""
    url = f"{BASE_URL}/api/{endpoint}/"
    
    try:
        response = requests.get(url, auth=(USERNAME, PASSWORD))
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Retrieved {len(data.get('results', data))} {endpoint}")
            return data
        else:
            print(f"❌ Failed to retrieve {endpoint}: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error retrieving {endpoint}: {str(e)}")
        return None

def main():
    """Main test function"""
    print("🚀 Career Transformation Planner - Upload Test")
    print("=" * 50)
    
    # Test API connection
    if not test_api_connection():
        return
    
    print("\n📁 Testing File Uploads")
    print("-" * 30)
    
    # Test file uploads
    test_files = [
        ("example_data/skills_example.csv", "skills"),
        ("example_data/education_example.csv", "education"),
        ("example_data/experience_example.csv", "experience"),
        ("example_data/goals_example.csv", "goals"),
        ("example_data/profile_example.csv", "profile"),
    ]
    
    for file_path, import_type in test_files:
        print(f"\n📤 Uploading {import_type}...")
        upload_file(file_path, import_type)
    
    print("\n📊 Testing Bulk Import")
    print("-" * 30)
    
    # Test bulk import
    bulk_import("example_data/skills_example.csv", "skills", overwrite_existing=True)
    bulk_import("downloads/sample_user_profile.json", "profile")
    
    print("\n📋 Retrieving User Data")
    print("-" * 30)
    
    # Retrieve uploaded data
    endpoints = ["user-skills", "education", "experience", "goals", "profiles"]
    
    for endpoint in endpoints:
        get_user_data(endpoint)
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    main() 