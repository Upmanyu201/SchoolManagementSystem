# Alternative migration - recreate table if needed

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0001_initial'),
        ('fees', '0002_fix_fees_consistency'),
    ]

    operations = [
        # Backup data, drop table, recreate with correct structure
        migrations.RunSQL(
            "CREATE TABLE fees_feestype_backup AS SELECT * FROM fees_feestype;",
            reverse_sql="DROP TABLE IF EXISTS fees_feestype_backup;"
        ),
        
        migrations.DeleteModel(
            name='FeesType',
        ),
        
        migrations.CreateModel(
            name='FeesType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('amount_type', models.CharField(choices=[('Monthly', 'Monthly'), ('Quarterly', 'Quarterly'), ('Yearly', 'Yearly'), ('One Time', 'One Time')], max_length=50)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('class_name', models.CharField(blank=True, max_length=50, null=True)),
                ('fee_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fee_types', to='fees.feesgroup')),
                ('related_stoppage', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fees_feestypes', to='transport.stoppage')),
            ],
            options={
                'unique_together': {('fee_group', 'amount_type', 'class_name', 'related_stoppage')},
            },
            bases=(models.Model,),
        ),
        
        # Restore data
        migrations.RunSQL(
            """
            INSERT INTO fees_feestype (id, created_at, updated_at, amount_type, amount, class_name, fee_group_id, related_stoppage_id)
            SELECT id, created_at, updated_at, amount_type, amount, class_name, fee_group_id, related_stoppage_id
            FROM fees_feestype_backup;
            """,
            reverse_sql="DELETE FROM fees_feestype;"
        ),
        
        migrations.RunSQL(
            "DROP TABLE fees_feestype_backup;",
            reverse_sql="SELECT 1;"
        ),
    ]