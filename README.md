# 🎓 Student Management and Registration System

A desktop application built with Python and Tkinter for managing student registration, authentication, and profile data. Designed for schools and institutions seeking a simple, secure, and user-friendly solution.

---

## 🚀 Features

- 🔐 **Student & Admin Login**
- 📝 **Student Registration with Photo Upload**
- 🧾 **Student Card Generation & Printing**
- 📧 **Email-Based Password Recovery**
- 🗂️ **SQLite Database Integration**
- 🖼️ **Custom Icons and Image Assets**
- 🖨️ **Print and Save Student Cards**
- 🧠 **Responsive GUI with Role-Based Navigation**

---

## 🛠️ Installation

### 🔧 Requirements

- Python 3.10+
- Required libraries:
  - `tkinter`
  - `Pillow`
  - `sqlite3`
  - `win32api`
  - `smtplib`
  - `email`
  - `threading`

Install dependencies via pip:

```bash
pip install pillow pywin32
```

To compile the app into a standalone .exe:
```bash
pyinstaller --onefile --windowed --icon=images/photo.ico --add-data "images;images" app.py
```
Ensure all image assets and fonts are inside the images/ folder.


📥 Installer Setup (Optional)
Use Inno Setup to create a branded installer:
Installs to Program Files\StudentManagement
Adds desktop and Start Menu shortcuts
Uses your custom icon
See ```bash installer_script.iss``` for configuration.

📁 Project Structure
Student_Management_System/
```bash
├── app.py
├── images/
│   ├── photo.ico
│   ├── login_student_img.png
│   ├── admin_img.png
│   ├── student_card_frame.png
│   └── ...
├── students_account_db
├── my_email.py
├── README.md
```


📧 Email Configuration
Edit my_email.py to include your sender credentials:
```bash
email_address = "your_email@gmail.com"
password = "your_app_password"
```

🧠 Notes
All external assets are loaded using resource_path() for PyInstaller compatibility.
Student images are stored as BLOBs in the SQLite database.
Printing uses win32api.ShellExecute()—Windows only.

📜 License
This project is licensed for educational and institutional use. Contact the author for commercial deployment.

👤 Author
Tabong Full-stack developer | App designer | Educator 📍 Kumba, Cameroon
email: tabongphilip@gmail.com
Tel: +(237) 675552594
website: philipstek.com


