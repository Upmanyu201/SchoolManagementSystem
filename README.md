# 🎓 School Management System

A full-featured web-based School Management System built to simplify and digitize core academic and administrative tasks. This project provides tools for managing students, teachers, fees, reports, attendance, transport, and more — with role-based access and modular design.

---

## 🚀 Features

- **Student Management**
  - Enrollment, profile management, and document storage
  - Class & section assignments
  - Promotion tracking

- **Fee Management**
  - Fee groups, types, and payments
  - Payment tracking and receipts
  - Customizable fee structures

- **Attendance**
  - Daily attendance tracking for students and teachers
  - Integrated with class assignments

- **Examinations & Results**
  - Exam schedules and result entries
  - Subject and class-level assessments

- **Transport Module**
  - Assign transport routes and stoppages
  - Link students to specific routes

- **Teacher & Staff Management**
  - Teacher assignments and roles
  - Upload photos and profiles

- **Reports**
  - Generate and download academic and financial reports
  - Custom filters for quick analysis

- **Admin Dashboard**
  - Real-time statistics and charts
  - Quick links to major modules

---

## 🧑‍💻 Tech Stack

- **Backend:** Python (Django)
- **Frontend:** HTML, CSS, Tailwind CSS
- **Database:** SQLite / PostgreSQL (optional)
- **Environment:** Virtualenv, XAMPP for local server use
- **Other Tools:** Vite, Pre-commit Hooks

---

## ⚙️ Setup Instructions

```bash
git clone https://github.com/W3UR/School-Management-System.git
cd School-Management-System

# Set up virtual environment
python -m venv venv
.\venv\Scripts\activate.bat  # Windows

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Run server
python manage.py runserver

=======
# School-Management-System
>>>>>>> 4608a9bb052dc099bdfd822857d732b7fcc80a29

# Setup Instructions
git clone https://github.com/W3UR/School-Management-System.git
cd School-Management-System

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate.bat  # On Windows

# Install Python dependencies
pip install -r requirements.txt

# Install System-Level Dependencies (Required for WeasyPrint on Windows)
''' Dependency	              Purpose	              Download Link
 GTK3 Runtime       Required for WeasyPrint      https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
Microsoft Visual  C++ 2015+ Redistributable  
                    Required for Cairo libraries    https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist/'''


# Apply Migrations
python manage.py migrate


# Generate Local HTTPS Certificate (Only once)
"""# Step 1: Generate a local Certificate Authority
openssl genrsa -out localCA.key 2048
openssl req -x509 -new -nodes -key localCA.key -sha256 -days 1825 -out localCA.pem -subj "/C=IN/ST=Local/L=Dev/O=LocalDevCA/OU=DevCA/CN=LocalDevCA"

# Step 2: Create key and CSR for the dev server
openssl genrsa -out devserver.key 2048
openssl req -new -key devserver.key -out devserver.csr -subj "/C=IN/ST=Local/L=Dev/O=DevServer/OU=LocalDev/CN=127.0.0.1"

# Step 3: Create devserver.ext (Subject Alt Name config)
echo authorityKeyIdentifier=keyid,issuer>devserver.ext
echo basicConstraints=CA:FALSE>>devserver.ext
echo keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment>>devserver.ext
echo subjectAltName = @alt_names>>devserver.ext
echo.>>devserver.ext
echo [alt_names]>>devserver.ext
echo IP.1 = 127.0.0.1>>devserver.ext
echo DNS.1 = localhost>>devserver.ext

# Step 4: Sign the certificate
openssl x509 -req -in devserver.csr -CA localCA.pem -CAkey localCA.key -CAcreateserial -out devserver.crt -days 825 -sha256 -extfile devserver.ext
"""