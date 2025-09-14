# Generated migration to transition from separate class/section to unified ClassSection

from django.db import migrations, models
import django.db.models.deletion


def migrate_to_class_section(apps, schema_editor):
    """
    Migrate existing student_class and student_section data to class_section field
    """
    Student = apps.get_model('students', 'Student')
    ClassSection = apps.get_model('subjects', 'ClassSection')
    
    # Get all students with existing class/section data
    students = Student.objects.all()
    
    for student in students:
        if hasattr(student, 'student_class') and student.student_class:
            # Try to find matching ClassSection
            try:
                class_name = student.student_class.name if hasattr(student.student_class, 'name') else str(student.student_class)
                section_name = student.student_section.name if hasattr(student, 'student_section') and student.student_section and hasattr(student.student_section, 'name') else 'A'
                
                # Find or create matching ClassSection
                class_section, created = ClassSection.objects.get_or_create(
                    class_name=class_name,
                    section_name=section_name,
                    defaults={
                        'room_number': f"{class_name}-{section_name}"
                    }
                )
                
                # Update student's class_section
                student.class_section = class_section
                student.save()
                
                if created:
                    print(f"Created new ClassSection: {class_section}")
                    
            except Exception as e:
                print(f"Error migrating student {student.id}: {e}")
                continue


def reverse_migration(apps, schema_editor):
    """
    Reverse migration - not implemented as it would require recreating old models
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0003_remove_student_students_st_student_2ef7c4_idx_and_more'),
        ('subjects', '0006_alter_classsection_options'),
    ]

    operations = [
        migrations.RunPython(migrate_to_class_section, reverse_migration),
    ]