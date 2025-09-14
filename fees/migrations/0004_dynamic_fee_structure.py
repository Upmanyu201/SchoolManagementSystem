from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('fees', '0003_recreate_feestype'),
    ]

    operations = [
        # Add new fields to FeesType
        migrations.AddField(
            model_name='feestype',
            name='context_type',
            field=models.CharField(
                choices=[
                    ('monthly', 'Monthly'),
                    ('class_based', 'Class Based'),
                    ('stoppage_based', 'Stoppage Based'),
                    ('general', 'General'),
                    ('quarterly', 'Quarterly'),
                    ('yearly', 'Yearly'),
                    ('one_time', 'One Time'),
                ],
                default='general',
                max_length=50
            ),
        ),
        migrations.AddField(
            model_name='feestype',
            name='context_data',
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name='feestype',
            name='month_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='feestype',
            name='stoppage_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        
        # Remove old unique constraint
        migrations.AlterUniqueTogether(
            name='feestype',
            unique_together=set(),
        ),
        
        # Add new unique constraint
        migrations.AlterUniqueTogether(
            name='feestype',
            unique_together={('fee_group', 'amount_type', 'month_name', 'class_name', 'stoppage_name')},
        ),
    ]