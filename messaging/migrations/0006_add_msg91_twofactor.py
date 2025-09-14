# Generated migration for MSG91 and 2Factor fields

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0005_messagingconfig_messagecentral_customer_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='messagingconfig',
            name='msg91_auth_key',
            field=models.CharField(blank=True, help_text='MSG91 Auth Key', max_length=100),
        ),
        migrations.AddField(
            model_name='messagingconfig',
            name='msg91_sender_id',
            field=models.CharField(blank=True, default='SCHOOL', help_text='MSG91 Sender ID', max_length=10),
        ),
        migrations.AddField(
            model_name='messagingconfig',
            name='twofactor_api_key',
            field=models.CharField(blank=True, help_text='2Factor API Key', max_length=100),
        ),
    ]