from django.contrib import admin
from django.urls import path, include
from pet_care_app import views
from rest_framework import routers
from rest_framework_simplejwt import views as jwt_views
from pet_care_app.views import (SignInView, SignUpView, PetListCreateView, PetDetailView,
                                UserProfileView, CalendarEventListCreateView, CalendarEventDetailView,
                                JournalEntryListCreateView, JournalEntryDetailView, SitePartnerListView,
                                ForumPostView, ForumCommentView, ForumLikeView, PartnerWatchlistListView,
                                PartnerWatchlistDetailView, CookieTokenRefreshView, LogoutView)

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
    path('journal/', JournalEntryListCreateView.as_view(), name='journal-list'),
    path('journal/<int:pk>/', JournalEntryDetailView.as_view(), name='journal-detail'),
    path('partners/', SitePartnerListView.as_view(), name='partners-list'),
    path('partners/watchlist/', PartnerWatchlistListView.as_view(), name='watchlist-list'),
    path('partners/watchlist/<int:partner_id>/', PartnerWatchlistDetailView.as_view(), name='watchlist-detail'),
    path('forum/', ForumPostView.as_view(), name='forum-post-list'),
    path('forum/<int:post_id>/', ForumPostView.as_view(), name='forum-detail'),  # <-- сюди
    path('forum/<int:post_id>/comments/', ForumCommentView.as_view(), name='forum-comments'),
    path('forum/<int:post_id>/like/', ForumLikeView.as_view(), name='forum-like'),
    path('api/token/refresh/', CookieTokenRefreshView.as_view(), name="token_refresh"),
    path('api/logout/', LogoutView.as_view(), name='logout'),

]
