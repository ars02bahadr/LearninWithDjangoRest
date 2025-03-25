from django.urls import path
from api.views import (
    LoginView, RegisterView, 
    ProfileView, ProfileDetailView,
    UserTypeView, UserTypeDetailView,
    UserRoleView, UserRoleDetailView
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    
    # Profile URLs
    path('profiles/', ProfileView.as_view(), name='profile-list'),
    path('profiles/<int:pk>/', ProfileDetailView.as_view(), name='profile-detail'),
    
    # User Type URLs
    path('user-types/', UserTypeView.as_view(), name='user-type-list'),
    path('user-types/<int:pk>/', UserTypeDetailView.as_view(), name='user-type-detail'),
    
    # User Role URLs
    path('user-roles/', UserRoleView.as_view(), name='user-role-list'),
    path('user-roles/<int:pk>/', UserRoleDetailView.as_view(), name='user-role-detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)