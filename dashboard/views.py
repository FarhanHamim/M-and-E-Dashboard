from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.db.models import Count, Sum, Avg, Q
from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
import csv
import json

from .models import Cluster, Project, Indicator, IndicatorValue, UserProfile
from .decorators import admin_required, project_user_required, project_access_required, indicator_access_required
from .forms import ProjectUserIndicatorEntryForm


def home(request):
    """Home page view"""
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard_home')
    
    context = {
        'title': 'Welcome to M&E Dashboard',
        'description': 'Monitor and evaluate your projects with our comprehensive dashboard system.'
    }
    return render(request, 'dashboard/home.html', context)


@login_required
def dashboard_home(request):
    """Main dashboard view - accessible only to authenticated users"""
    user = request.user
    
    # Get user profile
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = UserProfile.objects.create(user=user, role='project_user')
    
    # Get basic statistics based on user role
    if profile.is_admin:
        # Admin dashboard - show data review focused stats
        total_projects = Project.objects.filter(is_active=True).count()
        total_indicators = Indicator.objects.filter(is_active=True).count()
        total_submissions = IndicatorValue.objects.count()
        
        # Get recent indicator values
        recent_values = IndicatorValue.objects.select_related(
            'indicator', 'project', 'reported_by'
        ).order_by('-created_at')[:10]
        
        context = {
            'title': 'Admin Dashboard - Data Review',
            'total_projects': total_projects,
            'total_indicators': total_indicators,
            'total_submissions': total_submissions,
            'recent_values': recent_values,
            'is_admin': True,
        }
        
    else:
        # Project user dashboard - show only their own projects and data
        user_projects = Project.objects.filter(
            created_by=user,
            is_active=True
        ).distinct()
        
        total_user_projects = user_projects.count()
        
        # Get indicators created by this user
        user_indicators = Indicator.objects.filter(
            created_by=user,
            is_active=True
        ).distinct()
        
        total_indicators = user_indicators.count()
        
        # Get recent submissions by this user
        recent_submissions = IndicatorValue.objects.filter(
            reported_by=user
        ).select_related('indicator', 'project').order_by('-created_at')[:10]
        
        context = {
            'title': 'My Dashboard',
            'total_projects': total_user_projects,
            'total_indicators': total_indicators,
            'assigned_projects': user_projects,
            'recent_submissions': recent_submissions,
            'is_admin': False,
        }
    
    return render(request, 'dashboard/dashboard_home.html', context)


@login_required
def project_list(request):
    """List projects (filtered by user role)"""
    user = request.user
    
    if user.profile.is_admin:
        # Admins can see all projects for review
        projects = Project.objects.filter(is_active=True).select_related('cluster')
    else:
        # Project users can only see their own projects
        projects = Project.objects.filter(
            created_by=user,
            is_active=True
        ).select_related('cluster')
    
    # Add search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        projects = projects.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Add pagination
    paginator = Paginator(projects, 20)
    page_number = request.GET.get('page')
    projects = paginator.get_page(page_number)
    
    context = {
        'title': 'My Projects' if not user.profile.is_admin else 'All Projects',
        'projects': projects,
        'search_query': search_query,
    }
    
    return render(request, 'dashboard/project_list.html', context)


@project_access_required
def project_detail(request, project_id):
    """Project detail view"""
    user = request.user
    
    if user.profile.is_admin:
        project = get_object_or_404(Project, id=project_id, is_active=True)
    else:
        project = get_object_or_404(
            Project,
            id=project_id,
            assigned_users=user,
            is_active=True
        )
    
    # Get indicators for this project
    indicators = project.indicators.filter(is_active=True)
    
    # Get recent indicator values
    recent_values = IndicatorValue.objects.filter(
        project=project
    ).select_related('indicator', 'reported_by').order_by('-created_at')[:20]
    
    context = {
        'title': f'Project: {project.name}',
        'project': project,
        'indicators': indicators,
        'recent_values': recent_values,
    }
    
    return render(request, 'dashboard/project_detail.html', context)


@project_user_required
def data_entry_home(request):
    """Data entry home for project users"""
    
    # Get user's own projects
    user_projects = Project.objects.filter(
        created_by=request.user,
        is_active=True
    ).select_related('cluster')
    
    # Calculate statistics
    total_indicators = 0
    for project in user_projects:
        total_indicators += project.indicators.filter(is_active=True).count()
    
    # Get recent submissions
    recent_submissions = IndicatorValue.objects.filter(
        reported_by=request.user
    ).select_related('indicator', 'project').order_by('-created_at')[:10]
    
    context = {
        'title': 'Data Entry',
        'assigned_projects': user_projects,
        'total_indicators': total_indicators,
        'recent_submissions': recent_submissions,
    }
    
    return render(request, 'dashboard/data_entry_home.html', context)


