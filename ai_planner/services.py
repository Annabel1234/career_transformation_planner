import openai
import json
import time
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from .models import AIRequestLog

class AICareerPlanningService:
    """Service for AI-powered career planning"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.AI_PLANNING_CONFIG['model']
        self.max_tokens = settings.AI_PLANNING_CONFIG['max_tokens']
        self.temperature = settings.AI_PLANNING_CONFIG['temperature']
        self.system_prompt = settings.AI_PLANNING_CONFIG['system_prompt']
    
    def generate_career_plan(self, user_profile, user_prompt=""):
        """Generate a career transformation plan using OpenAI"""
        start_time = time.time()
        
        try:
            # Prepare the user message
            user_message = self._prepare_user_message(user_profile, user_prompt)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            # Extract response
            ai_response = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            processing_time = time.time() - start_time
            
            # Parse JSON response
            try:
                plan_data = json.loads(ai_response)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON response from AI: {str(e)}")
            
            # Validate response structure
            self._validate_plan_response(plan_data)
            
            return {
                'success': True,
                'plan_data': plan_data,
                'tokens_used': tokens_used,
                'processing_time': processing_time,
                'ai_response': ai_response
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            return {
                'success': False,
                'error': str(e),
                'processing_time': processing_time,
                'tokens_used': 0
            }
    
    def _prepare_user_message(self, user_profile, user_prompt):
        """Prepare the user message for AI"""
        message_parts = [
            f"Generate a career transformation plan for the following user:",
            f"\nName: {user_profile.name}",
            f"Age: {user_profile.age}",
            f"Gender: {user_profile.gender}",
            f"Current Title: {user_profile.title}",
            f"Education: {user_profile.education}",
            f"Years of Experience: {user_profile.years_experience}",
            f"Income Level: {user_profile.income_level}",
            f"Last Career Change: {user_profile.last_career_change}",
            f"User Type: {user_profile.user_type}",
            f"\nSummary: {user_profile.summary}",
            f"\nPersonality Traits: {json.dumps(user_profile.personality_traits, indent=2)}",
            f"\nMotivators: {json.dumps(user_profile.motivators, indent=2)}",
            f"\nWork Style: {json.dumps(user_profile.work_style, indent=2)}"
        ]
        
        if user_prompt:
            message_parts.append(f"\nAdditional Requirements: {user_prompt}")
        
        message_parts.append("\n\nPlease generate a comprehensive career transformation plan with exactly 4 milestones and 12 weekly plans. Each weekly plan should have maximum 5 focus areas.")
        
        return "\n".join(message_parts)
    
    def _validate_plan_response(self, plan_data):
        """Validate the AI response structure"""
        required_fields = ['goal_id', 'plan_description', 'blockers', 'milestones', 'weekly_plans']
        
        for field in required_fields:
            if field not in plan_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate milestones
        milestones = plan_data.get('milestones', [])
        if len(milestones) != 4:
            raise ValueError(f"Expected exactly 4 milestones, got {len(milestones)}")
        
        for i, milestone in enumerate(milestones):
            required_milestone_fields = ['milestone_order', 'title', 'description', 'target_date']
            for field in required_milestone_fields:
                if field not in milestone:
                    raise ValueError(f"Milestone {i+1} missing required field: {field}")
        
        # Validate weekly plans
        weekly_plans = plan_data.get('weekly_plans', [])
        if len(weekly_plans) != 12:
            raise ValueError(f"Expected exactly 12 weekly plans, got {len(weekly_plans)}")
        
        for i, plan in enumerate(weekly_plans):
            required_plan_fields = ['week_number', 'year', 'week_start_date', 'week_end_date', 
                                  'weekly_objective', 'focus_areas', 'weekly_time_commitment']
            for field in required_plan_fields:
                if field not in plan:
                    raise ValueError(f"Weekly plan {i+1} missing required field: {field}")
            
            # Validate focus areas limit
            focus_areas = plan.get('focus_areas', [])
            if len(focus_areas) > 5:
                raise ValueError(f"Weekly plan {i+1} has more than 5 focus areas: {len(focus_areas)}")
    
    def log_request(self, user_profile, request_type, input_data, output_data, 
                   ai_model, tokens_used, processing_time, status, error_message=""):
        """Log AI request for monitoring"""
        try:
            AIRequestLog.objects.create(
                user_profile=user_profile,
                request_type=request_type,
                input_data=input_data,
                output_data=output_data,
                ai_model=ai_model,
                tokens_used=tokens_used,
                processing_time=processing_time,
                status=status,
                error_message=error_message
            )
        except Exception as e:
            # Log error but don't fail the main request
            print(f"Failed to log AI request: {str(e)}")

class ResponseStorageService:
    """Service for storing API responses to local files"""
    
    def __init__(self):
        self.download_dir = settings.BASE_DIR / 'downloads'
        self.download_dir.mkdir(exist_ok=True)
    
    def save_response_to_file(self, data, filename, format_type='json'):
        """Save response data to local file"""
        file_path = self.download_dir / filename
        
        try:
            if format_type == 'json':
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            else:
                # For other formats, save as JSON for now
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            return str(file_path)
        except Exception as e:
            print(f"Error saving response to file: {e}")
            return None
    
    def generate_filename(self, prefix, user_name, timestamp=None):
        """Generate a filename with timestamp"""
        if timestamp is None:
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        
        # Clean user name for filename
        clean_name = "".join(c for c in user_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_name = clean_name.replace(' ', '_')
        
        return f"{prefix}_{clean_name}_{timestamp}.json" 