from django.conf import settings
from django.db import models
from django.utils import timezone


# Meeting tool choices
MEETING_TOOL_CHOICES = [
	("zoom", "Zoom"),
	("meet", "Google Meet"),
	("teams", "Microsoft Teams"),
	("other", "Other"),
]


class Session(models.Model):
	"""A scheduled session between a learner and a mentor.

	Use `completed` to mark finished sessions. Meeting URL/tool can be stored
	per-session; a user may also have a default meeting link on their profile.
	"""

	learner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="sessions", on_delete=models.CASCADE)
	mentor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="mentor_sessions", null=True, blank=True, on_delete=models.SET_NULL)
	title = models.CharField(max_length=200, blank=True)
	content_markdown = models.TextField(blank=True, help_text="Session content and tasks (Markdown allowed)")
	scheduled_at = models.DateTimeField(null=True, blank=True)
	completed = models.BooleanField(default=False)
	meeting_url = models.URLField(max_length=500, blank=True, null=True)
	meeting_tool = models.CharField(max_length=20, choices=MEETING_TOOL_CHOICES, blank=True, null=True)
	notes = models.TextField(blank=True)
	created_at = models.DateTimeField(default=timezone.now)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-scheduled_at", "-created_at"]

	def __str__(self):
		who = getattr(self.mentor, "username", "Unassigned")
		when = self.scheduled_at.isoformat() if self.scheduled_at else "unscheduled"
		return f"Session: {self.learner} with {who} at {when}"


class SessionTemplate(models.Model):
	"""Canonical session content shared by all learners. Editable only by superusers in admin."""

	title = models.CharField(max_length=200)
	content_markdown = models.TextField(blank=True, help_text="Session content and tasks (Markdown allowed)")
	order = models.PositiveIntegerField(default=0, help_text="Ordering for display")
	created_at = models.DateTimeField(default=timezone.now)

	class Meta:
		ordering = ["order", "-created_at"]

	def __str__(self):
		return self.title


class SessionCompletion(models.Model):
	"""Per-user completion record for a SessionTemplate."""

	user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="session_completions", on_delete=models.CASCADE)
	template = models.ForeignKey(SessionTemplate, related_name="completions", on_delete=models.CASCADE)
	completed = models.BooleanField(default=False)
	completed_at = models.DateTimeField(null=True, blank=True)
	notes = models.TextField(blank=True)

	class Meta:
		unique_together = ("user", "template")

	def __str__(self):
		return f"{self.user.username} - {self.template.title} ({'done' if self.completed else 'todo'})"


class Profile(models.Model):
	"""Extended user profile storing testing status and meeting defaults."""

	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
	intro_test_done = models.BooleanField(default=False)
	end_test_done = models.BooleanField(default=False)
	intro_test_score = models.IntegerField(null=True, blank=True)
	intro_test_taken_at = models.DateTimeField(null=True, blank=True)
	end_test_score = models.IntegerField(null=True, blank=True)
	end_test_taken_at = models.DateTimeField(null=True, blank=True)
	assigned_mentor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="mentees", null=True, blank=True, on_delete=models.SET_NULL)
	# next_session is a convenience pointer to a session template
	next_session = models.ForeignKey("SessionTemplate", related_name="as_next_for", null=True, blank=True, on_delete=models.SET_NULL)
	# default meeting link/tool for the user
	default_meeting_url = models.URLField(max_length=500, blank=True, null=True)
	default_meeting_tool = models.CharField(max_length=20, choices=MEETING_TOOL_CHOICES, blank=True, null=True)
	created_at = models.DateTimeField(default=timezone.now)
	updated_at = models.DateTimeField(auto_now=True)	
	# Is this user a mentor?
	is_mentor = models.BooleanField(default=False)


	def __str__(self):
		return f"Profile: {self.user.username}"

	def completed_sessions(self):
		"""Return queryset of completed sessions for this user."""
		return self.user.sessions.filter(completed=True)


class Message(models.Model):
	"""Simple one-to-one message between users (mentor/mentee).

	Messages are basic: sender → recipient, subject, body, created timestamp,
	and read flag.
	"""

	sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE)
	recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_messages', on_delete=models.CASCADE)
	body = models.TextField()
	created_at = models.DateTimeField(default=timezone.now)
	read = models.BooleanField(default=False)
	read_at = models.DateTimeField(null=True, blank=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f"Message from {self.sender.username} to {self.recipient.username} at {self.created_at.isoformat()}"


# Signal to create Profile when a new user is created.
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)
	else:
		# ensure profile exists and update timestamp
		Profile.objects.get_or_create(user=instance)
