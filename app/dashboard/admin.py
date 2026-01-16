from django.contrib import admin
from .models import Profile, Session


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	list_display = ("user", "assigned_mentor", "intro_test_done", "end_test_done", "default_meeting_tool")
	search_fields = ("user__username", "user__email")


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
	list_display = ("learner", "mentor", "scheduled_at", "completed")
	list_filter = ("completed", "meeting_tool")
	search_fields = ("learner__username", "mentor__username", "meeting_url")
