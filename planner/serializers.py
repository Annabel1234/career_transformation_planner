from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    UserProfile, Skill, UserSkill, Education, 
    WorkExperience, CareerGoal, DataImport
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = '__all__'

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'

class UserSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source='skill.name', read_only=True)
    skill_category = serializers.CharField(source='skill.category', read_only=True)
    
    class Meta:
        model = UserSkill
        fields = '__all__'

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = '__all__'

class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        fields = '__all__'

class CareerGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareerGoal
        fields = '__all__'

class DataImportSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataImport
        fields = '__all__'
        read_only_fields = ['status', 'records_processed', 'records_successful', 'records_failed', 'error_log', 'completed_at']

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    import_type = serializers.ChoiceField(choices=[
        ('skills', 'Skills'),
        ('education', 'Education'),
        ('experience', 'Work Experience'),
        ('goals', 'Career Goals'),
        ('profile', 'User Profile'),
        ('bulk', 'Bulk Import'),
    ])
    file_type = serializers.ChoiceField(choices=[
        ('csv', 'CSV'),
        ('excel', 'Excel'),
        ('json', 'JSON'),
        ('xml', 'XML'),
    ])

class BulkImportSerializer(serializers.Serializer):
    """Serializer for bulk importing data from CSV/Excel files"""
    file = serializers.FileField()
    import_type = serializers.ChoiceField(choices=[
        ('skills', 'Skills'),
        ('education', 'Education'),
        ('experience', 'Work Experience'),
        ('goals', 'Career Goals'),
        ('profile', 'User Profile'),
    ])
    overwrite_existing = serializers.BooleanField(default=False)
    skip_errors = serializers.BooleanField(default=True) 