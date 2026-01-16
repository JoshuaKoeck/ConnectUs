from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import CustomUserCreationForm


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
    
    return render(request, 'register.html', {'form': form})


def login_view(request):
    """Handle user login"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate using email only. Users must login with their email address.
        try:
            user_obj = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            user_obj = None

        if user_obj:
            user = authenticate(username=user_obj.username, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.email}!")
                return redirect('dashboard')
        messages.error(request, 'Invalid email or password.')
    
    return render(request, 'login.html')


@login_required(login_url='login')
def dashboard(request):
    """User dashboard view"""
    context = {
        'user': request.user,
        'sessions_completed': 1,
        'total_time': '45 min',
        'connections': 2,
    }
    return render(request, 'dashboard.html', context)



# Note: `login_view` handles rendering and POST; no separate `login` function needed.