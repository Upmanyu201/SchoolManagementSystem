# Data migration to clean up orphaned records

from django.db import migrations

def cleanup_orphaned_activity_records(apps, schema_editor):
    """Remove orphaned user activity records"""
    try:
        # Get models
        CustomUser = apps.get_model('users', 'CustomUser')
        
        # Check if UserActivity model exists
        try:
            UserActivity = apps.get_model('users', 'UserActivity')
            
            # Get valid user IDs
            valid_user_ids = set(CustomUser.objects.values_list('id', flat=True))
            
            # Delete orphaned activity records
            orphaned_activities = UserActivity.objects.exclude(user_id__in=valid_user_ids)
            count = orphaned_activities.count()
            orphaned_activities.delete()
            
            print(f"Cleaned up {count} orphaned user activity records")
            
        except LookupError:
            # UserActivity model doesn't exist, skip
            print("UserActivity model not found, skipping cleanup")
            
    except Exception as e:
        print(f"Error during cleanup: {e}")

def reverse_cleanup(apps, schema_editor):
    """Reverse operation - no action needed"""
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_remove_unused_modules'),
    ]

    operations = [
        migrations.RunPython(cleanup_orphaned_activity_records, reverse_cleanup),
    ]