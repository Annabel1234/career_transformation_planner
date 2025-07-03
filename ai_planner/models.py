from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import json

class UserProfile(models.Model):
    """User profile data from frontend"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    google_id = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=200)
    picture_url = models.URLField(blank=True, null=True)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    education = models.TextField()
    years_experience = models.PositiveIntegerField()
    income_level = models.CharField(max_length=50)
    last_career_change = models.DateField()
    summary = models.TextField()
    
    # Personality traits as JSON
    personality_traits = models.JSONField(default=dict)
    
    # Lists as JSON
    motivators = models.JSONField(default=list)
    
    # Work style as JSON
    work_style = models.JSONField(default=dict)
    
    user_type = models.CharField(max_length=50)
    onboarding_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.email})"

class CareerPlan(models.Model):
    """AI-generated career transformation plan"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='career_plans')
    goal_id = models.CharField(max_length=255)  # Can be email, UUID, or any string
    plan_description = models.TextField()
    
    # Blockers as JSON
    blockers = models.JSONField(default=list)
    
    # Milestones as JSON
    milestones = models.JSONField(default=list)
    
    # Weekly plans as JSON
    weekly_plans = models.JSONField(default=list)
    
    # User prompt for the plan
    user_prompt = models.TextField(blank=True)
    
    # AI response metadata
    ai_model_used = models.CharField(max_length=100, default='gpt-3.5-turbo')
    tokens_used = models.PositiveIntegerField(default=0)
    processing_time = models.FloatField(default=0.0)  # in seconds
    
    # Status tracking
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ], default='draft')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Career Plan for {self.user_profile.name} - {self.plan_description[:50]}..."

    def get_milestones_count(self):
        """Get the number of milestones"""
        return len(self.milestones) if self.milestones else 0

    def get_weekly_plans_count(self):
        """Get the number of weekly plans"""
        return len(self.weekly_plans) if self.weekly_plans else 0

    def get_total_time_commitment(self):
        """Calculate total time commitment from weekly plans"""
        if not self.weekly_plans:
            return 0
        return sum(plan.get('weekly_time_commitment', 0) for plan in self.weekly_plans)

class PlanExecution(models.Model):
    """Track execution of career plan milestones and tasks"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    career_plan = models.ForeignKey(CareerPlan, on_delete=models.CASCADE, related_name='executions')
    milestone_order = models.PositiveIntegerField()
    milestone_title = models.CharField(max_length=200)
    week_number = models.PositiveIntegerField()
    year = models.PositiveIntegerField()
    
    # Task details
    task_description = models.TextField()
    focus_areas = models.JSONField(default=list)
    time_commitment = models.PositiveIntegerField()  # in minutes
    
    # Progress tracking
    status = models.CharField(max_length=20, choices=[
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
    ], default='not_started')
    
    completion_percentage = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    
    # Dates
    planned_start_date = models.DateField()
    planned_end_date = models.DateField()
    actual_start_date = models.DateField(blank=True, null=True)
    actual_completion_date = models.DateField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['career_plan', 'milestone_order', 'week_number', 'year']

    def __str__(self):
        return f"{self.career_plan.user_profile.name} - Week {self.week_number} - {self.task_description[:50]}..."

class AIRequestLog(models.Model):
    """Log all AI requests for monitoring and debugging"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='ai_requests')
    career_plan = models.ForeignKey(CareerPlan, on_delete=models.CASCADE, related_name='ai_requests', blank=True, null=True)
    
    # Request details
    request_type = models.CharField(max_length=50, choices=[
        ('plan_generation', 'Plan Generation'),
        ('plan_refinement', 'Plan Refinement'),
        ('milestone_update', 'Milestone Update'),
    ])
    
    # Input and output
    input_data = models.JSONField()
    output_data = models.JSONField()
    
    # AI metadata
    ai_model = models.CharField(max_length=100)
    tokens_used = models.PositiveIntegerField()
    processing_time = models.FloatField()  # in seconds
    
    # Status
    status = models.CharField(max_length=20, choices=[
        ('success', 'Success'),
        ('error', 'Error'),
        ('partial', 'Partial Success'),
    ])
    
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AI Request {self.id} - {self.request_type} - {self.status}"

    class Meta:
        ordering = ['-created_at'] 