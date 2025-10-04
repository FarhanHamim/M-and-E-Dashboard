# Generated manually to add created_by fields

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cluster',
            name='created_by',
            field=models.ForeignKey(
                null=True, 
                blank=True, 
                on_delete=django.db.models.deletion.SET_NULL, 
                to=settings.AUTH_USER_MODEL,
                related_name='created_clusters'
            ),
        ),
        migrations.AddField(
            model_name='project',
            name='created_by',
            field=models.ForeignKey(
                null=True, 
                blank=True, 
                on_delete=django.db.models.deletion.SET_NULL, 
                to=settings.AUTH_USER_MODEL,
                related_name='created_projects'
            ),
        ),
        migrations.AddField(
            model_name='indicator',
            name='created_by',
            field=models.ForeignKey(
                null=True, 
                blank=True, 
                on_delete=django.db.models.deletion.SET_NULL, 
                to=settings.AUTH_USER_MODEL,
                related_name='created_indicators'
            ),
        ),
    ]
