from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from dashboard.models import Cluster, Project, Indicator


class Command(BaseCommand):
    help = 'Update existing records with created_by field'

    def handle(self, *args, **options):
        # Get or create a default user for existing data
        try:
            default_user = User.objects.get(username='undp_user')
        except User.DoesNotExist:
            default_user = User.objects.create_user(
                username='undp_user',
                email='user@undp.org',
                password='password123',
                first_name='UNDP',
                last_name='User'
            )
            self.stdout.write(
                self.style.SUCCESS('Created default user: undp_user')
            )

        # Update clusters
        clusters_updated = Cluster.objects.filter(created_by__isnull=True).update(created_by=default_user)
        self.stdout.write(
            self.style.SUCCESS(f'Updated {clusters_updated} clusters with created_by field')
        )

        # Update projects
        projects_updated = Project.objects.filter(created_by__isnull=True).update(created_by=default_user)
        self.stdout.write(
            self.style.SUCCESS(f'Updated {projects_updated} projects with created_by field')
        )

        # Update indicators
        indicators_updated = Indicator.objects.filter(created_by__isnull=True).update(created_by=default_user)
        self.stdout.write(
            self.style.SUCCESS(f'Updated {indicators_updated} indicators with created_by field')
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully updated existing data with created_by field!\n'
                f'All existing records are now assigned to: {default_user.username}'
            )
        )
