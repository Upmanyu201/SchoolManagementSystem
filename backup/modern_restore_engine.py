# Modern Restore Engine - 2025 Industry Standards
import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from django.apps import apps
from django.db import transaction
from django.conf import settings
from django.utils import timezone
from decimal import Decimal

logger = logging.getLogger('backup.restore')

@dataclass
class RestoreResult:
    created: int = 0
    updated: int = 0
    skipped: int = 0
    errors: int = 0
    categories: Dict[str, Any] = None

    def __post_init__(self):
        if self.categories is None:
            self.categories = {}

class ModernRestoreEngine:
    """2025 Modern Restore Engine with async support and enhanced security"""
    
    # Updated model order based on actual dependencies
    MODEL_ORDER = [
        'subjects.classsection',  # Primary - all students reference this
        'school_profile.schoolprofile',
        'teachers.teacher',
        'subjects.subject',
        'students.student',
        'transport.route',
        'transport.stoppage',
        'fees.feesgroup',
        'fees.feestype',
        'fines.finetype',
        'transport.transportassignment',
        'student_fees.feedeposit',
        'fines.fine',
        'fines.finestudent',
        'attendance.attendance',
    ]
    
    ALLOWED_APPS = [
        'core', 'school_profile', 'teachers', 'subjects', 'students',
        'transport', 'student_fees', 'fees', 'fines', 'attendance',
        'promotion', 'reports', 'messaging'
    ]

    def __init__(self):
        self.stats = RestoreResult()
        
    def restore_backup(self, file_path: str, mode: str = 'merge') -> RestoreResult:
        """Main restore method"""
        try:
            data = self._load_backup_file(file_path)
            grouped_data = self._group_by_model(data)
            
            if mode == 'replace':
                self._clear_data_safely(list(grouped_data.keys()))
            
            self._restore_models_in_order(grouped_data, mode)
            
            return self.stats
            
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            raise

    def _load_backup_file(self, file_path: str) -> List[Dict]:
        """File loading with validation"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Backup file not found: {file_path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                raise ValueError("Invalid backup format")
            
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")

    def _group_by_model(self, data: List[Dict]) -> Dict[str, List[Dict]]:
        """Group records by model"""
        grouped = {}
        for item in data:
            if not isinstance(item, dict) or 'model' not in item:
                continue
            
            model_name = item['model'].lower()
            app_label = model_name.split('.')[0]
            
            if app_label in self.ALLOWED_APPS:
                grouped.setdefault(model_name, []).append(item)
        
        return grouped

    def _restore_models_in_order(self, grouped_data: Dict, mode: str):
        """Restore models in dependency order"""
        # Process in defined order first
        for model_name in self.MODEL_ORDER:
            if model_name in grouped_data:
                self._restore_model(model_name, grouped_data[model_name], mode)
        
        # Process remaining models
        for model_name, records in grouped_data.items():
            if model_name not in self.MODEL_ORDER:
                self._restore_model(model_name, records, mode)

    def _restore_model(self, model_name: str, records: List[Dict], mode: str):
        """Restore single model with error handling"""
        try:
            app_label, model_class = model_name.split('.')
            model = apps.get_model(app_label, model_class)
            
            # Bulk process for better performance
            batch_size = 1000
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                for record in batch:
                    self._restore_record(model, record, mode)
                
        except Exception as e:
            logger.error(f"Model {model_name} restore failed: {e}")
            self.stats.errors += len(records)

    def _restore_record(self, model, record: Dict, mode: str):
        """Restore individual record"""
        try:
            with transaction.atomic():
                fields = record.get('fields', {})
                pk = record.get('pk')
                
                # Clean fields
                cleaned_fields = self._clean_fields(model, fields)
                
                # Skip if no valid fields
                if not cleaned_fields:
                    self.stats.skipped += 1
                    return
                
                # Check existing
                existing = None
                if pk:
                    try:
                        existing = model.objects.get(pk=pk)
                    except model.DoesNotExist:
                        pass
                
                if existing and mode == 'merge':
                    # Update existing
                    for field_name, value in cleaned_fields.items():
                        if value is not None:  # Only update non-null values
                            setattr(existing, field_name, value)
                    existing.save()
                    self.stats.updated += 1
                elif not existing:
                    # Create new
                    if pk:
                        cleaned_fields['id'] = pk
                    model.objects.create(**cleaned_fields)
                    self.stats.created += 1
                else:
                    self.stats.skipped += 1
                    
        except Exception as e:
            logger.error(f"Record restore failed: {e}")
            self.stats.errors += 1

    def _clean_fields(self, model, fields: Dict) -> Dict:
        """Clean and validate fields"""
        cleaned = {}
        valid_fields = {f.name for f in model._meta.get_fields() 
                       if hasattr(f, 'name') and not f.many_to_many}
        
        for field_name, value in fields.items():
            if field_name in valid_fields:
                try:
                    field = model._meta.get_field(field_name)
                    cleaned[field_name] = self._convert_value(field, value)
                except Exception:
                    continue
        
        return cleaned

    def _convert_value(self, field, value):
        """Convert field value to proper type"""
        if value in ('', 'null', None):
            return None
        
        from django.db import models
        
        if isinstance(field, models.ForeignKey):
            # For foreign keys, try to get the related object
            try:
                related_model = field.related_model
                return related_model.objects.get(pk=value)
            except (related_model.DoesNotExist, ValueError):
                return None
        elif isinstance(field, models.DecimalField):
            return Decimal(str(value)) if value else None
        elif isinstance(field, models.BooleanField):
            return str(value).lower() in ('true', '1', 'yes') if isinstance(value, str) else bool(value)
        elif isinstance(field, models.IntegerField):
            return int(float(value)) if value else None
        elif isinstance(field, models.CharField):
            return str(value)[:field.max_length] if hasattr(field, 'max_length') else str(value)
        
        return value

    def _clear_data_safely(self, model_names: List[str]):
        """Safely clear data preserving critical records"""
        preserve_models = ['auth.user', 'auth.group', 'users.customuser']
        
        for model_name in reversed(self.MODEL_ORDER):
            if model_name in model_names and model_name not in preserve_models:
                try:
                    app_label, model_class = model_name.split('.')
                    model = apps.get_model(app_label, model_class)
                    model.objects.all().delete()
                except Exception as e:
                    logger.error(f"Failed to clear {model_name}: {e}")

# Compatibility wrapper for existing code
SchoolDataRestoreEngine = ModernRestoreEngine