# Cleanup migration for promotion fields

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('promotion', '0003_migrate_data_to_class_section'),
        ('subjects', '0006_alter_classsection_options'),
    ]

    operations = [
        # Make class_section fields non-nullable
        migrations.AlterField(
            model_name='promotionrule',
            name='current_class_section',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='promotion_from', to='subjects.classsection'),
        ),
        migrations.AlterField(
            model_name='promotionrule',
            name='next_class_section',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='promotion_to', to='subjects.classsection'),
        ),
        # Remove legacy fields
        migrations.RemoveField(
            model_name='promotionrule',
            name='current_class',
        ),
        migrations.RemoveField(
            model_name='promotionrule',
            name='next_class',
        ),
        # Add unique constraint
        migrations.AlterUniqueTogether(
            name='promotionrule',
            unique_together={('current_class_section', 'next_class_section')},
        ),
    ]