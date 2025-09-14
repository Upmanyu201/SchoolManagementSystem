# Fix cascade deletion for user foreign keys
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_fix_foreign_key_constraint'),
    ]

    operations = [
        # Temporarily disable foreign key checks
        migrations.RunSQL(
            "PRAGMA foreign_keys=OFF;",
            reverse_sql="PRAGMA foreign_keys=ON;"
        ),
        
        # Fix the foreign key to ensure proper CASCADE deletion
        migrations.AlterField(
            model_name='usermodulepermission',
            name='user',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='module_permissions',
                to=settings.AUTH_USER_MODEL,
                db_constraint=True
            ),
        ),
        
        # Re-enable foreign key checks
        migrations.RunSQL(
            "PRAGMA foreign_keys=ON;",
            reverse_sql="PRAGMA foreign_keys=OFF;"
        ),
    ]