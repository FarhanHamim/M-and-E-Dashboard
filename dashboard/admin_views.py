from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import Cluster, Project, Indicator, IndicatorValue, UserProfile
from .forms import ClusterForm, ProjectForm, IndicatorForm, IndicatorValueForm
from .decorators import admin_required


@admin_required
def admin_dashboard(request):
    """Admin dashboard focused on data review and reporting only"""
    # Get basic statistics for submitted data only
    stats = {
        'total_submissions': IndicatorValue.objects.count(),
        'recent_submissions': IndicatorValue.objects.select_related(
            'indicator', 'project', 'reported_by'
        ).order_by('-created_at')[:10],
        'submissions_this_month': IndicatorValue.objects.filter(
            created_at__month=timezone.now().month,
            created_at__year=timezone.now().year
        ).count(),
        'submissions_this_year': IndicatorValue.objects.filter(
            created_at__year=timezone.now().year
        ).count(),
    }
    
    context = {
        'title': 'Admin Dashboard - Data Review',
        'stats': stats,
    }
    
    return render(request, 'dashboard/admin/admin_dashboard.html', context)


# Admin can only view data - no CRUD operations for clusters, projects, or indicators


# Data Review - Admin can only view submitted data
@admin_required
def submitted_data_list(request):
    """List all submitted data for review - READ ONLY"""
    search_query = request.GET.get('search', '')
    project_filter = request.GET.get('project', '')
    indicator_filter = request.GET.get('indicator', '')
    
    values = IndicatorValue.objects.select_related('indicator', 'project', 'reported_by').all()
    
    if search_query:
        values = values.filter(
            Q(indicator__name__icontains=search_query) |
            Q(project__name__icontains=search_query) |
            Q(reported_by__username__icontains=search_query)
        )
    
    if project_filter:
        values = values.filter(project_id=project_filter)
    
    if indicator_filter:
        values = values.filter(indicator_id=indicator_filter)
    
    paginator = Paginator(values.order_by('-created_at'), 20)
    page_number = request.GET.get('page')
    values = paginator.get_page(page_number)
    
    # Get filter options
    projects = Project.objects.filter(is_active=True)
    indicators = Indicator.objects.filter(is_active=True)
    
    context = {
        'title': 'Submitted Data Review',
        'values': values,
        'search_query': search_query,
        'project_filter': project_filter,
        'indicator_filter': indicator_filter,
        'projects': projects,
        'indicators': indicators,
    }
    
    return render(request, 'dashboard/admin/submitted_data_list.html', context)


@admin_required
def submitted_data_view(request, value_id):
    """View submitted data - READ ONLY for admins"""
    value = get_object_or_404(IndicatorValue, id=value_id)
    
    context = {
        'title': f'Data Submission: {value.indicator.name}',
        'value': value,
        'read_only': True,
    }
    
    return render(request, 'dashboard/admin/submitted_data_view.html', context)


# Reporting Tools - Admin can generate reports
@admin_required
def data_analytics(request):
    """Data analytics and insights for submitted data"""
    # Get analytics data
    analytics = {
        'submissions_by_month': IndicatorValue.objects.extra(
            select={'month': 'strftime("%Y-%m", created_at)'}
        ).values('month').annotate(count=Count('id')).order_by('month'),
        'submissions_by_project': IndicatorValue.objects.values('project__name').annotate(
            count=Count('id')
        ).order_by('-count')[:10],
        'submissions_by_indicator': IndicatorValue.objects.values('indicator__name').annotate(
            count=Count('id')
        ).order_by('-count')[:10],
        'recent_activity': IndicatorValue.objects.select_related(
            'indicator', 'project', 'reported_by'
        ).order_by('-created_at')[:20],
    }
    
    context = {
        'title': 'Data Analytics',
        'analytics': analytics,
    }
    
    return render(request, 'dashboard/admin/data_analytics.html', context)


# AJAX endpoints for data review
@admin_required
def get_submission_details(request, value_id):
    """Get detailed information about a specific submission (AJAX)"""
    value = get_object_or_404(IndicatorValue, id=value_id)
    
    data = {
        'id': value.id,
        'indicator_name': value.indicator.name,
        'indicator_code': value.indicator.code,
        'project_name': value.project.name,
        'reported_value': str(value.reported_value),
        'target_value': str(value.target_value) if value.target_value else None,
        'reported_by': value.reported_by.get_full_name() or value.reported_by.username,
        'reporting_period_start': value.reporting_period_start.isoformat(),
        'reporting_period_end': value.reporting_period_end.isoformat(),
        'created_at': value.created_at.isoformat(),
        'notes': value.notes or '',
    }
    
    return JsonResponse(data)
