# Data migration to set default status for existing students
from django.db import migrations


def set_default_status(apps, schema_editor):
    """Set all existing students to ACTIVE status"""
    Student = apps.get_model('students', 'Student')
    Student.objects.filter(status__isnull=True).update(status='ACTIVE')
    Student.objects.filter(status='').update(status='ACTIVE')


def reverse_set_default_status(apps, schema_editor):
    """Reverse migration - set status to None"""
    Student = apps.get_model('students', 'Student')
    Student.objects.all().update(status=None)


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0002_add_student_status'),
    ]

    operations = [
        migrations.RunPython(set_default_status, reverse_set_default_status),
    ]