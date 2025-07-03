from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

class UserProfile(models.Model):
    """Extended user profile for career planning"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    current_position = models.CharField(max_length=200, blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    current_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    desired_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True)
    linkedin_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    portfolio_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Skill(models.Model):
    """Skills that users can have"""
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, choices=[
        ('technical', 'Technical'),
        ('soft', 'Soft Skills'),
        ('language', 'Programming Language'),
        ('framework', 'Framework'),
        ('tool', 'Tool'),
        ('certification', 'Certification'),
    ])
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.category})"

class UserSkill(models.Model):
    """User's skills with proficiency levels"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    proficiency_level = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1=Beginner, 5=Expert"
    )
    years_of_experience = models.PositiveIntegerField(default=0)
    is_current = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'skill']

    def __str__(self):
        return f"{self.user.username} - {self.skill.name} (Level {self.proficiency_level})"

class Education(models.Model):
    """User's educational background"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='education')
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=200)
    field_of_study = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.degree} at {self.institution}"

class WorkExperience(models.Model):
    """User's work experience"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='work_experience')
    company = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField()
    achievements = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.position} at {self.company}"

class CareerGoal(models.Model):
    """User's career goals and aspirations"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='career_goals')
    title = models.CharField(max_length=200)
    description = models.TextField()
    target_date = models.DateField(blank=True, null=True)
    priority = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], default='medium')
    status = models.CharField(max_length=20, choices=[
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
    ], default='not_started')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"

class DataImport(models.Model):
    """Track data imports from local files"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='data_imports')
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50, choices=[
        ('csv', 'CSV'),
        ('excel', 'Excel'),
        ('json', 'JSON'),
        ('xml', 'XML'),
    ])
    uploaded_file = models.FileField(upload_to='imports/')
    import_type = models.CharField(max_length=50, choices=[
        ('skills', 'Skills'),
        ('education', 'Education'),
        ('experience', 'Work Experience'),
        ('goals', 'Career Goals'),
        ('profile', 'User Profile'),
        ('bulk', 'Bulk Import'),
    ])
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ], default='pending')
    records_processed = models.PositiveIntegerField(default=0)
    records_successful = models.PositiveIntegerField(default=0)
    records_failed = models.PositiveIntegerField(default=0)
    error_log = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.file_name} ({self.import_type})"
