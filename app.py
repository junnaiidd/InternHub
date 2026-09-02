# ============================================================
# Online Internship Portal Management System
# app.py - Main Flask Application
# ============================================================

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from threading import Thread
import mysql.connector
from functools import wraps
import os
from urllib.parse import urlparse
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'internship_portal_secret_2024')
serializer = URLSafeTimedSerializer(app.secret_key)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads', 'resumes')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB limit

# ============================================================
# EMAIL CONFIGURATION
# ============================================================
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = 'internhub.admin@gmail.com'
app.config['MAIL_PASSWORD'] = 'gxwsmgnvaabbjmss'
app.config['MAIL_DEFAULT_SENDER'] = app.config['MAIL_USERNAME']

mail = Mail(app)

def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Email failed to send: {e}")

def send_email(subject, recipient, html_body):
    msg = Message(subject, recipients=[recipient])
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()

# ============================================================
# DATABASE CONFIGURATION
# Update these credentials to match your MySQL setup
# ============================================================
DB_CONFIG = {
    'host': os.environ.get('DB_HOST'),
    'port': int(os.environ.get('DB_PORT', 20870)),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'database': os.environ.get('DB_NAME'),
    'ssl_disabled': False,
    'ssl_verify_cert': False
}

def get_db():
    """Create and return a MySQL database connection."""
    conn = mysql.connector.connect(**DB_CONFIG)
    return conn


def ensure_profile_schema():
    """Add missing profile columns for older existing databases without breaking current users."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        db_name = DB_CONFIG['database']
        student_columns = ['bio', 'cgpa', 'linkedin_url', 'github_profile_url']
        company_columns = ['bio', 'contact_email']

        def add_missing_columns(table_name, columns):
            for column_name in columns:
                cursor.execute(
                    """
                    SELECT COUNT(*) AS cnt
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s
                    """,
                    (db_name, table_name, column_name),
                )
                if cursor.fetchone()['cnt'] == 0:
                    if table_name == 'students':
                        if column_name == 'bio':
                            cursor.execute("ALTER TABLE students ADD COLUMN bio TEXT NULL")
                        elif column_name == 'cgpa':
                            cursor.execute("ALTER TABLE students ADD COLUMN cgpa VARCHAR(10) NULL")
                        elif column_name == 'linkedin_url':
                            cursor.execute("ALTER TABLE students ADD COLUMN linkedin_url VARCHAR(255) NULL")
                        elif column_name == 'github_profile_url':
                            cursor.execute("ALTER TABLE students ADD COLUMN github_profile_url VARCHAR(255) NULL")
                    elif table_name == 'companies':
                        if column_name == 'bio':
                            cursor.execute("ALTER TABLE companies ADD COLUMN bio TEXT NULL")
                        elif column_name == 'contact_email':
                            cursor.execute("ALTER TABLE companies ADD COLUMN contact_email VARCHAR(120) NULL")

        add_missing_columns('students', student_columns)
        add_missing_columns('companies', company_columns)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


@app.before_request
def ensure_schema_before_request():
    """Keep legacy databases compatible with the current profile schema."""
    ensure_profile_schema()

# ============================================================
# DECORATORS - Role-based access control
# ============================================================
def login_required(f):
    """Decorator: Requires user to be logged in."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def role_required(*roles):
    """Decorator: Restricts route to specific roles."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if session.get('role') not in roles:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated
    return decorator

# ============================================================
# ROUTE: Home Page
# ============================================================
@app.route('/')
def index():
    """Landing page — redirects logged-in users to dashboard."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

