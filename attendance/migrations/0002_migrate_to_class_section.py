# Generated migration for ClassSection integration

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0001_initial'),
        ('subjects', '0006_alter_classsection_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='class_section',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='subjects.classsection'),
        ),
        migrations.RunSQL(
            """
            UPDATE attendance_attendance 
            SET class_section_id = (
                SELECT cs.id 
                FROM subjects_classsection cs 
                INNER JOIN core_academicclass ac ON cs.class_name = ac.name AND cs.section_name = ac.section
                WHERE ac.id = attendance_attendance.student_class_id
            )
            WHERE student_class_id IS NOT NULL
            """,
            reverse_sql="-- No reverse migration needed"
        ),
        migrations.RemoveField(
            model_name='attendance',
            name='student_class',
        ),
        migrations.RemoveField(
            model_name='attendance',
            name='student_section',
        ),
    ]