from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction
import csv
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

from planner.models import (
    UserProfile, Skill, UserSkill, Education, 
    WorkExperience, CareerGoal, DataImport
)

class Command(BaseCommand):
    help = 'Import user data from local CSV, Excel, or JSON files'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the file to import')
        parser.add_argument('import_type', type=str, choices=[
            'skills', 'education', 'experience', 'goals', 'profile'
        ], help='Type of data to import')
        parser.add_argument('--username', type=str, help='Username to import data for')
        parser.add_argument('--overwrite', action='store_true', help='Overwrite existing records')
        parser.add_argument('--skip-errors', action='store_true', default=True, help='Skip rows with errors')

    def handle(self, *args, **options):
        file_path = options['file_path']
        import_type = options['import_type']
        username = options['username']
        overwrite = options['overwrite']
        skip_errors = options['skip_errors']

        # Validate file exists
        if not Path(file_path).exists():
            raise CommandError(f'File not found: {file_path}')

        # Get or create user
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                raise CommandError(f'User not found: {username}')
        else:
            # Use first available user or create one
            user = User.objects.first()
            if not user:
                user = User.objects.create_user(
                    username='testuser',
                    email='test@example.com',
                    password='testpass123'
                )
                self.stdout.write(f'Created test user: {user.username}')

        self.stdout.write(f'Importing {import_type} data for user: {user.username}')

        # Determine file type and process
        file_extension = Path(file_path).suffix.lower()
        
        try:
            if file_extension == '.csv':
                self.import_csv(file_path, import_type, user, overwrite, skip_errors)
            elif file_extension in ['.xlsx', '.xls']:
                self.import_excel(file_path, import_type, user, overwrite, skip_errors)
            elif file_extension == '.json':
                self.import_json(file_path, import_type, user, overwrite, skip_errors)
            else:
                raise CommandError(f'Unsupported file type: {file_extension}')
                
            self.stdout.write(
                self.style.SUCCESS(f'Successfully imported {import_type} data')
            )
            
        except Exception as e:
            raise CommandError(f'Import failed: {str(e)}')

    def import_csv(self, file_path, import_type, user, overwrite, skip_errors):
        """Import data from CSV file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            self.process_rows(reader, import_type, user, overwrite, skip_errors)

    def import_excel(self, file_path, import_type, user, overwrite, skip_errors):
        """Import data from Excel file"""
        df = pd.read_excel(file_path)
        rows = [row.to_dict() for _, row in df.iterrows()]
        self.process_rows(rows, import_type, user, overwrite, skip_errors)

    def import_json(self, file_path, import_type, user, overwrite, skip_errors):
        """Import data from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if isinstance(data, list):
                self.process_rows(data, import_type, user, overwrite, skip_errors)
            else:
                raise CommandError('JSON file must contain an array of objects')

    def process_rows(self, rows, import_type, user, overwrite, skip_errors):
        """Process rows of data"""
        processed = 0
        successful = 0
        failed = 0

        for row in rows:
            processed += 1
            try:
                with transaction.atomic():
                    if import_type == 'skills':
                        self.import_skill(row, user, overwrite)
                    elif import_type == 'education':
                        self.import_education(row, user, overwrite)
                    elif import_type == 'experience':
                        self.import_experience(row, user, overwrite)
                    elif import_type == 'goals':
                        self.import_goal(row, user, overwrite)
                    elif import_type == 'profile':
                        self.import_profile(row, user, overwrite)
                    successful += 1
                    
            except Exception as e:
                failed += 1
                error_msg = f'Row {processed}: {str(e)}'
                self.stdout.write(self.style.WARNING(error_msg))
                if not skip_errors:
                    raise CommandError(error_msg)

        self.stdout.write(f'Processed: {processed}, Successful: {successful}, Failed: {failed}')

    def import_skill(self, data, user, overwrite):
        """Import skill data"""
        skill_name = data.get('skill_name', data.get('name'))
        category = data.get('category', 'technical')
        proficiency_level = int(data.get('proficiency_level', 1))
        years_of_experience = int(data.get('years_of_experience', 0))
        
        skill, created = Skill.objects.get_or_create(
            name=skill_name,
            defaults={'category': category}
        )
        
        if created:
            self.stdout.write(f'Created skill: {skill_name}')
        
        if overwrite:
            UserSkill.objects.update_or_create(
                user=user,
                skill=skill,
                defaults={
                    'proficiency_level': proficiency_level,
                    'years_of_experience': years_of_experience
                }
            )
        else:
            UserSkill.objects.get_or_create(
                user=user,
                skill=skill,
                defaults={
                    'proficiency_level': proficiency_level,
                    'years_of_experience': years_of_experience
                }
            )

    def import_education(self, data, user, overwrite):
        """Import education data"""
        if overwrite:
            # Check for existing education
            existing = Education.objects.filter(
                user=user,
                institution=data.get('institution', ''),
                degree=data.get('degree', '')
            ).first()
            if existing:
                existing.delete()
        
        Education.objects.create(
            user=user,
            institution=data.get('institution', ''),
            degree=data.get('degree', ''),
            field_of_study=data.get('field_of_study', ''),
            start_date=datetime.strptime(data.get('start_date'), '%Y-%m-%d').date(),
            end_date=datetime.strptime(data.get('end_date'), '%Y-%m-%d').date() if data.get('end_date') else None,
            gpa=float(data.get('gpa')) if data.get('gpa') else None,
            description=data.get('description', '')
        )

    def import_experience(self, data, user, overwrite):
        """Import work experience data"""
        if overwrite:
            # Check for existing experience
            existing = WorkExperience.objects.filter(
                user=user,
                company=data.get('company', ''),
                position=data.get('position', '')
            ).first()
            if existing:
                existing.delete()
        
        WorkExperience.objects.create(
            user=user,
            company=data.get('company', ''),
            position=data.get('position', ''),
            start_date=datetime.strptime(data.get('start_date'), '%Y-%m-%d').date(),
            end_date=datetime.strptime(data.get('end_date'), '%Y-%m-%d').date() if data.get('end_date') else None,
            is_current=data.get('is_current', False),
            description=data.get('description', ''),
            achievements=data.get('achievements', '')
        )

    def import_goal(self, data, user, overwrite):
        """Import career goal data"""
        if overwrite:
            # Check for existing goal
            existing = CareerGoal.objects.filter(
                user=user,
                title=data.get('title', '')
            ).first()
            if existing:
                existing.delete()
        
        CareerGoal.objects.create(
            user=user,
            title=data.get('title', ''),
            description=data.get('description', ''),
            target_date=datetime.strptime(data.get('target_date'), '%Y-%m-%d').date() if data.get('target_date') else None,
            priority=data.get('priority', 'medium'),
            status=data.get('status', 'not_started')
        )

    def import_profile(self, data, user, overwrite):
        """Import user profile data"""
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'phone': data.get('phone', ''),
                'current_position': data.get('current_position', ''),
                'years_of_experience': int(data.get('years_of_experience', 0)),
                'current_salary': float(data.get('current_salary')) if data.get('current_salary') else None,
                'desired_salary': float(data.get('desired_salary')) if data.get('desired_salary') else None,
                'location': data.get('location', ''),
                'linkedin_url': data.get('linkedin_url', ''),
                'github_url': data.get('github_url', ''),
                'portfolio_url': data.get('portfolio_url', '')
            }
        )
        
        if not created and overwrite:
            # Update existing profile
            for field, value in data.items():
                if hasattr(profile, field) and value:
                    setattr(profile, field, value)
            profile.save() 