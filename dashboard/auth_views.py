from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.views.generic import View

from .forms import CustomUserCreationForm
from .models import UserProfile


class LoginView(View):
    """Custom login view with role-based redirects"""
    
    @method_decorator(never_cache)
    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard:dashboard_home')
        return render(request, 'registration/login.html')
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    
                    # Get user profile for role-based redirect
                    try:
                        profile = user.profile
                        if profile.is_admin:
                            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                            return redirect('dashboard:dashboard_home')
                        else:
                            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                            return redirect('dashboard:dashboard_home')
                    except UserProfile.DoesNotExist:
                        messages.warning(request, 'Your profile is being set up. Please contact an administrator.')
                        return redirect('dashboard:dashboard_home')
                else:
                    messages.error(request, 'Your account is inactive. Please contact an administrator.')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please fill in all fields.')
        
        return render(request, 'registration/login.html')


class RegisterView(View):
    """Public user registration view"""
    
    @method_decorator(never_cache)
    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard:dashboard_home')
        
        form = CustomUserCreationForm()
        return render(request, 'registration/register.html', {'form': form})
    
    def post(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard:dashboard_home')
        
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Account created successfully! Welcome, {user.get_full_name() or user.username}!')
            
            # Auto-login the user after successful registration
            user = authenticate(request, username=user.username, password=form.cleaned_data['password1'])
            if user is not None:
                login(request, user)
                return redirect('dashboard:dashboard_home')
        
        return render(request, 'registration/register.html', {'form': form})


class AdminRegisterView(View):
    """Admin-only user registration view for creating new users"""
    
    def get(self, request):
        if not request.user.is_authenticated or not request.user.profile.is_admin:
            messages.warning(request, 'Only administrators can register new users.')
            return redirect('dashboard:dashboard_home')
        
        form = CustomUserCreationForm()
        context = {
            'title': 'Register New User',
            'form': form,
        }
        return render(request, 'dashboard/admin/user_form.html', context)
    
    def post(self, request):
        if not request.user.is_authenticated or not request.user.profile.is_admin:
            messages.warning(request, 'Only administrators can register new users.')
            return redirect('dashboard:dashboard_home')
        
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User "{user.username}" has been registered successfully.')
            return redirect('dashboard:user_list')
        
        context = {
            'title': 'Register New User',
            'form': form,
        }
        return render(request, 'dashboard/admin/user_form.html', context)


@login_required
def logout_view(request):
    """Custom logout view"""
    from django.contrib.auth import logout
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def switch_role(request):
    """Switch user role (for testing purposes)"""
    if not request.user.is_superuser:
        messages.error(request, 'Access denied.')
        return redirect('dashboard:dashboard_home')
    
    try:
        profile = request.user.profile
        if profile.role == 'admin':
            profile.role = 'project_user'
        else:
            profile.role = 'admin'
        profile.save()
        
        messages.info(request, f'Role switched to {profile.get_role_display()}.')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found.')
    
    return redirect('dashboard:dashboard_home')


def password_reset_request(request):
    """Password reset request view"""
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            try:
                from django.contrib.auth.models import User
                user = User.objects.get(email=email)
                # Here you would typically send an email with reset link
                messages.info(request, 'Password reset instructions have been sent to your email.')
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, 'No user found with that email address.')
        else:
            messages.error(request, 'Please enter your email address.')
    
    return render(request, 'registration/password_reset.html')


def password_reset_confirm(request, uidb64, token):
    """Password reset confirmation view"""
    # This would typically handle the password reset confirmation
    messages.info(request, 'Password reset confirmation not implemented yet.')
    return redirect('login')


@login_required
def account_security(request):
    """Account security settings"""
    context = {
        'title': 'Account Security',
        'user': request.user,
    }
    
    return render(request, 'dashboard/account_security.html', context)


@login_required
def login_history(request):
    """User login history (if implemented)"""
    context = {
        'title': 'Login History',
        'user': request.user,
    }
    
    return render(request, 'dashboard/login_history.html', context)


def check_username_availability(request):
    """AJAX endpoint to check username availability"""
    from django.http import JsonResponse
    
    username = request.GET.get('username')
    if username:
        from django.contrib.auth.models import User
        exists = User.objects.filter(username=username).exists()
        return JsonResponse({'available': not exists})
    
    return JsonResponse({'error': 'Username required'}, status=400)


def check_email_availability(request):
    """AJAX endpoint to check email availability"""
    from django.http import JsonResponse
    
    email = request.GET.get('email')
    if email:
        from django.contrib.auth.models import User
        exists = User.objects.filter(email=email).exists()
        return JsonResponse({'available': not exists})
    
    return JsonResponse({'error': 'Email required'}, status=400)
