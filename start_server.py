#!/usr/bin/env python3
"""
🎓 School Management System - Smart Startup Script
Auto-detects network, launches server, and opens browser
"""

import os
import sys
import socket
import subprocess
import threading
import time
import webbrowser
import signal
import psutil
from datetime import datetime

class Colors:
    """ANSI color codes for beautiful terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class SchoolServerManager:
    def __init__(self):
        self.server_process = None
        self.server_urls = []
        self.selected_ip = None
        self.port = 8000
        self.ssl_port = 9000
        self.use_ssl = False
        
    def print_banner(self):
        """Display beautiful startup banner"""
        banner = f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║  {Colors.BOLD}🎓 SCHOOL MANAGEMENT SYSTEM - SMART LAUNCHER{Colors.END}{Colors.CYAN}              ║
║                                                              ║
║  {Colors.GREEN}✨ Auto Network Detection  📱 Mobile Hotspot Support{Colors.END}{Colors.CYAN}      ║
║  {Colors.GREEN}🌐 Browser Auto-Launch     📊 Real-time Logs{Colors.END}{Colors.CYAN}             ║
║  {Colors.GREEN}🔒 SSL Support             🔑 License Management{Colors.END}{Colors.CYAN}          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{Colors.END}
"""
        print(banner)
        
        # Check demo status
        self.check_demo_status()
        
    def get_network_interfaces(self):
        """Detect all available network interfaces"""
        interfaces = []
        
        try:
            for interface_name, interface_addresses in psutil.net_if_addrs().items():
                for address in interface_addresses:
                    if address.family == socket.AF_INET:  # IPv4
                        ip = address.address
                        if ip != '127.0.0.1' and not ip.startswith('169.254'):
                            interface_type = self.detect_interface_type(interface_name, ip)
                            interfaces.append({
                                'name': interface_name,
                                'ip': ip,
                                'type': interface_type,
                                'netmask': address.netmask
                            })
        except Exception as e:
            print(f"{Colors.RED}❌ Error detecting network interfaces: {e}{Colors.END}")
            
        return interfaces
    
    def detect_interface_type(self, interface_name, ip):
        """Detect the type of network interface"""
        name_lower = interface_name.lower()
        
        if 'wi-fi' in name_lower or 'wireless' in name_lower or 'wlan' in name_lower:
            if ip.startswith('192.168.43.') or ip.startswith('192.168.137.'):
                return '📱 Mobile Hotspot'
            return '📶 WiFi'
        elif 'ethernet' in name_lower or 'local' in name_lower or 'eth' in name_lower:
            return '🔌 Ethernet'
        elif 'bluetooth' in name_lower:
            return '🔵 Bluetooth'
        else:
            return '🌐 Network'
    
    def display_network_options(self, interfaces):
        """Display available network interfaces for selection"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}🌐 Available Network Interfaces:{Colors.END}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")
        
        if not interfaces:
            print(f"{Colors.RED}❌ No network interfaces found!{Colors.END}")
            print(f"{Colors.YELLOW}💡 Make sure you're connected to a network{Colors.END}")
            return None
            
        # Always add localhost option
        print(f"{Colors.GREEN}0.{Colors.END} 🏠 Localhost Only (127.0.0.1)")
        
        for i, interface in enumerate(interfaces, 1):
            status_icon = "🟢" if self.test_port_availability(interface['ip']) else "🔴"
            print(f"{Colors.GREEN}{i}.{Colors.END} {interface['type']} - {Colors.BOLD}{interface['ip']}{Colors.END} ({interface['name']}) {status_icon}")
        
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")
        
        while True:
            try:
                choice = input(f"\n{Colors.YELLOW}🎯 Select network interface (0-{len(interfaces)}): {Colors.END}")
                choice = int(choice)
                
                if choice == 0:
                    return '127.0.0.1'
                elif 1 <= choice <= len(interfaces):
                    return interfaces[choice - 1]['ip']
                else:
                    print(f"{Colors.RED}❌ Invalid choice! Please select 0-{len(interfaces)}{Colors.END}")
            except ValueError:
                print(f"{Colors.RED}❌ Please enter a valid number!{Colors.END}")
            except KeyboardInterrupt:
                print(f"\n{Colors.RED}❌ Startup cancelled by user{Colors.END}")
                sys.exit(1)
    
    def test_port_availability(self, ip):
        """Test if the port is available on the given IP"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((ip, self.port))
                return result != 0
        except:
            return False
    
    def check_ssl_certificates(self):
        """Check if SSL certificates exist"""
        cert_paths = ['certs/cert.pem', 'certs/key.pem', 'certs/devserver.crt', 'certs/devserver.key']
        return any(os.path.exists(cert_path) for cert_path in cert_paths)
    
    def setup_ssl_option(self):
        """Ask user about SSL preference"""
        if self.check_ssl_certificates():
            print(f"\n{Colors.GREEN}🔒 SSL certificates detected!{Colors.END}")
            while True:
                choice = input(f"{Colors.YELLOW}🔐 Use HTTPS? (y/n): {Colors.END}").lower().strip()
                if choice in ['y', 'yes']:
                    self.use_ssl = True
                    self.port = self.ssl_port
                    break
                elif choice in ['n', 'no']:
                    break
                else:
                    print(f"{Colors.RED}❌ Please enter 'y' or 'n'{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠️  No SSL certificates found - using HTTP{Colors.END}")
    
    def generate_server_urls(self):
        """Generate all possible server URLs"""
        protocol = 'https' if self.use_ssl else 'http'
        self.server_urls = [
            f"{protocol}://{self.selected_ip}:{self.port}/",
            f"{protocol}://localhost:{self.port}/",
            f"{protocol}://127.0.0.1:{self.port}/"
        ]
    
    def display_server_info(self):
        """Display server information and URLs"""
        protocol = 'https' if self.use_ssl else 'http'
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}🚀 Server Starting...{Colors.END}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}📍 Server Details:{Colors.END}")
        print(f"   🌐 Protocol: {Colors.BOLD}{protocol.upper()}{Colors.END}")
        print(f"   📡 IP Address: {Colors.BOLD}{self.selected_ip}{Colors.END}")
        print(f"   🔌 Port: {Colors.BOLD}{self.port}{Colors.END}")
        print(f"   🕐 Started: {Colors.BOLD}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
        
        print(f"\n{Colors.BOLD}🔗 Access URLs:{Colors.END}")
        for i, url in enumerate(self.server_urls, 1):
            print(f"   {i}. {Colors.BLUE}{Colors.UNDERLINE}{url}{Colors.END}")
        
        if self.selected_ip not in ['127.0.0.1', 'localhost']:
            print(f"\n{Colors.BOLD}📱 Mobile/Other Device Access:{Colors.END}")
            print(f"   📲 Use: {Colors.BOLD}{Colors.GREEN}{protocol}://{self.selected_ip}:{self.port}/{Colors.END}")
        
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")
    
    def start_django_server(self):
        """Start the Django development server"""
        try:
            cmd = [sys.executable, 'manage.py', 'runserver', f'{self.selected_ip}:{self.port}']
            
            if self.use_ssl:
                cmd.extend(['--cert-file', 'certs/cert.pem', '--key-file', 'certs/key.pem'])
            
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            return True
            
        except Exception as e:
            print(f"{Colors.RED}❌ Failed to start Django server: {e}{Colors.END}")
            return False
    
    def start_log_monitor(self):
        """Start log monitoring in a separate thread"""
        def monitor_logs():
            if self.server_process:
                print(f"\n{Colors.BOLD}{Colors.YELLOW}📊 Server Logs:{Colors.END}")
                print(f"{Colors.CYAN}{'-'*60}{Colors.END}")
                
                try:
                    for line in iter(self.server_process.stdout.readline, ''):
                        if line:
                            if 'ERROR' in line or 'error' in line:
                                print(f"{Colors.RED}{line.strip()}{Colors.END}")
                            elif 'WARNING' in line or 'warning' in line:
                                print(f"{Colors.YELLOW}{line.strip()}{Colors.END}")
                            elif 'Starting development server' in line:
                                print(f"{Colors.GREEN}{line.strip()}{Colors.END}")
                            else:
                                print(f"{Colors.CYAN}{line.strip()}{Colors.END}")
                except:
                    pass
        
        log_thread = threading.Thread(target=monitor_logs, daemon=True)
        log_thread.start()
    
    def open_browser(self):
        """Open default browser after server starts"""
        def delayed_browser_open():
            time.sleep(3)
            try:
                main_url = self.server_urls[0]
                print(f"\n{Colors.GREEN}🌐 Opening browser: {main_url}{Colors.END}")
                webbrowser.open(main_url)
            except Exception as e:
                print(f"{Colors.YELLOW}⚠️  Could not auto-open browser: {e}{Colors.END}")
        
        browser_thread = threading.Thread(target=delayed_browser_open, daemon=True)
        browser_thread.start()
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            print(f"\n{Colors.YELLOW}🛑 Shutdown signal received...{Colors.END}")
            self.cleanup()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def cleanup(self):
        """Clean up processes on exit"""
        print(f"{Colors.YELLOW}🧹 Cleaning up...{Colors.END}")
        
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
                print(f"{Colors.GREEN}✅ Django server stopped{Colors.END}")
            except:
                try:
                    self.server_process.kill()
                    print(f"{Colors.YELLOW}⚠️  Django server force-killed{Colors.END}")
                except:
                    pass
        
        print(f"{Colors.GREEN}👋 School Management System stopped successfully!{Colors.END}")
    
    def check_demo_status(self):
        """Check demo/license status before starting server"""
        try:
            # Import Django and setup
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
            import django
            django.setup()
            
            from demo.services import LicenseService
            
            status = LicenseService.get_demo_status()
            
            if status.is_licensed:
                print(f"{Colors.GREEN}✅ Licensed Version - Full Access{Colors.END}")
                print(f"{Colors.CYAN}   Activated: {status.activated_at.strftime('%Y-%m-%d') if status.activated_at else 'N/A'}{Colors.END}")
                return True
            elif status.is_active:
                print(f"{Colors.YELLOW}⏰ Demo Version - {status.days_remaining} days remaining{Colors.END}")
                if status.days_remaining <= 2:
                    print(f"{Colors.RED}⚠️  Demo expires soon!{Colors.END}")
                return True
            else:
                print(f"{Colors.RED}❌ Demo Expired - Activation Required{Colors.END}")
                print(f"{Colors.YELLOW}   Visit: /demo/expired/ to activate{Colors.END}")
                return True  # Allow server to start for activation
                
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️  Could not check license status: {e}{Colors.END}")
            
        return True
    

    
    def run(self):
        """Main execution method"""
        try:
            self.print_banner()
            
            # Check demo status first
            self.check_demo_status()
            
            print(f"{Colors.YELLOW}🔍 Detecting network interfaces...{Colors.END}")
            interfaces = self.get_network_interfaces()
            
            self.selected_ip = self.display_network_options(interfaces)
            if not self.selected_ip:
                return
            
            self.setup_ssl_option()
            self.generate_server_urls()
            self.display_server_info()
            self.show_license_reminder()
            self.setup_signal_handlers()
            
            if not self.start_django_server():
                return
            
            self.start_log_monitor()
            self.open_browser()
            
            try:
                while True:
                    time.sleep(1)
                    if self.server_process and self.server_process.poll() is not None:
                        print(f"{Colors.RED}❌ Django server stopped unexpectedly{Colors.END}")
                        break
            except KeyboardInterrupt:
                pass
            
        except Exception as e:
            print(f"{Colors.RED}❌ Unexpected error: {e}{Colors.END}")
        finally:
            self.cleanup()
    
    def show_license_reminder(self):
        """Show license reminder if in demo mode"""
        try:
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
            import django
            django.setup()
            
            from demo.services import LicenseService
            status = LicenseService.get_demo_status()
            
            if not status.is_licensed:
                if status.is_active:
                    print(f"\n{Colors.BOLD}{Colors.YELLOW}💡 Demo Mode:{Colors.END}")
                    print(f"{Colors.YELLOW}   • {status.days_remaining} days remaining{Colors.END}")
                    print(f"{Colors.YELLOW}   • Activate at: /demo/status/{Colors.END}")
                else:
                    print(f"\n{Colors.BOLD}{Colors.RED}🔑 Activation Required:{Colors.END}")
                    print(f"{Colors.RED}   • Visit: /demo/expired/ to activate{Colors.END}")
                
        except:
            pass

if __name__ == "__main__":
    if not os.path.exists('manage.py'):
        print(f"{Colors.RED}❌ manage.py not found! Please run from Django project root.{Colors.END}")
        sys.exit(1)
    
    if sys.version_info < (3, 8):
        print(f"{Colors.RED}❌ Python 3.8+ required. Current: {sys.version}{Colors.END}")
        sys.exit(1)
    
    server_manager = SchoolServerManager()
    server_manager.run()