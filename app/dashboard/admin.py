from django.contrib import admin
from .models import Profile, SessionTemplate, SessionCompletion


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	list_display = ("user", "assigned_mentor", "intro_test_done", "end_test_done", "default_meeting_tool")
	search_fields = ("user__username", "user__email")



@admin.register(SessionTemplate)
class SessionTemplateAdmin(admin.ModelAdmin):
	list_display = ("title", "order", "created_at")
	ordering = ("order",)
	fields = ("title", "order", "content_markdown")

	def has_add_permission(self, request):
		return request.user.is_superuser

	def has_change_permission(self, request, obj=None):
		return request.user.is_superuser


@admin.register(SessionCompletion)
class SessionCompletionAdmin(admin.ModelAdmin):
	list_display = ("user", "template", "completed", "completed_at")
	search_fields = ("user__username", "template__title")
