from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from django.db import transaction
from django.utils import timezone
import json

from .models import UserProfile, CareerPlan, PlanExecution, AIRequestLog
from .serializers import (
    UserProfileSerializer, CareerPlanSerializer, PlanExecutionSerializer,
    AIRequestLogSerializer, CareerPlanRequestSerializer, CareerPlanResponseSerializer,
    PlanGenerationResponseSerializer, ErrorResponseSerializer
)
from .services import AICareerPlanningService, ResponseStorageService

class CareerPlanningViewSet(viewsets.ModelViewSet):
    """ViewSet for AI-powered career planning"""
    queryset = CareerPlan.objects.all()
    serializer_class = CareerPlanSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ai_service = AICareerPlanningService()
        self.storage_service = ResponseStorageService()

    @action(detail=False, methods=['post'])
    def generate_plan(self, request):
        """Generate AI-powered career transformation plan"""
        try:
            # Validate request data
            request_serializer = CareerPlanRequestSerializer(data=request.data)
            if not request_serializer.is_valid():
                return Response({
                    'success': False,
                    'error': 'Invalid request data',
                    'details': request_serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            validated_data = request_serializer.validated_data
            user_profiles_data = validated_data['user_profiles']
            user_prompt = validated_data.get('user_prompt', '')
            
            # Process each user profile
            results = []
            
            for user_profile_data in user_profiles_data:
                try:
                    with transaction.atomic():
                        # Create or update user profile
                        user_profile, created = UserProfile.objects.get_or_create(
                            email=user_profile_data['email'],
                            defaults=user_profile_data
                        )
                        
                        if not created:
                            # Update existing profile
                            for field, value in user_profile_data.items():
                                setattr(user_profile, field, value)
                            user_profile.save()
                        
                        # Generate career plan using AI
                        ai_result = self.ai_service.generate_career_plan(user_profile, user_prompt)
                        
                        if ai_result['success']:
                            # Create career plan
                            plan_data = ai_result['plan_data']
                            career_plan = CareerPlan.objects.create(
                                user_profile=user_profile,
                                goal_id=plan_data['goal_id'],
                                plan_description=plan_data['plan_description'],
                                blockers=plan_data['blockers'],
                                milestones=plan_data['milestones'],
                                weekly_plans=plan_data['weekly_plans'],
                                user_prompt=user_prompt,
                                ai_model_used=self.ai_service.model,
                                tokens_used=ai_result['tokens_used'],
                                processing_time=ai_result['processing_time'],
                                status='draft'
                            )
                            
                            # Log successful request
                            self.ai_service.log_request(
                                user_profile=user_profile,
                                request_type='plan_generation',
                                input_data={'user_profile': user_profile_data, 'user_prompt': user_prompt},
                                output_data=plan_data,
                                ai_model=self.ai_service.model,
                                tokens_used=ai_result['tokens_used'],
                                processing_time=ai_result['processing_time'],
                                status='success'
                            )
                            
                            # Save response to local file
                            filename = self.storage_service.generate_filename(
                                'career_plan', user_profile.name
                            )
                            file_path = self.storage_service.save_response_to_file(
                                plan_data, filename, 'json'
                            )
                            
                            # Prepare response
                            plan_serializer = CareerPlanSerializer(career_plan)
                            response_data = {
                                'success': True,
                                'message': f'Career plan generated successfully for {user_profile.name}',
                                'career_plan': plan_serializer.data,
                                'file_path': file_path,
                                'processing_time': ai_result['processing_time'],
                                'tokens_used': ai_result['tokens_used']
                            }
                            
                            results.append(response_data)
                            
                        else:
                            # Log failed request
                            self.ai_service.log_request(
                                user_profile=user_profile,
                                request_type='plan_generation',
                                input_data={'user_profile': user_profile_data, 'user_prompt': user_prompt},
                                output_data={},
                                ai_model=self.ai_service.model,
                                tokens_used=ai_result['tokens_used'],
                                processing_time=ai_result['processing_time'],
                                status='error',
                                error_message=ai_result['error']
                            )
                            
                            # Save error response to local file
                            error_data = {
                                'success': False,
                                'error': ai_result['error'],
                                'user_profile': user_profile_data,
                                'user_prompt': user_prompt,
                                'timestamp': timezone.now().isoformat()
                            }
                            
                            filename = self.storage_service.generate_filename(
                                'career_plan_error', user_profile.name
                            )
                            file_path = self.storage_service.save_response_to_file(
                                error_data, filename, 'json'
                            )
                            
                            results.append({
                                'success': False,
                                'error': f'Failed to generate plan for {user_profile.name}',
                                'details': ai_result['error'],
                                'file_path': file_path
                            })
                
                except Exception as e:
                    results.append({
                        'success': False,
                        'error': f'Error processing {user_profile_data.get("name", "user")}',
                        'details': str(e)
                    })
            
            # Return results
            if len(results) == 1:
                result = results[0]
                if result['success']:
                    return Response(result, status=status.HTTP_201_CREATED)
                else:
                    return Response(result, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Multiple results
                return Response({
                    'success': True,
                    'message': f'Processed {len(results)} user profiles',
                    'results': results
                }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            error_data = {
                'success': False,
                'error': 'Failed to generate career plan',
                'details': str(e),
                'timestamp': timezone.now().isoformat()
            }
            
            # Save error to local file
            filename = f"career_plan_generation_error_{timezone.now().strftime('%Y%m%d_%H%M%S')}.json"
            file_path = self.storage_service.save_response_to_file(error_data, filename, 'json')
            error_data['file_path'] = file_path
            
            return Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def export_plans(self, request):
        """Export all career plans to local file"""
        try:
            plans = self.get_queryset()
            data = CareerPlanSerializer(plans, many=True).data
            
            filename = f"all_career_plans_{timezone.now().strftime('%Y%m%d_%H%M%S')}.json"
            file_path = self.storage_service.save_response_to_file(data, filename, 'json')
            
            return Response({
                'success': True,
                'message': f'Exported {len(data)} career plans',
                'file_path': file_path,
                'count': len(data)
            })
        
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Failed to export plans',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for user profiles"""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Create multiple user profiles from JSON data"""
        try:
            # Handle different input formats
            if 'file' in request.FILES:
                # File upload
                file_obj = request.FILES['file']
                if file_obj.name.endswith('.json'):
                    data = json.load(file_obj)
                else:
                    return Response({
                        'success': False,
                        'error': 'Only JSON files are supported'
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Direct JSON data
                data = request.data
            
            # Extract user profiles
            if 'user_profiles' in data:
                user_profiles_data = data['user_profiles']
            else:
                user_profiles_data = [data]  # Single profile
            
            created_profiles = []
            updated_profiles = []
            
            for profile_data in user_profiles_data:
                try:
                    user_profile, created = UserProfile.objects.get_or_create(
                        email=profile_data['email'],
                        defaults=profile_data
                    )
                    
                    if created:
                        created_profiles.append(user_profile)
                    else:
                        # Update existing profile
                        for field, value in profile_data.items():
                            setattr(user_profile, field, value)
                        user_profile.save()
                        updated_profiles.append(user_profile)
                
                except Exception as e:
                    return Response({
                        'success': False,
                        'error': f'Error processing profile: {str(e)}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Save response to local file
            response_data = {
                'success': True,
                'message': f'Processed {len(user_profiles_data)} user profiles',
                'created_count': len(created_profiles),
                'updated_count': len(updated_profiles),
                'profiles': UserProfileSerializer(created_profiles + updated_profiles, many=True).data
            }
            
            filename = f"user_profiles_bulk_{timezone.now().strftime('%Y%m%d_%H%M%S')}.json"
            file_path = self.storage_service.save_response_to_file(response_data, filename, 'json')
            response_data['file_path'] = file_path
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            error_data = {
                'success': False,
                'error': 'Failed to process user profiles',
                'details': str(e)
            }
            
            filename = f"user_profiles_error_{timezone.now().strftime('%Y%m%d_%H%M%S')}.json"
            file_path = self.storage_service.save_response_to_file(error_data, filename, 'json')
            error_data['file_path'] = file_path
            
            return Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PlanExecutionViewSet(viewsets.ModelViewSet):
    """ViewSet for plan execution tracking"""
    queryset = PlanExecution.objects.all()
    serializer_class = PlanExecutionSerializer

class AIRequestLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for AI request logs (read-only)"""
    queryset = AIRequestLog.objects.all()
    serializer_class = AIRequestLogSerializer
    
    @action(detail=False, methods=['get'])
    def export_logs(self, request):
        """Export AI request logs to local file"""
        try:
            logs = self.get_queryset()
            data = AIRequestLogSerializer(logs, many=True).data
            
            filename = f"ai_request_logs_{timezone.now().strftime('%Y%m%d_%H%M%S')}.json"
            storage_service = ResponseStorageService()
            file_path = storage_service.save_response_to_file(data, filename, 'json')
            
            return Response({
                'success': True,
                'message': f'Exported {len(data)} AI request logs',
                'file_path': file_path,
                'count': len(data)
            })
        
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Failed to export logs',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 