# ============================================================
# ROUTE: Login
# ============================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login with email and password."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('login.html')

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        try:
            # Parameterized query — safe from SQL injection
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if user and check_password_hash(user['password_hash'], password):
                # Store session data
                session['user_id'] = user['id']
                session['email'] = user['email']
                session['role'] = user['role']
                flash(f"Welcome back! Logged in as {user['role'].capitalize()}.", 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password.', 'danger')
        finally:
            cursor.close()
            conn.close()

    return render_template('login.html')

# ============================================================
# ROUTE: Register
# ============================================================
@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle student and company registration."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        role = request.form.get('role', '')
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        # --- Validation ---
        if not all([role, email, password, confirm]):
            flash('All fields are required.', 'danger')
            return render_template('register.html')

        if role not in ('student', 'company'):
            flash('Invalid role selected.', 'danger')
            return render_template('register.html')

        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('register.html')

        hashed_pw = generate_password_hash(password)
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        try:
            # Check if email already exists
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                flash('An account with this email already exists.', 'danger')
                return render_template('register.html')

            # Insert into users table
            cursor.execute(
                "INSERT INTO users (email, password_hash, role) VALUES (%s, %s, %s)",
                (email, hashed_pw, role)
            )
            user_id = cursor.lastrowid

            # Insert role-specific profile
            if role == 'student':
                full_name = request.form.get('full_name', '').strip()
                college = request.form.get('college', '').strip()
                degree = request.form.get('degree', '').strip()
                if not full_name:
                    flash('Full name is required.', 'danger')
                    conn.rollback()
                    return render_template('register.html')
                cursor.execute(
                    "INSERT INTO students (user_id, full_name, college, degree) VALUES (%s, %s, %s, %s)",
                    (user_id, full_name, college, degree)
                )
            elif role == 'company':
                company_name = request.form.get('company_name', '').strip()
                industry = request.form.get('industry', '').strip()
                if not company_name:
                    flash('Company name is required.', 'danger')
                    conn.rollback()
                    return render_template('register.html')
                cursor.execute(
                    "INSERT INTO companies (user_id, company_name, industry) VALUES (%s, %s, %s)",
                    (user_id, company_name, industry)
                )

            conn.commit()
            
            # Send professional welcome email
            html_msg = render_template('emails/welcome.html', email=email, role=role)
            send_email("Welcome to InternHub!", email, html_msg)
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            conn.rollback()
            flash(f'Registration failed: {str(e)}', 'danger')
        finally:
            cursor.close()
            conn.close()

    return render_template('register.html')

# ============================================================
# ROUTE: Logout
# ============================================================
@app.route('/logout')
def logout():
    """Clear session and log out the user."""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

# ============================================================
# ROUTE: Dashboard (Role-based)
# ============================================================
@app.route('/dashboard')
@login_required
def dashboard():
    """Display role-specific dashboard with relevant data."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    data = {}

    try:
        role = session['role']
        user_id = session['user_id']

        if role == 'student':
            # Get student profile
            cursor.execute("SELECT * FROM students WHERE user_id = %s", (user_id,))
            student = cursor.fetchone()
            if not student:
                flash('Student profile not found.', 'warning')
                return redirect(url_for('logout'))

            # Get student's applications with internship and company details
            cursor.execute("""
                SELECT a.*,
                       i.title, i.location, i.stipend,
                       c.company_name
                FROM applications a
                JOIN internships i ON a.internship_id = i.id
                JOIN companies c ON i.company_id = c.id
                WHERE a.student_id = %s
                ORDER BY a.applied_at DESC
            """, (student['id'],))
            applications = cursor.fetchall()
            data = {'student': student, 'applications': applications}

        elif role == 'company':
            # Get company profile
            cursor.execute("SELECT * FROM companies WHERE user_id = %s", (user_id,))
            company = cursor.fetchone()
            if not company:
                flash('Company profile not found.', 'warning')
                return redirect(url_for('logout'))

            # Get company's internship listings with applicant count
            cursor.execute("""
                SELECT i.*,
                       COUNT(a.id) AS applicant_count
                FROM internships i
                LEFT JOIN applications a ON i.id = a.internship_id
                WHERE i.company_id = %s
                GROUP BY i.id
                ORDER BY i.posted_at DESC
            """, (company['id'],))
            internships = cursor.fetchall()
            data = {'company': company, 'internships': internships}

        elif role == 'admin':
            # Summary stats for admin
            cursor.execute("SELECT COUNT(*) AS cnt FROM users WHERE role = 'student'")
            data['student_count'] = cursor.fetchone()['cnt']

            cursor.execute("SELECT COUNT(*) AS cnt FROM users WHERE role = 'company'")
            data['company_count'] = cursor.fetchone()['cnt']

            cursor.execute("SELECT COUNT(*) AS cnt FROM internships WHERE is_active = 1")
            data['active_internships'] = cursor.fetchone()['cnt']

            cursor.execute("SELECT COUNT(*) AS cnt FROM applications")
            data['total_applications'] = cursor.fetchone()['cnt']

            # Recent users
            cursor.execute("SELECT id, email, role, created_at FROM users ORDER BY created_at DESC LIMIT 10")
            data['recent_users'] = cursor.fetchall()
            
            # Application status counts for Chart.js
            cursor.execute("SELECT status, COUNT(*) as cnt FROM applications GROUP BY status")
            data['app_status_counts'] = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    return render_template('dashboard.html', **data)

# ============================================================
# ROUTE: Edit Profile
# ============================================================
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Allow students and companies to edit their profiles."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        role = session['role']
        user_id = session['user_id']
        
        if request.method == 'POST':
            if role == 'student':
                full_name = request.form.get('full_name', '').strip()
                phone = request.form.get('phone', '').strip()
                college = request.form.get('college', '').strip()
                degree = request.form.get('degree', '').strip()
                skills = request.form.get('skills', '').strip()
                bio = request.form.get('bio', '').strip()
                cgpa = request.form.get('cgpa', '').strip()
                linkedin_url = request.form.get('linkedin_url', '').strip()
                github_profile_url = request.form.get('github_profile_url', '').strip()

                if github_profile_url:
                    parsed = urlparse(github_profile_url)
                    host = (parsed.netloc or '').lower()
                    path = (parsed.path or '').lower()
                    if parsed.scheme not in ('http', 'https') or not host or ('github.com' not in host and 'github.com' not in path):
                        flash('Please enter a valid GitHub profile URL, such as https://github.com/username.', 'danger')
                        return redirect(url_for('edit_profile'))

                cursor.execute("SELECT resume_link FROM students WHERE user_id = %s", (user_id,))
                current_resume = cursor.fetchone()['resume_link']
                
                resume_file = request.files.get('resume')
                resume_link = current_resume
                
                if resume_file and resume_file.filename:
                    if resume_file.filename.lower().endswith('.pdf'):
                        # Create directory if it doesn't exist
                        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                        filename = secure_filename(f"resume_{user_id}_{resume_file.filename}")
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        resume_file.save(filepath)
                        # Normalize path for web viewing
                        resume_link = filepath.replace('\\', '/')
                    else:
                        flash('Only PDF resumes are allowed.', 'danger')
                        return redirect(url_for('edit_profile'))
                
                cursor.execute("""
                    UPDATE students 
                    SET full_name=%s, phone=%s, college=%s, degree=%s, skills=%s, resume_link=%s, bio=%s, cgpa=%s, linkedin_url=%s, github_profile_url=%s
                    WHERE user_id=%s
                """, (full_name, phone, college, degree, skills, resume_link, bio, cgpa, linkedin_url, github_profile_url, user_id))
                
            elif role == 'company':
                company_name = request.form.get('company_name', '').strip()
                industry = request.form.get('industry', '').strip()
                website = request.form.get('website', '').strip()
                bio = request.form.get('bio', '').strip()
                location = request.form.get('location', '').strip()
                contact_email = request.form.get('contact_email', '').strip()
                
                cursor.execute("""
                    UPDATE companies 
                    SET company_name=%s, industry=%s, website=%s, bio=%s, location=%s, contact_email=%s
                    WHERE user_id=%s
                """, (company_name, industry, website, bio, location, contact_email, user_id))
                
            conn.commit()
            
            # Send Profile Security Alert Email
            email = session['email']
            html_msg = render_template('emails/profile_security_alert.html',
                                       email=email,
                                       role=role.capitalize())
            send_email("Security Alert: Profile Information Updated", email, html_msg)
            
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('dashboard'))

        # GET request
        if role == 'student':
            cursor.execute("SELECT * FROM students WHERE user_id = %s", (user_id,))
            profile = cursor.fetchone()
        elif role == 'company':
            cursor.execute("SELECT * FROM companies WHERE user_id = %s", (user_id,))
            profile = cursor.fetchone()
        else:
            flash('Admins do not have a profile to edit.', 'warning')
            return redirect(url_for('dashboard'))
            
    finally:
        cursor.close()
        conn.close()
        
    return render_template('edit_profile.html', profile=profile)

# ============================================================
# ROUTE: Public Company Profile
# ============================================================
@app.route('/company/<int:company_id>')
@login_required
def company_profile(company_id):
    """View public company profile and active listings."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM companies WHERE id = %s", (company_id,))
        company = cursor.fetchone()
        if not company:
            flash('Company not found.', 'danger')
            return redirect(url_for('internships'))
            
        cursor.execute("""
            SELECT * FROM internships 
            WHERE company_id = %s AND is_active = 1
            ORDER BY posted_at DESC
        """, (company_id,))
        active_internships = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    return render_template('company_profile.html', company=company, internships=active_internships)

