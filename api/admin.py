from django.contrib import admin
from .models import User, Event, RSVP, Announcement, Feedback, Attendance, JoinRequest

admin.site.register(User)
admin.site.register(Event)
admin.site.register(RSVP)
admin.site.register(Announcement)
admin.site.register(Feedback)
admin.site.register(Attendance)
admin.site.register(JoinRequest)