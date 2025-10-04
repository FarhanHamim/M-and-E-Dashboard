from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse


def admin_required(view_func):
    """
    Decorator that requires the user to be an admin.
    Redirects to dashboard home if user is not an admin.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to access this page.')
            return redirect('login')
        
        try:
            profile = request.user.profile
        except AttributeError:
            messages.error(request, 'User profile not found. Please contact administrator.')
            return redirect('dashboard:dashboard_home')
        
        if not profile.is_admin:
            messages.warning(request, 'Access denied. Admin privileges required.')
            return redirect('dashboard:dashboard_home')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def project_user_required(view_func):
    """
    Decorator that requires the user to be a project user.
    Redirects to dashboard home if user is not a project user.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to access this page.')
            return redirect('login')
        
        try:
            profile = request.user.profile
        except AttributeError:
            messages.error(request, 'User profile not found. Please contact administrator.')
            return redirect('dashboard:dashboard_home')
        
        if not profile.is_project_user:
            messages.warning(request, 'Access denied. Project user privileges required.')
            return redirect('dashboard:dashboard_home')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def api_admin_required(view_func):
    """
    API decorator that requires the user to be an admin.
    Returns JSON error response if user is not an admin.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        try:
            profile = request.user.profile
        except AttributeError:
            return JsonResponse({'error': 'User profile not found'}, status=400)
        
        if not profile.is_admin:
            return JsonResponse({'error': 'Admin privileges required'}, status=403)
        
        return view_func(request, *args, **kwargs)
    return wrapper


def api_project_user_required(view_func):
    """
    API decorator that requires the user to be a project user.
    Returns JSON error response if user is not a project user.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        try:
            profile = request.user.profile
        except AttributeError:
            return JsonResponse({'error': 'User profile not found'}, status=400)
        
        if not profile.is_project_user:
            return JsonResponse({'error': 'Project user privileges required'}, status=403)
        
        return view_func(request, *args, **kwargs)
    return wrapper


def project_access_required(view_func):
    """
    Decorator that ensures the user has access to the specific project.
    The view function should accept project_id as a parameter.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to access this page.')
            return redirect('login')
        
        try:
            profile = request.user.profile
        except AttributeError:
            messages.error(request, 'User profile not found. Please contact administrator.')
            return redirect('dashboard:dashboard_home')
        
        # Admins have access to all projects
        if profile.is_admin:
            return view_func(request, *args, **kwargs)
        
        # Project users need to own the project
        project_id = kwargs.get('project_id')
        if project_id:
            from .models import Project
            try:
                project = Project.objects.get(id=project_id, is_active=True)
                if project.created_by != request.user:
                    messages.warning(request, 'Access denied. You can only access your own projects.')
                    return redirect('dashboard:dashboard_home')
            except Project.DoesNotExist:
                messages.error(request, 'Project not found.')
                return redirect('dashboard:dashboard_home')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def indicator_access_required(view_func):
    """
    Decorator that ensures the user has access to the specific indicator.
    The view function should accept indicator_id as a parameter.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to access this page.')
            return redirect('login')
        
        try:
            profile = request.user.profile
        except AttributeError:
            messages.error(request, 'User profile not found. Please contact administrator.')
            return redirect('dashboard:dashboard_home')
        
        # Admins have access to all indicators
        if profile.is_admin:
            return view_func(request, *args, **kwargs)
        
        # Project users need to own the indicator
        indicator_id = kwargs.get('indicator_id')
        if indicator_id:
            from .models import Indicator
            try:
                indicator = Indicator.objects.get(id=indicator_id, is_active=True)
                if indicator.created_by != request.user:
                    messages.warning(request, 'Access denied. You can only access your own indicators.')
                    return redirect('dashboard:dashboard_home')
            except Indicator.DoesNotExist:
                messages.error(request, 'Indicator not found.')
                return redirect('dashboard:dashboard_home')
        
        return view_func(request, *args, **kwargs)
    return wrapper
