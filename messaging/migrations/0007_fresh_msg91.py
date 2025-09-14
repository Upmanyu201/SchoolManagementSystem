# Fresh MSG91 migration

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0006_add_msg91_twofactor'),
        ('students', '0001_initial'),
        ('student_fees', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        # Remove old models
        migrations.DeleteModel(name='MessagingConfig'),
        migrations.DeleteModel(name='MessagingSettings'),
        migrations.DeleteModel(name='WhatsAppGroup'),
        migrations.DeleteModel(name='GroupMessage'),
        migrations.DeleteModel(name='MessageTemplate'),
        migrations.DeleteModel(name='MessageRecipient'),
        migrations.DeleteModel(name='MessageLog'),
        
        # Create new MSG91 models
        migrations.CreateModel(
            name='MSG91Config',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('auth_key', models.CharField(help_text='MSG91 Auth Key', max_length=100)),
                ('sender_id', models.CharField(default='TXTLCL', help_text='MSG91 Sender ID', max_length=10)),
            ],
            options={
                'verbose_name': 'MSG91 Configuration',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MessageLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('recipient_phone', models.CharField(max_length=15)),
                ('recipient_name', models.CharField(max_length=100)),
                ('message_content', models.TextField()),
                ('status', models.CharField(choices=[('SENT', 'Sent'), ('FAILED', 'Failed')], max_length=10)),
                ('msg91_message_id', models.CharField(blank=True, max_length=100)),
                ('error_message', models.TextField(blank=True)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('student', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='students.student')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]