@project_access_required
def data_entry_form(request, project_id):
    """Data entry form for a specific project - PROJECT USERS ONLY"""
    if request.user.profile.is_admin:
        messages.warning(request, 'Admins cannot submit data. Only project users can enter data.')
        return redirect('dashboard:dashboard_home')
    
    # Verify user owns this project
    project = get_object_or_404(
        Project,
        id=project_id,
        created_by=request.user,
        is_active=True
    )
    
    # Get indicators for this project
    indicators = project.indicators.filter(is_active=True)
    
    context = {
        'title': f'Data Entry: {project.name}',
        'project': project,
        'indicators': indicators,
    }
    
    return render(request, 'dashboard/data_entry_form.html', context)


@login_required
def submit_data(request):
    """Handle data submission - PROJECT USERS ONLY"""
    # Block admins from submitting data
    if request.user.profile.is_admin:
        messages.error(request, 'Admins cannot submit data. Only project users can enter data.')
        return redirect('dashboard:dashboard_home')
    
    if request.method == 'POST':
        project_id = request.POST.get('project_id')
        
        if not project_id:
            messages.error(request, 'Project ID is required.')
            return redirect('dashboard:data_entry_home')
        
        try:
            project = get_object_or_404(Project, id=project_id, is_active=True)
            
            # Verify user owns this project (only for project users)
            if project.created_by != request.user:
                messages.error(request, 'You can only submit data for your own projects.')
                return redirect('dashboard:data_entry_home')
            
            # Process each indicator submission
            submitted_count = 0
            errors = []
            
            # Get all indicators for this project
            indicators = project.indicators.filter(is_active=True)
            
            for indicator in indicators:
                form_data = {
                    'indicator_id': indicator.id,
                    'reported_value': request.POST.get(f'indicator_{indicator.id}_reported_value'),
                    'target_value': request.POST.get(f'indicator_{indicator.id}_target_value') or indicator.target_value,
                    'reporting_period_start': request.POST.get(f'indicator_{indicator.id}_period_start'),
                    'reporting_period_end': request.POST.get(f'indicator_{indicator.id}_period_end'),
                    'notes': request.POST.get(f'indicator_{indicator.id}_notes', ''),
                }
                entry_form = ProjectUserIndicatorEntryForm(indicator, request.user, data=form_data)

                if not entry_form.is_valid():
                    # Collect all field errors per indicator
                    for field, field_errors in entry_form.errors.items():
                        for err in field_errors:
                            errors.append(f'{indicator.name}: {err}')
                    continue

                cleaned = entry_form.cleaned_data
                try:
                    indicator_value, created = IndicatorValue.objects.get_or_create(
                        indicator=indicator,
                        project=project,
                        reporting_period_start=cleaned['reporting_period_start'],
                        reporting_period_end=cleaned['reporting_period_end'],
                        defaults={
                            'reported_by': request.user,
                            'reported_value': cleaned['reported_value'],
                            'target_value': cleaned['target_value'] or indicator.target_value,
                            'notes': cleaned.get('notes', ''),
                        }
                    )

                    if not created:
                        indicator_value.reported_value = cleaned['reported_value']
                        indicator_value.target_value = cleaned['target_value'] or indicator.target_value
                        indicator_value.notes = cleaned.get('notes', '')
                        indicator_value.reported_by = request.user
                        indicator_value.save()

                    submitted_count += 1
                except Exception as e:
                    errors.append(f'Error saving data for indicator {indicator.name}: {str(e)}')
            
            # Show results
            if submitted_count > 0:
                messages.success(
                    request, 
                    f'Successfully submitted data for {submitted_count} indicator(s).'
                )
            
            if errors:
                for error in errors:
                    messages.error(request, error)
            
            if submitted_count == 0 and not errors:
                messages.warning(request, 'No data was submitted. Please check your input.')
            
            return redirect('dashboard:data_entry_home')
            
        except Project.DoesNotExist:
            messages.error(request, 'Project not found.')
            return redirect('dashboard:data_entry_home')
    
    return redirect('dashboard:data_entry_home')


@login_required
def reports_home(request):
    """Reports home page"""
    if not request.user.profile.is_admin:
        messages.warning(request, 'Only administrators can access reports.')
        return redirect('dashboard:dashboard_home')
    
    context = {
        'title': 'Reports',
        'clusters': Cluster.objects.filter(is_active=True),
        'projects': Project.objects.filter(is_active=True),
        'indicators': Indicator.objects.filter(is_active=True),
    }
    
    return render(request, 'dashboard/reports_home.html', context)


@login_required
def generate_report(request):
    """Generate reports based on filters"""
    if not request.user.profile.is_admin:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    project_id = request.GET.get('project_id')
    indicator_id = request.GET.get('indicator_id')
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    values = IndicatorValue.objects.select_related('project', 'indicator', 'reported_by').all()

    if project_id:
        values = values.filter(project_id=project_id)
    if indicator_id:
        values = values.filter(indicator_id=indicator_id)

    # Date filters (inclusive)
    try:
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            values = values.filter(reporting_period_start__gte=start_date)
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            values = values.filter(reporting_period_end__lte=end_date)
    except ValueError:
        return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

    values = values.order_by('-created_at')[:1000]

    html = render_to_string('dashboard/partials/report_rows.html', {
        'values': values,
    })

    return JsonResponse({'html': html, 'count': values.count()})


