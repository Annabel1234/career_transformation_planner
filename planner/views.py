from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from django.conf import settings
import csv
import json
import pandas as pd
from io import StringIO
from datetime import datetime
import os
from pathlib import Path

from .models import (
    UserProfile, Skill, UserSkill, Education, 
    WorkExperience, CareerGoal, DataImport
)
from .serializers import (
    UserProfileSerializer, SkillSerializer, UserSkillSerializer,
    EducationSerializer, WorkExperienceSerializer, CareerGoalSerializer,
    DataImportSerializer, FileUploadSerializer, BulkImportSerializer
)

class ResponseStorageMixin:
    """Mixin to handle storing API responses to local download folder"""
    
    def save_response_to_file(self, data, filename, format_type='json'):
        """Save API response data to local download folder"""
        download_dir = Path(settings.BASE_DIR) / 'downloads'
        download_dir.mkdir(exist_ok=True)
        
        file_path = download_dir / filename
        
        try:
            if format_type == 'json':
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            elif format_type == 'csv':
                if isinstance(data, dict) and 'results' in data:
                    data = data['results']
                if data:
                    df = pd.DataFrame(data)
                    df.to_csv(file_path, index=False, encoding='utf-8')
                else:
                    # Create empty CSV with headers
                    pd.DataFrame().to_csv(file_path, index=False, encoding='utf-8')
            elif format_type == 'excel':
                if isinstance(data, dict) and 'results' in data:
                    data = data['results']
                if data:
                    df = pd.DataFrame(data)
                    df.to_excel(file_path, index=False)
                else:
                    # Create empty Excel file
                    pd.DataFrame().to_excel(file_path, index=False)
            
            return str(file_path)
        except Exception as e:
            print(f"Error saving response to file: {e}")
            return None

    def export_user_data(self, user, format_type='json'):
        """Export all user data in specified format"""
        data = {
            'user_info': {
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'date_joined': user.date_joined.isoformat(),
            },
            'profile': None,
            'skills': [],
            'education': [],
            'experience': [],
            'goals': [],
            'imports': [],
            'export_date': timezone.now().isoformat()
        }
        
        # Get user profile
        try:
            profile = UserProfile.objects.get(user=user)
            data['profile'] = UserProfileSerializer(profile).data
        except UserProfile.DoesNotExist:
            pass
        
        # Get user skills
        user_skills = UserSkill.objects.filter(user=user).select_related('skill')
        data['skills'] = UserSkillSerializer(user_skills, many=True).data
        
        # Get education
        education = Education.objects.filter(user=user)
        data['education'] = EducationSerializer(education, many=True).data
        
        # Get work experience
        experience = WorkExperience.objects.filter(user=user)
        data['experience'] = WorkExperienceSerializer(experience, many=True).data
        
        # Get career goals
        goals = CareerGoal.objects.filter(user=user)
        data['goals'] = CareerGoalSerializer(goals, many=True).data
        
        # Get import history
        imports = DataImport.objects.filter(user=user)
        data['imports'] = DataImportSerializer(imports, many=True).data
        
        return data

