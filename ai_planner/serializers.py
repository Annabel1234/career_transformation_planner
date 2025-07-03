from rest_framework import serializers
from .models import UserProfile, CareerPlan, PlanExecution, AIRequestLog

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile data"""
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class CareerPlanSerializer(serializers.ModelSerializer):
    """Serializer for career plans"""
    user_profile = UserProfileSerializer(read_only=True)
    milestones_count = serializers.ReadOnlyField(source='get_milestones_count')
    weekly_plans_count = serializers.ReadOnlyField(source='get_weekly_plans_count')
    total_time_commitment = serializers.ReadOnlyField(source='get_total_time_commitment')
    
    class Meta:
        model = CareerPlan
        fields = '__all__'
        read_only_fields = ['id', 'goal_id', 'created_at', 'updated_at', 'ai_model_used', 'tokens_used', 'processing_time']

class PlanExecutionSerializer(serializers.ModelSerializer):
    """Serializer for plan execution tracking"""
    career_plan = CareerPlanSerializer(read_only=True)
    
    class Meta:
        model = PlanExecution
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

class AIRequestLogSerializer(serializers.ModelSerializer):
    """Serializer for AI request logs"""
    user_profile = UserProfileSerializer(read_only=True)
    career_plan = CareerPlanSerializer(read_only=True)
    
    class Meta:
        model = AIRequestLog
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

class CareerPlanRequestSerializer(serializers.Serializer):
    """Serializer for career plan generation requests"""
    user_profiles = UserProfileSerializer(many=True)
    user_prompt = serializers.CharField(required=False, allow_blank=True)
    
    def validate_user_profiles(self, value):
        """Validate that at least one user profile is provided"""
        if not value:
            raise serializers.ValidationError("At least one user profile is required.")
        return value

class CareerPlanResponseSerializer(serializers.Serializer):
    """Serializer for career plan responses"""
    goal_id = serializers.UUIDField()
    plan_description = serializers.CharField()
    blockers = serializers.ListField(child=serializers.CharField())
    milestones = serializers.ListField(child=serializers.DictField())
    weekly_plans = serializers.ListField(child=serializers.DictField())
    
    def validate_milestones(self, value):
        """Validate milestones structure"""
        for milestone in value:
            required_fields = ['milestone_order', 'title', 'description', 'target_date']
            for field in required_fields:
                if field not in milestone:
                    raise serializers.ValidationError(f"Milestone missing required field: {field}")
        return value
    
    def validate_weekly_plans(self, value):
        """Validate weekly plans structure"""
        for plan in value:
            required_fields = ['week_number', 'year', 'week_start_date', 'week_end_date', 
                             'weekly_objective', 'focus_areas', 'weekly_time_commitment']
            for field in required_fields:
                if field not in plan:
                    raise serializers.ValidationError(f"Weekly plan missing required field: {field}")
            
            # Validate focus areas limit
            focus_areas = plan.get('focus_areas', [])
            if len(focus_areas) > 5:
                raise serializers.ValidationError("Weekly plan cannot have more than 5 focus areas")
        
        return value

class PlanGenerationResponseSerializer(serializers.Serializer):
    """Serializer for complete plan generation response"""
    success = serializers.BooleanField()
    message = serializers.CharField()
    career_plan = CareerPlanSerializer()
    file_path = serializers.CharField(required=False)
    processing_time = serializers.FloatField()
    tokens_used = serializers.IntegerField()

class ErrorResponseSerializer(serializers.Serializer):
    """Serializer for error responses"""
    success = serializers.BooleanField(default=False)
    error = serializers.CharField()
    details = serializers.CharField(required=False)
    file_path = serializers.CharField(required=False) 