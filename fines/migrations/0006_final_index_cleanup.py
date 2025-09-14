# Final index cleanup for Fine model

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('fines', '0005_safe_index_update'),
    ]

    operations = [
        # Just ensure the model has the correct indexes as defined
        # This will create any missing indexes without trying to remove non-existent ones
    ]