# ============================================================
# ROUTE: View All Internships (Students + Public)
# ============================================================
@app.route('/internships')
@login_required
def internships():
    """List all active internship listings."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    applied_ids = set()

    try:
        # Get search/filter params
        search = request.args.get('search', '').strip()
        location_filter = request.args.get('location', '').strip()
        stipend_filter = request.args.get('stipend', '').strip()
        duration_filter = request.args.get('duration', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = 6

        query = """
            SELECT i.*, c.company_name, c.location AS company_location
            FROM internships i
            JOIN companies c ON i.company_id = c.id
            WHERE i.is_active = 1
        """
        params = []

        if search:
            query += " AND (i.title LIKE %s OR i.skills_required LIKE %s OR c.company_name LIKE %s)"
            params += [f'%{search}%', f'%{search}%', f'%{search}%']

        if location_filter:
            query += " AND i.location LIKE %s"
            params.append(f'%{location_filter}%')
            
        if stipend_filter == 'unpaid':
            query += " AND (LOWER(i.stipend) LIKE '%%unpaid%%' OR i.stipend IS NULL OR i.stipend = '')"
        elif stipend_filter == 'paid':
            query += " AND LOWER(i.stipend) NOT LIKE '%%unpaid%%' AND i.stipend != ''"
            
        if duration_filter == '1-2':
            query += " AND (i.duration LIKE '%%1 %%' OR i.duration LIKE '%%2 %%')"
        elif duration_filter == '3-5':
            query += " AND (i.duration LIKE '%%3 %%' OR i.duration LIKE '%%4 %%' OR i.duration LIKE '%%5 %%')"
        elif duration_filter == '6+':
            query += " AND (i.duration LIKE '%%6 %%' OR i.duration LIKE '%%7 %%' OR i.duration LIKE '%%8 %%' OR i.duration LIKE '%%9 %%' OR i.duration LIKE '%%10 %%' OR i.duration LIKE '%%11 %%' OR i.duration LIKE '%%12 %%')"

        # Count total rows for pagination
        count_query = "SELECT COUNT(*) as total FROM (" + query + ") as subquery"
        cursor.execute(count_query, params)
        total_items = cursor.fetchone()['total']
        total_pages = (total_items + per_page - 1) // per_page

        query += " ORDER BY i.posted_at DESC LIMIT %s OFFSET %s"
        params += [per_page, (page - 1) * per_page]
        
        cursor.execute(query, params)
        all_internships = cursor.fetchall()

        # If student, find which ones they've already applied to and saved
        saved_ids = set()
        if session['role'] == 'student':
            cursor.execute("SELECT id FROM students WHERE user_id = %s", (session['user_id'],))
            student = cursor.fetchone()
            if student:
                cursor.execute("SELECT internship_id FROM applications WHERE student_id = %s", (student['id'],))
                applied_ids = {row['internship_id'] for row in cursor.fetchall()}
                
                cursor.execute("SELECT internship_id FROM saved_internships WHERE student_id = %s", (student['id'],))
                saved_ids = {row['internship_id'] for row in cursor.fetchall()}

    finally:
        cursor.close()
        conn.close()

    return render_template('internships.html',
                           internships=all_internships,
                           applied_ids=applied_ids,
                           saved_ids=saved_ids,
                           search=search,
                           location_filter=location_filter,
                           stipend_filter=stipend_filter,
                           duration_filter=duration_filter,
                           page=page,
                           total_pages=total_pages)

# ============================================================
# ROUTE: Toggle Save/Bookmark Internship
# ============================================================
@app.route('/toggle_save/<int:internship_id>')
@login_required
@role_required('student')
def toggle_save(internship_id):
    """Student bookmarks or un-bookmarks an internship."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM students WHERE user_id = %s", (session['user_id'],))
        student = cursor.fetchone()
        
        cursor.execute("SELECT * FROM saved_internships WHERE student_id = %s AND internship_id = %s", (student['id'], internship_id))
        is_saved = cursor.fetchone()
        
        if is_saved:
            cursor.execute("DELETE FROM saved_internships WHERE student_id = %s AND internship_id = %s", (student['id'], internship_id))
            flash('Internship removed from saved list.', 'info')
        else:
            cursor.execute("INSERT INTO saved_internships (student_id, internship_id) VALUES (%s, %s)", (student['id'], internship_id))
            flash('Internship saved successfully!', 'success')
        conn.commit()
    finally:
        cursor.close()
        conn.close()
    return redirect(request.referrer or url_for('internships'))

# ============================================================
# ROUTE: View My Applications (Student - Global view)
# ============================================================
@app.route('/student/applications')
@login_required
@role_required('student')
def student_applications():
    """Student views all their applications, optionally filtered by status."""
    status_filter = request.args.get('status', '').strip().lower()
    if status_filter not in ('accepted', 'pending', 'rejected'):
        status_filter = None

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT id FROM students WHERE user_id = %s", (session['user_id'],))
        student = cursor.fetchone()

        if not student:
            flash('Student profile not found.', 'danger')
            return redirect(url_for('dashboard'))

        # Fetch student applications
        query = """
            SELECT a.*,
                   i.title, i.location, i.stipend, i.duration, i.skills_required, i.description,
                   c.company_name, c.id AS company_id
            FROM applications a
            JOIN internships i ON a.internship_id = i.id
            JOIN companies c ON i.company_id = c.id
            WHERE a.student_id = %s
        """
        params = [student['id']]

        if status_filter:
            query += " AND a.status = %s"
            params.append(status_filter)

        query += " ORDER BY a.applied_at DESC"

        cursor.execute(query, params)
        applications = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    return render_template('student_applications.html',
                           student=student,
                           applications=applications,
                           status_filter=status_filter)

