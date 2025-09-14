# Final migration to remove unused module fields

from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_cleanup_orphaned_records'),
    ]

    operations = [
        # Remove unused module fields
        migrations.RemoveField(
            model_name='usermodulepermission',
            name='classes_view',
        ),
        migrations.RemoveField(
            model_name='usermodulepermission',
            name='classes_edit',
        ),
        migrations.RemoveField(
            model_name='usermodulepermission',
            name='exams_view',
        ),
        migrations.RemoveField(
            model_name='usermodulepermission',
            name='exams_edit',
        ),
        migrations.RemoveField(
            model_name='usermodulepermission',
            name='results_view',
        ),
        migrations.RemoveField(
            model_name='usermodulepermission',
            name='results_edit',
        ),
    ]