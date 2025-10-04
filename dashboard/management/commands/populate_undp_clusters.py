from django.core.management.base import BaseCommand
from dashboard.models import Cluster


class Command(BaseCommand):
    help = 'Populate database with UNDP-specific clusters'

    def handle(self, *args, **options):
        # UNDP clusters based on their thematic areas
        undp_clusters = [
            {
                'name': 'Poverty Reduction',
                'code': 'PR',
                'description': 'Programmes and projects focused on reducing poverty and inequality, improving livelihoods, and promoting inclusive economic growth.',
                'is_active': True
            },
            {
                'name': 'Democratic Governance',
                'code': 'DG',
                'description': 'Initiatives to strengthen democratic institutions, promote human rights, and enhance public administration and justice systems.',
                'is_active': True
            },
            {
                'name': 'Crisis Prevention and Recovery',
                'code': 'CPR',
                'description': 'Programmes addressing conflict prevention, disaster risk reduction, and post-crisis recovery and reconstruction.',
                'is_active': True
            },
            {
                'name': 'Environment and Energy',
                'code': 'EE',
                'description': 'Projects promoting environmental sustainability, climate change adaptation and mitigation, and access to clean energy.',
                'is_active': True
            },
            {
                'name': 'HIV/AIDS',
                'code': 'HIV',
                'description': 'Programmes focused on HIV/AIDS prevention, treatment, care, and support, and addressing related health and social issues.',
                'is_active': True
            },
            {
                'name': 'Gender Equality',
                'code': 'GE',
                'description': 'Initiatives promoting gender equality, women\'s empowerment, and addressing gender-based violence and discrimination.',
                'is_active': True
            },
            {
                'name': 'Youth Development',
                'code': 'YD',
                'description': 'Programmes supporting youth employment, education, civic engagement, and leadership development.',
                'is_active': True
            },
            {
                'name': 'Private Sector Development',
                'code': 'PSD',
                'description': 'Initiatives to promote inclusive business, entrepreneurship, and private sector engagement in development.',
                'is_active': True
            },
            {
                'name': 'South-South Cooperation',
                'code': 'SSC',
                'description': 'Programmes facilitating knowledge sharing, technical cooperation, and partnerships between developing countries.',
                'is_active': True
            },
            {
                'name': 'Innovation and Technology',
                'code': 'IT',
                'description': 'Projects leveraging technology and innovation to accelerate development progress and digital inclusion.',
                'is_active': True
            }
        ]

        created_count = 0
        updated_count = 0

        for cluster_data in undp_clusters:
            cluster, created = Cluster.objects.get_or_create(
                code=cluster_data['code'],
                defaults={
                    'name': cluster_data['name'],
                    'description': cluster_data['description'],
                    'is_active': cluster_data['is_active']
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created cluster: {cluster.name}')
                )
            else:
                # Update existing cluster
                cluster.name = cluster_data['name']
                cluster.description = cluster_data['description']
                cluster.is_active = cluster_data['is_active']
                cluster.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated cluster: {cluster.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully processed {len(undp_clusters)} UNDP clusters:\n'
                f'- Created: {created_count}\n'
                f'- Updated: {updated_count}'
            )
        )