# ============================================================
# ROUTE: View Saved Internships
# ============================================================
@app.route('/saved_internships')
@login_required
@role_required('student')
def saved_internships():
    """List student's saved internships."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id FROM students WHERE user_id = %s", (session['user_id'],))
        student = cursor.fetchone()
        
        cursor.execute("""
            SELECT i.*, c.company_name, c.location AS company_location
            FROM saved_internships si
            JOIN internships i ON si.internship_id = i.id
            JOIN companies c ON i.company_id = c.id
            WHERE si.student_id = %s AND i.is_active = 1
            ORDER BY si.saved_at DESC
        """, (student['id'],))
        saved = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    return render_template('saved_internships.html', internships=saved)

# ============================================================
# ROUTE: Edit Submitted Application (Student)
# ============================================================
@app.route('/edit_application/<int:app_id>', methods=['GET', 'POST'])
@login_required
@role_required('student')
def edit_application(app_id):
    """Allow students to edit their submitted application if status allows."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get student profile
        cursor.execute("SELECT * FROM students WHERE user_id = %s", (session['user_id'],))
        student = cursor.fetchone()
        if not student:
            flash('Student profile not found.', 'danger')
            return redirect(url_for('dashboard'))

        # Fetch the application, verifying it belongs to this student
        cursor.execute("""
            SELECT a.*, i.title, i.description, i.location, i.duration, i.stipend, i.skills_required, i.openings, i.deadline, i.company_id, c.company_name
            FROM applications a
            JOIN internships i ON a.internship_id = i.id
            JOIN companies c ON i.company_id = c.id
            WHERE a.id = %s AND a.student_id = %s
        """, (app_id, student['id']))
        application = cursor.fetchone()

        if not application:
            flash('Application not found or access denied.', 'danger')
            return redirect(url_for('student_applications'))

        # Check status rules
        if application['status'] in ('accepted', 'rejected'):
            flash('This application can no longer be edited.', 'danger')
            return redirect(url_for('student_applications'))

        if request.method == 'POST':
            full_name = request.form.get('full_name', '').strip() or student['full_name']
            college = request.form.get('college', '').strip() or student['college']
            degree = request.form.get('degree', '').strip() or student['degree']
            cover_letter = request.form.get('cover_letter', '').strip()
            phone = request.form.get('phone', '').strip() or student['phone']
            skills = request.form.get('skills', '').strip() or student['skills']
            cgpa = request.form.get('cgpa', '').strip()
            portfolio_links = request.form.get('portfolio_links', '').strip()
            preferred_location = request.form.get('preferred_location', '').strip()
            certifications = request.form.get('certifications', '').strip()

            # Handle Resume
            resume_file = request.files.get('resume')
            resume_link = application['resume_link']

            if resume_file and resume_file.filename:
                if resume_file.filename.lower().endswith('.pdf'):
                    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                    filename = secure_filename(f"resume_app_{student['id']}_{application['internship_id']}_{resume_file.filename}")
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    resume_file.save(filepath)
                    resume_link = filepath.replace('\\', '/')
                else:
                    flash('Only PDF resumes are allowed.', 'danger')
                    return redirect(url_for('edit_application', app_id=app_id))

            # Increment count and set edit metadata
            edit_count = (application['edit_count'] or 0) + 1

            cursor.execute("""
                UPDATE applications
                SET full_name = %s,
                    college = %s,
                    degree = %s,
                    cover_letter = %s,
                    resume_link = %s,
                    skills = %s,
                    phone = %s,
                    cgpa = %s,
                    portfolio_links = %s,
                    preferred_location = %s,
                    certifications = %s,
                    is_edited = 1,
                    edit_count = %s,
                    edited_by_student = 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (full_name, college, degree, cover_letter, resume_link, skills, phone, cgpa, portfolio_links, preferred_location, certifications, edit_count, app_id))
            conn.commit()

            # Notify company if status is "pending" (actively being reviewed)
            if application['status'] == 'pending':
                # Fetch company email address
                cursor.execute("""
                    SELECT u.email, c.company_name
                    FROM companies c
                    JOIN users u ON c.user_id = u.id
                    WHERE c.id = %s
                """, (application['company_id'],))
                company_data = cursor.fetchone()
                if company_data:
                    company_html_msg = render_template('emails/new_applicant_alert.html',
                                                       company_name=company_data['company_name'],
                                                       title=application['title'],
                                                       student_name=student['full_name'],
                                                       college=student['college'] or '—',
                                                       degree=student['degree'] or '—',
                                                       is_update=True)
                    send_email(f"Application Update Alert — {student['full_name']}", company_data['email'], company_html_msg)

            flash('Application updated successfully!', 'success')
            cursor.close()
            conn.close()
            return redirect(url_for('student_applications'))

    finally:
        cursor.close()
        conn.close()

    # Build internship dict from the application row (which contains all joined internship fields)
    internship = {
        'id': application['internship_id'],
        'title': application['title'],
        'description': application.get('description', ''),
        'location': application.get('location', ''),
        'duration': application.get('duration', ''),
        'stipend': application.get('stipend', ''),
        'skills_required': application.get('skills_required', ''),
        'openings': application.get('openings', ''),
        'deadline': application.get('deadline', ''),
        'company_id': application['company_id'],
        'company_name': application['company_name'],
    }

    # Render original apply.html in edit mode — restores the exact cinematic two-panel layout
    return render_template('apply.html',
                           internship=internship,
                           student=student,
                           application=application,
                           is_editing=True)

# ============================================================
# ROUTE: Apply for Internship
# ============================================================
@app.route('/apply/<int:internship_id>', methods=['GET', 'POST'])
@login_required
@role_required('student')
def apply(internship_id):
    """Student applies for a specific internship."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get the internship details
        cursor.execute("""
            SELECT i.*, c.company_name
            FROM internships i
            JOIN companies c ON i.company_id = c.id
            WHERE i.id = %s AND i.is_active = 1
        """, (internship_id,))
        internship = cursor.fetchone()

        if not internship:
            flash('Internship not found or no longer active.', 'danger')
            return redirect(url_for('internships'))

        # Get student profile
        cursor.execute("SELECT * FROM students WHERE user_id = %s", (session['user_id'],))
        student = cursor.fetchone()

        if not student:
            flash('Student profile not found.', 'danger')
            return redirect(url_for('internships'))

        # Check if already applied
        cursor.execute(
            "SELECT id FROM applications WHERE student_id = %s AND internship_id = %s",
            (student['id'], internship_id)
        )
        if cursor.fetchone():
            flash('You have already applied for this internship.', 'warning')
            return redirect(url_for('internships'))

        if request.method == 'POST':
            full_name = request.form.get('full_name', '').strip() or student['full_name']
            college = request.form.get('college', '').strip() or student['college']
            degree = request.form.get('degree', '').strip() or student['degree']
            cover_letter = request.form.get('cover_letter', '').strip()
            phone = request.form.get('phone', '').strip() or student['phone']
            skills = request.form.get('skills', '').strip() or student['skills']
            cgpa = request.form.get('cgpa', '').strip()
            portfolio_links = request.form.get('portfolio_links', '').strip()
            preferred_location = request.form.get('preferred_location', '').strip()
            certifications = request.form.get('certifications', '').strip()

            # Handle Resume Specific to Application
            resume_file = request.files.get('resume')
            resume_link = student['resume_link']

            if resume_file and resume_file.filename:
                if resume_file.filename.lower().endswith('.pdf'):
                    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                    filename = secure_filename(f"resume_app_{student['id']}_{internship_id}_{resume_file.filename}")
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    resume_file.save(filepath)
                    resume_link = filepath.replace('\\', '/')
                else:
                    flash('Only PDF resumes are allowed.', 'danger')
                    return redirect(url_for('apply', internship_id=internship_id))

            cursor.execute("""
                INSERT INTO applications 
                (student_id, internship_id, full_name, college, degree, cover_letter, resume_link, skills, phone, cgpa, portfolio_links, preferred_location, certifications)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (student['id'], internship_id, full_name, college, degree, cover_letter, resume_link, skills, phone, cgpa, portfolio_links, preferred_location, certifications))
            conn.commit()
            
            # Send professional Application Confirmation Email
            html_msg = render_template('emails/application_confirmation.html', 
                                       student_name=student['full_name'],
                                       title=internship['title'],
                                       company_name=internship['company_name'])
            send_email(f"Application Submitted: {internship['title']}", session['email'], html_msg)

            # Fetch company details and company's email address
            cursor.execute("""
                SELECT u.email, c.company_name
                FROM companies c
                JOIN users u ON c.user_id = u.id
                WHERE c.id = %s
            """, (internship['company_id'],))
            company_data = cursor.fetchone()
            
            if company_data:
                company_email = company_data['email']
                company_name = company_data['company_name']
                
                # Send Company Applicant Alert Email
                company_html_msg = render_template('emails/new_applicant_alert.html',
                                                   company_name=company_name,
                                                   title=internship['title'],
                                                   student_name=student['full_name'],
                                                   college=student['college'] or '—',
                                                   degree=student['degree'] or '—')
                send_email(f"New Applicant Alert — {student['full_name']}", company_email, company_html_msg)

            flash(f'Application submitted for "{internship["title"]}" successfully!', 'success')
            return redirect(url_for('dashboard'))

    finally:
        cursor.close()
        conn.close()
    return render_template('apply.html', internship=internship, student=student)
# ============================================================
# ROUTE: Post Internship (Company)
# ============================================================
@app.route('/post_internship', methods=['GET', 'POST'])
@login_required
@role_required('company')
def post_internship():
    """Company posts a new internship listing."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM companies WHERE user_id = %s", (session['user_id'],))
        company = cursor.fetchone()

        if not company:
            flash('Company profile not found.', 'danger')
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            location = request.form.get('location', '').strip()
            duration = request.form.get('duration', '').strip()
            stipend = request.form.get('stipend', '').strip()
            skills_required = request.form.get('skills_required', '').strip()
            openings = request.form.get('openings', 1)
            deadline = request.form.get('deadline', None) or None

            if not title or not description:
                flash('Title and description are required.', 'danger')
                return render_template('post_internship.html', company=company)

            cursor.execute("""
                INSERT INTO internships
                    (company_id, title, description, location, duration, stipend,
                     skills_required, openings, deadline)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (company['id'], title, description, location, duration, stipend,
                  skills_required, int(openings), deadline))
            conn.commit()
            flash(f'Internship "{title}" posted successfully!', 'success')
            return redirect(url_for('dashboard'))

    finally:
        cursor.close()
        conn.close()

    return render_template('post_internship.html', company=company)

# ============================================================
# ROUTE: View Applications (Company)
# ============================================================
@app.route('/view_applications/<int:internship_id>')
@login_required
@role_required('company')
def view_applications(internship_id):
    """Company views all applicants for a specific internship."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM companies WHERE user_id = %s", (session['user_id'],))
        company = cursor.fetchone()

        if not company:
            flash('Company profile not found.', 'danger')
            return redirect(url_for('dashboard'))

        # Verify this internship belongs to this company
        cursor.execute(
            "SELECT * FROM internships WHERE id = %s AND company_id = %s",
            (internship_id, company['id'])
        )
        internship = cursor.fetchone()

        if not internship:
            flash('Internship not found or access denied.', 'danger')
            return redirect(url_for('dashboard'))

        # Get all applications with student info
        cursor.execute("""
            SELECT a.id, a.cover_letter, a.status, a.applied_at, a.cgpa, a.portfolio_links, a.preferred_location, a.certifications, a.is_edited, a.updated_at, a.edit_count,
                   COALESCE(a.full_name, s.full_name) AS full_name,
                   COALESCE(a.college, s.college) AS college,
                   COALESCE(a.degree, s.degree) AS degree,
                   COALESCE(a.skills, s.skills) AS skills,
                   COALESCE(a.phone, s.phone) AS phone,
                   COALESCE(a.resume_link, s.resume_link) AS resume_link,
                   u.email
            FROM applications a
            JOIN students s ON a.student_id = s.id
            JOIN users u ON s.user_id = u.id
            WHERE a.internship_id = %s
            ORDER BY a.applied_at DESC
        """, (internship_id,))
        applications = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    return render_template('view_applications.html',
                           internship=internship,
                           applications=applications)

# ============================================================
# ROUTE: Update Application Status (Company)
# ============================================================
@app.route('/update_application/<int:app_id>/<string:new_status>')
@login_required
@role_required('company')
def update_application(app_id, new_status):
    """Company accepts or rejects an application."""
    if new_status not in ('accepted', 'rejected', 'pending'):
        flash('Invalid status.', 'danger')
        return redirect(url_for('dashboard'))

    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        # Verify the application belongs to this company's internship
        cursor.execute("SELECT id FROM companies WHERE user_id = %s", (session['user_id'],))
        company = cursor.fetchone()

        cursor.execute("""
            SELECT a.id FROM applications a
            JOIN internships i ON a.internship_id = i.id
            WHERE a.id = %s AND i.company_id = %s
        """, (app_id, company['id']))

        if not cursor.fetchone():
            flash('Application not found or access denied.', 'danger')
            return redirect(url_for('dashboard'))

        cursor.execute(
            "UPDATE applications SET status = %s WHERE id = %s",
            (new_status, app_id)
        )
        conn.commit()
        flash(f'Application has been {new_status}.', 'success')

        # Send Email Notification
        cursor.execute("""
            SELECT u.email, s.full_name, i.title, c.company_name
            FROM applications a
            JOIN students s ON a.student_id = s.id
            JOIN users u ON s.user_id = u.id
            JOIN internships i ON a.internship_id = i.id
            JOIN companies c ON i.company_id = c.id
            WHERE a.id = %s
        """, (app_id,))
        app_data = cursor.fetchone()
        
        if app_data:
            # Send professional Status Update Email
            html_msg = render_template('emails/status_update.html',
                                       student_name=app_data['full_name'],
                                       title=app_data['title'],
                                       company_name=app_data['company_name'],
                                       status=new_status)
            send_email(f"Application Status: {new_status.capitalize()}", app_data['email'], html_msg)

        # Get internship_id to redirect back
        cursor.execute("SELECT internship_id FROM applications WHERE id = %s", (app_id,))
        row = cursor.fetchone()
        
        # Smart redirect back to Referrer (e.g. all applicants overview or specific page)
        referrer = request.referrer or ''
        if 'company/applicants' in referrer:
            return redirect(url_for('all_applicants'))
            
        return redirect(url_for('view_applications', internship_id=row['internship_id']))

    finally:
        cursor.close()
        conn.close()

# ============================================================
# ROUTE: View All Applicants (Company - Global view)
# ============================================================
@app.route('/company/applicants')
@login_required
@role_required('company')
def all_applicants():
    """Company views all applicants across all posted internships."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM companies WHERE user_id = %s", (session['user_id'],))
        company = cursor.fetchone()

        if not company:
            flash('Company profile not found.', 'danger')
            return redirect(url_for('dashboard'))

        # Get all applications for all of this company's internships
        cursor.execute("""
            SELECT a.id, a.cover_letter, a.status, a.applied_at, a.cgpa, a.portfolio_links, a.preferred_location, a.certifications, a.is_edited, a.updated_at, a.edit_count,
                   COALESCE(a.full_name, s.full_name) AS full_name,
                   COALESCE(a.college, s.college) AS college,
                   COALESCE(a.degree, s.degree) AS degree,
                   COALESCE(a.skills, s.skills) AS skills,
                   COALESCE(a.phone, s.phone) AS phone,
                   COALESCE(a.resume_link, s.resume_link) AS resume_link,
                   u.email,
                   i.title AS internship_title, i.id AS internship_id
            FROM applications a
            JOIN students s ON a.student_id = s.id
            JOIN users u ON s.user_id = u.id
            JOIN internships i ON a.internship_id = i.id
            WHERE i.company_id = %s
            ORDER BY a.applied_at DESC
        """, (company['id'],))
        applications = cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

    return render_template('all_applicants.html',
                           company=company,
                           applications=applications)

# ============================================================
# ROUTE: Admin - Manage Users
# ============================================================
@app.route('/admin/users')
@login_required
@role_required('admin')
def admin_users():
    """Admin views all registered users."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, email, role, created_at FROM users ORDER BY created_at DESC")
        users = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    return render_template('admin_users.html', users=users)

