#!/usr/bin/env python3
"""
Test script for AI Career Planning functionality
This script demonstrates how to use the AI-powered career planning API
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

# Sample user data for testing
SAMPLE_USER_DATA = {
    "user_profiles": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "email": "sarah.johnson@example.com",
            "google_id": "google_123456789012345678901",
            "name": "Sarah Johnson",
            "picture_url": "https://example.com/profiles/sarah_johnson.jpg",
            "age": 29,
            "gender": "Female",
            "title": "Senior Marketing Manager",
            "education": "MBA in Marketing, Bachelor's in Business Administration",
            "years_experience": 7,
            "income_level": "80000-120000",
            "last_career_change": "2022-03-15",
            "summary": "Experienced marketing professional with expertise in digital campaigns, brand management, and team leadership. Passionate about data-driven marketing strategies and customer experience optimization. Based in Seattle, WA. Married with two young children (ages 4 and 7). Prefers warm, encouraging communication with practical examples. Values work-life balance and tends to work best with structured, step-by-step guidance. Has a morning routine that includes meditation and prefers solutions that can be implemented during commute time or lunch breaks. Appreciates visual aids and actionable takeaways.",
            "personality_traits": {
                "openness": 8.2,
                "conscientiousness": 9.1,
                "extraversion": 7.5,
                "agreeableness": 8.7,
                "neuroticism": 3.2,
                "leadership_style": "collaborative",
                "communication_preference": "direct",
                "decision_making": "analytical"
            },
            "motivators": [
                "career_advancement",
                "skill_development",
                "work_life_balance",
                "team_leadership",
                "creative_challenges"
            ],
            "work_style": {
                "preferred_environment": "hybrid",
                "peak_productivity_hours": "morning",
                "collaboration_preference": "team_oriented",
                "feedback_style": "frequent_constructive",
                "goal_setting_approach": "SMART_goals",
                "stress_management": "time_blocking"
            },
            "user_type": "elevator",
            "onboarding_completed": True,
            "created_at": "2024-01-15T09:30:00Z",
            "updated_at": "2024-05-20T14:22:00Z"
        }
    ],
    "user_prompt": "I want to transition into an AI Product Manager role within the next 3 months. I have strong marketing and team leadership experience but need to build technical AI/ML knowledge and product management skills."
}

def test_ai_planning_api():
    """Test the AI planning API endpoints"""
    base_url = "http://localhost:8000"
    
    print("🤖 Testing AI Career Planning API")
    print("=" * 50)
    
    # Test 1: Generate career plan
    print("\n1. Testing Career Plan Generation...")
    try:
        response = requests.post(
            f"{base_url}/plan/api/career-plans/generate_plan/",
            json=SAMPLE_USER_DATA,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Career plan generated successfully!")
            print(f"   User: {result.get('career_plan', {}).get('user_profile', {}).get('name', 'Unknown')}")
            print(f"   Plan Description: {result.get('career_plan', {}).get('plan_description', 'N/A')[:100]}...")
            print(f"   Processing Time: {result.get('processing_time', 0):.2f} seconds")
            print(f"   Tokens Used: {result.get('tokens_used', 0)}")
            print(f"   File Saved: {result.get('file_path', 'N/A')}")
            
            # Check if file was created
            if result.get('file_path'):
                if os.path.exists(result['file_path']):
                    print("✅ Response file saved successfully!")
                else:
                    print("⚠️  Response file not found")
        else:
            print(f"❌ Failed to generate career plan: {response.status_code}")
            print(f"   Error: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure Django is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 2: List career plans
    print("\n2. Testing Career Plans List...")
    try:
        response = requests.get(f"{base_url}/plan/api/career-plans/")
        if response.status_code == 200:
            plans = response.json()
            print(f"✅ Found {len(plans)} career plans")
            for plan in plans:
                print(f"   - {plan.get('user_profile', {}).get('name', 'Unknown')}: {plan.get('plan_description', 'N/A')[:50]}...")
        else:
            print(f"❌ Failed to list career plans: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 3: Export plans
    print("\n3. Testing Export Plans...")
    try:
        response = requests.get(f"{base_url}/plan/api/career-plans/export_plans/")
        if response.status_code == 200:
            result = response.json()
            print("✅ Plans exported successfully!")
            print(f"   File: {result.get('file_path', 'N/A')}")
            print(f"   Count: {result.get('count', 0)}")
        else:
            print(f"❌ Failed to export plans: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 4: List user profiles
    print("\n4. Testing User Profiles List...")
    try:
        response = requests.get(f"{base_url}/plan/api/user-profiles/")
        if response.status_code == 200:
            profiles = response.json()
            print(f"✅ Found {len(profiles)} user profiles")
            for profile in profiles:
                print(f"   - {profile.get('name', 'Unknown')} ({profile.get('email', 'N/A')})")
        else:
            print(f"❌ Failed to list user profiles: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 5: List AI request logs
    print("\n5. Testing AI Request Logs...")
    try:
        response = requests.get(f"{base_url}/plan/api/ai-logs/")
        if response.status_code == 200:
            logs = response.json()
            print(f"✅ Found {len(logs)} AI request logs")
            for log in logs:
                print(f"   - {log.get('user_profile', {}).get('name', 'Unknown')}: {log.get('request_type', 'N/A')} ({log.get('status', 'N/A')})")
        else:
            print(f"❌ Failed to list AI logs: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_django_models():
    """Test Django models directly"""
    print("\n🔧 Testing Django Models Directly")
    print("=" * 50)
    
    try:
        from ai_planner.models import UserProfile, CareerPlan, AIRequestLog
        
        # Count records
        user_count = UserProfile.objects.count()
        plan_count = CareerPlan.objects.count()
        log_count = AIRequestLog.objects.count()
        
        print(f"📊 Database Records:")
        print(f"   User Profiles: {user_count}")
        print(f"   Career Plans: {plan_count}")
        print(f"   AI Request Logs: {log_count}")
        
        # Show recent plans
        if plan_count > 0:
            print(f"\n📋 Recent Career Plans:")
            recent_plans = CareerPlan.objects.order_by('-created_at')[:3]
            for plan in recent_plans:
                print(f"   - {plan.user_profile.name}: {plan.plan_description[:50]}...")
                print(f"     Milestones: {plan.get_milestones_count()}, Weekly Plans: {plan.get_weekly_plans_count()}")
        
        # Show recent logs
        if log_count > 0:
            print(f"\n📝 Recent AI Request Logs:")
            recent_logs = AIRequestLog.objects.order_by('-created_at')[:3]
            for log in recent_logs:
                print(f"   - {log.user_profile.name}: {log.request_type} ({log.status})")
                print(f"     Tokens: {log.tokens_used}, Time: {log.processing_time:.2f}s")
    
    except Exception as e:
        print(f"❌ Error testing models: {str(e)}")

def check_downloads_folder():
    """Check the downloads folder for saved responses"""
    print("\n📁 Checking Downloads Folder")
    print("=" * 50)
    
    downloads_dir = os.path.join(os.path.dirname(__file__), 'downloads')
    
    if os.path.exists(downloads_dir):
        files = os.listdir(downloads_dir)
        json_files = [f for f in files if f.endswith('.json')]
        
        print(f"✅ Downloads folder found: {downloads_dir}")
        print(f"📄 Found {len(json_files)} JSON files:")
        
        for file in sorted(json_files):
            file_path = os.path.join(downloads_dir, file)
            file_size = os.path.getsize(file_path)
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            
            print(f"   - {file}")
            print(f"     Size: {file_size} bytes, Modified: {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Try to read and show basic info
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        if 'success' in data:
                            print(f"     Status: {'✅ Success' if data['success'] else '❌ Error'}")
                        if 'career_plan' in data:
                            print(f"     Type: Career Plan Response")
                        elif 'user_profiles' in data:
                            print(f"     Type: User Profiles Data")
                        elif 'error' in data:
                            print(f"     Type: Error Response")
                    elif isinstance(data, list):
                        print(f"     Type: List with {len(data)} items")
            except Exception as e:
                print(f"     Error reading file: {str(e)}")
    else:
        print(f"❌ Downloads folder not found: {downloads_dir}")

def main():
    """Main test function"""
    print("🚀 AI Career Transformation Planner - Test Suite")
    print("=" * 60)
    
    # Check if Django is properly configured
    try:
        from django.conf import settings
        print(f"✅ Django configured: {settings.DEBUG}")
        print(f"✅ OpenAI API Key: {'✅ Set' if settings.OPENAI_API_KEY else '❌ Not Set'}")
        print(f"✅ OpenAI Assistant ID: {'✅ Set' if settings.OPENAI_ASSISTANT_ID else '❌ Not Set'}")
    except Exception as e:
        print(f"❌ Django configuration error: {str(e)}")
        return
    
    # Run tests
    test_ai_planning_api()
    test_django_models()
    check_downloads_folder()
    
    print("\n" + "=" * 60)
    print("🎉 Test suite completed!")
    print("\nNext steps:")
    print("1. Start Django server: python manage.py runserver")
    print("2. Run migrations: python manage.py makemigrations && python manage.py migrate")
    print("3. Create superuser: python manage.py createsuperuser")
    print("4. Access admin: http://localhost:8000/admin")
    print("5. Test API: http://localhost:8000/plan/api/career-plans/")

if __name__ == "__main__":
    main() 