class UserProfileViewSet(viewsets.ModelViewSet, ResponseStorageMixin):
    """ViewSet for user profile management"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def export(self, request):
        """Export user profile data to local file"""
        format_type = request.query_params.get('format', 'json')
        user = request.user
        
        try:
            profile = self.get_queryset().first()
            if profile:
                data = UserProfileSerializer(profile).data
                filename = f"user_profile_{user.username}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.{format_type}"
                file_path = self.save_response_to_file(data, filename, format_type)
                
                if file_path:
                    return Response({
                        'message': 'Profile exported successfully',
                        'file_path': file_path,
                        'format': format_type
                    })
                else:
                    return Response({'error': 'Failed to save file'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({'error': 'No profile found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SkillViewSet(viewsets.ModelViewSet):
    """ViewSet for skills management"""
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticated]

class UserSkillViewSet(viewsets.ModelViewSet, ResponseStorageMixin):
    """ViewSet for user skills management"""
    serializer_class = UserSkillSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserSkill.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def export(self, request):
        """Export user skills data to local file"""
        format_type = request.query_params.get('format', 'json')
        user = request.user
        
        try:
            skills = self.get_queryset()
            data = UserSkillSerializer(skills, many=True).data
            filename = f"user_skills_{user.username}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.{format_type}"
            file_path = self.save_response_to_file(data, filename, format_type)
            
            if file_path:
                return Response({
                    'message': 'Skills exported successfully',
                    'file_path': file_path,
                    'format': format_type,
                    'count': len(data)
                })
            else:
                return Response({'error': 'Failed to save file'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class EducationViewSet(viewsets.ModelViewSet, ResponseStorageMixin):
    """ViewSet for education management"""
    serializer_class = EducationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Education.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def export(self, request):
        """Export education data to local file"""
        format_type = request.query_params.get('format', 'json')
        user = request.user
        
        try:
            education = self.get_queryset()
            data = EducationSerializer(education, many=True).data
            filename = f"education_{user.username}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.{format_type}"
            file_path = self.save_response_to_file(data, filename, format_type)
            
            if file_path:
                return Response({
                    'message': 'Education data exported successfully',
                    'file_path': file_path,
                    'format': format_type,
                    'count': len(data)
                })
            else:
                return Response({'error': 'Failed to save file'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class WorkExperienceViewSet(viewsets.ModelViewSet, ResponseStorageMixin):
    """ViewSet for work experience management"""
    serializer_class = WorkExperienceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return WorkExperience.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def export(self, request):
        """Export work experience data to local file"""
        format_type = request.query_params.get('format', 'json')
        user = request.user
        
        try:
            experience = self.get_queryset()
            data = WorkExperienceSerializer(experience, many=True).data
            filename = f"work_experience_{user.username}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.{format_type}"
            file_path = self.save_response_to_file(data, filename, format_type)
            
            if file_path:
                return Response({
                    'message': 'Work experience exported successfully',
                    'file_path': file_path,
                    'format': format_type,
                    'count': len(data)
                })
            else:
                return Response({'error': 'Failed to save file'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CareerGoalViewSet(viewsets.ModelViewSet, ResponseStorageMixin):
    """ViewSet for career goals management"""
    serializer_class = CareerGoalSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CareerGoal.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def export(self, request):
        """Export career goals data to local file"""
        format_type = request.query_params.get('format', 'json')
        user = request.user
        
        try:
            goals = self.get_queryset()
            data = CareerGoalSerializer(goals, many=True).data
            filename = f"career_goals_{user.username}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.{format_type}"
            file_path = self.save_response_to_file(data, filename, format_type)
            
            if file_path:
                return Response({
                    'message': 'Career goals exported successfully',
                    'file_path': file_path,
                    'format': format_type,
                    'count': len(data)
                })
            else:
                return Response({'error': 'Failed to save file'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DataImportViewSet(viewsets.ModelViewSet, ResponseStorageMixin):
    """ViewSet for data import management"""
    serializer_class = DataImportSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_queryset(self):
        return DataImport.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def export(self, request):
        """Export import history to local file"""
        format_type = request.query_params.get('format', 'json')
        user = request.user
        
        try:
            imports = self.get_queryset()
            data = DataImportSerializer(imports, many=True).data
            filename = f"import_history_{user.username}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.{format_type}"
            file_path = self.save_response_to_file(data, filename, format_type)
            
            if file_path:
                return Response({
                    'message': 'Import history exported successfully',
                    'file_path': file_path,
                    'format': format_type,
                    'count': len(data)
                })
            else:
                return Response({'error': 'Failed to save file'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def upload_file(self, request):
        """Upload and process a file for data import"""
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            file_obj = request.FILES['file']
            import_type = serializer.validated_data['import_type']
            file_type = serializer.validated_data['file_type']
            
            # Create import record
            data_import = DataImport.objects.create(
                user=request.user,
                file_name=file_obj.name,
                file_type=file_type,
                import_type=import_type,
                uploaded_file=file_obj,
                status='processing'
            )
            
            try:
                # Process the file based on type
                if file_type == 'csv':
                    self._process_csv_file(data_import, file_obj, import_type)
                elif file_type == 'excel':
                    self._process_excel_file(data_import, file_obj, import_type)
                elif file_type == 'json':
                    self._process_json_file(data_import, file_obj, import_type)
                
                data_import.status = 'completed'
                data_import.completed_at = timezone.now()
                data_import.save()
                
                # Save response to local file
                response_data = {
                    'message': 'File uploaded and processed successfully',
                    'import_id': data_import.id,
                    'records_processed': data_import.records_processed,
                    'records_successful': data_import.records_successful,
                    'records_failed': data_import.records_failed,
                    'timestamp': timezone.now().isoformat()
                }
                
                filename = f"import_response_{request.user.username}_{data_import.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.json"
                file_path = self.save_response_to_file(response_data, filename, 'json')
                
                response_data['file_path'] = file_path
                
                return Response(response_data, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                data_import.status = 'failed'
                data_import.error_log = str(e)
                data_import.save()
                
                error_data = {
                    'error': 'Failed to process file',
                    'details': str(e),
                    'import_id': data_import.id,
                    'timestamp': timezone.now().isoformat()
                }
                
                filename = f"import_error_{request.user.username}_{data_import.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.json"
                file_path = self.save_response_to_file(error_data, filename, 'json')
                
                error_data['file_path'] = file_path
                
                return Response(error_data, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _process_csv_file(self, data_import, file_obj, import_type):
        """Process CSV file for data import"""
        decoded_file = file_obj.read().decode('utf-8')
        csv_data = csv.DictReader(StringIO(decoded_file))
        
        records_processed = 0
        records_successful = 0
        records_failed = 0
        errors = []
        
        for row in csv_data:
            records_processed += 1
            try:
                with transaction.atomic():
                    if import_type == 'skills':
                        self._import_skill_from_csv(row, data_import.user)
                    elif import_type == 'education':
                        self._import_education_from_csv(row, data_import.user)
                    elif import_type == 'experience':
                        self._import_experience_from_csv(row, data_import.user)
                    elif import_type == 'goals':
                        self._import_goal_from_csv(row, data_import.user)
                    elif import_type == 'profile':
                        self._import_profile_from_csv(row, data_import.user)
                    records_successful += 1
            except Exception as e:
                records_failed += 1
                errors.append(f"Row {records_processed}: {str(e)}")
        
        data_import.records_processed = records_processed
        data_import.records_successful = records_successful
        data_import.records_failed = records_failed
        data_import.error_log = '\n'.join(errors)
        data_import.save()

    def _process_excel_file(self, data_import, file_obj, import_type):
        """Process Excel file for data import"""
        df = pd.read_excel(file_obj)
        records_processed = 0
        records_successful = 0
        records_failed = 0
        errors = []
        
        for index, row in df.iterrows():
            records_processed += 1
            try:
                with transaction.atomic():
                    row_dict = row.to_dict()
                    if import_type == 'skills':
                        self._import_skill_from_dict(row_dict, data_import.user)
                    elif import_type == 'education':
                        self._import_education_from_dict(row_dict, data_import.user)
                    elif import_type == 'experience':
                        self._import_experience_from_dict(row_dict, data_import.user)
                    elif import_type == 'goals':
                        self._import_goal_from_dict(row_dict, data_import.user)
                    elif import_type == 'profile':
                        self._import_profile_from_dict(row_dict, data_import.user)
                    records_successful += 1
            except Exception as e:
                records_failed += 1
                errors.append(f"Row {index + 1}: {str(e)}")
        
        data_import.records_processed = records_processed
        data_import.records_successful = records_successful
        data_import.records_failed = records_failed
        data_import.error_log = '\n'.join(errors)
        data_import.save()

    def _process_json_file(self, data_import, file_obj, import_type):
        """Process JSON file for data import"""
        json_data = json.load(file_obj)
        records_processed = 0
        records_successful = 0
        records_failed = 0
        errors = []
        
        if isinstance(json_data, list):
            for item in json_data:
                records_processed += 1
                try:
                    with transaction.atomic():
                        if import_type == 'skills':
                            self._import_skill_from_dict(item, data_import.user)
                        elif import_type == 'education':
                            self._import_education_from_dict(item, data_import.user)
                        elif import_type == 'experience':
                            self._import_experience_from_dict(item, data_import.user)
                        elif import_type == 'goals':
                            self._import_goal_from_dict(item, data_import.user)
                        elif import_type == 'profile':
                            self._import_profile_from_dict(item, data_import.user)
                        records_successful += 1
                except Exception as e:
                    records_failed += 1
                    errors.append(f"Item {records_processed}: {str(e)}")
        
        data_import.records_processed = records_processed
        data_import.records_successful = records_successful
        data_import.records_failed = records_failed
        data_import.error_log = '\n'.join(errors)
        data_import.save()

    def _import_skill_from_dict(self, data, user):
        """Import skill from dictionary data"""
        skill_name = data.get('skill_name', data.get('name'))
        category = data.get('category', 'technical')
        proficiency_level = int(data.get('proficiency_level', 1))
        years_of_experience = int(data.get('years_of_experience', 0))
        
        skill, created = Skill.objects.get_or_create(
            name=skill_name,
            defaults={'category': category}
        )
        
        UserSkill.objects.get_or_create(
            user=user,
            skill=skill,
            defaults={
                'proficiency_level': proficiency_level,
                'years_of_experience': years_of_experience
            }
        )

    def _import_education_from_dict(self, data, user):
        """Import education from dictionary data"""
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

    def _import_experience_from_dict(self, data, user):
        """Import work experience from dictionary data"""
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

    def _import_goal_from_dict(self, data, user):
        """Import career goal from dictionary data"""
        CareerGoal.objects.create(
            user=user,
            title=data.get('title', ''),
            description=data.get('description', ''),
            target_date=datetime.strptime(data.get('target_date'), '%Y-%m-%d').date() if data.get('target_date') else None,
            priority=data.get('priority', 'medium'),
            status=data.get('status', 'not_started')
        )

    def _import_profile_from_dict(self, data, user):
        """Import user profile from dictionary data"""
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
        if not created:
            # Update existing profile
            for field, value in data.items():
                if hasattr(profile, field) and value:
                    setattr(profile, field, value)
            profile.save()

    # Alias methods for CSV processing
    def _import_skill_from_csv(self, row, user):
        self._import_skill_from_dict(row, user)
    
    def _import_education_from_csv(self, row, user):
        self._import_education_from_dict(row, user)
    
    def _import_experience_from_csv(self, row, user):
        self._import_experience_from_dict(row, user)
    
    def _import_goal_from_csv(self, row, user):
        self._import_goal_from_dict(row, user)
    
    def _import_profile_from_csv(self, row, user):
        self._import_profile_from_dict(row, user)

class UploadViewSet(viewsets.ViewSet, ResponseStorageMixin):
    """ViewSet for simple file uploads"""
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @action(detail=False, methods=['get'])
    def export_all(self, request):
        """Export all user data to local files"""
        format_type = request.query_params.get('format', 'json')
        user = request.user
        
        try:
            # Export all user data
            all_data = self.export_user_data(user, format_type)
            
            # Save to file
            filename = f"all_user_data_{user.username}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.{format_type}"
            file_path = self.save_response_to_file(all_data, filename, format_type)
            
            if file_path:
                return Response({
                    'message': 'All user data exported successfully',
                    'file_path': file_path,
                    'format': format_type,
                    'data_summary': {
                        'skills_count': len(all_data['skills']),
                        'education_count': len(all_data['education']),
                        'experience_count': len(all_data['experience']),
                        'goals_count': len(all_data['goals']),
                        'imports_count': len(all_data['imports'])
                    }
                })
            else:
                return Response({'error': 'Failed to save file'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def bulk_import(self, request):
        """Bulk import data from various file formats"""
        serializer = BulkImportSerializer(data=request.data)
        if serializer.is_valid():
            file_obj = request.FILES['file']
            import_type = serializer.validated_data['import_type']
            overwrite_existing = serializer.validated_data['overwrite_existing']
            skip_errors = serializer.validated_data['skip_errors']
            
            # Process the file
            try:
                if file_obj.name.endswith('.csv'):
                    result = self._process_csv_bulk(file_obj, import_type, request.user, overwrite_existing, skip_errors)
                elif file_obj.name.endswith(('.xlsx', '.xls')):
                    result = self._process_excel_bulk(file_obj, import_type, request.user, overwrite_existing, skip_errors)
                elif file_obj.name.endswith('.json'):
                    result = self._process_json_bulk(file_obj, import_type, request.user, overwrite_existing, skip_errors)
                else:
                    return Response({'error': 'Unsupported file format'}, status=status.HTTP_400_BAD_REQUEST)
                
                # Save response to local file
                result['timestamp'] = timezone.now().isoformat()
                result['user'] = request.user.username
                result['import_type'] = import_type
                
                filename = f"bulk_import_response_{request.user.username}_{import_type}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.json"
                file_path = self.save_response_to_file(result, filename, 'json')
                
                result['file_path'] = file_path
                
                return Response(result, status=status.HTTP_200_OK)
                
            except Exception as e:
                error_data = {
                    'error': str(e),
                    'timestamp': timezone.now().isoformat(),
                    'user': request.user.username,
                    'import_type': import_type
                }
                
                filename = f"bulk_import_error_{request.user.username}_{import_type}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.json"
                file_path = self.save_response_to_file(error_data, filename, 'json')
                
                error_data['file_path'] = file_path
                
                return Response(error_data, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _process_csv_bulk(self, file_obj, import_type, user, overwrite_existing, skip_errors):
        """Process CSV file for bulk import"""
        decoded_file = file_obj.read().decode('utf-8')
        csv_data = csv.DictReader(StringIO(decoded_file))
        
        results = {
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        for row in csv_data:
            results['processed'] += 1
            try:
                # Process based on import type
                if import_type == 'skills':
                    self._import_skill_bulk(row, user, overwrite_existing)
                elif import_type == 'education':
                    self._import_education_bulk(row, user, overwrite_existing)
                elif import_type == 'experience':
                    self._import_experience_bulk(row, user, overwrite_existing)
                elif import_type == 'goals':
                    self._import_goal_bulk(row, user, overwrite_existing)
                elif import_type == 'profile':
                    self._import_profile_bulk(row, user, overwrite_existing)
                
                results['successful'] += 1
            except Exception as e:
                results['failed'] += 1
                if not skip_errors:
                    raise e
                results['errors'].append(f"Row {results['processed']}: {str(e)}")
        
        return results

    def _process_excel_bulk(self, file_obj, import_type, user, overwrite_existing, skip_errors):
        """Process Excel file for bulk import"""
        df = pd.read_excel(file_obj)
        results = {
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        for index, row in df.iterrows():
            results['processed'] += 1
            try:
                row_dict = row.to_dict()
                if import_type == 'skills':
                    self._import_skill_bulk(row_dict, user, overwrite_existing)
                elif import_type == 'education':
                    self._import_education_bulk(row_dict, user, overwrite_existing)
                elif import_type == 'experience':
                    self._import_experience_bulk(row_dict, user, overwrite_existing)
                elif import_type == 'goals':
                    self._import_goal_bulk(row_dict, user, overwrite_existing)
                elif import_type == 'profile':
                    self._import_profile_bulk(row_dict, user, overwrite_existing)
                
                results['successful'] += 1
            except Exception as e:
                results['failed'] += 1
                if not skip_errors:
                    raise e
                results['errors'].append(f"Row {index + 1}: {str(e)}")
        
        return results

    def _process_json_bulk(self, file_obj, import_type, user, overwrite_existing, skip_errors):
        """Process JSON file for bulk import"""
        json_data = json.load(file_obj)
        results = {
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        if isinstance(json_data, list):
            for item in json_data:
                results['processed'] += 1
                try:
                    if import_type == 'skills':
                        self._import_skill_bulk(item, user, overwrite_existing)
                    elif import_type == 'education':
                        self._import_education_bulk(item, user, overwrite_existing)
                    elif import_type == 'experience':
                        self._import_experience_bulk(item, user, overwrite_existing)
                    elif import_type == 'goals':
                        self._import_goal_bulk(item, user, overwrite_existing)
                    elif import_type == 'profile':
                        self._import_profile_bulk(item, user, overwrite_existing)
                    
                    results['successful'] += 1
                except Exception as e:
                    results['failed'] += 1
                    if not skip_errors:
                        raise e
                    results['errors'].append(f"Item {results['processed']}: {str(e)}")
        
        return results

    def _import_skill_bulk(self, data, user, overwrite_existing):
        """Import skill with bulk processing"""
        skill_name = data.get('skill_name', data.get('name'))
        category = data.get('category', 'technical')
        proficiency_level = int(data.get('proficiency_level', 1))
        years_of_experience = int(data.get('years_of_experience', 0))
        
        skill, created = Skill.objects.get_or_create(
            name=skill_name,
            defaults={'category': category}
        )
        
        if overwrite_existing:
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

    def _import_education_bulk(self, data, user, overwrite_existing):
        """Import education with bulk processing"""
        if overwrite_existing:
            # Check for existing education with same institution and degree
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

    def _import_experience_bulk(self, data, user, overwrite_existing):
        """Import work experience with bulk processing"""
        if overwrite_existing:
            # Check for existing experience with same company and position
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

    def _import_goal_bulk(self, data, user, overwrite_existing):
        """Import career goal with bulk processing"""
        if overwrite_existing:
            # Check for existing goal with same title
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

    def _import_profile_bulk(self, data, user, overwrite_existing):
        """Import user profile with bulk processing"""
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
        
        if not created and overwrite_existing:
            # Update existing profile
            for field, value in data.items():
                if hasattr(profile, field) and value:
                    setattr(profile, field, value)
            profile.save()