@login_required
def export_report(request, format):
    """Export reports in various formats"""
    if not request.user.profile.is_admin:
        return HttpResponse('Unauthorized', status=403)
    
    project_id = request.GET.get('project_id')
    indicator_id = request.GET.get('indicator_id')
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    values = IndicatorValue.objects.select_related('project', 'indicator', 'reported_by').all()

    if project_id:
        values = values.filter(project_id=project_id)
    if indicator_id:
        values = values.filter(indicator_id=indicator_id)

    try:
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            values = values.filter(reporting_period_start__gte=start_date)
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            values = values.filter(reporting_period_end__lte=end_date)
    except ValueError:
        return HttpResponse('Invalid date format. Use YYYY-MM-DD.', status=400)

    values = values.order_by('-created_at')

    if format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="report.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Project', 'Indicator', 'Reported Value', 'Target Value', 'Period Start', 'Period End', 'Reported By', 'Created'
        ])
        for v in values:
            writer.writerow([
                v.project.name,
                v.indicator.name,
                f"{v.reported_value}",
                f"{v.target_value if v.target_value is not None else ''}",
                v.reporting_period_start.isoformat(),
                v.reporting_period_end.isoformat(),
                v.reported_by.get_full_name() or v.reported_by.username,
                v.created_at.strftime('%Y-%m-%d %H:%M'),
            ])
        return response

    if format == 'pdf':
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            from reportlab.lib.units import cm
        except Exception:
            return HttpResponse('PDF generation library not installed.', status=500)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="report.pdf"'

        c = canvas.Canvas(response, pagesize=A4)
        width, height = A4
        x_margin = 2 * cm
        y = height - 2 * cm

        c.setFont('Helvetica-Bold', 14)
        c.drawString(x_margin, y, 'M&E Report')
        y -= 1 * cm

        c.setFont('Helvetica', 9)
        headers = ['Project', 'Indicator', 'Reported', 'Target', 'Start', 'End', 'By', 'Created']
        col_widths = [5*cm, 5*cm, 2*cm, 2*cm, 2.2*cm, 2.2*cm, 3*cm, 2.8*cm]
        x_positions = [x_margin]
        for w in col_widths[:-1]:
            x_positions.append(x_positions[-1] + w)

        # Header
        c.setFont('Helvetica-Bold', 8)
        for i, htext in enumerate(headers):
            c.drawString(x_positions[i], y, htext)
        y -= 0.5 * cm
        c.line(x_margin, y, width - x_margin, y)
        y -= 0.3 * cm

        c.setFont('Helvetica', 8)
        for v in values:
            row = [
                v.project.name,
                v.indicator.name,
                str(v.reported_value),
                '' if v.target_value is None else str(v.target_value),
                v.reporting_period_start.isoformat(),
                v.reporting_period_end.isoformat(),
                v.reported_by.get_full_name() or v.reported_by.username,
                v.created_at.strftime('%Y-%m-%d %H:%M'),
            ]
            row_height = 0.5 * cm
            if y < 2 * cm:
                c.showPage()
                y = height - 2 * cm
                c.setFont('Helvetica-Bold', 8)
                for i, htext in enumerate(headers):
                    c.drawString(x_positions[i], y, htext)
                y -= 0.5 * cm
                c.line(x_margin, y, width - x_margin, y)
                y -= 0.3 * cm
                c.setFont('Helvetica', 8)
            for i, cell in enumerate(row):
                c.drawString(x_positions[i], y, (cell[:40] + '…') if len(cell) > 45 else cell)
            y -= row_height

        c.showPage()
        c.save()
        return response

    return HttpResponse('Unsupported export format', status=400)


# Admin can only view data - no CRUD operations allowed


@login_required
def indicator_list(request):
    """List indicators"""
    if request.user.profile.is_admin:
        # Admins can see all indicators for review
        indicators = Indicator.objects.filter(is_active=True).order_by('name')
    else:
        # Project users can only see their own indicators
        indicators = Indicator.objects.filter(
            created_by=request.user,
            is_active=True
        ).order_by('name')
    
    # Add pagination
    paginator = Paginator(indicators, 20)
    page_number = request.GET.get('page')
    indicators = paginator.get_page(page_number)
    
    context = {
        'title': 'My Indicators' if not request.user.profile.is_admin else 'All Indicators',
        'indicators': indicators,
    }
    
    return render(request, 'dashboard/indicator_list.html', context)


@indicator_access_required
def indicator_detail(request, indicator_id):
    """Indicator detail view"""
    if request.user.profile.is_admin:
        indicator = get_object_or_404(Indicator, id=indicator_id, is_active=True)
    else:
        # Verify user has access to this indicator
        assigned_projects = Project.objects.filter(assigned_users=request.user)
        indicator = get_object_or_404(
            Indicator,
            id=indicator_id,
            projects__in=assigned_projects,
            is_active=True
        )
    
    # Get values for this indicator
    values = IndicatorValue.objects.filter(
        indicator=indicator
    ).select_related('project', 'reported_by').order_by('-created_at')
    
    context = {
        'title': f'Indicator: {indicator.name}',
        'indicator': indicator,
        'values': values,
    }
    
    return render(request, 'dashboard/indicator_detail.html', context)
