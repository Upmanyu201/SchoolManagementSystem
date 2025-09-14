# Data migration for ClassSection integration

from django.db import migrations

def migrate_promotion_data(apps, schema_editor):
    """Migrate data from old class fields to new class_section fields"""
    PromotionRule = apps.get_model('promotion', 'PromotionRule')
    ClassSection = apps.get_model('subjects', 'ClassSection')
    AcademicClass = apps.get_model('core', 'AcademicClass')
    
    for rule in PromotionRule.objects.all():
        if rule.current_class:
            try:
                current_cs = ClassSection.objects.get(
                    class_name=rule.current_class.name,
                    section_name=rule.current_class.section
                )
                rule.current_class_section = current_cs
            except ClassSection.DoesNotExist:
                # Create ClassSection if it doesn't exist
                current_cs = ClassSection.objects.create(
                    class_name=rule.current_class.name,
                    section_name=rule.current_class.section
                )
                rule.current_class_section = current_cs
        
        if rule.next_class:
            try:
                next_cs = ClassSection.objects.get(
                    class_name=rule.next_class.name,
                    section_name=rule.next_class.section
                )
                rule.next_class_section = next_cs
            except ClassSection.DoesNotExist:
                # Create ClassSection if it doesn't exist
                next_cs = ClassSection.objects.create(
                    class_name=rule.next_class.name,
                    section_name=rule.next_class.section
                )
                rule.next_class_section = next_cs
        
        rule.save()

def reverse_migrate_promotion_data(apps, schema_editor):
    """Reverse migration - not implemented"""
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('promotion', '0002_alter_promotionrule_unique_together_and_more'),
        ('subjects', '0006_alter_classsection_options'),
    ]

    operations = [
        migrations.RunPython(migrate_promotion_data, reverse_migrate_promotion_data),
    ]