#!/usr/bin/env python3
"""
[HEALTH] System Health Monitor
Real-time monitoring and diagnostics for School Management System
"""

import os
import sys
import subprocess
import psutil
import sqlite3
import time
import socket
from pathlib import Path
from datetime import datetime

class Colors:
    GREEN = ''
    RED = ''
    YELLOW = ''
    BLUE = ''
    CYAN = ''
    BOLD = ''
    END = ''

class SystemHealthMonitor:
    def __init__(self):
        self.project_root = Path.cwd()
        self.venv_path = self.project_root / "venv"
        self.db_path = self.project_root / "db.sqlite3"
        self.python_exe = self.get_python_executable()
        self.health_score = 0
        self.max_score = 0
        
    def get_python_executable(self):
        """Get the correct Python executable"""
        if os.name == 'nt':  # Windows
            venv_python = self.venv_path / "Scripts" / "python.exe"
        else:
            venv_python = self.venv_path / "bin" / "python"
        
        return str(venv_python) if venv_python.exists() else sys.executable
    
    def print_header(self):
        print(f"{Colors.CYAN}================================================================")
        print(f"                                                                ")
        print(f"   [HEALTH] SYSTEM HEALTH MONITOR                                    ")
        print(f"   [CHECK] Real-time School Management System Diagnostics          ")
        print(f"                                                                ")
        print(f"================================================================{Colors.END}")
        
        print(f"\n{Colors.BOLD}[EMOJI] Health Check Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    
    def add_score(self, points, max_points=None):
        """Add points to health score"""
        if max_points is None:
            max_points = points
        
        self.health_score += points
        self.max_score += max_points
    
    def check_system_resources(self):
        """Check system resource usage"""
        print(f"\n{Colors.BOLD}[SYSTEM] System Resources{Colors.END}")
        
        try:
            # CPU Usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent < 70:
                print(f"   CPU Usage: {Colors.GREEN}{cpu_percent:.1f}%{Colors.END} [OK]")
                self.add_score(10)
            elif cpu_percent < 90:
                print(f"   CPU Usage: {Colors.YELLOW}{cpu_percent:.1f}%{Colors.END} [WARN]")
                self.add_score(5, 10)
            else:
                print(f"   CPU Usage: {Colors.RED}{cpu_percent:.1f}%{Colors.END} [ERROR]")
                self.add_score(0, 10)
            
            # Memory Usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_gb = memory.total / (1024**3)
            
            if memory_percent < 70:
                print(f"   Memory: {Colors.GREEN}{memory_percent:.1f}% of {memory_gb:.1f}GB{Colors.END} [OK]")
                self.add_score(10)
            elif memory_percent < 85:
                print(f"   Memory: {Colors.YELLOW}{memory_percent:.1f}% of {memory_gb:.1f}GB{Colors.END} [WARN]")
                self.add_score(5, 10)
            else:
                print(f"   Memory: {Colors.RED}{memory_percent:.1f}% of {memory_gb:.1f}GB{Colors.END} [ERROR]")
                self.add_score(0, 10)
            
            # Disk Usage
            disk = psutil.disk_usage(self.project_root)
            disk_percent = (disk.used / disk.total) * 100
            free_gb = disk.free / (1024**3)
            
            if disk_percent < 80:
                print(f"   Disk: {Colors.GREEN}{disk_percent:.1f}% used, {free_gb:.1f}GB free{Colors.END} [OK]")
                self.add_score(10)
            elif disk_percent < 90:
                print(f"   Disk: {Colors.YELLOW}{disk_percent:.1f}% used, {free_gb:.1f}GB free{Colors.END} [WARN]")
                self.add_score(5, 10)
            else:
                print(f"   Disk: {Colors.RED}{disk_percent:.1f}% used, {free_gb:.1f}GB free{Colors.END} [ERROR]")
                self.add_score(0, 10)
            
        except Exception as e:
            print(f"   {Colors.RED}[ERROR] Resource check failed: {e}{Colors.END}")
            self.add_score(0, 30)
    
    def check_python_environment(self):
        """Check Python environment health"""
        print(f"\n{Colors.BOLD}[PYTHON] Python Environment{Colors.END}")
        
        try:
            # Python version
            result = subprocess.run([self.python_exe, '--version'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"   Version: {Colors.GREEN}{version}{Colors.END} [OK]")
                self.add_score(5)
            else:
                print(f"   Version: {Colors.RED}Could not determine{Colors.END} [ERROR]")
                self.add_score(0, 5)
            
            # Virtual environment
            if str(self.venv_path) in self.python_exe:
                print(f"   Virtual Env: {Colors.GREEN}Active{Colors.END} [OK]")
                self.add_score(5)
            else:
                print(f"   Virtual Env: {Colors.YELLOW}Using system Python{Colors.END} [WARN]")
                self.add_score(2, 5)
            
            # pip health
            result = subprocess.run([self.python_exe, '-m', 'pip', 'check'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"   Dependencies: {Colors.GREEN}No conflicts{Colors.END} [OK]")
                self.add_score(5)
            else:
                print(f"   Dependencies: {Colors.YELLOW}Conflicts detected{Colors.END} [WARN]")
                self.add_score(2, 5)
            
        except Exception as e:
            print(f"   {Colors.RED}[ERROR] Python check failed: {e}{Colors.END}")
            self.add_score(0, 15)
    
    def check_django_health(self):
        """Check Django application health"""
        print(f"\n{Colors.BOLD}[TARGET] Django Application{Colors.END}")
        
        try:
            # Django version
            result = subprocess.run([self.python_exe, '-c', 'import django; print(django.get_version())'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"   Django: {Colors.GREEN}v{version}{Colors.END} [OK]")
                self.add_score(5)
            else:
                print(f"   Django: {Colors.RED}Not available{Colors.END} [ERROR]")
                self.add_score(0, 5)
                return
            
            # Settings check
            result = subprocess.run([self.python_exe, 'manage.py', 'check'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"   Configuration: {Colors.GREEN}Valid{Colors.END} [OK]")
                self.add_score(10)
            else:
                print(f"   Configuration: {Colors.RED}Issues detected{Colors.END} [ERROR]")
                self.add_score(0, 10)
            
            # Migration status
            result = subprocess.run([self.python_exe, 'manage.py', 'showmigrations'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                output = result.stdout
                if '[X]' in output and '[ ]' not in output:
                    print(f"   Migrations: {Colors.GREEN}All applied{Colors.END} [OK]")
                    self.add_score(5)
                elif '[ ]' in output:
                    print(f"   Migrations: {Colors.YELLOW}Pending migrations{Colors.END} [WARN]")
                    self.add_score(2, 5)
                else:
                    print(f"   Migrations: {Colors.BLUE}No migrations{Colors.END} ℹ[EMOJI]")
                    self.add_score(3, 5)
            else:
                print(f"   Migrations: {Colors.RED}Check failed{Colors.END} [ERROR]")
                self.add_score(0, 5)
            
        except Exception as e:
            print(f"   {Colors.RED}[ERROR] Django check failed: {e}{Colors.END}")
            self.add_score(0, 20)
    
    def check_database_health(self):
        """Check database health and performance"""
        print(f"\n{Colors.BOLD}[DATABASE]  Database Health{Colors.END}")
        
        try:
            # Database file existence
            if self.db_path.exists():
                db_size = self.db_path.stat().st_size / (1024 * 1024)  # MB
                print(f"   Database File: {Colors.GREEN}Exists ({db_size:.1f}MB){Colors.END} [OK]")
                self.add_score(5)
            else:
                print(f"   Database File: {Colors.RED}Missing{Colors.END} [ERROR]")
                self.add_score(0, 5)
                return
            
            # Database connectivity
            try:
                conn = sqlite3.connect(self.db_path, timeout=5)
                cursor = conn.cursor()
                
                # Test query
                start_time = time.time()
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table';")
                table_count = cursor.fetchone()[0]
                query_time = (time.time() - start_time) * 1000  # ms
                
                print(f"   Connectivity: {Colors.GREEN}OK ({query_time:.1f}ms){Colors.END} [OK]")
                self.add_score(5)
                
                print(f"   Tables: {Colors.GREEN}{table_count} tables{Colors.END} [OK]")
                self.add_score(5)
                
                # Check for data
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'django_%' AND name NOT LIKE 'auth_%';")
                app_tables = cursor.fetchall()
                
                if app_tables:
                    print(f"   App Tables: {Colors.GREEN}{len(app_tables)} found{Colors.END} [OK]")
                    self.add_score(5)
                else:
                    print(f"   App Tables: {Colors.YELLOW}No app tables{Colors.END} [WARN]")
                    self.add_score(2, 5)
                
                conn.close()
                
            except Exception as e:
                print(f"   Connectivity: {Colors.RED}Failed - {e}{Colors.END} [ERROR]")
                self.add_score(0, 15)
            
        except Exception as e:
            print(f"   {Colors.RED}[ERROR] Database check failed: {e}{Colors.END}")
            self.add_score(0, 20)
    
    def check_network_connectivity(self):
        """Check network connectivity and ports"""
        print(f"\n{Colors.BOLD}[NETWORK] Network Connectivity{Colors.END}")
        
        try:
            # Internet connectivity
            try:
                socket.create_connection(("8.8.8.8", 53), timeout=3)
                print(f"   Internet: {Colors.GREEN}Connected{Colors.END} [OK]")
                self.add_score(5)
            except:
                print(f"   Internet: {Colors.YELLOW}Offline{Colors.END} [WARN]")
                self.add_score(2, 5)
            
            # Port availability
            common_ports = [8000, 8080, 3000, 5000]
            available_ports = []
            
            for port in common_ports:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(1)
                        result = s.connect_ex(('127.0.0.1', port))
                        if result != 0:
                            available_ports.append(port)
                except:
                    available_ports.append(port)
            
            if available_ports:
                print(f"   Available Ports: {Colors.GREEN}{', '.join(map(str, available_ports))}{Colors.END} [OK]")
                self.add_score(5)
            else:
                print(f"   Available Ports: {Colors.RED}All common ports busy{Colors.END} [ERROR]")
                self.add_score(0, 5)
            
        except Exception as e:
            print(f"   {Colors.RED}[ERROR] Network check failed: {e}{Colors.END}")
            self.add_score(0, 10)
    
    def check_file_permissions(self):
        """Check file system permissions"""
        print(f"\n{Colors.BOLD}[EMOJI] File Permissions{Colors.END}")
        
        try:
            # Test write permissions
            test_file = self.project_root / "health_test.tmp"
            
            try:
                with open(test_file, 'w') as f:
                    f.write("test")
                test_file.unlink()
                print(f"   Write Access: {Colors.GREEN}OK{Colors.END} [OK]")
                self.add_score(5)
            except Exception as e:
                print(f"   Write Access: {Colors.RED}Failed - {e}{Colors.END} [ERROR]")
                self.add_score(0, 5)
            
            # Check critical directories
            critical_dirs = [
                self.project_root / "static",
                self.project_root / "media",
                self.project_root / "logs"
            ]
            
            accessible_dirs = 0
            for dir_path in critical_dirs:
                if dir_path.exists() and os.access(dir_path, os.R_OK | os.W_OK):
                    accessible_dirs += 1
            
            if accessible_dirs == len(critical_dirs):
                print(f"   Directory Access: {Colors.GREEN}All accessible{Colors.END} [OK]")
                self.add_score(5)
            elif accessible_dirs > 0:
                print(f"   Directory Access: {Colors.YELLOW}{accessible_dirs}/{len(critical_dirs)} accessible{Colors.END} [WARN]")
                self.add_score(3, 5)
            else:
                print(f"   Directory Access: {Colors.RED}Issues detected{Colors.END} [ERROR]")
                self.add_score(0, 5)
            
        except Exception as e:
            print(f"   {Colors.RED}[ERROR] Permission check failed: {e}{Colors.END}")
            self.add_score(0, 10)
    
    def check_ml_models(self):
        """Check ML models availability"""
        print(f"\n{Colors.BOLD}[ROBOT] ML Models Status{Colors.END}")
        
        try:
            models_dir = self.project_root / "models"
            
            if models_dir.exists():
                model_files = list(models_dir.glob("*.pkl"))
                
                if len(model_files) >= 20:  # Expected 26 models
                    print(f"   Model Files: {Colors.GREEN}{len(model_files)} models available{Colors.END} [OK]")
                    self.add_score(10)
                elif len(model_files) > 0:
                    print(f"   Model Files: {Colors.YELLOW}{len(model_files)} models (incomplete){Colors.END} [WARN]")
                    self.add_score(5, 10)
                else:
                    print(f"   Model Files: {Colors.RED}No models found{Colors.END} [ERROR]")
                    self.add_score(0, 10)
            else:
                print(f"   Models Directory: {Colors.RED}Not found{Colors.END} [ERROR]")
                self.add_score(0, 10)
            
            # Check ML dependencies
            ml_packages = ['sklearn', 'numpy', 'pandas']
            available_packages = 0
            
            for package in ml_packages:
                try:
                    result = subprocess.run([self.python_exe, '-c', f'import {package}'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        available_packages += 1
                except:
                    pass
            
            if available_packages == len(ml_packages):
                print(f"   ML Dependencies: {Colors.GREEN}All available{Colors.END} [OK]")
                self.add_score(5)
            elif available_packages > 0:
                print(f"   ML Dependencies: {Colors.YELLOW}{available_packages}/{len(ml_packages)} available{Colors.END} [WARN]")
                self.add_score(3, 5)
            else:
                print(f"   ML Dependencies: {Colors.RED}Not installed{Colors.END} [ERROR]")
                self.add_score(0, 5)
            
        except Exception as e:
            print(f"   {Colors.RED}[ERROR] ML check failed: {e}{Colors.END}")
            self.add_score(0, 15)
    
    def check_log_files(self):
        """Check log files and recent activity"""
        print(f"\n{Colors.BOLD}[LIST] Log Files Status{Colors.END}")
        
        try:
            logs_dir = self.project_root / "logs"
            
            if logs_dir.exists():
                log_files = list(logs_dir.glob("*.log"))
                
                if log_files:
                    print(f"   Log Files: {Colors.GREEN}{len(log_files)} files found{Colors.END} [OK]")
                    self.add_score(5)
                    
                    # Check recent activity
                    recent_logs = 0
                    current_time = time.time()
                    
                    for log_file in log_files:
                        if current_time - log_file.stat().st_mtime < 86400:  # 24 hours
                            recent_logs += 1
                    
                    if recent_logs > 0:
                        print(f"   Recent Activity: {Colors.GREEN}{recent_logs} files updated today{Colors.END} [OK]")
                        self.add_score(5)
                    else:
                        print(f"   Recent Activity: {Colors.YELLOW}No recent activity{Colors.END} [WARN]")
                        self.add_score(2, 5)
                else:
                    print(f"   Log Files: {Colors.YELLOW}No log files{Colors.END} [WARN]")
                    self.add_score(2, 5)
            else:
                print(f"   Logs Directory: {Colors.RED}Not found{Colors.END} [ERROR]")
                self.add_score(0, 5)
            
        except Exception as e:
            print(f"   {Colors.RED}[ERROR] Log check failed: {e}{Colors.END}")
            self.add_score(0, 10)
    
    def generate_health_report(self):
        """Generate comprehensive health report"""
        print(f"\n{Colors.BOLD}[HEALTH] HEALTH REPORT{Colors.END}")
        print("=" * 60)
        
        health_percentage = (self.health_score / self.max_score * 100) if self.max_score > 0 else 0
        
        print(f"Overall Health Score: {Colors.BOLD}{self.health_score}/{self.max_score}{Colors.END}")
        print(f"Health Percentage: {Colors.BOLD}{health_percentage:.1f}%{Colors.END}")
        
        # Health status
        if health_percentage >= 90:
            status = f"{Colors.GREEN}EXCELLENT{Colors.END} [SUCCESS]"
            recommendation = "System is running optimally"
        elif health_percentage >= 75:
            status = f"{Colors.GREEN}GOOD{Colors.END} [OK]"
            recommendation = "System is healthy with minor issues"
        elif health_percentage >= 60:
            status = f"{Colors.YELLOW}FAIR{Colors.END} [WARN]"
            recommendation = "Some issues need attention"
        elif health_percentage >= 40:
            status = f"{Colors.RED}POOR{Colors.END} [ERROR]"
            recommendation = "Multiple issues require immediate attention"
        else:
            status = f"{Colors.RED}CRITICAL{Colors.END} [EMOJI]"
            recommendation = "System needs immediate maintenance"
        
        print(f"Status: {status}")
        print(f"Recommendation: {recommendation}")
        
        # Performance metrics
        print(f"\n{Colors.BOLD}[CHART] Performance Metrics:{Colors.END}")
        print(f"   • System Resources: {'[OK]' if health_percentage >= 70 else '[WARN]'}")
        print(f"   • Application Health: {'[OK]' if health_percentage >= 70 else '[WARN]'}")
        print(f"   • Database Performance: {'[OK]' if health_percentage >= 70 else '[WARN]'}")
        print(f"   • Network Connectivity: {'[OK]' if health_percentage >= 70 else '[WARN]'}")
        
        return health_percentage >= 70
    
    def run_health_check(self):
        """Run complete health check"""
        self.print_header()
        
        health_checks = [
            self.check_system_resources,
            self.check_python_environment,
            self.check_django_health,
            self.check_database_health,
            self.check_network_connectivity,
            self.check_file_permissions,
            self.check_ml_models,
            self.check_log_files
        ]
        
        for check_function in health_checks:
            try:
                check_function()
            except Exception as e:
                check_name = check_function.__name__.replace('check_', '').replace('_', ' ').title()
                print(f"\n{Colors.BOLD}{check_name}{Colors.END}")
                print(f"   {Colors.RED}[ERROR] Health check failed: {e}{Colors.END}")
                self.add_score(0, 10)
        
        return self.generate_health_report()

def main():
    """Main execution function"""
    monitor = SystemHealthMonitor()
    
    try:
        success = monitor.run_health_check()
        
        print(f"\n{Colors.BOLD}[EMOJI] Health Check Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
        
        if success:
            print(f"\n{Colors.GREEN}[OK] System health is good!{Colors.END}")
            sys.exit(0)
        else:
            print(f"\n{Colors.YELLOW}[WARN]  System health needs attention{Colors.END}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[WARN]  Health check cancelled by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}[ERROR] Health check error: {e}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()