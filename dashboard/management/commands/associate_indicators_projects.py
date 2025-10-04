from django.core.management.base import BaseCommand
from dashboard.models import Project, Indicator


class Command(BaseCommand):
    help = 'Associate indicators with appropriate projects'

    def handle(self, *args, **options):
        try:
            # Get projects
            slp_project = Project.objects.get(code='SLP-2024')
            dgi_project = Project.objects.get(code='DGI-2024')
            crp_project = Project.objects.get(code='CRP-2024')
            wee_project = Project.objects.get(code='WEE-2024')

            # Get indicators
            pr_001 = Indicator.objects.get(code='PR-001')
            pr_002 = Indicator.objects.get(code='PR-002')
            dg_001 = Indicator.objects.get(code='DG-001')
            dg_002 = Indicator.objects.get(code='DG-002')
            ee_001 = Indicator.objects.get(code='EE-001')
            ee_002 = Indicator.objects.get(code='EE-002')
            ge_001 = Indicator.objects.get(code='GE-001')
            ge_002 = Indicator.objects.get(code='GE-002')

            # Associate indicators with projects
            associations = [
                # Sustainable Livelihoods Programme
                (slp_project, [pr_001, pr_002]),
                # Digital Governance Initiative
                (dgi_project, [dg_001, dg_002]),
                # Climate Resilience Project
                (crp_project, [ee_001, ee_002]),
                # Women Economic Empowerment
                (wee_project, [ge_001, ge_002]),
            ]

            total_associations = 0
            for project, indicators in associations:
                for indicator in indicators:
                    project.indicators.add(indicator)
                    total_associations += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'Associated {indicator.name} with {project.name}')
                    )

            self.stdout.write(
                self.style.SUCCESS(
                    f'\nSuccessfully created {total_associations} project-indicator associations!'
                )
            )

        except (Project.DoesNotExist, Indicator.DoesNotExist) as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {e}. Please run populate_undp_sample_data first!')
            )
