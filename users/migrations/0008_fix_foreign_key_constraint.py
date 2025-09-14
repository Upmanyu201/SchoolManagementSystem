# Fix foreign key constraint issue
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_add_missing_module_permissions'),
    ]

    operations = [
        # Ensure the foreign key constraint is properly handled
        migrations.RunSQL(
            "PRAGMA foreign_keys=OFF;",
            reverse_sql="PRAGMA foreign_keys=ON;"
        ),
        migrations.AlterField(
            model_name='usermodulepermission',
            name='user',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='module_permissions',
                to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.RunSQL(
            "PRAGMA foreign_keys=ON;",
            reverse_sql="PRAGMA foreign_keys=OFF;"
        ),
    ]