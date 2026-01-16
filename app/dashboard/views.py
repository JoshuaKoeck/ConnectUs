from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.utils import timezone
from datetime import datetime
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.utils.safestring import mark_safe
import markdown as md
from .models import SessionTemplate, SessionCompletion, Profile, MEETING_TOOL_CHOICES, Message
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponseForbidden


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def english_test(request):
    """Render and grade a 20-question English test (20 options each).

    For simplicity the questions and correct answers are defined here. On POST
    we compute score, save it to the user's profile, mark intro_test_done and
    redirect back to the dashboard.
    """
    # Sample questions: each question has 20 options; correct index stored in answers list
        # Curated question bank (20 questions) with difficulties.
        # Each question has a small set of options (4) and a difficulty tag.
    qb = [
            {"text": "Choose the correct form: 'There ___ many people at the party.'", "options": ["is", "are", "was", "be"], "answer": "2", "difficulty": "easy"},
            {"text": "Select the correct past tense: 'I ___ to the store yesterday.'", "options": ["go", "goed", "went", "gone"], "answer": "3", "difficulty": "easy"},
            {"text": "Which sentence is grammatically correct?", "options": ["She don't like tea.", "She doesn't likes tea.", "She doesn't like tea.", "She not like tea."], "answer": "3", "difficulty": "easy"},
            {"text": "Choose the best word: 'He is very ___ about football.'", "options": ["interesting", "interested", "interest", "interestful"], "answer": "2", "difficulty": "easy"},
            {"text": "Fill the blank: 'If I ___ time, I would help you.'", "options": ["have", "had", "will have", "would have"], "answer": "2", "difficulty": "medium"},
            {"text": "Choose the correct preposition: 'She is good ___ mathematics.'", "options": ["in", "at", "on", "for"], "answer": "2", "difficulty": "medium"},
            {"text": "Select the sentence with the correct article usage.", "options": ["I saw a eagle.", "I saw an eagle.", "I saw the eagle.", "I saw eagle."], "answer": "2", "difficulty": "medium"},
            {"text": "Which word best fits: 'Their house is ___ than mine.'", "options": ["big", "bigger", "more big", "biggest"], "answer": "2", "difficulty": "medium"},
            {"text": "Choose the correct phrasal verb: 'She decided to ___ smoking.'", "options": ["give up", "put up", "take up", "bring up"], "answer": "1", "difficulty": "medium"},
            {"text": "Identify the correct passive form: 'They will finish the project next week.' →", "options": ["The project will be finished next week.", "The project will finished next week.", "The project is finished next week.", "The project be finished next week."], "answer": "1", "difficulty": "medium"},
            {"text": "Choose the word closest in meaning to 'abundant'.", "options": ["scarce", "plentiful", "tiny", "rare"], "answer": "2", "difficulty": "medium"},
            {"text": "Which is the correct conditional: 'If he ___ earlier, he would have caught the train.'", "options": ["arrived", "had arrived", "has arrived", "would arrive"], "answer": "2", "difficulty": "hard"},
            {"text": "Choose the best connector: '___ she was tired, she finished her work.'", "options": ["Although", "Because", "So", "Therefore"], "answer": "1", "difficulty": "hard"},
            {"text": "Identify the error: 'Neither of the answers are correct.'", "options": ["Neither", "of", "are", "correct"], "answer": "3", "difficulty": "hard"},
            {"text": "Choose the correct tense: 'By this time next year, I ___ my degree.'", "options": ["will finish", "will have finished", "finished", "have finished"], "answer": "2", "difficulty": "hard"},
            {"text": "Pick the most formal synonym for 'get' in the sentence: 'We need to get permission.'", "options": ["obtain", "have", "fetch", "take"], "answer": "1", "difficulty": "hard"},
            {"text": "Choose the sentence with correct subject-verb agreement.", "options": ["Each of the students have a book.", "Each of the students has a book.", "Each of the student have a book.", "Each of the students are having a book."], "answer": "2", "difficulty": "medium"},
            {"text": "Which word best completes the collocation: '___ a decision'", "options": ["Make", "Do", "Take", "Have"], "answer": "1", "difficulty": "easy"},
            {"text": "Choose the correct reported speech: 'He said, \"I am tired.\"' →", "options": ["He said that he is tired.", "He said that he was tired.", "He said he will be tired.", "He said that he had been tired."], "answer": "2", "difficulty": "medium"},
            {"text": "Fill in the blank with the correct preposition: 'She is keen ___ learning languages.'", "options": ["in", "on", "for", "about"], "answer": "4", "difficulty": "medium"},
        ]

    questions = []
    answers = []
    for idx, item in enumerate(qb, start=1):
        questions.append({"id": idx, "text": item['text'], "options": item['options'], "difficulty": item['difficulty']})
        answers.append(str(item['answer']))

    if request.method == 'POST':
        score = 0
        total = len(questions)
        for idx, q in enumerate(questions, start=1):
            key = f"q{idx}"
            val = request.POST.get(key)
            if val and val == answers[idx-1]:
                score += 1

        # Save to profile
        try:
            profile = request.user.profile
        except Exception:
            profile = None
        if profile:
            profile.intro_test_score = score
            profile.intro_test_taken_at = timezone.now()
            profile.intro_test_done = True
            profile.save()

        messages.success(request, f'You scored {score}/{total} on the introductory English test.')
        return redirect('dashboard')

    context = {"questions": questions}
    return render(request, 'english_test.html', context)


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def end_test(request):
    """Advanced (B2-level) end-of-course test.

    Only available if the user has completed all SessionTemplate items.
    """
    total_templates = SessionTemplate.objects.count()
    completed_count = SessionCompletion.objects.filter(user=request.user, completed=True).count()
    if total_templates == 0 or completed_count < total_templates:
        messages.error(request, "You must complete all sessions before taking the end test.")
        return redirect('dashboard')

    # B2-style question bank (shortened for brevity; use 20 Qs)
    qb = [
        {"text": "Choose the best option: If I ___ earlier, I would have helped.", "options": ["had arrived", "arrived", "have arrived", "would arrive"], "answer": "1", "difficulty": "hard"},
        {"text": "Which sentence is most natural?", "options": ["Despite of the rain, we went out.", "Although the rain, we went out.", "Although it rained, we went out.", "Despite it was raining, we went out."], "answer": "3", "difficulty": "hard"},
        {"text": "Choose the best collocation: to ___ a decision.", "options": ["make", "have", "take", "do"], "answer": "1", "difficulty": "medium"},
        {"text": "Which is the correct passive: 'They will have finished the work.' →", "options": ["The work will be finished by them.", "The work will have been finished.", "The work will be finish.", "The work will have finished."], "answer": "2", "difficulty": "hard"},
        {"text": "Select the sentence without error.", "options": ["Neither of the books are interesting.", "Neither of the books is interesting.", "Neither the books are interesting.", "Neither of the books were interesting."], "answer": "2", "difficulty": "hard"},
        {"text": "Choose the correct modal: You ___ have told me earlier.", "options": ["should", "must", "might", "couldn't"], "answer": "1", "difficulty": "medium"},
        {"text": "Pick the best meaning of 'albeit' in context:", "options": ["although", "because", "so that", "unless"], "answer": "1", "difficulty": "hard"},
        {"text": "Choose the correct reduction: 'I have to' →", "options": ["I hafta", "I have to", "I'va", "I gotta"], "answer": "1", "difficulty": "medium"},
        {"text": "Which is more formal? 'Ask' vs 'request' → choose the most formal.", "options": ["ask", "request", "tell", "order"], "answer": "2", "difficulty": "medium"},
        {"text": "Choose the correct preposition: 'He is good ___ managing people.'", "options": ["in", "at", "on", "for"], "answer": "2", "difficulty": "medium"},
        {"text": "Identify the most appropriate link word: '___ he was tired, he continued.'", "options": ["Although", "Because", "So", "Therefore"], "answer": "1", "difficulty": "hard"},
        {"text": "Choose the right conditional: 'If she ___ known, she would have acted.'", "options": ["has", "had", "have", "was"], "answer": "2", "difficulty": "hard"},
        {"text": "Choose the correct collocation: 'to ___ a contribution'", "options": ["make", "do", "take", "have"], "answer": "1", "difficulty": "medium"},
        {"text": "Which sentence uses reported speech correctly?", "options": ["She said she will come.", "She said she would come.", "She said she comes.", "She said she'll come."], "answer": "2", "difficulty": "medium"},
        {"text": "Choose the most precise verb: 'to improve' — which is more intense?", "options": ["enhance", "get better", "fix", "alter"], "answer": "1", "difficulty": "medium"},
        {"text": "Which word completes: 'He has a good command ___ English.'", "options": ["on", "of", "in", "for"], "answer": "3", "difficulty": "medium"},
        {"text": "Choose the sentence with correct agreement.", "options": ["Each of them are ready.", "Each of them is ready.", "Each of them were ready.", "Each of them have been ready."], "answer": "2", "difficulty": "medium"},
        {"text": "Pick the best paraphrase for 'nevertheless'", "options": ["therefore", "however", "because", "as a result"], "answer": "2", "difficulty": "medium"},
        {"text": "Choose the correct tense: 'By next year I ___ my thesis.'", "options": ["will finish", "will have finished", "finished", "have finished"], "answer": "2", "difficulty": "hard"},
        {"text": "Select the best collocation: 'strongly ___'", "options": ["advise", "advocate", "recommend", "suggest"], "answer": "3", "difficulty": "medium"},
    ]

    questions = []
    answers = []
    for idx, item in enumerate(qb, start=1):
        questions.append({"id": idx, "text": item['text'], "options": item['options'], "difficulty": item['difficulty']})
        answers.append(str(item['answer']))

    if request.method == 'POST':
        score = 0
        total = len(questions)
        for idx, q in enumerate(questions, start=1):
            key = f"q{idx}"
            val = request.POST.get(key)
            if val and val == answers[idx-1]:
                score += 1

        # Save to profile
        try:
            profile = request.user.profile
        except Exception:
            profile = None
        if profile:
            profile.end_test_score = score
            profile.end_test_taken_at = timezone.now()
            profile.end_test_done = True
            profile.save()

        messages.success(request, f'You scored {score}/{total} on the end (B2) English test.')
        return redirect('dashboard')

    context = {"questions": questions}
    return render(request, 'end_test.html', context)


