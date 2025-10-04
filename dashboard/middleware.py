from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from .models import UserProfile


class UserProfileMiddleware(MiddlewareMixin):
    """
    Middleware to automatically create user profiles and handle role-based redirects.
    """
    
    def process_request(self, request):
        # Only process authenticated users
        if not request.user.is_authenticated:
            return None
        
        # Skip for admin URLs to avoid infinite redirects
        if request.path.startswith('/admin/'):
            return None
        
        # Create profile if it doesn't exist
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            # Create a default project_user profile
            profile = UserProfile.objects.create(
                user=request.user,
                role='project_user'
            )
            messages.info(
                request, 
                'Your profile has been created. Please contact an administrator to update your role if needed.'
            )
        
        # Store profile in request for easy access
        request.user_profile = profile
        
        return None


class RoleBasedRedirectMiddleware(MiddlewareMixin):
    """
    Middleware to handle role-based redirects after login.
    """
    
    def process_request(self, request):
        # Only process authenticated users
        if not request.user.is_authenticated:
            return None
        
        # Skip for admin URLs, API URLs, and static files
        if (request.path.startswith('/admin/') or 
            request.path.startswith('/api/') or 
            request.path.startswith('/static/') or
            request.path.startswith('/media/')):
            return None
        
        # Skip if user doesn't have a profile yet
        if not hasattr(request.user, 'profile'):
            return None
        
        # Handle role-based redirects
        profile = request.user.profile
        
        # If user is on home page and authenticated, redirect to appropriate dashboard
        if request.path == '/' and profile.is_admin:
            return redirect('dashboard:dashboard_home')
        
        # Prevent project users from accessing admin-only URLs
        admin_only_paths = [
            '/dashboard/reports/',
            '/dashboard/admin/',
        ]
        
        if profile.is_project_user:
            for path in admin_only_paths:
                if request.path.startswith(path):
                    messages.warning(request, 'Access denied. Admin privileges required.')
                    return redirect('dashboard:dashboard_home')
        
        return None


class ProjectAccessMiddleware(MiddlewareMixin):
    """
    Middleware to check project access for project users.
    """
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Only process authenticated users
        if not request.user.is_authenticated:
            return None
        
        # Skip for admin users
        try:
            if request.user.profile.is_admin:
                return None
        except UserProfile.DoesNotExist:
            return None
        
        # Check project access for project-specific URLs
        if 'project_id' in view_kwargs:
            from .models import Project
            project_id = view_kwargs['project_id']
            
            try:
                project = Project.objects.get(id=project_id, is_active=True)
                if project.created_by != request.user:
                    messages.warning(request, 'Access denied. You can only access your own projects.')
                    return redirect('dashboard:dashboard_home')
            except Project.DoesNotExist:
                messages.error(request, 'Project not found.')
                return redirect('dashboard:dashboard_home')
        
        # Check indicator access for indicator-specific URLs
        if 'indicator_id' in view_kwargs:
            from .models import Indicator
            indicator_id = view_kwargs['indicator_id']
            
            try:
                indicator = Indicator.objects.get(id=indicator_id, is_active=True)
                if indicator.created_by != request.user:
                    messages.warning(request, 'Access denied. You can only access your own indicators.')
                    return redirect('dashboard:dashboard_home')
            except Indicator.DoesNotExist:
                messages.error(request, 'Indicator not found.')
                return redirect('dashboard:dashboard_home')
        
        return None
