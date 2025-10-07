# 📅 MANUAL DEMO EXTENSION GUIDE

## Method 1: SQLite Database Direct Edit

### Step 1: Stop the Django server
```bash
# Press Ctrl+C to stop the server
```

### Step 2: Open SQLite database
```bash
# Navigate to project root
cd "D:\Web Applications\SchoolManagement\School-Management-System-main"

# Open database with SQLite browser or command line
sqlite3 db.sqlite3
```

### Step 3: Check current demo status
```sql
SELECT * FROM demo_demostatus;
```

### Step 4: Extend demo period (30 days max)
```sql
-- Extend by 30 days from current expiry
UPDATE demo_demostatus 
SET demo_expires = datetime(demo_expires, '+30 days') 
WHERE id = 1;

-- Or set specific date (YYYY-MM-DD HH:MM:SS format)
UPDATE demo_demostatus 
SET demo_expires = '2024-12-31 23:59:59' 
WHERE id = 1;
```

### Step 5: Verify changes
```sql
SELECT machine_id, demo_started, demo_expires, is_licensed 
FROM demo_demostatus;
```

### Step 6: Exit SQLite and restart server
```sql
.exit
```

## Method 2: Django Admin Panel

### Step 1: Create superuser (if not exists)
```bash
python manage.py createsuperuser
```

### Step 2: Access admin panel
- Go to: http://127.0.0.1:8000/admin/
- Login with superuser credentials

### Step 3: Navigate to Demo Status
- Click "Demo" → "Demo statuses"
- Edit the demo status record
- Change "Demo expires" field
- Save changes

## Method 3: Django Shell

### Step 1: Open Django shell
```bash
python manage.py shell
```

### Step 2: Extend demo programmatically
```python
from demo.models import DemoStatus
from django.utils import timezone
from datetime import timedelta

# Get demo status
demo = DemoStatus.get_current_status()
print(f"Current expiry: {demo.demo_expires}")

# Extend by 30 days
demo.demo_expires = demo.demo_expires + timedelta(days=30)
demo.save()

print(f"New expiry: {demo.demo_expires}")
print(f"Days remaining: {demo.days_remaining}")
```

### Step 3: Exit shell
```python
exit()
```

## Security Notes

- ⚠️ Manual methods bypass security checks
- 🔒 Use secure script for production environments
- 📝 Keep audit trail of extensions
- 🚫 Limit extensions to reasonable periods
- 👥 Restrict access to authorized personnel only

## Recommended Approach

Use the secure demo extender script:
```bash
cd ImpScripts
python secure_demo_extender.py
```

**Default Credentials:**
- Username: `admin` | Password: `admin123`
- Username: `support` | Password: `support456`
- Username: `developer` | Password: `dev789`

**Change these passwords in production!**