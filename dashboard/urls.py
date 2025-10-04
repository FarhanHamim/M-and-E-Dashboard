from django.urls import path
from . import views, user_views, auth_views, admin_views, user_crud_views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard views
    path('', views.dashboard_home, name='dashboard_home'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('indicators/', views.indicator_list, name='indicator_list'),
    path('indicators/<int:indicator_id>/', views.indicator_detail, name='indicator_detail'),
    
    # Data entry views (for project users)
    path('data-entry/', views.data_entry_home, name='data_entry_home'),
    path('data-entry/project/<int:project_id>/', views.data_entry_form, name='data_entry_form'),
    path('data-entry/submit/', views.submit_data, name='submit_data'),
    
    # User management views
    path('profile/', user_views.profile_view, name='profile_view'),
    path('profile/edit/', user_views.profile_edit, name='profile_edit'),
    path('password-change/', user_views.password_change, name='password_change'),
    
    # Admin Dashboard - Data Review Only
    path('admin/', admin_views.admin_dashboard, name='admin_dashboard'),
    
    # Admin data review views (read-only)
    path('admin/submitted-data/', admin_views.submitted_data_list, name='submitted_data_list'),
    path('admin/submitted-data/<int:value_id>/', admin_views.submitted_data_view, name='submitted_data_view'),
    path('admin/analytics/', admin_views.data_analytics, name='data_analytics'),
    
    # Admin AJAX endpoints for data review
    path('admin/api/submission/<int:value_id>/', admin_views.get_submission_details, name='get_submission_details'),
    
    # User CRUD operations (project users can manage everything)
    # Cluster management
    path('clusters/', user_crud_views.user_cluster_list, name='user_cluster_list'),
    path('clusters/create/', user_crud_views.user_cluster_create, name='user_cluster_create'),
    path('clusters/<int:cluster_id>/edit/', user_crud_views.user_cluster_edit, name='user_cluster_edit'),
    path('clusters/<int:cluster_id>/delete/', user_crud_views.user_cluster_delete, name='user_cluster_delete'),
    
    # Project management
    path('projects/manage/', user_crud_views.user_project_list, name='user_project_list'),
    path('projects/create/', user_crud_views.user_project_create, name='user_project_create'),
    path('projects/<int:project_id>/edit/', user_crud_views.user_project_edit, name='user_project_edit'),
    path('projects/<int:project_id>/delete/', user_crud_views.user_project_delete, name='user_project_delete'),
    
    # Indicator management
    path('indicators/manage/', user_crud_views.user_indicator_list, name='user_indicator_list'),
    path('indicators/create/', user_crud_views.user_indicator_create, name='user_indicator_create'),
    path('indicators/<int:indicator_id>/edit/', user_crud_views.user_indicator_edit, name='user_indicator_edit'),
    path('indicators/<int:indicator_id>/delete/', user_crud_views.user_indicator_delete, name='user_indicator_delete'),
    
    # User AJAX endpoints
    path('api/toggle-status/<str:model_name>/<int:object_id>/', user_crud_views.toggle_user_object_status, name='toggle_user_object_status'),
    path('api/project/<int:project_id>/indicators/', user_crud_views.get_user_project_indicators, name='get_user_project_indicators'),
    
    # User management (admin only)
    path('admin/users/', user_views.user_list, name='user_list'),
    path('admin/users/create/', user_views.user_create, name='user_create'),
    path('admin/users/<int:user_id>/edit/', user_views.user_edit, name='user_edit'),
    path('admin/users/<int:user_id>/toggle/', user_views.user_toggle_status, name='user_toggle_status'),
    path('admin/users/<int:user_id>/delete/', user_views.user_delete, name='user_delete'),
    path('admin/users/stats/', user_views.user_stats, name='user_stats'),
    
    # Authentication views
    path('auth/admin-register/', auth_views.AdminRegisterView.as_view(), name='admin_register'),
    path('auth/logout/', auth_views.logout_view, name='logout'),
    path('auth/switch-role/', auth_views.switch_role, name='switch_role'),
    path('auth/password-reset/', auth_views.password_reset_request, name='password_reset'),
    path('auth/password-reset-confirm/<str:uidb64>/<str:token>/', auth_views.password_reset_confirm, name='password_reset_confirm'),
    path('auth/account-security/', auth_views.account_security, name='account_security'),
    path('auth/login-history/', auth_views.login_history, name='login_history'),
    
    # API endpoints
    path('api/check-username/', auth_views.check_username_availability, name='check_username'),
    path('api/check-email/', auth_views.check_email_availability, name='check_email'),
    
    # Reporting views
    path('reports/', views.reports_home, name='reports_home'),
    path('reports/generate/', views.generate_report, name='generate_report'),
    path('reports/export/<str:format>/', views.export_report, name='export_report'),
]
