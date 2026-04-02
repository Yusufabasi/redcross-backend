from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Event, RSVP, Announcement, Feedback, Attendance, JoinRequest
from .serializers import (
    UserSerializer, RegisterSerializer, EventSerializer,
    AnnouncementSerializer, FeedbackSerializer, AttendanceSerializer,
    JoinRequestSerializer
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# ── Events ───────────────────────────────────────────────────────────────────

class PublicEventListView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        from django.utils import timezone
        return Event.objects.filter(date__gte=timezone.now()).order_by('date')[:6]


class EventListCreateView(generics.ListCreateAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Event.objects.all()

    def perform_create(self, serializer):
        if self.request.user.role != 'leader':
            raise permissions.PermissionDenied("Only leaders can create events.")
        serializer.save(created_by=self.request.user)


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Event.objects.all()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def rsvp_event(request, event_id):
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return Response({'error': 'Event not found'}, status=404)

    status_val = request.data.get('status')
    if status_val not in ['going', 'not_going']:
        return Response({'error': 'Invalid status'}, status=400)

    RSVP.objects.update_or_create(
        user=request.user, event=event,
        defaults={'status': status_val}
    )
    return Response({'message': f'RSVP updated to {status_val}', 'status': status_val})


# ── Announcements ─────────────────────────────────────────────────────────────

class AnnouncementListCreateView(generics.ListCreateAPIView):
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Announcement.objects.all()

    def perform_create(self, serializer):
        if self.request.user.role != 'leader':
            raise permissions.PermissionDenied("Only leaders can post announcements.")
        serializer.save(created_by=self.request.user)


# ── Feedback ──────────────────────────────────────────────────────────────────

class FeedbackListCreateView(generics.ListCreateAPIView):
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'leader':
            return Feedback.objects.all()
        return Feedback.objects.filter(submitted_by=self.request.user)

    def perform_create(self, serializer):
        is_anonymous = self.request.data.get('is_anonymous', False)
        if is_anonymous:
            serializer.save(submitted_by=None)
        else:
            serializer.save(submitted_by=self.request.user)


# ── Attendance ────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def check_in(request, event_id):
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return Response({'error': 'Event not found'}, status=404)

    if Attendance.objects.filter(user=request.user, event=event).exists():
        return Response({'error': 'Already checked in'}, status=400)

    from django.utils import timezone
    is_late = timezone.now() > event.date
    Attendance.objects.create(user=request.user, event=event, is_late=is_late)
    return Response({'message': 'Checked in successfully', 'is_late': is_late})


class AttendanceListView(generics.ListAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'leader':
            event_id = self.request.query_params.get('event_id')
            if event_id:
                return Attendance.objects.filter(event_id=event_id)
            return Attendance.objects.all()
        return Attendance.objects.filter(user=self.request.user)


# ── Join Request ──────────────────────────────────────────────────────────────

class JoinRequestView(generics.CreateAPIView):
    serializer_class = JoinRequestSerializer
    permission_classes = [permissions.AllowAny]


# ── Dashboard Summary ─────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def dashboard_summary(request):
    from django.utils import timezone
    upcoming_events = Event.objects.filter(date__gte=timezone.now()).count()
    total_announcements = Announcement.objects.count()
    my_attendance = Attendance.objects.filter(user=request.user).count()

    recent_announcements = AnnouncementSerializer(
        Announcement.objects.all()[:3], many=True
    ).data

    upcoming_events_list = EventSerializer(
        Event.objects.filter(date__gte=timezone.now()).order_by('date')[:3],
        many=True,
        context={'request': request}
    ).data

    return Response({
        'upcoming_events': upcoming_events,
        'total_announcements': total_announcements,
        'my_attendance': my_attendance,
        'recent_announcements': recent_announcements,
        'upcoming_events_list': upcoming_events_list,
    })