from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from dashboard.models import Cluster, Project, Indicator, UserProfile


class Command(BaseCommand):
    help = 'Populate database with sample UNDP projects and indicators'

    def handle(self, *args, **options):
        # Get clusters
        try:
            poverty_cluster = Cluster.objects.get(code='PR')
            governance_cluster = Cluster.objects.get(code='DG')
            environment_cluster = Cluster.objects.get(code='EE')
            gender_cluster = Cluster.objects.get(code='GE')
        except Cluster.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Please run populate_undp_clusters first!')
            )
            return

        # Create a sample user if it doesn't exist
        user, created = User.objects.get_or_create(
            username='undp_user',
            defaults={
                'email': 'user@undp.org',
                'first_name': 'UNDP',
                'last_name': 'User'
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            UserProfile.objects.create(user=user, role='project_user')

        # Sample UNDP Projects
        sample_projects = [
            {
                'name': 'Sustainable Livelihoods Programme',
                'code': 'SLP-2024',
                'description': 'A comprehensive programme to improve livelihoods through skills training, microfinance, and market access for vulnerable communities.',
                'cluster': poverty_cluster,
                'start_date': '2024-01-01',
                'end_date': '2026-12-31',
                'status': 'active'
            },
            {
                'name': 'Digital Governance Initiative',
                'code': 'DGI-2024',
                'description': 'Modernizing public service delivery through digital platforms and improving citizen engagement in governance processes.',
                'cluster': governance_cluster,
                'start_date': '2024-03-01',
                'end_date': '2027-02-28',
                'status': 'active'
            },
            {
                'name': 'Climate Resilience Project',
                'code': 'CRP-2024',
                'description': 'Building community resilience to climate change through adaptation measures, early warning systems, and sustainable practices.',
                'cluster': environment_cluster,
                'start_date': '2024-02-01',
                'end_date': '2026-01-31',
                'status': 'active'
            },
            {
                'name': 'Women Economic Empowerment',
                'code': 'WEE-2024',
                'description': 'Promoting women\'s economic participation through entrepreneurship support, financial literacy, and leadership development.',
                'cluster': gender_cluster,
                'start_date': '2024-01-15',
                'end_date': '2025-12-31',
                'status': 'active'
            }
        ]

        # Sample UNDP Indicators
        sample_indicators = [
            # Poverty Reduction Indicators
            {
                'name': 'Number of households with improved income',
                'code': 'PR-001',
                'description': 'Total number of households that have increased their monthly income by at least 20% through programme interventions',
                'indicator_type': 'quantitative',
                'target_value': 1000,
                'measurement_unit': 'households',
                'is_active': True
            },
            {
                'name': 'Percentage of participants with new skills',
                'code': 'PR-002',
                'description': 'Proportion of programme participants who have acquired new vocational or business skills',
                'indicator_type': 'quantitative',
                'target_value': 85.0,
                'measurement_unit': 'percentage',
                'is_active': True
            },
            # Democratic Governance Indicators
            {
                'name': 'Citizen satisfaction with public services',
                'code': 'DG-001',
                'description': 'Level of satisfaction among citizens with digital public services (measured through surveys)',
                'indicator_type': 'quantitative',
                'target_value': 80.0,
                'measurement_unit': 'percentage',
                'is_active': True
            },
            {
                'name': 'Number of government services digitized',
                'code': 'DG-002',
                'description': 'Total number of government services that have been successfully digitized and made available online',
                'indicator_type': 'quantitative',
                'target_value': 25,
                'measurement_unit': 'services',
                'is_active': True
            },
            # Environment and Energy Indicators
            {
                'name': 'Hectares of land under climate-smart agriculture',
                'code': 'EE-001',
                'description': 'Total area of agricultural land where climate-smart practices have been implemented',
                'indicator_type': 'quantitative',
                'target_value': 500,
                'measurement_unit': 'hectares',
                'is_active': True
            },
            {
                'name': 'Number of early warning systems installed',
                'code': 'EE-002',
                'description': 'Total number of weather monitoring and early warning systems installed in vulnerable communities',
                'indicator_type': 'quantitative',
                'target_value': 15,
                'measurement_unit': 'systems',
                'is_active': True
            },
            # Gender Equality Indicators
            {
                'name': 'Number of women-led businesses created',
                'code': 'GE-001',
                'description': 'Total number of new businesses established and led by women through programme support',
                'indicator_type': 'quantitative',
                'target_value': 200,
                'measurement_unit': 'businesses',
                'is_active': True
            },
            {
                'name': 'Women participation in leadership roles',
                'code': 'GE-002',
                'description': 'Percentage of women in leadership positions within supported organizations and communities',
                'indicator_type': 'quantitative',
                'target_value': 40.0,
                'measurement_unit': 'percentage',
                'is_active': True
            }
        ]

        # Create projects
        created_projects = 0
        for project_data in sample_projects:
            project, created = Project.objects.get_or_create(
                code=project_data['code'],
                defaults={
                    'name': project_data['name'],
                    'description': project_data['description'],
                    'cluster': project_data['cluster'],
                    'start_date': project_data['start_date'],
                    'end_date': project_data['end_date'],
                    'status': project_data['status'],
                    'is_active': True
                }
            )
            if created:
                project.assigned_users.add(user)
                created_projects += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created project: {project.name}')
                )

        # Create indicators
        created_indicators = 0
        for indicator_data in sample_indicators:
            indicator, created = Indicator.objects.get_or_create(
                code=indicator_data['code'],
                defaults=indicator_data
            )
            if created:
                created_indicators += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created indicator: {indicator.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully created sample UNDP data:\n'
                f'- Projects: {created_projects}\n'
                f'- Indicators: {created_indicators}\n'
                f'- Sample user: undp_user (password: password123)'
            )
        )
