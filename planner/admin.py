from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    UserProfile, Skill, UserSkill, Education, 
    WorkExperience, CareerGoal, DataImport
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_position', 'years_of_experience', 'location', 'created_at']
    list_filter = ['years_of_experience', 'created_at']
    search_fields = ['user__username', 'user__email', 'current_position', 'location']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'phone', 'date_of_birth')
        }),
        ('Career Information', {
            'fields': ('current_position', 'years_of_experience', 'current_salary', 'desired_salary')
        }),
        ('Location & Links', {
            'fields': ('location', 'linkedin_url', 'github_url', 'portfolio_url')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'description']
    list_filter = ['category']
    search_fields = ['name', 'description']
    ordering = ['category', 'name']

@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    list_display = ['user', 'skill', 'proficiency_level', 'years_of_experience', 'is_current']
    list_filter = ['proficiency_level', 'is_current', 'skill__category']
    search_fields = ['user__username', 'skill__name']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('User & Skill', {
            'fields': ('user', 'skill')
        }),
        ('Proficiency', {
            'fields': ('proficiency_level', 'years_of_experience', 'is_current')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['user', 'institution', 'degree', 'field_of_study', 'start_date', 'end_date']
    list_filter = ['start_date', 'end_date']
    search_fields = ['user__username', 'institution', 'degree', 'field_of_study']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Education Details', {
            'fields': ('institution', 'degree', 'field_of_study')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Additional Information', {
            'fields': ('gpa', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ['user', 'company', 'position', 'start_date', 'end_date', 'is_current']
    list_filter = ['is_current', 'start_date', 'end_date']
    search_fields = ['user__username', 'company', 'position']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Work Details', {
            'fields': ('company', 'position')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'is_current')
        }),
        ('Description', {
            'fields': ('description', 'achievements')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(CareerGoal)
class CareerGoalAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'priority', 'status', 'target_date']
    list_filter = ['priority', 'status', 'target_date']
    search_fields = ['user__username', 'title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Goal Details', {
            'fields': ('title', 'description')
        }),
        ('Planning', {
            'fields': ('target_date', 'priority', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(DataImport)
class DataImportAdmin(admin.ModelAdmin):
    list_display = ['user', 'file_name', 'import_type', 'status', 'records_processed', 'records_successful', 'records_failed', 'created_at']
    list_filter = ['status', 'import_type', 'file_type', 'created_at']
    search_fields = ['user__username', 'file_name']
    readonly_fields = ['created_at', 'completed_at', 'records_processed', 'records_successful', 'records_failed']
    
    fieldsets = (
        ('File Information', {
            'fields': ('user', 'file_name', 'file_type', 'uploaded_file')
        }),
        ('Import Settings', {
            'fields': ('import_type',)
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Results', {
            'fields': ('records_processed', 'records_successful', 'records_failed', 'error_log')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return list(self.readonly_fields) + ['user', 'file_name', 'file_type', 'uploaded_file', 'import_type']
        return self.readonly_fields

# Custom admin site configuration
admin.site.site_header = "Career Transformation Planner Admin"
admin.site.site_title = "Career Planner Admin"
admin.site.index_title = "Welcome to Career Transformation Planner"