# ============================================================
# ROUTE: Admin - Delete User
# ============================================================
@app.route('/admin/delete_user/<int:user_id>')
@login_required
@role_required('admin')
def delete_user(user_id):
    """Admin deletes a user account (cascades to profile) and sends alert."""
    if user_id == session['user_id']:
        flash('You cannot delete your own admin account.', 'danger')
        return redirect(url_for('admin_users'))

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        # Retrieve target user email before deletion
        cursor.execute("SELECT email FROM users WHERE id = %s", (user_id,))
        user_row = cursor.fetchone()
        if not user_row:
            flash('User not found.', 'danger')
            return redirect(url_for('admin_users'))

        email = user_row['email']

        # Delete the user row (cascades automatically)
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()

        # Send polite termination notification email
        html_msg = render_template('emails/account_terminated.html')
        send_email("Account Notice — InternHub", email, html_msg)

        flash('User deleted and notification sent successfully.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Failed to delete user: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin_users'))

# ============================================================
# ROUTE: Admin - Manage Internships
# ============================================================
@app.route('/admin/internships')
@login_required
@role_required('admin')
def admin_internships():
    """Admin views all internship listings."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT i.*, c.company_name,
                   COUNT(a.id) AS applicant_count
            FROM internships i
            JOIN companies c ON i.company_id = c.id
            LEFT JOIN applications a ON i.id = a.internship_id
            GROUP BY i.id
            ORDER BY i.posted_at DESC
        """)
        internships = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    return render_template('admin_internships.html', internships=internships)

