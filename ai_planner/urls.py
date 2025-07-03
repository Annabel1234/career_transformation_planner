from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'career-plans', views.CareerPlanningViewSet, basename='career-plan')
router.register(r'user-profiles', views.UserProfileViewSet, basename='user-profile')
router.register(r'plan-executions', views.PlanExecutionViewSet, basename='plan-execution')
router.register(r'ai-logs', views.AIRequestLogViewSet, basename='ai-log')

app_name = 'ai_planner'

urlpatterns = [
    path('api/', include(router.urls)),
] 