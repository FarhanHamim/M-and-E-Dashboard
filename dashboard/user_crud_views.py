from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import Cluster, Project, Indicator, IndicatorValue, UserProfile
from .forms import ClusterForm, ProjectForm, IndicatorForm, IndicatorValueForm
from .decorators import project_user_required


# Cluster Management for Project Users
@project_user_required
def user_cluster_list(request):
    """List clusters created by current user only"""
    search_query = request.GET.get('search', '')
    clusters = Cluster.objects.filter(created_by=request.user)
    
    if search_query:
        clusters = clusters.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    paginator = Paginator(clusters, 20)
    page_number = request.GET.get('page')
    clusters = paginator.get_page(page_number)
    
    context = {
        'title': 'My Clusters',
        'clusters': clusters,
        'search_query': search_query,
    }
    
    return render(request, 'dashboard/user/cluster_list.html', context)


@project_user_required
def user_cluster_create(request):
    """Create new cluster - Project users can create clusters"""
    if request.method == 'POST':
        form = ClusterForm(request.POST)
        if form.is_valid():
            cluster = form.save(commit=False)
            cluster.created_by = request.user
            cluster.save()
            messages.success(request, f'Cluster "{cluster.name}" has been created successfully.')
            return redirect('dashboard:user_cluster_list')
    else:
        form = ClusterForm()
    
    context = {
        'title': 'Create New Cluster',
        'form': form,
    }
    
    return render(request, 'dashboard/user/cluster_form.html', context)


@project_user_required
def user_cluster_edit(request, cluster_id):
    """Edit existing cluster - Project users can only edit their own clusters"""
    cluster = get_object_or_404(Cluster, id=cluster_id, created_by=request.user)
    
    if request.method == 'POST':
        form = ClusterForm(request.POST, instance=cluster)
        if form.is_valid():
            cluster = form.save()
            messages.success(request, f'Cluster "{cluster.name}" has been updated successfully.')
            return redirect('dashboard:user_cluster_list')
    else:
        form = ClusterForm(instance=cluster)
    
    context = {
        'title': f'Edit Cluster: {cluster.name}',
        'form': form,
        'cluster': cluster,
    }
    
    return render(request, 'dashboard/user/cluster_form.html', context)


@project_user_required
def user_cluster_delete(request, cluster_id):
    """Delete cluster - Project users can only delete their own clusters"""
    cluster = get_object_or_404(Cluster, id=cluster_id, created_by=request.user)
    
    if request.method == 'POST':
        cluster_name = cluster.name
        cluster.delete()
        messages.success(request, f'Cluster "{cluster_name}" has been deleted.')
        return redirect('dashboard:user_cluster_list')
    
    context = {
        'title': 'Delete Cluster',
        'cluster': cluster,
    }
    
    return render(request, 'dashboard/user/cluster_confirm_delete.html', context)


# Project Management for Project Users
@project_user_required
def user_project_list(request):
    """List projects created by current user only"""
    search_query = request.GET.get('search', '')
    projects = Project.objects.filter(created_by=request.user).select_related('cluster')
    
    if search_query:
        projects = projects.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    paginator = Paginator(projects, 20)
    page_number = request.GET.get('page')
    projects = paginator.get_page(page_number)
    
    context = {
        'title': 'My Projects',
        'projects': projects,
        'search_query': search_query,
    }
    
    return render(request, 'dashboard/user/project_list.html', context)


@project_user_required
def user_project_create(request):
    """Create new project - Project users can create projects"""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            # Assign the current user to the project
            project.assigned_users.add(request.user)
            messages.success(request, f'Project "{project.name}" has been created successfully.')
            return redirect('dashboard:user_project_list')
    else:
        form = ProjectForm()
    
    context = {
        'title': 'Create New Project',
        'form': form,
    }
    
    return render(request, 'dashboard/user/project_form.html', context)


@project_user_required
def user_project_edit(request, project_id):
    """Edit existing project - Project users can only edit their own projects"""
    project = get_object_or_404(Project, id=project_id, created_by=request.user)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save()
            messages.success(request, f'Project "{project.name}" has been updated successfully.')
            return redirect('dashboard:user_project_list')
    else:
        form = ProjectForm(instance=project)
    
    context = {
        'title': f'Edit Project: {project.name}',
        'form': form,
        'project': project,
    }
    
    return render(request, 'dashboard/user/project_form.html', context)