# ============================================================
# ROUTE: Admin - Toggle Internship Active Status
# ============================================================
@app.route('/admin/toggle_internship/<int:internship_id>')
@login_required
@role_required('admin')
def toggle_internship(internship_id):
    """Admin activates or deactivates an internship listing."""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE internships SET is_active = NOT is_active WHERE id = %s",
            (internship_id,)
        )
        conn.commit()
        flash('Internship status updated.', 'success')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin_internships'))

# ============================================================
# ROUTE: Admin - View All Applications
# ============================================================
@app.route('/admin/applications')
@login_required
@role_required('admin')
def admin_applications():
    """Admin views all applications from all students."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT a.*,
                   s.full_name, s.college, s.degree,
                   i.title, i.company_id,
                   c.company_name,
                   u.email
            FROM applications a
            JOIN students s ON a.student_id = s.id
            JOIN users u ON s.user_id = u.id
            JOIN internships i ON a.internship_id = i.id
            JOIN companies c ON i.company_id = c.id
            ORDER BY a.applied_at DESC
        """)
        applications = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    return render_template('admin_applications.html', applications=applications)

# ============================================================
# ROUTE: Admin - View All Companies
# ============================================================
@app.route('/admin/companies')
@login_required
@role_required('admin')
def admin_companies():
    """Admin views all registered companies."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT c.*, u.email,
                   COUNT(i.id) AS internships_posted,
                   COUNT(a.id) AS total_applications
            FROM companies c
            JOIN users u ON c.user_id = u.id
            LEFT JOIN internships i ON c.id = i.company_id
            LEFT JOIN applications a ON i.id = a.internship_id
            GROUP BY c.id
            ORDER BY c.id DESC
        """)
        companies = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    return render_template('admin_companies.html', companies=companies)

