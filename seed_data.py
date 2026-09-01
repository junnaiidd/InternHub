"""
seed_data.py
============
Inserts realistic seed data into the existing `internship_portal` database.

Inserts:
  - 100 students  (users + students tables)
  - 10  companies (users + companies tables)
  - 50  internships
  - 200 applications

Requirements:
  pip install faker mysql-connector-python

Usage:
  python seed_data.py
"""

import random
from faker import Faker
import mysql.connector
from werkzeug.security import generate_password_hash

# ---------------------------------------------
# DATABASE CONFIG - update password if needed
# ---------------------------------------------
DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "junnaiidd",
    "database": "internship_portal",
}

fake = Faker("en_IN")   # Indian locale for realistic names/cities
Faker.seed(42)
random.seed(42)

# ---------------------------------------------
# DOMAIN DATA
# ---------------------------------------------
INDIAN_CITIES = [
    "Bengaluru", "Mumbai", "Delhi", "Hyderabad", "Chennai",
    "Pune", "Kolkata", "Ahmedabad", "Jaipur", "Surat",
    "Remote", "Bengaluru (Remote)", "Mumbai (Hybrid)", "Delhi (Remote)",
]

INDUSTRIES = [
    "Information Technology", "Finance & Banking", "Healthcare",
    "E-commerce", "Education", "Media & Entertainment",
    "Manufacturing", "Consulting", "Logistics", "Cybersecurity",
]

DEGREES = [
    "B.Tech CSE", "B.Tech IT", "B.Tech ECE", "B.Tech EEE",
    "BCA", "B.Sc Computer Science", "B.Com", "BBA",
    "MBA", "MCA", "M.Tech CSE", "M.Sc Data Science",
]

SKILLS_POOL = [
    "Python", "Java", "JavaScript", "React", "Node.js", "Flask",
    "Django", "SQL", "MySQL", "MongoDB", "REST APIs", "HTML/CSS",
    "Bootstrap", "Data Analysis", "Machine Learning", "Excel",
    "Communication", "Teamwork", "Problem Solving", "Git",
    "AWS", "Docker", "Linux", "C++", "TypeScript", "Figma",
    "SEO", "Content Writing", "Digital Marketing", "Canva",
    "Tableau", "Power BI", "TensorFlow", "OpenCV", "Pandas",
]

INTERNSHIP_ROLES = [
    "Python Backend Developer Intern",
    "Frontend Developer Intern",
    "Full Stack Developer Intern",
    "Data Science Intern",
    "Machine Learning Intern",
    "UI/UX Design Intern",
    "Digital Marketing Intern",
    "Business Development Intern",
    "Content Writing Intern",
    "Cybersecurity Intern",
    "DevOps Intern",
    "Android Developer Intern",
    "iOS Developer Intern",
    "Data Analyst Intern",
    "Cloud Computing Intern",
    "Java Developer Intern",
    "React Developer Intern",
    "HR & Recruitment Intern",
    "Finance & Accounting Intern",
    "Operations Management Intern",
]

DURATIONS = ["1 Month", "2 Months", "3 Months", "4 Months", "6 Months"]

STIPENDS = [
    "Unpaid", "₹5,000/month", "₹8,000/month", "₹10,000/month",
    "₹12,000/month", "₹15,000/month", "₹18,000/month", "₹20,000/month",
    "₹25,000/month", "Performance-based",
]

COVER_LETTER_TEMPLATES = [
    (
        "I am a highly motivated {degree} student with a strong interest in {role}. "
        "I have hands-on experience in {skill1} and {skill2}, and I am eager to apply "
        "my skills in a real-world setting. I am confident that this internship will "
        "help me grow professionally and contribute meaningfully to your team."
    ),
    (
        "Having studied {degree}, I have developed a solid foundation in {skill1}. "
        "I came across this {role} opportunity and felt it perfectly aligns with my "
        "career goals. I am a quick learner, a team player, and deeply passionate "
        "about technology and innovation. I look forward to contributing to your organization."
    ),
    (
        "I am writing to express my keen interest in the {role} position. "
        "My academic background in {degree} combined with practical projects using "
        "{skill1} and {skill2} has prepared me well for this role. I am excited about "
        "the opportunity to learn from industry professionals and add real value."
    ),
    (
        "As a {degree} student with a passion for {skill1}, I believe I am a strong "
        "candidate for the {role} position. I have completed several projects that "
        "demonstrate my ability to work with {skill2} and deliver quality results. "
        "I am enthusiastic, detail-oriented, and ready to take on new challenges."
    ),
    (
        "This {role} position caught my attention immediately. With my background in "
        "{degree} and hands-on experience in {skill1}, I am well-equipped to hit the "
        "ground running. I am passionate about continuous learning and would love the "
        "chance to contribute to your team while developing my professional skills."
    ),
]

