from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Event, RSVP, Announcement, Feedback, Attendance, JoinRequest

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class EventSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    user_rsvp = serializers.SerializerMethodField()
    user_attended = serializers.SerializerMethodField()
    going_count = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'date', 'location',
            'created_by', 'created_by_name', 'created_at',
            'user_rsvp', 'user_attended', 'going_count'
        ]
        read_only_fields = ['created_by', 'created_at']

    def get_created_by_name(self, obj):
        name = f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
        return name or obj.created_by.username

    def get_user_rsvp(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                return RSVP.objects.get(user=request.user, event=obj).status
            except RSVP.DoesNotExist:
                return None
        return None

    def get_user_attended(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Attendance.objects.filter(user=request.user, event=obj).exists()
        return False

    def get_going_count(self, obj):
        return obj.rsvps.filter(status='going').count()


class AnnouncementSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Announcement
        fields = ['id', 'title', 'content', 'created_by', 'created_by_name', 'created_at']
        read_only_fields = ['created_by', 'created_at']

    def get_created_by_name(self, obj):
        name = f"{obj.created_by.first_name} {obj.created_by.last_name}".strip()
        return name or obj.created_by.username


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'content', 'is_anonymous', 'submitted_at', 'submitted_by']
        read_only_fields = ['submitted_by', 'submitted_at']


class AttendanceSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    event_title = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = ['id', 'user', 'user_name', 'event', 'event_title', 'checked_in_at', 'is_late']
        read_only_fields = ['user', 'checked_in_at']

    def get_user_name(self, obj):
        name = f"{obj.user.first_name} {obj.user.last_name}".strip()
        return name or obj.user.username

    def get_event_title(self, obj):
        return obj.event.title


class JoinRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = JoinRequest
        fields = ['id', 'name', 'email', 'message', 'submitted_at']
        read_only_fields = ['submitted_at']