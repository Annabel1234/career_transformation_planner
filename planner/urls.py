from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'profiles', views.UserProfileViewSet, basename='profile')
router.register(r'skills', views.SkillViewSet, basename='skill')
router.register(r'user-skills', views.UserSkillViewSet, basename='user-skill')
router.register(r'education', views.EducationViewSet, basename='education')
router.register(r'experience', views.WorkExperienceViewSet, basename='experience')
router.register(r'goals', views.CareerGoalViewSet, basename='goal')
router.register(r'imports', views.DataImportViewSet, basename='import')
router.register(r'upload', views.UploadViewSet, basename='upload')

app_name = 'planner'

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/auth/', include('rest_framework.urls')),
] 