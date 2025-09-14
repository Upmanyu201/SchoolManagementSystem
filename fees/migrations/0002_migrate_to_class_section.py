# Generated migration for ClassSection integration

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fees', '0001_initial'),
        ('subjects', '0006_alter_classsection_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='feesgroup',
            name='related_class_section',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='subjects.classsection'),
        ),
        migrations.RunSQL(
            "UPDATE fees_feesgroup SET related_class_section_id = related_class_id WHERE related_class_id IS NOT NULL",
            reverse_sql="UPDATE fees_feesgroup SET related_class_id = related_class_section_id WHERE related_class_section_id IS NOT NULL"
        ),
        migrations.RemoveField(
            model_name='feesgroup',
            name='related_class',
        ),
    ]