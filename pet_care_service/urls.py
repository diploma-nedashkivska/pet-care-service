"""
URL configuration for pet_care_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from pet_care_app import views
from rest_framework import routers
from rest_framework_simplejwt import views as jwt_views
from pet_care_app.views import (SignInView, SignUpView, PetListCreateView, PetDetailView,
                                UserProfileView, CalendarEventListCreateView, CalendarEventDetailView, )

# router = routers.DefaultRouter()
# router.register(r'users', views.UserView, 'user')
urlpatterns = [
    path('admin/', admin.site.urls),
    # path('api/', include(router.urls)),
    path('signin/', SignInView.as_view(), name="signin"),
    path('signup/', SignUpView.as_view(), name="signup"),
    # path('pets/', PetProfileView.as_view(), name='pets'),
    path('pets/', PetListCreateView.as_view(), name='pets-list'),
    path('pets/<int:pk>/', PetDetailView.as_view(), name='pets-detail'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('calendar/', CalendarEventListCreateView.as_view(), name='calendar-list'),
    path('calendar/<int:pk>/', CalendarEventDetailView.as_view(), name='calendar-detail'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name="token_refresh"),

]