INTERNSHIP_DESCRIPTIONS = [
    (
        "Join our dynamic team as a {role}. You will work on live projects, collaborate "
        "with senior engineers, and gain exposure to industry best practices. "
        "Responsibilities include coding, testing, and participating in daily stand-ups. "
        "This is a great opportunity to kick-start your career in {industry}."
    ),
    (
        "We are looking for a motivated {role} to join our {industry} team. "
        "You will assist in designing and implementing solutions, writing clean code, "
        "and learning from an experienced mentorship team. Ideal for final-year students "
        "or recent graduates looking for real-world experience."
    ),
    (
        "As a {role} at our company, you'll be contributing to impactful projects in "
        "the {industry} space. You'll have the opportunity to work with modern tools, "
        "participate in code reviews, and develop solutions that reach thousands of users. "
        "We believe in learning by doing - expect real responsibilities from day one."
    ),
    (
        "This internship is designed for students passionate about {industry}. "
        "As a {role}, you will shadow senior team members, take ownership of assigned modules, "
        "and present your work in weekly review meetings. Hardworking interns may receive "
        "a pre-placement offer at the end of the program."
    ),
]


# ---------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------
def pick_skills(n=4):
    """Return a comma-separated string of n unique skills."""
    return ", ".join(random.sample(SKILLS_POOL, n))


def unique_email(existing: set) -> str:
    """Generate an email that doesn't collide with existing ones."""
    for _ in range(100):
        email = fake.unique.email()
        if email not in existing:
            existing.add(email)
            return email
    # Fallback with uuid suffix
    email = f"user_{fake.uuid4()[:8]}@example.com"
    existing.add(email)
    return email


def build_cover_letter(degree, role, skills_str):
    skills = [s.strip() for s in skills_str.split(",")]
    skill1 = skills[0] if len(skills) > 0 else "Python"
    skill2 = skills[1] if len(skills) > 1 else "SQL"
    template = random.choice(COVER_LETTER_TEMPLATES)
    return template.format(degree=degree, role=role, skill1=skill1, skill2=skill2)


def build_description(role, industry):
    template = random.choice(INTERNSHIP_DESCRIPTIONS)
    return template.format(role=role, industry=industry)


# ---------------------------------------------
# SEED FUNCTIONS
# ---------------------------------------------
def seed_students(cursor, existing_emails, count=100):
    """Insert 100 students into users + students tables."""
    print(f"  Inserting {count} students...")
    student_ids = []
    password_hash = generate_password_hash("student123")

    for i in range(count):
        email = unique_email(existing_emails)
        cursor.execute(
            "INSERT INTO users (email, password_hash, role) VALUES (%s, %s, 'student')",
            (email, password_hash),
        )
        user_id = cursor.lastrowid

        full_name      = fake.name()
        phone          = fake.numerify("9#########")
        college        = f"{fake.last_name()} Institute of Technology, {random.choice(INDIAN_CITIES[:10])}"
        degree         = random.choice(DEGREES)
        grad_year      = random.randint(2024, 2026)
        skills         = pick_skills(random.randint(3, 6))
        resume_link    = f"https://drive.google.com/file/d/{fake.uuid4().replace('-','')[:20]}"

        cursor.execute(
            """INSERT INTO students
               (user_id, full_name, phone, college, degree, graduation_year, skills, resume_link)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (user_id, full_name, phone, college, degree, grad_year, skills, resume_link),
        )
        student_ids.append(cursor.lastrowid)

        if (i + 1) % 20 == 0:
            print(f"    -> {i + 1}/{count} students done")

    return student_ids


def seed_companies(cursor, existing_emails, count=10):
    """Insert 10 companies into users + companies tables."""
    print(f"  Inserting {count} companies...")
    company_ids = []
    password_hash = generate_password_hash("company123")

    company_names = [
        "NexGen Solutions", "TechVista India", "CloudBridge Systems",
        "InnovateSoft", "DataPulse Analytics", "SwiftByte Technologies",
        "ZenithWorks", "AgileMind Consulting", "PixelForge Studios",
        "GreenPath Ventures",
    ]

    for i in range(count):
        company_name = company_names[i]
        domain = company_name.lower().replace(" ", "").replace(".", "")[:12]
        email = f"hr@{domain}.in"
        if email in existing_emails:
            email = f"careers@{domain}.co.in"
        existing_emails.add(email)

        cursor.execute(
            "INSERT INTO users (email, password_hash, role) VALUES (%s, %s, 'company')",
            (email, password_hash),
        )
        user_id = cursor.lastrowid

        industry    = INDUSTRIES[i % len(INDUSTRIES)]
        website     = f"https://www.{domain}.in"
        location    = random.choice(INDIAN_CITIES[:10])
        description = (
            f"{company_name} is a leading player in the {industry} space, "
            f"headquartered in {location}. We are committed to innovation, "
            f"quality, and nurturing the next generation of professionals through "
            f"our internship programs."
        )

        cursor.execute(
            """INSERT INTO companies
               (user_id, company_name, industry, website, description, location)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (user_id, company_name, industry, website, description, location),
        )
        company_ids.append(cursor.lastrowid)
        print(f"    -> Company added: {company_name} ({industry})")

    return company_ids


