from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    # Authentication
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/profile/', views.UserProfileView.as_view(), name='profile'),

    # Events  (public must come before <int:pk>)
    path('events/public/', views.PublicEventListView.as_view(), name='public-events'),
    path('events/', views.EventListCreateView.as_view(), name='events'),
    path('events/<int:pk>/', views.EventDetailView.as_view(), name='event-detail'),
    path('events/<int:event_id>/rsvp/', views.rsvp_event, name='rsvp'),
    path('events/<int:event_id>/checkin/', views.check_in, name='checkin'),

    # Announcements
    path('announcements/', views.AnnouncementListCreateView.as_view(), name='announcements'),

    # Feedback
    path('feedback/', views.FeedbackListCreateView.as_view(), name='feedback'),

    # Attendance
    path('attendance/', views.AttendanceListView.as_view(), name='attendance'),

    # Join request (public)
    path('join/', views.JoinRequestView.as_view(), name='join'),

    # Dashboard
    path('dashboard/', views.dashboard_summary, name='dashboard'),
]
