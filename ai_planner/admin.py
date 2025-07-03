from django.contrib import admin
from .models import UserProfile, CareerPlan, PlanExecution, AIRequestLog

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'title', 'age', 'years_experience', 'user_type', 'created_at']
    list_filter = ['user_type', 'age', 'years_experience', 'income_level', 'created_at']
    search_fields = ['name', 'email', 'title', 'summary']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'email', 'google_id', 'name', 'picture_url', 'age', 'gender')
        }),
        ('Career Information', {
            'fields': ('title', 'education', 'years_experience', 'income_level', 'last_career_change')
        }),
        ('Personal Details', {
            'fields': ('summary', 'user_type', 'onboarding_completed')
        }),
        ('Personality & Preferences', {
            'fields': ('personality_traits', 'motivators', 'work_style'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(CareerPlan)
class CareerPlanAdmin(admin.ModelAdmin):
    list_display = ['user_profile', 'plan_description', 'status', 'milestones_count', 'weekly_plans_count', 'created_at']
    list_filter = ['status', 'ai_model_used', 'created_at']
    search_fields = ['user_profile__name', 'user_profile__email', 'plan_description']
    readonly_fields = ['id', 'goal_id', 'created_at', 'updated_at', 'ai_model_used', 'tokens_used', 'processing_time']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user_profile', 'goal_id', 'status')
        }),
        ('Plan Details', {
            'fields': ('plan_description', 'user_prompt')
        }),
        ('Plan Data', {
            'fields': ('blockers', 'milestones', 'weekly_plans'),
            'classes': ('collapse',)
        }),
        ('AI Metadata', {
            'fields': ('ai_model_used', 'tokens_used', 'processing_time'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def milestones_count(self, obj):
        return obj.get_milestones_count()
    milestones_count.short_description = 'Milestones'
    
    def weekly_plans_count(self, obj):
        return obj.get_weekly_plans_count()
    weekly_plans_count.short_description = 'Weekly Plans'

@admin.register(PlanExecution)
class PlanExecutionAdmin(admin.ModelAdmin):
    list_display = ['career_plan', 'milestone_title', 'week_number', 'year', 'status', 'completion_percentage']
    list_filter = ['status', 'year', 'week_number', 'created_at']
    search_fields = ['career_plan__user_profile__name', 'milestone_title', 'task_description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'career_plan', 'milestone_order', 'milestone_title')
        }),
        ('Task Details', {
            'fields': ('week_number', 'year', 'task_description', 'focus_areas', 'time_commitment')
        }),
        ('Progress Tracking', {
            'fields': ('status', 'completion_percentage', 'notes')
        }),
        ('Dates', {
            'fields': ('planned_start_date', 'planned_end_date', 'actual_start_date', 'actual_completion_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(AIRequestLog)
class AIRequestLogAdmin(admin.ModelAdmin):
    list_display = ['user_profile', 'request_type', 'ai_model', 'tokens_used', 'processing_time', 'status', 'created_at']
    list_filter = ['request_type', 'ai_model', 'status', 'created_at']
    search_fields = ['user_profile__name', 'user_profile__email', 'error_message']
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user_profile', 'career_plan', 'request_type')
        }),
        ('Request Data', {
            'fields': ('input_data', 'output_data'),
            'classes': ('collapse',)
        }),
        ('AI Metadata', {
            'fields': ('ai_model', 'tokens_used', 'processing_time', 'status')
        }),
        ('Error Information', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False  # Read-only model

# Custom admin site configuration
admin.site.site_header = "AI Career Transformation Planner Admin"
admin.site.site_title = "AI Career Planner Admin"
admin.site.index_title = "Welcome to AI Career Transformation Planner" 