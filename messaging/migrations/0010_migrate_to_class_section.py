# Generated migration for ClassSection integration

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0009_remove_whatsappgroup_class_filter_and_more'),
        ('subjects', '0006_alter_classsection_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='messagelog',
            name='class_section_filter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='subjects.classsection'),
        ),
        migrations.RunSQL(
            """
            UPDATE messaging_messagelog 
            SET class_section_filter_id = (
                SELECT cs.id 
                FROM subjects_classsection cs 
                INNER JOIN core_academicclass ac ON cs.class_name = ac.name AND cs.section_name = ac.section
                WHERE ac.id = messaging_messagelog.class_filter_id
            )
            WHERE class_filter_id IS NOT NULL
            """,
            reverse_sql="-- No reverse migration needed"
        ),
        migrations.RemoveField(
            model_name='messagelog',
            name='class_filter',
        ),
    ]