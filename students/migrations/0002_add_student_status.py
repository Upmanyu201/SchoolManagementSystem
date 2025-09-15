# Generated migration for student status management
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='status',
            field=models.CharField(
                choices=[
                    ('ACTIVE', 'Active'),
                    ('SUSPENDED', 'Suspended'),
                    ('ARCHIVED', 'Archived'),
                    ('GRADUATED', 'Graduated')
                ],
                default='ACTIVE',
                max_length=20,
                verbose_name='Status'
            ),
        ),
        migrations.AddField(
            model_name='student',
            name='status_reason',
            field=models.TextField(blank=True, null=True, verbose_name='Status Change Reason'),
        ),
        migrations.AddField(
            model_name='student',
            name='status_changed_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Status Changed Date'),
        ),
        migrations.AddField(
            model_name='student',
            name='status_changed_by',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Status Changed By'),
        ),
        migrations.AddIndex(
            model_name='student',
            index=models.Index(fields=['status'], name='students_st_status_idx'),
        ),
        migrations.AddIndex(
            model_name='student',
            index=models.Index(fields=['status', 'class_section'], name='students_st_status_class_idx'),
        ),
    ]