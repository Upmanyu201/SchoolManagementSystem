# Generated migration for ClassSection integration

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fines', '0003_remove_feedepositfine_fee_deposit_and_more'),
        ('subjects', '0006_alter_classsection_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='fine',
            name='class_section',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='subjects.classsection'),
        ),
        migrations.RunSQL(
            "UPDATE fines_fine SET class_section_id = class_group_id WHERE class_group_id IS NOT NULL",
            reverse_sql="UPDATE fines_fine SET class_group_id = class_section_id WHERE class_section_id IS NOT NULL"
        ),
        migrations.RemoveField(
            model_name='fine',
            name='class_group',
        ),
        migrations.AlterModelOptions(
            name='fine',
            options={},
        ),
        migrations.AlterIndexTogether(
            name='fine',
            index_together={('class_section',), ('applied_date',), ('target_scope',)},
        ),
    ]