# ============================================================
# ROUTE: Admin - View Analytics
# ============================================================
@app.route('/admin/analytics')
@login_required
@role_required('admin')
def admin_analytics():
    """Admin views platform analytics and statistics."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        # Get summary stats
        cursor.execute("SELECT COUNT(*) AS cnt FROM users WHERE role = 'student'")
        student_count = cursor.fetchone()['cnt']
        
        cursor.execute("SELECT COUNT(*) AS cnt FROM users WHERE role = 'company'")
        company_count = cursor.fetchone()['cnt']
        
        cursor.execute("SELECT COUNT(*) AS cnt FROM internships WHERE is_active = 1")
        active_internships = cursor.fetchone()['cnt']
        
        cursor.execute("SELECT COUNT(*) AS cnt FROM applications")
        total_applications = cursor.fetchone()['cnt']
        
        # Get application status distribution
        cursor.execute("SELECT status, COUNT(*) as cnt FROM applications GROUP BY status")
        app_status_dist = cursor.fetchall()
        
        # Get top companies by applications
        cursor.execute("""
            SELECT c.company_name, COUNT(a.id) AS app_count
            FROM companies c
            JOIN internships i ON c.id = i.company_id
            LEFT JOIN applications a ON i.id = a.internship_id
            GROUP BY c.id
            ORDER BY app_count DESC
            LIMIT 10
        """)
        top_companies = cursor.fetchall()
        
    finally:
        cursor.close()
        conn.close()
    
    return render_template('admin_analytics.html',
                          student_count=student_count,
                          company_count=company_count,
                          active_internships=active_internships,
                          total_applications=total_applications,
                          app_status_dist=app_status_dist,
                          top_companies=top_companies)

# ============================================================
# ROUTE: Notifications Center
# ============================================================
@app.route('/notifications')
@login_required
def notifications():
    """Display a role-aware notifications page for all logged-in users."""
    role = session.get('role')
    user_id = session.get('user_id')
    notifications_data = {
        'recent_users': [],
        'recent_applications': [],
        'timeline': [],
        'heading': 'Notifications'
    }

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        if role == 'admin':
            notifications_data['heading'] = 'System Notifications'
            cursor.execute("""
                SELECT id, email, role, created_at FROM users
                ORDER BY created_at DESC LIMIT 5
            """)
            notifications_data['recent_users'] = cursor.fetchall()

            cursor.execute("""
                SELECT a.id, a.status, a.applied_at, s.full_name, i.title, c.company_name
                FROM applications a
                JOIN students s ON a.student_id = s.id
                JOIN internships i ON a.internship_id = i.id
                JOIN companies c ON i.company_id = c.id
                ORDER BY a.applied_at DESC LIMIT 5
            """)
            notifications_data['recent_applications'] = cursor.fetchall()

        elif role == 'student':
            notifications_data['heading'] = 'Your Updates'
            cursor.execute("""
                SELECT a.id, a.status, a.applied_at, i.title, c.company_name
                FROM applications a
                JOIN internships i ON a.internship_id = i.id
                JOIN companies c ON i.company_id = c.id
                WHERE a.student_id = (SELECT id FROM students WHERE user_id = %s)
                ORDER BY a.applied_at DESC LIMIT 5
            """, (user_id,))
            notifications_data['timeline'] = cursor.fetchall()

        elif role == 'company':
            notifications_data['heading'] = 'Company Alerts'
            cursor.execute("""
                SELECT a.id, a.status, a.applied_at, s.full_name, i.title
                FROM applications a
                JOIN students s ON a.student_id = s.id
                JOIN internships i ON a.internship_id = i.id
                WHERE i.company_id = (SELECT id FROM companies WHERE user_id = %s)
                ORDER BY a.applied_at DESC LIMIT 5
            """, (user_id,))
            notifications_data['timeline'] = cursor.fetchall()

        else:
            notifications_data['timeline'] = []

    finally:
        cursor.close()
        conn.close()

    return render_template('notifications.html', **notifications_data)


@app.route('/admin/notifications')
@login_required
@role_required('admin')
def admin_notifications():
    """Backward-compatible admin notifications page."""
    return redirect(url_for('notifications'))

# ============================================================
# ROUTE: Forgot Password
# ============================================================
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """Handle request to reset password by sending tokenized link."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        if not email:
            flash('Email address is required.', 'danger')
            return render_template('forgot_password.html')

        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            if user:
                # Generate time-bound token (valid for 30 mins)
                token = serializer.dumps(email, salt='password-reset-salt')
                reset_url = url_for('reset_password', token=token, _external=True)

                # Send email
                html_msg = render_template('emails/password_reset.html', reset_url=reset_url)
                send_email("Password Reset Request", email, html_msg)
            
            # Show a generic success message even if user doesn't exist (security best practice)
            flash('If that email is registered, we have sent a secure recovery link.', 'success')
            return redirect(url_for('login'))
        finally:
            cursor.close()
            conn.close()

    return render_template('forgot_password.html')

