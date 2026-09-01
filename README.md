# 🎓 Online Internship Portal Management System

A full-stack web application built with **Python Flask**, **MySQL**, and **Bootstrap 5**.

---

## 📁 Project Structure

```
internship-portal/
│── app.py                  # Main Flask application (all routes & logic)
│── setup_admin.py          # One-time script to set demo account passwords
│── database.sql            # Full MySQL schema + seed data
│── requirements.txt        # Python dependencies
│── static/
│   └── style.css           # Custom CSS (Syne + DM Sans fonts, CSS vars)
└── templates/
    ├── base.html           # Master layout (navbar, flash messages, footer)
    ├── index.html          # Landing page
    ├── login.html          # Login form
    ├── register.html       # Dynamic registration form (student/company)
    ├── dashboard.html      # Role-based dashboard (student/company/admin)
    ├── internships.html    # Browse & search listings
    ├── apply.html          # Application form
    ├── post_internship.html# Company posts a listing
    ├── view_applications.html # Company manages applicants
    ├── admin_users.html    # Admin manages users
    └── admin_internships.html # Admin manages listings
```

---

## ⚙️ Setup Instructions

### Step 1 — Prerequisites

Make sure you have the following installed:
- **Python 3.8+** — https://www.python.org/downloads/
- **MySQL 8.0+** — https://dev.mysql.com/downloads/installer/
- **pip** (comes with Python)

---

### Step 2 — MySQL Setup

1. Open MySQL Workbench or your terminal MySQL client.
2. Log in:
   ```bash
   mysql -u root -p
   ```
3. Import the database schema:
   ```bash
   mysql -u root -p < database.sql
   ```
   Or paste the contents of `database.sql` into MySQL Workbench and execute.

4. Verify the database was created:
   ```sql
   USE internship_portal;
   SHOW TABLES;
   ```
   You should see: `users`, `students`, `companies`, `internships`, `applications`.

---

### Step 3 — Python Setup

1. Navigate into the project folder:
   ```bash
   cd internship-portal
   ```

2. (Recommended) Create a virtual environment:
   ```bash
   python -m venv venv

   # Windows:
   venv\Scripts\activate

   # macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

### Step 4 — Configure Database Password

Open `app.py` and update line ~20 with your MySQL credentials:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'YOUR_MYSQL_PASSWORD',   # <-- Change this
    'database': 'internship_portal',
}
```

Do the same in `setup_admin.py`.

---

### Step 5 — Initialize Demo Account Passwords

Run the setup script **once** to hash and store demo passwords properly:

```bash
python setup_admin.py
```

You'll see:
```
✅ Admin password set for: admin@portal.com (password: admin123)
✅ Company password set for: techcorp@example.com (password: company123)
✅ Setup complete!
```

---

### Step 6 — Run the Application

```bash
python app.py
```

Open your browser and go to:
```
http://localhost:5000
```

---

## 🔑 Demo Accounts

| Role    | Email                   | Password     |
|---------|-------------------------|--------------|
| Admin   | admin@portal.com        | admin123     |
| Company | techcorp@example.com    | company123   |

To create a **student** account, click **Register** → select **Student**.

---

## 🧩 Features

### 👨‍🎓 Student
- Register and log in
- Browse all active internships (with search + location filter)
- Apply with a cover letter
- View application statuses (Pending / Accepted / Rejected) on dashboard
- Duplicate applications are prevented

### 🏢 Company
- Register and log in
- Post new internship listings (title, description, location, duration, stipend, skills, deadline)
- View all applicants per listing
- Accept or Reject applications
- See applicant count per listing on dashboard

### 🛡️ Admin
- Platform-wide statistics (students, companies, listings, applications)
- View all registered users
- Delete any user account (cascades to profile/applications)
- View all internship listings
- Activate / Deactivate listings

---

## 🔒 Security

- Passwords hashed using `werkzeug.security` (PBKDF2-SHA256)
- Parameterized SQL queries (no SQL injection possible)
- Session-based authentication
- Role-based access control decorators
- Duplicate application prevention via DB UNIQUE constraint
- Admin cannot delete their own account

---

## 🛠️ Tech Stack

| Layer     | Technology                        |
|-----------|-----------------------------------|
| Backend   | Python 3 + Flask 3.0              |
| Database  | MySQL 8 + mysql-connector-python  |
| Frontend  | HTML5 + Bootstrap 5 + Jinja2      |
| Styling   | Custom CSS (CSS Variables)        |
| Fonts     | Syne (display) + DM Sans (body)   |
| Icons     | Bootstrap Icons                   |
"# demo" 