def seed_internships(cursor, company_ids, count=50):
    """Insert 50 internships linked to existing companies."""
    print(f"  Inserting {count} internships...")
    internship_ids = []

    for i in range(count):
        company_id    = random.choice(company_ids)
        role          = random.choice(INTERNSHIP_ROLES)
        industry      = random.choice(INDUSTRIES)
        description   = build_description(role, industry)
        location      = random.choice(INDIAN_CITIES)
        duration      = random.choice(DURATIONS)
        stipend       = random.choice(STIPENDS)
        skills_req    = pick_skills(random.randint(3, 5))
        openings      = random.randint(1, 10)
        is_active     = random.choices([1, 0], weights=[85, 15])[0]  # 85% active
        days_ahead    = random.randint(7, 60)

        cursor.execute(
            """INSERT INTO internships
               (company_id, title, description, location, duration, stipend,
                skills_required, openings, deadline, is_active)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s,
                       DATE_ADD(CURDATE(), INTERVAL %s DAY), %s)""",
            (company_id, role, description, location, duration, stipend,
             skills_req, openings, days_ahead, is_active),
        )
        internship_ids.append(cursor.lastrowid)

        if (i + 1) % 10 == 0:
            print(f"    -> {i + 1}/{count} internships done")

    return internship_ids


def seed_applications(cursor, student_ids, internship_ids, count=200):
    """Insert 200 applications avoiding duplicates (student+internship unique)."""
    print(f"  Inserting up to {count} applications (skipping duplicates)...")

    # Pre-fetch student degree/skills for cover letters
    cursor.execute("SELECT id, degree, skills FROM students")
    student_info = {row[0]: {"degree": row[1] or "B.Tech", "skills": row[2] or "Python, SQL"}
                    for row in cursor.fetchall()}

    # Pre-fetch internship titles
    cursor.execute("SELECT id, title FROM internships")
    internship_titles = {row[0]: row[1] for row in cursor.fetchall()}

    used_pairs = set()
    inserted = 0
    attempts = 0
    statuses = ["pending", "pending", "pending", "accepted", "rejected"]  # weighted

    while inserted < count and attempts < count * 5:
        attempts += 1
        student_db_id   = random.choice(student_ids)
        internship_id   = random.choice(internship_ids)
        pair            = (student_db_id, internship_id)

        if pair in used_pairs:
            continue  # Skip duplicate

        used_pairs.add(pair)

        info        = student_info.get(student_db_id, {})
        degree      = info.get("degree", "B.Tech CSE")
        skills      = info.get("skills", "Python, SQL")
        role        = internship_titles.get(internship_id, "Intern")
        cover_letter = build_cover_letter(degree, role, skills) if random.random() > 0.15 else ""
        status      = random.choice(statuses)

        cursor.execute(
            """INSERT INTO applications
               (student_id, internship_id, cover_letter, status)
               VALUES (%s, %s, %s, %s)""",
            (student_db_id, internship_id, cover_letter, status),
        )
        inserted += 1

        if inserted % 50 == 0:
            print(f"    -> {inserted}/{count} applications done")

    print(f"    -> Total applications inserted: {inserted} (attempted {attempts})")
    return inserted


# ---------------------------------------------
# MAIN
# ---------------------------------------------
def main():
    print("\n" + "=" * 50)
    print("  InternHub Portal - Seed Data Script")
    print("=" * 50)

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        # Fetch existing emails to avoid duplicates
        cursor.execute("SELECT email FROM users")
        existing_emails = {row[0] for row in cursor.fetchall()}
        print(f"\n  Found {len(existing_emails)} existing user(s) in database.\n")

        # -- Students --------------------------------
        student_ids = seed_students(cursor, existing_emails, count=100)
        conn.commit()
        print(f"  [OK] {len(student_ids)} students committed.\n")

        # -- Companies -------------------------------
        company_ids = seed_companies(cursor, existing_emails, count=10)
        conn.commit()
        print(f"  [OK] {len(company_ids)} companies committed.\n")

        # -- Internships -----------------------------
        internship_ids = seed_internships(cursor, company_ids, count=50)
        conn.commit()
        print(f"  [OK] {len(internship_ids)} internships committed.\n")

        # -- Applications ----------------------------
        app_count = seed_applications(cursor, student_ids, internship_ids, count=200)
        conn.commit()
        print(f"  [OK] {app_count} applications committed.\n")

        # -- Summary ---------------------------------
        print("=" * 50)
        print("  SEED COMPLETE - Summary")
        print("=" * 50)
        for table in ("users", "students", "companies", "internships", "applications"):
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            total = cursor.fetchone()[0]
            print(f"  {table:<20} -> {total:>4} rows")
        print("=" * 50)
        print("\n  Login credentials for seeded accounts:")
        print("  Students  -> any student email  | password: student123")
        print("  Companies -> any company email  | password: company123")
        print("\n  Tip: Run `SELECT email FROM users WHERE role='student' LIMIT 5;`")
        print("       in MySQL to find student emails.\n")

    except Exception as e:
        conn.rollback()
        print(f"\n  [ERROR] {e}")
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