@login_required(login_url='login')
def session_detail(request, pk):
    """Render a single session: title, markdown content, scheduled info."""
    # session detail now displays a SessionTemplate
    template = get_object_or_404(SessionTemplate, pk=pk)

    # render markdown from template content
    raw = template.content_markdown or ''
    html = mark_safe(md.markdown(raw, extensions=['fenced_code', 'nl2br']))

    # Provide optional meeting info derived from the current user's profile
    meeting = None
    try:
        prof = request.user.profile
        if prof.next_meeting_at or prof.next_meeting_url or prof.next_meeting_tool:
            class M:
                pass
            meeting = M()
            meeting.scheduled_at = prof.next_meeting_at
            meeting.meeting_url = prof.next_meeting_url or prof.default_meeting_url
            meeting.meeting_tool = prof.next_meeting_tool or prof.default_meeting_tool
            meeting.mentor = prof.assigned_mentor
            meeting.get_meeting_tool_display = (dict(MEETING_TOOL_CHOICES).get(meeting.meeting_tool) if meeting.meeting_tool else '')
    except Exception:
        meeting = None

    context = {
        'session': template,
        'content_html': html,
        'meeting': meeting,
    }
    return render(request, 'session_detail.html', context)


def register(request):
    """Handle user registration"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Create the user
            user = form.save()
            auth_login(request, user)
            
            messages.success(request, f'Welcome {user.email}! Your account has been created.')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'register.html', {'form': form, "role": request.GET.get('role', 'learner')})



@login_required(login_url='login')
def mentor_dashboard(request):
    """Dashboard for mentors: list assigned students and allow assigning unassigned students."""
    try:
        if not request.user.profile.is_mentor:
            return HttpResponseForbidden('Access denied')
    except Exception:
        return HttpResponseForbidden('Access denied')

    # mentees assigned to this mentor
    from .models import Profile
    mentee_profiles = Profile.objects.filter(assigned_mentor=request.user)
    # session template totals
    total_templates = SessionTemplate.objects.count()
    mentees = []
    for prof in mentee_profiles:
        # Build a lightweight next_meeting object from profile fields (if present)
        nm = None
        if prof.next_meeting_at or prof.next_meeting_url or prof.next_meeting_tool:
            class NM:
                pass
            nm = NM()
            nm.scheduled_at = prof.next_meeting_at
            nm.meeting_url = prof.next_meeting_url or prof.default_meeting_url
            nm.meeting_tool = prof.next_meeting_tool or prof.default_meeting_tool
            nm.mentor = request.user
            # convenience display property
            nm.get_meeting_tool_display = (dict(MEETING_TOOL_CHOICES).get(nm.meeting_tool) if nm.meeting_tool else '')

        completed_count = SessionCompletion.objects.filter(user=prof.user, completed=True).count()
        mentees.append({
            'profile': prof,
            'next_meeting': nm,
            'completed_count': completed_count,
            'total_templates': total_templates,
        })

    # candidates: users who are not mentors and have no assigned_mentor
    candidates = Profile.objects.filter(assigned_mentor__isnull=True, is_mentor=False).exclude(user=request.user)

    context = {
        'mentees': mentees,
        'candidates': candidates,
        'unread_messages_count': Message.objects.filter(recipient=request.user, read=False).count()
    }
    return render(request, 'mentor_dashboard.html', context)


@login_required(login_url='login')
@require_http_methods(["POST"])
def mentor_assign_student(request, user_id):
    """Assign a student (Profile) to the current mentor."""
    try:
        if not request.user.profile.is_mentor:
            return HttpResponseForbidden('Access denied')
    except Exception:
        return HttpResponseForbidden('Access denied')

    profile = get_object_or_404(Profile, user__id=user_id)
    profile.assigned_mentor = request.user
    profile.save()
    messages.success(request, f"Assigned {profile.user.get_full_name() or profile.user.username} to you.")
    return redirect('mentor_dashboard')



@login_required(login_url='login')
def mentor_set_meeting(request, user_id):
    """Allow a mentor to set the next meeting for a mentee (date + link + tool)."""
    try:
        if not request.user.profile.is_mentor:
            return HttpResponseForbidden('Access denied')
    except Exception:
        return HttpResponseForbidden('Access denied')

    profile = get_object_or_404(Profile, user__id=user_id)
    if profile.assigned_mentor_id != request.user.id:
        return HttpResponseForbidden('Not your mentee')

    # Meeting info is stored on the mentee's Profile
    next_sess = None
    if profile.next_meeting_at or profile.next_meeting_url or profile.next_meeting_tool:
        class NM:
            pass
        next_sess = NM()
        next_sess.scheduled_at = profile.next_meeting_at
        next_sess.meeting_url = profile.next_meeting_url or profile.default_meeting_url
        next_sess.meeting_tool = profile.next_meeting_tool or profile.default_meeting_tool

    if request.method == 'POST':
        dt = request.POST.get('scheduled_at')
        meeting_url = request.POST.get('meeting_url')
        meeting_tool = request.POST.get('meeting_tool')

        scheduled_at = None
        if dt:
            try:
                parsed = datetime.fromisoformat(dt)
                scheduled_at = timezone.make_aware(parsed)
            except Exception:
                scheduled_at = None

        # Save meeting info directly onto the learner's profile
        profile.next_meeting_at = scheduled_at
        profile.next_meeting_url = meeting_url
        profile.next_meeting_tool = meeting_tool
        profile.save()

        messages.success(request, 'Next meeting updated.')
        return redirect('mentor_dashboard')

    context = {
        'mentee': profile.user,
        'next_sess': next_sess,
        'tools': MEETING_TOOL_CHOICES if 'MEETING_TOOL_CHOICES' in globals() else [],
    }
    return render(request, 'mentor_set_meeting.html', context)


@login_required(login_url='login')
def mentor_manage_sessions(request, user_id):
    try:
        if not request.user.profile.is_mentor:
            return HttpResponseForbidden('Access denied')
    except Exception:
        return HttpResponseForbidden('Access denied')

    profile = get_object_or_404(Profile, user__id=user_id)
    if profile.assigned_mentor_id != request.user.id:
        return HttpResponseForbidden('Not your mentee')

    templates = list(SessionTemplate.objects.all().order_by('order'))
    completions_qs = SessionCompletion.objects.filter(user=profile.user)
    completions = {c.template_id: c for c in completions_qs}
    completed_ids = {c.template_id for c in completions_qs if c.completed}

    if request.method == 'POST':
        completed_ids = set(int(i) for i in request.POST.getlist('completed'))
        for t in templates:
            comp = completions.get(t.id)
            if t.id in completed_ids:
                if not comp:
                    SessionCompletion.objects.create(user=profile.user, template=t, completed=True, completed_at=timezone.now())
                else:
                    comp.completed = True
                    comp.completed_at = comp.completed_at or timezone.now()
                    comp.save()
            else:
                if comp and comp.completed:
                    comp.completed = False
                    comp.completed_at = None
                    comp.save()

        messages.success(request, f"Updated sessions for {profile.user.get_full_name() or profile.user.username}.")
        return redirect('mentor_manage_sessions', user_id=user_id)

    context = {
        'mentee': profile.user,
        'templates': templates,
        'completions': completions,
        'completed_ids': completed_ids,
    }
    return render(request, 'mentor_manage_sessions.html', context)


@login_required(login_url='login')
@require_http_methods(["POST"])
def send_message(request):
    """Allow a learner to send a message to their assigned mentor."""
    try:
        profile = request.user.profile
    except Exception:
        messages.error(request, "Profile not found.")
        return redirect('dashboard')

    mentor = profile.assigned_mentor
    if not mentor:
        messages.error(request, "You don't have an assigned mentor to message.")
        return redirect('dashboard')

    body = request.POST.get('body', '').strip()
    if not body:
        messages.error(request, "Message body cannot be empty.")
        return redirect('dashboard')

    Message.objects.create(sender=request.user, recipient=mentor, body=body)
    messages.success(request, "Message sent to your mentor.")
    return redirect('dashboard')


@login_required(login_url='login')
def mentor_messages(request):
    """List conversations (mentees) for the current mentor."""
    try:
        if not request.user.profile.is_mentor:
            return HttpResponseForbidden('Access denied')
    except Exception:
        return HttpResponseForbidden('Access denied')

    # mentees assigned to this mentor
    mentee_profiles = Profile.objects.filter(assigned_mentor=request.user)
    conversations = []
    for prof in mentee_profiles:
        last_msg = Message.objects.filter(Q(sender=prof.user, recipient=request.user) | Q(sender=request.user, recipient=prof.user)).order_by('-created_at').first()
        unread = Message.objects.filter(sender=prof.user, recipient=request.user, read=False).count()
        conversations.append({
            'profile': prof,
            'last_message': last_msg,
            'unread': unread,
        })

    context = {'conversations': conversations,
    'unread_messages_count': Message.objects.filter(recipient=request.user, read=False).count()
               }
    return render(request, 'mentor_messages.html', context)


@login_required(login_url='login')
def mentor_message_thread(request, user_id):
    """View message thread between mentor and a specific mentee and allow replies."""
    try:
        if not request.user.profile.is_mentor:
            return HttpResponseForbidden('Access denied')
    except Exception:
        return HttpResponseForbidden('Access denied')

    prof = get_object_or_404(Profile, user__id=user_id)
    if prof.assigned_mentor_id != request.user.id:
        return HttpResponseForbidden('Not your mentee')

    # fetch messages in chronological order
    thread_qs = Message.objects.filter(Q(sender=request.user, recipient=prof.user) | Q(sender=prof.user, recipient=request.user)).order_by('created_at')

    # Mark incoming messages as read
    incoming_unread = thread_qs.filter(recipient=request.user, read=False)
    if incoming_unread.exists():
        incoming_unread.update(read=True, read_at=timezone.now())

    if request.method == 'POST':
        body = request.POST.get('body', '').strip()
        if body:
            Message.objects.create(sender=request.user, recipient=prof.user, body=body)
            messages.success(request, 'Message sent.')
            return redirect('mentor_message_thread', user_id=user_id)
        else:
            messages.error(request, 'Message body cannot be empty.')

    context = {
        'other_user': prof.user,
        'thread': thread_qs,
    
    'unread_messages_count': Message.objects.filter(recipient=request.user, read=False).count()
    }
    return render(request, 'mentor_message_thread.html', context)


@login_required(login_url='login')
def message_thread(request, user_id):
    """Generic message thread view for mentor/mentee pairs.

    Allows either side to view and reply when they are paired (assigned_mentor).
    """
    other = get_object_or_404(User, id=user_id)

    # Check relationship: either request.user has assigned_mentor == other, or other has assigned_mentor == request.user
    try:
        req_profile = request.user.profile
        other_profile = other.profile
    except Exception:
        return HttpResponseForbidden('Access denied')

    allowed = False
    if req_profile.assigned_mentor_id == other.id:
        allowed = True
    if other_profile.assigned_mentor_id == request.user.id:
        allowed = True

    if not allowed:
        return HttpResponseForbidden('Not connected')

    thread_qs = Message.objects.filter(Q(sender=request.user, recipient=other) | Q(sender=other, recipient=request.user)).order_by('created_at')

    # mark incoming unread messages as read
    incoming_unread = thread_qs.filter(recipient=request.user, read=False)
    if incoming_unread.exists():
        incoming_unread.update(read=True, read_at=timezone.now())

    if request.method == 'POST':
        body = request.POST.get('body', '').strip()
        if body:
            Message.objects.create(sender=request.user, recipient=other, body=body)
            messages.success(request, 'Message sent.')
            return redirect('message_thread', user_id=user_id)
        else:
            messages.error(request, 'Message body cannot be empty.')

    context = {
        'other_user': other,
        'thread': thread_qs,
        'unread_messages_count': Message.objects.filter(recipient=request.user, read=False).count()
    }
    return render(request, 'mentor_message_thread.html', context)


@login_required(login_url='login')
@require_http_methods(["POST"])
def mentor_unassign_student(request, user_id):
    try:
        if not request.user.profile.is_mentor:
            return HttpResponseForbidden('Access denied')
    except Exception:
        return HttpResponseForbidden('Access denied')

    profile = get_object_or_404(Profile, user__id=user_id)
    if profile.assigned_mentor_id == request.user.id:
        profile.assigned_mentor = None
        profile.save()
        messages.success(request, f"Unassigned {profile.user.get_full_name() or profile.user.username}.")
    return redirect('mentor_dashboard')

def login_view(request):
    """Handle user login via email"""
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")

        # Try to resolve email → username
        user_obj = User.objects.filter(email__iexact=email).first()

        if user_obj:
            user = authenticate(
                request,
                username=user_obj.username,
                password=password,
            )
        else:
            user = None

        if user:
            auth_login(request, user)
            messages.success(
                request,
                f"Welcome back, {user.first_name or user.email}!"
            )

            # Mentor redirect (safe, explicit)
            if hasattr(user, "profile") and user.profile.is_mentor:
                return redirect("mentor_dashboard")

            return redirect("dashboard")

        # Authentication failed
        return render(
            request,
            "login.html",
            {
                "form_error": "Invalid email or password.",
                "email": email,
            },
        )

    return render(request, "login.html")


@login_required(login_url='login')
def dashboard(request):
    """User dashboard view"""
    # If the current user is a mentor, redirect to the mentor dashboard.
    try:
        if hasattr(request.user, 'profile') and request.user.profile.is_mentor:
            return redirect('mentor_dashboard')
    except Exception:
        # If profile lookup fails, continue to render normal dashboard
        pass
    # Find the user's next scheduled Session (if any)
    # Build next_meeting from the user's profile
    next_meeting = None
    try:
        prof = request.user.profile
        if prof.next_meeting_at or prof.next_meeting_url or prof.next_meeting_tool:
            class NM:
                pass
            next_meeting = NM()
            next_meeting.scheduled_at = prof.next_meeting_at
            next_meeting.meeting_url = prof.next_meeting_url or prof.default_meeting_url
            next_meeting.meeting_tool = prof.next_meeting_tool or prof.default_meeting_tool
            next_meeting.mentor = prof.assigned_mentor
            next_meeting.get_meeting_tool_display = (dict(MEETING_TOOL_CHOICES).get(next_meeting.meeting_tool) if next_meeting.meeting_tool else '')
    except Exception:
        next_meeting = None

    # Pull session templates and per-user completion status
    templates = list(SessionTemplate.objects.all().order_by('order'))
    completions_qs = SessionCompletion.objects.filter(user=request.user)
    completions = {c.template_id: c for c in completions_qs}

    # Build combined list for template with user's completion (if any)
    session_items = []
    for t in templates:
        session_items.append({
            'template': t,
            'completion': completions.get(t.id)
        })
    # Filtering: allow toggling between todo/completed/all via ?filter=
    f = request.GET.get('filter', 'todo')
    if f == 'todo':
        session_items = [si for si in session_items if not (si['completion'] and si['completion'].completed)]
    elif f == 'completed':
        session_items = [si for si in session_items if si['completion'] and si['completion'].completed]

    total_templates = SessionTemplate.objects.count()
    completed_templates = SessionCompletion.objects.filter(user=request.user, completed=True).count()
    allow_end_test = (total_templates > 0 and completed_templates >= total_templates)

    context = {
        'user': request.user,
        'session_items': session_items,
        'sessions_completed': sum(1 for c in completions.values() if c.completed),
        'total_time': '45 min',
        'connections': 2,
        'next_meeting': next_meeting,
        'filter': f,
        'allow_end_test': allow_end_test,
        'unread_messages_count': Message.objects.filter(recipient=request.user, read=False).count(),
    }
    return render(request, 'dashboard.html', context)


@login_required(login_url='login')
@require_http_methods(["POST"])
def reset_progress(request):
    """Reset the current user's progress: clear test results and session completions."""
    user = request.user
    try:
        profile = user.profile
    except Exception:
        profile = None

    # Clear profile test flags and scores
    if profile:
        profile.intro_test_done = False
        profile.intro_test_score = None
        profile.intro_test_taken_at = None
        profile.end_test_done = False
        profile.end_test_score = None
        profile.end_test_taken_at = None
        profile.save()

    # Reset session completions and clear any scheduled meeting info on the profile
    SessionCompletion.objects.filter(user=user).update(completed=False, completed_at=None)
    if profile:
        profile.next_meeting_at = None
        profile.next_meeting_url = None
        profile.next_meeting_tool = None
        profile.next_meeting_notes = ''
        profile.save()

    messages.success(request, "Your progress has been reset.")
    return redirect('dashboard')



@login_required(login_url='login')
@require_http_methods(["POST"])
def complete_session_template(request, pk):
    """Mark a SessionTemplate as completed (or undo).

    Expects optional POST param `action=undo` to mark as not completed.
    """
    template = get_object_or_404(SessionTemplate, pk=pk)
    completion, created = SessionCompletion.objects.get_or_create(user=request.user, template=template)

    action = request.POST.get('action')
    if action == 'undo':
        completion.completed = False
        completion.completed_at = None
    else:
        completion.completed = True
        completion.completed_at = timezone.now()

    completion.save()
    messages.success(request, f"Updated status for '{template.title}'.")
    # Redirect back to dashboard, preserving filter if provided
    return redirect(request.POST.get('next', 'dashboard'))



# Note: `login_view` handles rendering and POST; no separate `login` function needed.