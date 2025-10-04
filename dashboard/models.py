from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Cluster(models.Model):
    """Represents a cluster or thematic area in the M&E system"""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    code = models.CharField(max_length=10, unique=True, help_text="Short code for the cluster")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_clusters')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Project(models.Model):
    """Represents a project within the M&E system"""
    PROJECT_STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('suspended', 'Suspended'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=300)
    description = models.TextField(blank=True, null=True)
    code = models.CharField(max_length=20, unique=True, help_text="Project code/identifier")
    cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE, related_name='projects')
    assigned_users = models.ManyToManyField(User, related_name='assigned_projects', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_projects')
    status = models.CharField(max_length=20, choices=PROJECT_STATUS_CHOICES, default='active')
    start_date = models.DateField()
    end_date = models.DateField()
    budget = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def is_overdue(self):
        """Check if project is overdue"""
        return timezone.now().date() > self.end_date and self.status == 'active'


class Indicator(models.Model):
    """Represents an indicator for measuring project progress"""
    INDICATOR_TYPE_CHOICES = [
        ('output', 'Output'),
        ('outcome', 'Outcome'),
        ('impact', 'Impact'),
        ('process', 'Process'),
    ]

    MEASUREMENT_UNIT_CHOICES = [
        ('number', 'Number'),
        ('percentage', 'Percentage'),
        ('currency', 'Currency'),
        ('text', 'Text'),
        ('date', 'Date'),
    ]

    name = models.CharField(max_length=300)
    description = models.TextField(blank=True, null=True)
    code = models.CharField(max_length=20, unique=True, help_text="Indicator code")
    indicator_type = models.CharField(max_length=20, choices=INDICATOR_TYPE_CHOICES, default='output')
    measurement_unit = models.CharField(max_length=20, choices=MEASUREMENT_UNIT_CHOICES, default='number')
    target_value = models.DecimalField(max_digits=15, decimal_places=2, help_text="Target value to achieve")
    projects = models.ManyToManyField(Project, related_name='indicators', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_indicators')
    frequency = models.CharField(
        max_length=20, 
        choices=[
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('semi-annual', 'Semi-Annual'),
            ('annual', 'Annual'),
        ],
        default='quarterly'
    )
    responsible_user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='responsible_indicators'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class IndicatorValue(models.Model):
    """Represents actual values reported for indicators"""
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE, related_name='values')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='indicator_values')
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_values')
    reported_value = models.DecimalField(max_digits=15, decimal_places=2)
    target_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    reporting_period_start = models.DateField()
    reporting_period_end = models.DateField()
    notes = models.TextField(blank=True, null=True, help_text="Additional notes or comments")
    attachment = models.FileField(upload_to='indicator_attachments/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['indicator', 'project', 'reporting_period_start', 'reporting_period_end']

    def __str__(self):
        return f"{self.indicator.name} - {self.reported_value} ({self.reporting_period_start} to {self.reporting_period_end})"

    @property
    def achievement_rate(self):
        """Calculate achievement rate as percentage of target"""
        if self.target_value and self.target_value > 0:
            return (self.reported_value / self.target_value) * 100
        return None

    @property
    def is_target_met(self):
        """Check if target is met or exceeded"""
        if self.target_value:
            return self.reported_value >= self.target_value
        return None


class UserProfile(models.Model):
    """Extended user profile for role management"""
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('project_user', 'Project User'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='project_user')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    organization = models.CharField(max_length=200, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_project_user(self):
        return self.role == 'project_user'