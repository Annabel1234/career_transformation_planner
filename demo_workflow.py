#!/usr/bin/env python3
"""
Demo script showing the complete workflow:
1. Load local user profile JSON
2. Send to OpenAI for career plan generation
3. Store response locally
"""

import os
import sys
import django
import json
import requests
from datetime import datetime

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'career_planner.settings')
django.setup()

def load_user_profile_from_json(file_path):
    """Load user profile data from local JSON file"""
    print(f"📁 Loading user profile from: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ Successfully loaded user profile data")
        print(f"   User: {data['user_profiles'][0]['name']}")
        print(f"   Email: {data['user_profiles'][0]['email']}")
        print(f"   Current Title: {data['user_profiles'][0]['title']}")
        print(f"   User Prompt: {data.get('user_prompt', 'N/A')}")
        
        return data
    
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON format: {e}")
        return None
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return None

def send_to_ai_planning_api(user_data, base_url="http://localhost:8000"):
    """Send user data to AI planning API"""
    print(f"\n🤖 Sending data to AI Planning API...")
    print(f"   API Endpoint: {base_url}/plan/api/career-plans/generate_plan/")
    
    try:
        response = requests.post(
            f"{base_url}/plan/api/career-plans/generate_plan/",
            json=user_data,
            headers={'Content-Type': 'application/json'},
            timeout=60  # 60 second timeout for AI processing
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ AI Plan generated successfully!")
            print(f"   Processing Time: {result.get('processing_time', 0):.2f} seconds")
            print(f"   Tokens Used: {result.get('tokens_used', 0)}")
            print(f"   File Saved: {result.get('file_path', 'N/A')}")
            
            return result
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to server. Make sure Django is running on {base_url}")
        return None
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out. AI processing took too long.")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def check_local_storage(file_path):
    """Check if the response was saved locally"""
    print(f"\n📁 Checking local storage...")
    
    if file_path and os.path.exists(file_path):
        print(f"✅ Response file found: {file_path}")
        
        # Get file info
        file_size = os.path.getsize(file_path)
        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        
        print(f"   File Size: {file_size} bytes")
        print(f"   Created: {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Try to read and show basic info
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, dict):
                if 'goal_id' in data:
                    print(f"   Type: Career Plan Response")
                    print(f"   Goal ID: {data.get('goal_id', 'N/A')}")
                    print(f"   Plan Description: {data.get('plan_description', 'N/A')[:100]}...")
                    print(f"   Milestones: {len(data.get('milestones', []))}")
                    print(f"   Weekly Plans: {len(data.get('weekly_plans', []))}")
                elif 'success' in data:
                    print(f"   Type: API Response")
                    print(f"   Status: {'✅ Success' if data['success'] else '❌ Error'}")
        
        except Exception as e:
            print(f"   Error reading file content: {str(e)}")
    
    else:
        print(f"❌ Response file not found: {file_path}")

def demonstrate_workflow():
    """Demonstrate the complete workflow"""
    print("🚀 AI Career Planning - Complete Workflow Demo")
    print("=" * 60)
    
    # Step 1: Load local JSON file
    json_file_path = "sample_user_profile.json"
    user_data = load_user_profile_from_json(json_file_path)
    
    if not user_data:
        print("❌ Failed to load user data. Exiting.")
        return
    
    # Step 2: Send to AI Planning API
    result = send_to_ai_planning_api(user_data)
    
    if not result:
        print("❌ Failed to generate AI plan. Exiting.")
        return
    
    # Step 3: Check local storage
    file_path = result.get('file_path')
    check_local_storage(file_path)
    
    # Step 4: Show summary
    print(f"\n" + "=" * 60)
    print("🎉 Workflow Summary:")
    print(f"✅ User profile loaded from: {json_file_path}")
    print(f"✅ AI plan generated via API")
    print(f"✅ Response saved to: {file_path}")
    print(f"✅ Processing time: {result.get('processing_time', 0):.2f} seconds")
    print(f"✅ Tokens used: {result.get('tokens_used', 0)}")
    
    print(f"\n📋 Next Steps:")
    print(f"1. Review the generated plan in: {file_path}")
    print(f"2. Access admin interface: http://localhost:8000/admin")
    print(f"3. View all career plans: http://localhost:8000/plan/api/career-plans/")

def show_manual_workflow():
    """Show how to do this manually with curl"""
    print(f"\n🔧 Manual Workflow (using curl):")
    print("=" * 60)
    
    print(f"1. Start Django server:")
    print(f"   python manage.py runserver")
    
    print(f"\n2. Send user data to API:")
    print(f"   curl -X POST http://localhost:8000/plan/api/career-plans/generate_plan/ \\")
    print(f"        -H 'Content-Type: application/json' \\")
    print(f"        -d @sample_user_profile.json")
    
    print(f"\n3. Check generated files in downloads/ folder")
    print(f"   ls -la downloads/")

if __name__ == "__main__":
    # Check if Django server is running
    try:
        response = requests.get("http://localhost:8000/admin/", timeout=5)
        if response.status_code == 200:
            print("✅ Django server is running")
            demonstrate_workflow()
        else:
            print("❌ Django server is not responding properly")
            show_manual_workflow()
    except requests.exceptions.ConnectionError:
        print("❌ Django server is not running")
        show_manual_workflow()
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        show_manual_workflow() 