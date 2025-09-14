# Generated migration to fix fees consistency issues

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fees', '0001_initial'),
    ]

    operations = [
        # First remove the unique_together constraint
        migrations.AlterUniqueTogether(
            name='feestype',
            unique_together=set(),
        ),
        # Remove redundant fields from FeesType
        migrations.RemoveField(
            model_name='feestype',
            name='group_type',
        ),
        migrations.RemoveField(
            model_name='feestype',
            name='fee_type',
        ),
        # Add choices to amount_type
        migrations.AlterField(
            model_name='feestype',
            name='amount_type',
            field=models.CharField(
                choices=[
                    ('Monthly', 'Monthly'),
                    ('Quarterly', 'Quarterly'),
                    ('Yearly', 'Yearly'),
                    ('One Time', 'One Time'),
                ],
                max_length=50
            ),
        ),
        # Add new unique_together constraint
        migrations.AlterUniqueTogether(
            name='feestype',
            unique_together={('fee_group', 'amount_type', 'class_name', 'related_stoppage')},
        ),
    ]