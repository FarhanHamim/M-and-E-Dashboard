from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from dashboard.models import Cluster, Project, Indicator, IndicatorValue


class Command(BaseCommand):
    help = 'Create user groups and assign permissions for M&E Dashboard'

    def handle(self, *args, **options):
        self.stdout.write('Setting up user groups and permissions...')
        
        # Create user groups
        admin_group, created = Group.objects.get_or_create(name='Admins')
        project_user_group, created = Group.objects.get_or_create(name='ProjectUsers')
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created group: {"Admins" if admin_group else "ProjectUsers"}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Group already exists: {"Admins" if admin_group else "ProjectUsers"}')
            )
        
        # Get content types for our models
        cluster_ct = ContentType.objects.get_for_model(Cluster)
        project_ct = ContentType.objects.get_for_model(Project)
        indicator_ct = ContentType.objects.get_for_model(Indicator)
        indicator_value_ct = ContentType.objects.get_for_model(IndicatorValue)
        
        # Define permissions for each group
        
        # Admin group permissions - full access to all models
        admin_permissions = [
            # Cluster permissions
            Permission.objects.get(codename='add_cluster', content_type=cluster_ct),
            Permission.objects.get(codename='change_cluster', content_type=cluster_ct),
            Permission.objects.get(codename='delete_cluster', content_type=cluster_ct),
            Permission.objects.get(codename='view_cluster', content_type=cluster_ct),
            
            # Project permissions
            Permission.objects.get(codename='add_project', content_type=project_ct),
            Permission.objects.get(codename='change_project', content_type=project_ct),
            Permission.objects.get(codename='delete_project', content_type=project_ct),
            Permission.objects.get(codename='view_project', content_type=project_ct),
            
            # Indicator permissions
            Permission.objects.get(codename='add_indicator', content_type=indicator_ct),
            Permission.objects.get(codename='change_indicator', content_type=indicator_ct),
            Permission.objects.get(codename='delete_indicator', content_type=indicator_ct),
            Permission.objects.get(codename='view_indicator', content_type=indicator_ct),
            
            # Indicator Value permissions
            Permission.objects.get(codename='add_indicatorvalue', content_type=indicator_value_ct),
            Permission.objects.get(codename='change_indicatorvalue', content_type=indicator_value_ct),
            Permission.objects.get(codename='delete_indicatorvalue', content_type=indicator_value_ct),
            Permission.objects.get(codename='view_indicatorvalue', content_type=indicator_value_ct),
        ]
        
        # Project user group permissions - limited access
        project_user_permissions = [
            # Can only view clusters (for project assignment context)
            Permission.objects.get(codename='view_cluster', content_type=cluster_ct),
            
            # Can view assigned projects
            Permission.objects.get(codename='view_project', content_type=project_ct),
            
            # Can view indicators for their projects
            Permission.objects.get(codename='view_indicator', content_type=indicator_ct),
            
            # Can add and change indicator values (data entry)
            Permission.objects.get(codename='add_indicatorvalue', content_type=indicator_value_ct),
            Permission.objects.get(codename='change_indicatorvalue', content_type=indicator_value_ct),
            Permission.objects.get(codename='view_indicatorvalue', content_type=indicator_value_ct),
        ]
        
        # Assign permissions to groups
        admin_group.permissions.set(admin_permissions)
        project_user_group.permissions.set(project_user_permissions)
        
        self.stdout.write(
            self.style.SUCCESS(f'Assigned {len(admin_permissions)} permissions to Admins group')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Assigned {len(project_user_permissions)} permissions to ProjectUsers group')
        )
        
        self.stdout.write(
            self.style.SUCCESS('User groups and permissions setup completed successfully!')
        )