@project_user_required
def user_project_delete(request, project_id):
    """Delete project - Project users can only delete their own projects"""
    project = get_object_or_404(Project, id=project_id, created_by=request.user)
    
    if request.method == 'POST':
        project_name = project.name
        project.delete()
        messages.success(request, f'Project "{project_name}" has been deleted.')
        return redirect('dashboard:user_project_list')
    
    context = {
        'title': 'Delete Project',
        'project': project,
    }
    
    return render(request, 'dashboard/user/project_confirm_delete.html', context)


# Indicator Management for Project Users
@project_user_required
def user_indicator_list(request):
    """List indicators created by current user only"""
    indicators = Indicator.objects.filter(created_by=request.user).order_by('name')
    
    paginator = Paginator(indicators, 20)
    page_number = request.GET.get('page')
    indicators = paginator.get_page(page_number)
    
    context = {
        'title': 'My Indicators',
        'indicators': indicators,
    }
    
    return render(request, 'dashboard/user/indicator_list.html', context)


@project_user_required
def user_indicator_create(request):
    """Create new indicator - Project users can create indicators"""
    if request.method == 'POST':
        form = IndicatorForm(request.POST)
        if form.is_valid():
            indicator = form.save(commit=False)
            indicator.created_by = request.user
            indicator.save()
            messages.success(request, f'Indicator "{indicator.name}" has been created successfully.')
            return redirect('dashboard:user_indicator_list')
    else:
        form = IndicatorForm()
    
    context = {
        'title': 'Create New Indicator',
        'form': form,
    }
    
    return render(request, 'dashboard/user/indicator_form.html', context)


@project_user_required
def user_indicator_edit(request, indicator_id):
    """Edit existing indicator - Project users can only edit their own indicators"""
    indicator = get_object_or_404(Indicator, id=indicator_id, created_by=request.user)
    
    if request.method == 'POST':
        form = IndicatorForm(request.POST, instance=indicator)
        if form.is_valid():
            indicator = form.save()
            messages.success(request, f'Indicator "{indicator.name}" has been updated successfully.')
            return redirect('dashboard:user_indicator_list')
    else:
        form = IndicatorForm(instance=indicator)
    
    context = {
        'title': f'Edit Indicator: {indicator.name}',
        'form': form,
        'indicator': indicator,
    }
    
    return render(request, 'dashboard/user/indicator_form.html', context)


@project_user_required
def user_indicator_delete(request, indicator_id):
    """Delete indicator - Project users can only delete their own indicators"""
    indicator = get_object_or_404(Indicator, id=indicator_id, created_by=request.user)
    
    if request.method == 'POST':
        indicator_name = indicator.name
        indicator.delete()
        messages.success(request, f'Indicator "{indicator_name}" has been deleted.')
        return redirect('dashboard:user_indicator_list')
    
    context = {
        'title': 'Delete Indicator',
        'indicator': indicator,
    }
    
    return render(request, 'dashboard/user/indicator_confirm_delete.html', context)


# AJAX endpoints for user management
@project_user_required
@require_POST
def toggle_user_object_status(request, model_name, object_id):
    """Toggle active status of any object - Project users can toggle status"""
    model_map = {
        'cluster': Cluster,
        'project': Project,
        'indicator': Indicator,
    }
    
    if model_name not in model_map:
        return JsonResponse({'error': 'Invalid model'}, status=400)
    
    model_class = model_map[model_name]
    obj = get_object_or_404(model_class, id=object_id)
    
    obj.is_active = not obj.is_active
    obj.save()
    
    return JsonResponse({
        'success': True,
        'is_active': obj.is_active,
        'message': f'{model_name.title()} status updated successfully'
    })


@project_user_required
def get_user_project_indicators(request, project_id):
    """Get indicators for a specific project (AJAX) - Project users can access this"""
    project = get_object_or_404(Project, id=project_id)
    indicators = project.indicators.filter(is_active=True)
    
    data = [{
        'id': indicator.id,
        'name': indicator.name,
        'code': indicator.code,
        'target_value': float(indicator.target_value),
        'measurement_unit': indicator.get_measurement_unit_display(),
    } for indicator in indicators]
    
    return JsonResponse({'indicators': data})
