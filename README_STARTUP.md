# 🚀 School Management System - Startup Guide

## Quick Start Options

### 1. Smart Launcher (Recommended) 🎯

**Windows:**
```bash
# Double-click or run in terminal
start_server.bat
```

**Linux/Mac:**
```bash
# Make executable and run
chmod +x start_server.sh
./start_server.sh
```

**Python (All platforms):**
```bash
python start_server.py
```

### 2. Quick Development Start 🔧
```bash
python dev_tools/scripts/quick_start.py
```

### 3. Manual Start 📝
```bash
# Activate virtual environment
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

python manage.py runserver 0.0.0.0:8000
```

---

## 🌟 Smart Launcher Features

### ✨ Auto Network Detection
- Automatically detects all network interfaces
- Shows Ethernet, WiFi, Mobile Hotspot connections
- Tests port availability before starting

### 📱 Mobile Hotspot Support
- Detects mobile hotspot connections (192.168.43.x, 192.168.137.x)
- Allows access from connected mobile devices
- Shows mobile-friendly access URLs

### 🌐 Browser Auto-Launch
- Automatically opens default browser after server starts
- Waits for server to be fully ready
- Handles browser launch errors gracefully

### 📊 Real-time Logs
- Color-coded log output (errors in red, warnings in yellow)
- Real-time server status monitoring
- Structured log display

### 🔒 SSL Support
- Auto-detects SSL certificates in `certs/` folder
- Prompts for HTTPS preference
- Supports both HTTP and HTTPS modes

### 🛑 Graceful Shutdown
- Handles Ctrl+C gracefully
- Properly terminates Django server
- Cleans up background processes

---

## 📋 Network Interface Examples

```
🌐 Available Network Interfaces:
============================================================
0. 🏠 Localhost Only (127.0.0.1)
1. 🔌 Ethernet - 192.168.1.100 (Ethernet) 🟢
2. 📶 WiFi - 192.168.0.50 (Wi-Fi) 🟢
3. 📱 Mobile Hotspot - 192.168.43.1 (Mobile Hotspot) 🟢
============================================================

🎯 Select network interface (0-3): 2
```

## 🔗 Generated URLs

After selection, you'll see:

```
🚀 Server Starting...
============================================================
📍 Server Details:
   🌐 Protocol: HTTP
   📡 IP Address: 192.168.0.50
   🔌 Port: 8000
   🕐 Started: 2025-01-15 10:30:45

🔗 Access URLs:
   1. http://192.168.0.50:8000/
   2. http://localhost:8000/
   3. http://127.0.0.1:8000/

📱 Mobile/Other Device Access:
   📲 Use: http://192.168.0.50:8000/
============================================================
```

## 🛠️ Troubleshooting

### Port Already in Use
```
❌ Port 8000 is already in use
💡 Kill existing process: netstat -ano | findstr :8000
```

### Network Interface Not Detected
```
❌ No network interfaces found!
💡 Make sure you're connected to a network
```

### SSL Certificates Missing
```
⚠️ No SSL certificates found - using HTTP
💡 Generate certificates: openssl req -x509 -newkey rsa:4096 -nodes -out certs/cert.pem -keyout certs/key.pem -days 365
```

### Virtual Environment Issues
```
❌ Virtual environment not found!
💡 Create: python -m venv venv
💡 Activate: venv\Scripts\activate (Windows) or source venv/bin/activate (Linux/Mac)
```

## 📦 Dependencies

The startup script automatically installs required dependencies:
- `psutil` - For network interface detection
- Standard Python libraries (socket, subprocess, threading, etc.)

## 🎨 Customization

### Change Default Port
Edit `start_server.py`:
```python
self.port = 8080  # Change from 8000 to 8080
```

### Add Custom URLs
Edit the `generate_server_urls()` method:
```python
# Add custom module URLs
modules = ['dashboard', 'students', 'teachers', 'fees']
for module in modules:
    self.server_urls.append(f"{protocol}://{self.selected_ip}:{self.port}/{module}/")
```

### Modify Colors
Edit the `Colors` class:
```python
class Colors:
    GREEN = '\033[92m'    # Success messages
    RED = '\033[91m'      # Error messages
    YELLOW = '\033[93m'   # Warning messages
    BLUE = '\033[94m'     # Info messages
```

---

## 🚀 Usage Examples

### Development (Localhost Only)
```bash
python start_server.py
# Select option 0 for localhost
# Access: http://127.0.0.1:8000/
```

### Team Development (Network Access)
```bash
python start_server.py
# Select your network interface (WiFi/Ethernet)
# Share IP with team members
# Access: http://192.168.x.x:8000/
```

### Mobile Testing
```bash
python start_server.py
# Select mobile hotspot interface
# Connect mobile device to same hotspot
# Access: http://192.168.43.1:8000/
```

### Production-like (HTTPS)
```bash
# First generate SSL certificates
openssl req -x509 -newkey rsa:4096 -nodes -out certs/cert.pem -keyout certs/key.pem -days 365

python start_server.py
# Select network interface
# Choose 'y' for HTTPS
# Access: https://192.168.x.x:9000/
```

---

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Ensure all dependencies are installed
3. Verify you're in the correct directory (contains `manage.py`)
4. Check firewall settings for network access

Happy coding! 🎓✨