# Generated migration to fix amount_type display issue

from django.db import migrations

def fix_amount_type_data(apps, schema_editor):
    """Fix existing fee types with incorrect amount_type values"""
    FeesType = apps.get_model('fees', 'FeesType')
    
    # Fix records where amount_type contains month names instead of user input
    for fee_type in FeesType.objects.all():
        if fee_type.context_type == 'monthly' and fee_type.context_data.get('months'):
            # If amount_type contains month names, set it to 'monthly'
            if any(month in fee_type.amount_type for month in [
                'January', 'February', 'March', 'April', 'May', 'June',
                'July', 'August', 'September', 'October', 'November', 'December'
            ]):
                fee_type.amount_type = 'monthly'
                fee_type.save()

def reverse_fix_amount_type_data(apps, schema_editor):
    """Reverse migration - no action needed"""
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('fees', '0006_merge_20250910_1055'),
    ]

    operations = [
        migrations.RunPython(fix_amount_type_data, reverse_fix_amount_type_data),
    ]