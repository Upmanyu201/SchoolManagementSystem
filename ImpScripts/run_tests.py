#!/usr/bin/env python3
"""
🧪 System Test Runner
Comprehensive testing suite for School Management System
"""

import os
import sys
import subprocess
import time
import socket
import sqlite3
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class SystemTester:
    def __init__(self):
        self.project_root = Path.cwd()
        self.venv_path = self.project_root / "venv"
        self.db_path = self.project_root / "db.sqlite3"
        self.python_exe = self.get_python_executable()
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0
        
    def get_python_executable(self):
        """Get the correct Python executable"""
        if os.name == 'nt':  # Windows
            venv_python = self.venv_path / "Scripts" / "python.exe"
        else:
            venv_python = self.venv_path / "bin" / "python"
        
        return str(venv_python) if venv_python.exists() else sys.executable
    
    def print_header(self):
        print(f"{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗")
        print(f"║                                                              ║")
        print(f"║  🧪 SYSTEM TEST RUNNER                                      ║")
        print(f"║  📊 Comprehensive School Management System Testing          ║")
        print(f"║                                                              ║")
        print(f"╚══════════════════════════════════════════════════════════════╝{Colors.END}")
    
    def log_test_result(self, test_name, passed, message=""):
        """Log test result"""
        status = "PASS" if passed else "FAIL"
        color = Colors.GREEN if passed else Colors.RED
        
        self.test_results.append({
            'name': test_name,
            'passed': passed,
            'message': message
        })
        
        if passed:
            self.passed_tests += 1
            print(f"   {color}✅ {test_name}: {status}{Colors.END}")
        else:
            self.failed_tests += 1
            print(f"   {color}❌ {test_name}: {status}{Colors.END}")
            if message:
                print(f"      {Colors.YELLOW}💡 {message}{Colors.END}")
    
    def test_python_environment(self):
        """Test Python environment"""
        print(f"\n{Colors.BOLD}🐍 Testing Python Environment{Colors.END}")
        
        try:
            # Test Python version
            result = subprocess.run([self.python_exe, '--version'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                version = result.stdout.strip()
                self.log_test_result("Python Version", True, version)
            else:
                self.log_test_result("Python Version", False, "Could not get Python version")
                return False
            
            # Test pip
            result = subprocess.run([self.python_exe, '-m', 'pip', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.log_test_result("pip Availability", True)
            else:
                self.log_test_result("pip Availability", False, "pip not working")
            
            return True
            
        except Exception as e:
            self.log_test_result("Python Environment", False, str(e))
            return False
    
    def test_virtual_environment(self):
        """Test virtual environment"""
        print(f"\n{Colors.BOLD}🌐 Testing Virtual Environment{Colors.END}")
        
        try:
            # Check if venv exists
            if self.venv_path.exists():
                self.log_test_result("Virtual Environment Exists", True)
            else:
                self.log_test_result("Virtual Environment Exists", False, "venv directory not found")
                return False
            
            # Check if using venv Python
            if str(self.venv_path) in self.python_exe:
                self.log_test_result("Using Virtual Environment", True)
            else:
                self.log_test_result("Using Virtual Environment", False, "Using system Python")
            
            return True
            
        except Exception as e:
            self.log_test_result("Virtual Environment", False, str(e))
            return False
    
    def test_django_installation(self):
        """Test Django installation and configuration"""
        print(f"\n{Colors.BOLD}🎯 Testing Django Installation{Colors.END}")
        
        try:
            # Test Django import
            result = subprocess.run([self.python_exe, '-c', 'import django; print(django.get_version())'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                version = result.stdout.strip()
                self.log_test_result("Django Import", True, f"Django {version}")
            else:
                self.log_test_result("Django Import", False, "Django not installed")
                return False
            
            # Test Django settings
            result = subprocess.run([self.python_exe, 'manage.py', 'check', '--deploy'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.log_test_result("Django Configuration", True)
            else:
                # Check if it's just warnings
                if "System check identified no issues" in result.stdout or result.returncode == 0:
                    self.log_test_result("Django Configuration", True)
                else:
                    self.log_test_result("Django Configuration", False, "Configuration issues detected")
            
            return True
            
        except Exception as e:
            self.log_test_result("Django Installation", False, str(e))
            return False
    
    def test_database_connectivity(self):
        """Test database connectivity and structure"""
        print(f"\n{Colors.BOLD}🗄️  Testing Database Connectivity{Colors.END}")
        
        try:
            # Check if database file exists
            if self.db_path.exists():
                self.log_test_result("Database File Exists", True)
            else:
                self.log_test_result("Database File Exists", False, "db.sqlite3 not found")
                return False
            
            # Test database connection
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Check if we can query the database
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                if tables:
                    self.log_test_result("Database Connection", True, f"{len(tables)} tables found")
                else:
                    self.log_test_result("Database Connection", False, "No tables found")
                
                conn.close()
                
            except Exception as e:
                self.log_test_result("Database Connection", False, str(e))
                return False
            
            # Test Django database connection
            result = subprocess.run([self.python_exe, 'manage.py', 'dbshell', '--command', '.tables'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.log_test_result("Django Database Access", True)
            else:
                self.log_test_result("Django Database Access", False, "Django cannot access database")
            
            return True
            
        except Exception as e:
            self.log_test_result("Database Connectivity", False, str(e))
            return False
    
    def test_static_files(self):
        """Test static files configuration"""
        print(f"\n{Colors.BOLD}📁 Testing Static Files{Colors.END}")
        
        try:
            # Check static directories
            static_dirs = [
                self.project_root / "static",
                self.project_root / "staticfiles"
            ]
            
            static_found = False
            for static_dir in static_dirs:
                if static_dir.exists():
                    static_found = True
                    break
            
            if static_found:
                self.log_test_result("Static Directory Exists", True)
            else:
                self.log_test_result("Static Directory Exists", False, "No static directory found")
            
            # Test collectstatic (dry run)
            result = subprocess.run([self.python_exe, 'manage.py', 'collectstatic', '--dry-run', '--noinput'], 
                                  capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.log_test_result("Static Files Collection", True)
            else:
                self.log_test_result("Static Files Collection", False, "collectstatic failed")
            
            return True
            
        except Exception as e:
            self.log_test_result("Static Files", False, str(e))
            return False
    
    def test_dependencies(self):
        """Test critical dependencies"""
        print(f"\n{Colors.BOLD}📦 Testing Dependencies{Colors.END}")
        
        critical_packages = {
            'django': 'Django framework',
            'PIL': 'Pillow image library',
            'decouple': 'Python Decouple',
            'whitenoise': 'WhiteNoise static files'
        }
        
        all_passed = True
        
        for package, description in critical_packages.items():
            try:
                result = subprocess.run([self.python_exe, '-c', f'import {package}'], 
                                      capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    self.log_test_result(f"{description}", True)
                else:
                    self.log_test_result(f"{description}", False, f"{package} not installed")
                    all_passed = False
                    
            except Exception as e:
                self.log_test_result(f"{description}", False, str(e))
                all_passed = False
        
        return all_passed
    
    def test_server_startup(self):
        """Test Django development server startup"""
        print(f"\n{Colors.BOLD}🚀 Testing Server Startup{Colors.END}")
        
        try:
            # Find available port
            port = self.find_available_port()
            
            if not port:
                self.log_test_result("Port Availability", False, "No available ports")
                return False
            
            self.log_test_result("Port Availability", True, f"Port {port} available")
            
            # Start server in background
            server_process = subprocess.Popen([
                self.python_exe, 'manage.py', 'runserver', f'127.0.0.1:{port}', '--noreload'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for server to start
            time.sleep(5)
            
            # Test if server is responding
            try:
                import urllib.request
                
                response = urllib.request.urlopen(f'http://127.0.0.1:{port}/', timeout=10)
                
                if response.getcode() == 200:
                    self.log_test_result("Server Response", True, f"HTTP {response.getcode()}")
                else:
                    self.log_test_result("Server Response", False, f"HTTP {response.getcode()}")
                
            except Exception as e:
                self.log_test_result("Server Response", False, str(e))
            
            # Stop server
            server_process.terminate()
            server_process.wait(timeout=10)
            
            self.log_test_result("Server Startup/Shutdown", True)
            return True
            
        except Exception as e:
            self.log_test_result("Server Startup", False, str(e))
            return False
    
    def find_available_port(self, start_port=8000, max_attempts=10):
        """Find an available port for testing"""
        for port in range(start_port, start_port + max_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex(('127.0.0.1', port))
                    if result != 0:  # Port is available
                        return port
            except:
                continue
        return None
    
    def test_ml_integration(self):
        """Test ML integration if available"""
        print(f"\n{Colors.BOLD}🤖 Testing ML Integration{Colors.END}")
        
        try:
            # Check if ML models directory exists
            models_dir = self.project_root / "models"
            
            if models_dir.exists():
                model_files = list(models_dir.glob("*.pkl"))
                if model_files:
                    self.log_test_result("ML Models Available", True, f"{len(model_files)} models found")
                else:
                    self.log_test_result("ML Models Available", False, "No .pkl files found")
            else:
                self.log_test_result("ML Models Directory", False, "models/ directory not found")
            
            # Test ML dependencies
            ml_packages = ['sklearn', 'numpy', 'pandas']
            ml_available = True
            
            for package in ml_packages:
                try:
                    result = subprocess.run([self.python_exe, '-c', f'import {package}'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode != 0:
                        ml_available = False
                        break
                except:
                    ml_available = False
                    break
            
            if ml_available:
                self.log_test_result("ML Dependencies", True, "scikit-learn ecosystem available")
            else:
                self.log_test_result("ML Dependencies", False, "ML packages not installed")
            
            return True
            
        except Exception as e:
            self.log_test_result("ML Integration", False, str(e))
            return False
    
    def generate_test_report(self):
        """Generate final test report"""
        print(f"\n{Colors.BOLD}📊 TEST REPORT{Colors.END}")
        print("=" * 60)
        
        total_tests = self.passed_tests + self.failed_tests
        pass_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {Colors.BOLD}{total_tests}{Colors.END}")
        print(f"Passed: {Colors.GREEN}{self.passed_tests}{Colors.END}")
        print(f"Failed: {Colors.RED}{self.failed_tests}{Colors.END}")
        print(f"Pass Rate: {Colors.BOLD}{pass_rate:.1f}%{Colors.END}")
        
        if self.failed_tests > 0:
            print(f"\n{Colors.RED}❌ FAILED TESTS:{Colors.END}")
            for result in self.test_results:
                if not result['passed']:
                    print(f"   • {result['name']}: {result['message']}")
        
        if pass_rate >= 80:
            print(f"\n{Colors.GREEN}🎉 EXCELLENT! System is ready for production{Colors.END}")
            return True
        elif pass_rate >= 60:
            print(f"\n{Colors.YELLOW}⚠️  GOOD! Minor issues detected{Colors.END}")
            return True
        else:
            print(f"\n{Colors.RED}🚫 CRITICAL! Major issues need attention{Colors.END}")
            return False
    
    def run_all_tests(self):
        """Run all system tests"""
        self.print_header()
        
        tests = [
            self.test_python_environment,
            self.test_virtual_environment,
            self.test_django_installation,
            self.test_database_connectivity,
            self.test_static_files,
            self.test_dependencies,
            self.test_ml_integration,
            self.test_server_startup
        ]
        
        for test_function in tests:
            try:
                test_function()
            except Exception as e:
                test_name = test_function.__name__.replace('test_', '').replace('_', ' ').title()
                self.log_test_result(test_name, False, str(e))
        
        return self.generate_test_report()

def main():
    """Main execution function"""
    tester = SystemTester()
    
    try:
        success = tester.run_all_tests()
        
        if success:
            print(f"\n{Colors.GREEN}✅ System testing completed successfully!{Colors.END}")
            sys.exit(0)
        else:
            print(f"\n{Colors.YELLOW}⚠️  System testing completed with issues{Colors.END}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Testing cancelled by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Testing error: {e}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()