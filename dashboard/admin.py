from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import Cluster, Project, Indicator, IndicatorValue, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__role')

    def get_role(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.get_role_display()
        return 'No Role'
    get_role.short_description = 'Role'


@admin.register(Cluster)
class ClusterAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code', 'description')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'cluster', 'status', 'start_date', 'end_date', 'is_overdue', 'is_active')
    list_filter = ('status', 'cluster', 'is_active', 'start_date', 'end_date')
    search_fields = ('name', 'code', 'description')
    filter_horizontal = ('assigned_users',)
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at', 'is_overdue')

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description', 'cluster')
        }),
        ('Project Details', {
            'fields': ('status', 'start_date', 'end_date', 'budget')
        }),
        ('Assignment', {
            'fields': ('assigned_users',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def is_overdue(self, obj):
        if obj.is_overdue:
            return format_html('<span style="color: red;">Overdue</span>')
        return 'On Track'
    is_overdue.short_description = 'Status'


@admin.register(Indicator)
class IndicatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'indicator_type', 'measurement_unit', 'target_value', 'frequency', 'responsible_user', 'is_active')
    list_filter = ('indicator_type', 'measurement_unit', 'frequency', 'is_active')
    search_fields = ('name', 'code', 'description')
    filter_horizontal = ('projects',)
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description')
        }),
        ('Indicator Details', {
            'fields': ('indicator_type', 'measurement_unit', 'target_value', 'frequency')
        }),
        ('Assignment', {
            'fields': ('projects', 'responsible_user')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(IndicatorValue)
class IndicatorValueAdmin(admin.ModelAdmin):
    list_display = ('indicator', 'project', 'reported_value', 'target_value', 'achievement_rate', 'reported_by', 'reporting_period_start', 'created_at')
    list_filter = ('indicator__indicator_type', 'project__cluster', 'reporting_period_start', 'created_at')
    search_fields = ('indicator__name', 'project__name', 'reported_by__username')
    readonly_fields = ('created_at', 'updated_at', 'achievement_rate', 'is_target_met')
    date_hierarchy = 'reporting_period_start'

    fieldsets = (
        ('Basic Information', {
            'fields': ('indicator', 'project', 'reported_by')
        }),
        ('Values', {
            'fields': ('reported_value', 'target_value')
        }),
        ('Reporting Period', {
            'fields': ('reporting_period_start', 'reporting_period_end')
        }),
        ('Additional Information', {
            'fields': ('notes', 'attachment')
        }),
        ('Calculated Fields', {
            'fields': ('achievement_rate', 'is_target_met'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def achievement_rate(self, obj):
        if obj.achievement_rate:
            color = 'green' if obj.achievement_rate >= 100 else 'orange' if obj.achievement_rate >= 80 else 'red'
            return format_html('<span style="color: {};">{:.1f}%</span>', color, obj.achievement_rate)
        return 'N/A'
    achievement_rate.short_description = 'Achievement Rate'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'organization', 'position', 'created_at')
    list_filter = ('role', 'organization', 'created_at')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'organization')
    ordering = ('user__username',)
    readonly_fields = ('created_at', 'updated_at')


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)