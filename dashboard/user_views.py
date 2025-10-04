from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from .models import UserProfile
from .forms import CustomUserCreationForm, UserProfileForm, UserEditForm, PasswordChangeForm
from .decorators import admin_required, project_user_required


@admin_required
def user_list(request):
    """List all users (admin only)"""
    search_query = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    
    users = User.objects.select_related('profile').all()
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    if role_filter:
        users = users.filter(profile__role=role_filter)
    
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    
    context = {
        'title': 'User Management',
        'users': users,
        'search_query': search_query,
        'role_filter': role_filter,
        'role_choices': UserProfile.ROLE_CHOICES,
    }
    
    return render(request, 'dashboard/admin/user_list.html', context)


@admin_required
def user_create(request):
    """Create new user (admin only)"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User "{user.username}" has been created successfully.')
            return redirect('dashboard:user_list')
    else:
        form = CustomUserCreationForm()
    
    context = {
        'title': 'Create New User',
        'form': form,
    }
    
    return render(request, 'dashboard/admin/user_form.html', context)


@admin_required
def user_edit(request, user_id):
    """Edit user (admin only)"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, instance=user.profile)
        
        if form.is_valid() and profile_form.is_valid():
            form.save()
            profile_form.save()
            messages.success(request, f'User "{user.username}" has been updated successfully.')
            return redirect('dashboard:user_list')
    else:
        form = UserEditForm(instance=user)
        profile_form = UserProfileForm(instance=user.profile)
    
    context = {
        'title': f'Edit User: {user.username}',
        'form': form,
        'profile_form': profile_form,
        'user': user,
    }
    
    return render(request, 'dashboard/admin/user_edit.html', context)


@login_required
def profile_view(request):
    """View user's own profile"""
    context = {
        'title': 'My Profile',
        'user': request.user,
    }
    
    return render(request, 'dashboard/profile.html', context)


@login_required
def profile_edit(request):
    """Edit user's own profile"""
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=request.user.profile)
        
        if form.is_valid() and profile_form.is_valid():
            form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('dashboard:profile_view')
    else:
        form = UserEditForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.profile)
    
    context = {
        'title': 'Edit Profile',
        'form': form,
        'profile_form': profile_form,
    }
    
    return render(request, 'dashboard/profile_edit.html', context)


@login_required
def password_change(request):
    """Change user's password"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your password has been changed successfully.')
            return redirect('dashboard:profile_view')
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'title': 'Change Password',
        'form': form,
    }
    
    return render(request, 'dashboard/password_change.html', context)


@admin_required
def user_toggle_status(request, user_id):
    """Toggle user active status (admin only)"""
    user = get_object_or_404(User, id=user_id)
    
    if user == request.user:
        messages.error(request, 'You cannot deactivate your own account.')
        return redirect('dashboard:user_list')
    
    user.is_active = not user.is_active
    user.save()
    
    status = 'activated' if user.is_active else 'deactivated'
    messages.success(request, f'User "{user.username}" has been {status}.')
    
    return redirect('dashboard:user_list')


@admin_required
def user_delete(request, user_id):
    """Delete user (admin only)"""
    user = get_object_or_404(User, id=user_id)
    
    if user == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('dashboard:user_list')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User "{username}" has been deleted.')
        return redirect('dashboard:user_list')
    
    context = {
        'title': 'Delete User',
        'user': user,
    }
    
    return render(request, 'dashboard/admin/user_confirm_delete.html', context)


@login_required
def user_stats(request):
    """User statistics (admin only)"""
    if not request.user.profile.is_admin:
        messages.warning(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard:dashboard_home')
    
    from .models import Project, Indicator, IndicatorValue
    
    # User statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    admin_users = UserProfile.objects.filter(role='admin').count()
    project_users = UserProfile.objects.filter(role='project_user').count()
    
    # Recent activity
    recent_users = User.objects.filter(is_active=True).order_by('-date_joined')[:10]
    
    # Project assignments
    user_project_counts = []
    for user in User.objects.filter(is_active=True):
        project_count = Project.objects.filter(assigned_users=user).count()
        if project_count > 0:
            user_project_counts.append({
                'user': user,
                'project_count': project_count
            })
    
    user_project_counts.sort(key=lambda x: x['project_count'], reverse=True)
    user_project_counts = user_project_counts[:10]
    
    context = {
        'title': 'User Statistics',
        'total_users': total_users,
        'active_users': active_users,
        'admin_users': admin_users,
        'project_users': project_users,
        'recent_users': recent_users,
        'user_project_counts': user_project_counts,
    }
    
    return render(request, 'dashboard/admin/user_stats.html', context)
