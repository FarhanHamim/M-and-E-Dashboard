from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from dashboard.models import UserProfile, Cluster, Project, Indicator


class Command(BaseCommand):
    help = 'Create a test user to demonstrate data isolation'

    def handle(self, *args, **options):
        # Create test user
        test_user, created = User.objects.get_or_create(
            username='test_user',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        if created:
            test_user.set_password('password123')
            test_user.save()
            UserProfile.objects.create(user=test_user, role='project_user')
            self.stdout.write(
                self.style.SUCCESS('Created test user: test_user (password: password123)')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Test user already exists: test_user')
            )

        # Create some sample data for the test user
        if created:
            # Create a cluster for the test user
            test_cluster = Cluster.objects.create(
                name='Test Cluster',
                code='TEST',
                description='A test cluster for demonstration',
                created_by=test_user
            )
            
            # Create a project for the test user
            test_project = Project.objects.create(
                name='Test Project',
                code='TEST-PROJ',
                description='A test project for demonstration',
                cluster=test_cluster,
                created_by=test_user,
                start_date='2024-01-01',
                end_date='2024-12-31'
            )
            test_project.assigned_users.add(test_user)
            
            # Create an indicator for the test user
            test_indicator = Indicator.objects.create(
                name='Test Indicator',
                code='TEST-IND',
                description='A test indicator for demonstration',
                indicator_type='output',
                measurement_unit='number',
                target_value=100,
                created_by=test_user
            )
            test_indicator.projects.add(test_project)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Created sample data for test user:\n'
                    f'- Cluster: {test_cluster.name}\n'
                    f'- Project: {test_project.name}\n'
                    f'- Indicator: {test_indicator.name}'
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nTest user credentials:\n'
                f'Username: test_user\n'
                f'Password: password123\n'
                f'Role: Project User\n\n'
                f'This user can only see and edit their own data!'
            )
        )
