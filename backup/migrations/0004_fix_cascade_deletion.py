# Generated migration to fix CASCADE deletion issues
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('backup', '0003_backupjob_backup_type_backupjob_created_by_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='backupjob',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.customuser'),
        ),
        migrations.AlterField(
            model_name='scheduledbackup',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.customuser'),
        ),
    ]