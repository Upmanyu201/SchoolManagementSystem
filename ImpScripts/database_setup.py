#!/usr/bin/env python3
"""
🗄️ Database Setup & Migration Manager
Handles SQLite database creation, migrations, and initial data setup
"""

import os
import sys
import subprocess
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class DatabaseSetup:
    def __init__(self):
        self.project_root = Path.cwd()
        self.venv_path = self.project_root / "venv"
        self.db_path = self.project_root / "db.sqlite3"
        self.backup_dir = self.project_root / "backups"
        self.python_exe = self.get_python_executable()
        
    def get_python_executable(self):
        """Get the correct Python executable (venv or system)"""
        if os.name == 'nt':  # Windows
            venv_python = self.venv_path / "Scripts" / "python.exe"
        else:  # Unix-like
            venv_python = self.venv_path / "bin" / "python"
        
        if venv_python.exists():
            return str(venv_python)
        else:
            return sys.executable
    
    def print_header(self):
        print(f"{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗")
        print(f"║                                                              ║")
        print(f"║  🗄️  DATABASE SETUP & MIGRATION MANAGER                     ║")
        print(f"║  📊 SQLite Database Configuration                           ║")
        print(f"║                                                              ║")
        print(f"╚══════════════════════════════════════════════════════════════╝{Colors.END}")
    
    def check_django_availability(self):
        """Check if Django is available"""
        print(f"\n{Colors.BOLD}🔍 Checking Django availability...{Colors.END}")
        
        try:
            cmd = [self.python_exe, "-c", "import django; print(django.get_version())"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"   {Colors.GREEN}✅ Django {version} available{Colors.END}")
                return True
            else:
                print(f"   {Colors.RED}❌ Django not available{Colors.END}")
                return False
                
        except Exception as e:
            print(f"   {Colors.RED}❌ Django check failed: {e}{Colors.END}")
            return False
    
    def backup_existing_database(self):
        """Backup existing database if it exists"""
        if not self.db_path.exists():
            print(f"\n{Colors.BLUE}ℹ️  No existing database found{Colors.END}")
            return True
        
        print(f"\n{Colors.BOLD}💾 Backing up existing database...{Colors.END}")
        
        try:
            # Create backup directory
            self.backup_dir.mkdir(exist_ok=True)
            
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"db_backup_{timestamp}.sqlite3"
            backup_path = self.backup_dir / backup_name
            
            # Copy database
            shutil.copy2(self.db_path, backup_path)
            
            print(f"   {Colors.GREEN}✅ Database backed up to: {backup_name}{Colors.END}")
            return True
            
        except Exception as e:
            print(f"   {Colors.RED}❌ Backup failed: {e}{Colors.END}")
            return False
    
    def remove_existing_database(self):
        """Remove existing database"""
        if self.db_path.exists():
            print(f"\n{Colors.BOLD}🗑️  Removing existing database...{Colors.END}")
            
            try:
                os.remove(self.db_path)
                print(f"   {Colors.GREEN}✅ Existing database removed{Colors.END}")
            except Exception as e:
                print(f"   {Colors.RED}❌ Could not remove database: {e}{Colors.END}")
                return False
        
        return True
    
    def clean_migration_files(self):
        """Remove existing migration files (except __init__.py)"""
        print(f"\n{Colors.BOLD}🧹 Cleaning migration files...{Colors.END}")
        
        migration_dirs = []
        
        # Find all migration directories
        for item in self.project_root.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                migrations_dir = item / "migrations"
                if migrations_dir.exists():
                    migration_dirs.append(migrations_dir)
        
        cleaned_count = 0
        
        for migrations_dir in migration_dirs:
            try:
                for migration_file in migrations_dir.iterdir():
                    if (migration_file.is_file() and 
                        migration_file.name.endswith('.py') and 
                        migration_file.name != '__init__.py'):
                        
                        migration_file.unlink()
                        cleaned_count += 1
                
                # Also remove __pycache__
                pycache_dir = migrations_dir / "__pycache__"
                if pycache_dir.exists():
                    shutil.rmtree(pycache_dir)
                    
            except Exception as e:
                print(f"   {Colors.YELLOW}⚠️  Could not clean {migrations_dir}: {e}{Colors.END}")
        
        print(f"   {Colors.GREEN}✅ Cleaned {cleaned_count} migration files{Colors.END}")
        return True
    
    def create_initial_migrations(self):
        """Create initial migration files"""
        print(f"\n{Colors.BOLD}📝 Creating initial migrations...{Colors.END}")
        
        try:
            cmd = [self.python_exe, "manage.py", "makemigrations"]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print(f"   {Colors.GREEN}✅ Initial migrations created{Colors.END}")
                
                # Show what was created
                if result.stdout:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if 'Create model' in line or 'migrations for' in line:
                            print(f"   📄 {line}")
                
                return True
            else:
                print(f"   {Colors.RED}❌ Migration creation failed{Colors.END}")
                print(f"   Error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"   {Colors.RED}❌ Migration creation error: {e}{Colors.END}")
            return False
    
    def apply_migrations(self):
        """Apply migrations to create database schema"""
        print(f"\n{Colors.BOLD}🔧 Applying migrations...{Colors.END}")
        
        try:
            cmd = [self.python_exe, "manage.py", "migrate"]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"   {Colors.GREEN}✅ Migrations applied successfully{Colors.END}")
                
                # Show applied migrations
                if result.stdout:
                    lines = result.stdout.strip().split('\n')
                    applied_count = 0
                    for line in lines:
                        if 'Applying' in line:
                            applied_count += 1
                    
                    if applied_count > 0:
                        print(f"   📊 {applied_count} migrations applied")
                
                return True
            else:
                print(f"   {Colors.RED}❌ Migration application failed{Colors.END}")
                print(f"   Error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"   {Colors.RED}❌ Migration application error: {e}{Colors.END}")
            return False
    
    def verify_database_structure(self):
        """Verify database was created correctly"""
        print(f"\n{Colors.BOLD}✅ Verifying database structure...{Colors.END}")
        
        if not self.db_path.exists():
            print(f"   {Colors.RED}❌ Database file not created{Colors.END}")
            return False
        
        try:
            # Connect to database and check tables
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get list of tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            table_names = [table[0] for table in tables]
            
            # Check for essential Django tables
            essential_tables = [
                'django_migrations',
                'auth_user',
                'django_content_type'
            ]
            
            missing_tables = []
            for table in essential_tables:
                if table not in table_names:
                    missing_tables.append(table)
            
            if missing_tables:
                print(f"   {Colors.RED}❌ Missing essential tables: {missing_tables}{Colors.END}")
                return False
            
            print(f"   {Colors.GREEN}✅ Database structure valid{Colors.END}")
            print(f"   📊 {len(table_names)} tables created")
            
            # Show some key tables
            key_tables = ['auth_user', 'students_student', 'fees_fee', 'teachers_teacher']
            found_tables = [t for t in key_tables if t in table_names]
            
            if found_tables:
                print(f"   📋 Key tables: {', '.join(found_tables)}")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"   {Colors.RED}❌ Database verification failed: {e}{Colors.END}")
            return False
    
    def create_superuser_prompt(self):
        """Prompt to create superuser account"""
        print(f"\n{Colors.BOLD}👤 Superuser Account Setup{Colors.END}")
        
        try:
            response = input(f"   {Colors.YELLOW}Create superuser account now? (y/n): {Colors.END}")
            
            if response.lower() in ['y', 'yes']:
                print(f"   {Colors.CYAN}Creating superuser account...{Colors.END}")
                
                cmd = [self.python_exe, "manage.py", "createsuperuser"]
                
                # Run interactively
                result = subprocess.run(cmd, timeout=300)
                
                if result.returncode == 0:
                    print(f"   {Colors.GREEN}✅ Superuser created successfully{Colors.END}")
                else:
                    print(f"   {Colors.YELLOW}⚠️  Superuser creation cancelled or failed{Colors.END}")
            else:
                print(f"   {Colors.BLUE}ℹ️  Superuser creation skipped{Colors.END}")
                print(f"   {Colors.CYAN}💡 Run 'python manage.py createsuperuser' later{Colors.END}")
            
            return True
            
        except Exception as e:
            print(f"   {Colors.YELLOW}⚠️  Superuser setup error: {e}{Colors.END}")
            return True  # Not critical
    
    def load_initial_data(self):
        """Load initial data if fixtures exist"""
        print(f"\n{Colors.BOLD}📊 Loading initial data...{Colors.END}")
        
        # Look for fixture files
        fixture_dirs = [
            self.project_root / "fixtures",
            self.project_root / "initial_data"
        ]
        
        fixture_files = []
        for fixture_dir in fixture_dirs:
            if fixture_dir.exists():
                for fixture_file in fixture_dir.glob("*.json"):
                    fixture_files.append(fixture_file)
        
        if not fixture_files:
            print(f"   {Colors.BLUE}ℹ️  No fixture files found{Colors.END}")
            return True
        
        loaded_count = 0
        for fixture_file in fixture_files:
            try:
                print(f"   📄 Loading {fixture_file.name}...")
                
                cmd = [self.python_exe, "manage.py", "loaddata", str(fixture_file)]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    print(f"   {Colors.GREEN}✅ {fixture_file.name} loaded{Colors.END}")
                    loaded_count += 1
                else:
                    print(f"   {Colors.YELLOW}⚠️  {fixture_file.name} failed to load{Colors.END}")
                    
            except Exception as e:
                print(f"   {Colors.YELLOW}⚠️  Error loading {fixture_file.name}: {e}{Colors.END}")
        
        if loaded_count > 0:
            print(f"   {Colors.GREEN}✅ {loaded_count} fixture files loaded{Colors.END}")
        
        return True
    
    def run_database_setup(self):
        """Run complete database setup process"""
        self.print_header()
        
        # Check Django availability
        if not self.check_django_availability():
            return False
        
        # Backup existing database
        if not self.backup_existing_database():
            return False
        
        # Remove existing database
        if not self.remove_existing_database():
            return False
        
        # Clean migration files
        if not self.clean_migration_files():
            return False
        
        # Create initial migrations
        if not self.create_initial_migrations():
            return False
        
        # Apply migrations
        if not self.apply_migrations():
            return False
        
        # Verify database structure
        if not self.verify_database_structure():
            return False
        
        # Load initial data
        self.load_initial_data()
        
        # Create superuser
        self.create_superuser_prompt()
        
        print(f"\n{Colors.GREEN}🎉 Database setup completed successfully!{Colors.END}")
        print(f"\n{Colors.BOLD}📋 Database Information:{Colors.END}")
        print(f"   📍 Location: {self.db_path}")
        print(f"   💾 Backup Directory: {self.backup_dir}")
        print(f"   🔧 Type: SQLite3")
        
        return True

def main():
    """Main execution function"""
    setup = DatabaseSetup()
    
    try:
        success = setup.run_database_setup()
        
        if success:
            print(f"\n{Colors.GREEN}✅ Database is ready for School Management System!{Colors.END}")
            sys.exit(0)
        else:
            print(f"\n{Colors.RED}❌ Database setup failed{Colors.END}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Database setup cancelled by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Database setup error: {e}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()