# ============================================================
# ROUTE: Reset Password
# ============================================================
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset with a valid token."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    try:
        # Load and verify token. Limit to 1800 seconds (30 mins)
        email = serializer.loads(token, salt='password-reset-salt', max_age=1800)
    except SignatureExpired:
        flash('The password reset link has expired. Please request a new one.', 'danger')
        return redirect(url_for('forgot_password'))
    except Exception:
        flash('Invalid reset link. Please check the URL or request a new one.', 'danger')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if not password or not confirm:
            flash('All fields are required.', 'danger')
            return render_template('reset_password.html')

        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('reset_password.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('reset_password.html')

        hashed_pw = generate_password_hash(password)
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE users SET password_hash = %s WHERE email = %s", (hashed_pw, email))
            conn.commit()

            # Send confirmation security alert
            html_msg = render_template('emails/password_changed_alert.html', email=email)
            send_email("Your Password Has Been Changed", email, html_msg)

            flash('Your password has been reset successfully! Please sign in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            conn.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
        finally:
            cursor.close()
            conn.close()

    return render_template('reset_password.html')

# ============================================================
# ROUTE: Delete Account (Voluntary Self-Deletion)
# ============================================================
@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    """Allow a user to permanently delete their account and data."""
    user_id = session['user_id']
    email = session['email']

    conn = get_db()
    cursor = conn.cursor()
    try:
        # Delete user record (will cascade to student/company profiles and related tables)
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()

        # Send goodbye email
        html_msg = render_template('emails/account_deleted.html')
        send_email("Account Closed — InternHub", email, html_msg)

        # Clear session
        session.clear()
        flash('Your account has been deleted successfully.', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Failed to delete account: {str(e)}', 'danger')
        return redirect(url_for('edit_profile'))
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('index'))

# ============================================================
# ROUTE: Admin - Trigger Weekly Match Digest Simulation
# ============================================================
@app.route('/admin/trigger_weekly_digest')
@login_required
@role_required('admin')
def trigger_weekly_digest():
    """Simulate sending the Weekly Match Digest to all students."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        # Fetch all students and their users emails
        cursor.execute("""
            SELECT s.*, u.email
            FROM students s
            JOIN users u ON s.user_id = u.id
        """)
        students = cursor.fetchall()

        # Fetch all active internships with company name
        cursor.execute("""
            SELECT i.*, c.company_name
            FROM internships i
            JOIN companies c ON i.company_id = c.id
            WHERE i.is_active = 1
            ORDER BY i.posted_at DESC
        """)
        all_internships = cursor.fetchall()

        if not all_internships:
            flash('No active internships available to digest.', 'warning')
            return redirect(url_for('dashboard'))

        emails_sent = 0
        for student in students:
            # Match based on skills overlap (case-insensitive substring match)
            matched = []
            student_skills = [sk.strip().lower() for sk in (student['skills'] or '').split(',') if sk.strip()]
            
            if student_skills:
                for job in all_internships:
                    job_skills = job['skills_required'].lower() if job['skills_required'] else ''
                    # If any student skill is in the job skills required
                    if any(skill in job_skills for skill in student_skills):
                        matched.append(job)
            
            # Fallback to the 3 most recent active internships if no matching skills or few matches
            if len(matched) < 3:
                for job in all_internships:
                    if job not in matched:
                        matched.append(job)
                    if len(matched) >= 3:
                        break

            # Limit digest to top 5 recommendations
            matched = matched[:5]

            html_msg = render_template('emails/weekly_digest.html',
                                       name=student['full_name'],
                                       internships=matched)
            send_email("Your Weekly Internship Match Digest — InternHub", student['email'], html_msg)
            emails_sent += 1

        flash(f'Simulated weekly digest campaign successfully! Sent {emails_sent} emails.', 'success')
    except Exception as e:
        flash(f'Digest trigger failed: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('dashboard'))

# ============================================================
# ROUTE: Admin - Trigger Saved Internship Deadline Alerts Simulation
# ============================================================
@app.route('/admin/trigger_deadline_alerts')
@login_required
@role_required('admin')
def trigger_deadline_alerts():
    """Simulate sending approaching deadline alerts to students for saved internships."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    try:
        # Get all saved active internships with student, company, and internship details
        cursor.execute("""
            SELECT si.saved_at, 
                   s.full_name AS student_name, u.email AS student_email,
                   i.id AS internship_id, i.title, i.deadline,
                   c.company_name
            FROM saved_internships si
            JOIN students s ON si.student_id = s.id
            JOIN users u ON s.user_id = u.id
            JOIN internships i ON si.internship_id = i.id
            JOIN companies c ON i.company_id = c.id
            WHERE i.is_active = 1
        """)
        saved_items = cursor.fetchall()

        if not saved_items:
            flash('No saved internships found on the platform to alert.', 'info')
            return redirect(url_for('dashboard'))

        emails_sent = 0
        for item in saved_items:
            # Send deadline reminder email
            html_msg = render_template('emails/deadline_reminder.html',
                                       name=item['student_name'],
                                       title=item['title'],
                                       company_name=item['company_name'],
                                       deadline=item['deadline'],
                                       id=item['internship_id'])
            send_email(f"Deadline Approaching: {item['title']}", item['student_email'], html_msg)
            emails_sent += 1

        flash(f'Simulated approaching deadline alerts successfully! Sent {emails_sent} emails.', 'success')
    except Exception as e:
        flash(f'Deadline alert trigger failed: {str(e)}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('dashboard'))

# ============================================================
# ERROR HANDLERS
# ============================================================
@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors gracefully."""
    flash("The requested page could not be found.", "warning")
    return redirect(url_for('dashboard') if 'user_id' in session else url_for('index'))

@app.errorhandler(403)
def forbidden(e):
    """Handle 403 forbidden access errors gracefully."""
    flash("You do not have permission to access this resource.", "danger")
    return redirect(url_for('dashboard'))

@app.errorhandler(413)
def request_entity_too_large(e):
    """Handle file uploads that exceed the maximum size limit."""
    flash("The uploaded file exceeds the 5MB size limit. Please upload a smaller PDF.", "danger")
    return redirect(request.referrer or url_for('edit_profile'))

@app.errorhandler(500)
def internal_server_error(e):
    return "Internal Server Error. Check Vercel logs.", 500

# ============================================================
# RUN APPLICATION
# ============================================================
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
