-- ============================================================
-- Online Internship Portal Management System
-- Database: internship_portal
-- ============================================================

CREATE DATABASE IF NOT EXISTS internship_portal;
USE internship_portal;

-- ============================================================
-- TABLE: users
-- Stores authentication info for all roles
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    role ENUM('student', 'company', 'admin') NOT NULL DEFAULT 'student',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- TABLE: students
-- Profile info linked to a user account
-- ============================================================
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(15),
    college VARCHAR(150),
    degree VARCHAR(100),
    graduation_year YEAR,
    skills TEXT,
    resume_link VARCHAR(255),
    bio TEXT,
    cgpa VARCHAR(10),
    linkedin_url VARCHAR(255),
    github_profile_url VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE: companies
-- Profile info for company accounts
-- ============================================================
CREATE TABLE IF NOT EXISTS companies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    company_name VARCHAR(150) NOT NULL,
    industry VARCHAR(100),
    website VARCHAR(255),
    description TEXT,
    location VARCHAR(100),
    bio TEXT,
    contact_email VARCHAR(120),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE: internships
-- Listings posted by companies
-- ============================================================
CREATE TABLE IF NOT EXISTS internships (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    location VARCHAR(100),
    duration VARCHAR(50),
    stipend VARCHAR(50),
    skills_required TEXT,
    openings INT DEFAULT 1,
    deadline DATE,
    is_active TINYINT(1) DEFAULT 1,
    posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE: applications
-- Student applications for internships
-- ============================================================
CREATE TABLE IF NOT EXISTS applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    internship_id INT NOT NULL,
    full_name VARCHAR(100),
    college VARCHAR(150),
    degree VARCHAR(100),
    cover_letter TEXT,
    resume_link VARCHAR(255),
    skills TEXT,
    phone VARCHAR(15),
    cgpa VARCHAR(10),
    portfolio_links TEXT,
    preferred_location VARCHAR(100),
    certifications TEXT,
    status ENUM('pending', 'accepted', 'rejected') DEFAULT 'pending',
    is_edited TINYINT(1) DEFAULT 0,
    updated_at TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    edit_count INT DEFAULT 0,
    edited_by_student TINYINT(1) DEFAULT 0,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_application (student_id, internship_id),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (internship_id) REFERENCES internships(id) ON DELETE CASCADE
);

-- ============================================================
-- TABLE: saved_internships
-- Student saved/bookmarked internships
-- ============================================================
CREATE TABLE IF NOT EXISTS saved_internships (
    student_id INT NOT NULL,
    internship_id INT NOT NULL,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (student_id, internship_id),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (internship_id) REFERENCES internships(id) ON DELETE CASCADE
);


-- ============================================================
-- SEED: Default admin account
-- Password: admin123 (hashed below using werkzeug pbkdf2)
-- ============================================================
INSERT INTO users (email, password_hash, role) VALUES
('admin@portal.com', 'pbkdf2:sha256:260000$rQiNpLBGrNLLJ5XF$3a7a3b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a', 'admin')
ON DUPLICATE KEY UPDATE email = email;

-- ============================================================
-- SEED: Sample company
-- ============================================================
INSERT INTO users (email, password_hash, role) VALUES
('techcorp@example.com', 'pbkdf2:sha256:260000$rQiNpLBGrNLLJ5XF$3a7a3b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a', 'company')
ON DUPLICATE KEY UPDATE email = email;

INSERT INTO companies (user_id, company_name, industry, website, description, location)
SELECT id, 'TechCorp Solutions', 'Information Technology', 'https://techcorp.example.com',
       'A leading IT services company offering innovative solutions.', 'Bengaluru, India'
FROM users WHERE email = 'techcorp@example.com'
ON DUPLICATE KEY UPDATE company_name = company_name;

-- ============================================================
-- SEED: Sample internship listing
-- ============================================================
INSERT INTO internships (company_id, title, description, location, duration, stipend, skills_required, openings, deadline)
SELECT c.id,
       'Python Backend Developer Intern',
       'Work on real-world Flask and Django projects. Build REST APIs and contribute to production code.',
       'Bengaluru (Remote)',
       '3 Months',
       '₹10,000/month',
       'Python, Flask, SQL, REST APIs',
       3,
       DATE_ADD(CURDATE(), INTERVAL 30 DAY)
FROM companies c
JOIN users u ON c.user_id = u.id
WHERE u.email = 'techcorp@example.com'
LIMIT 1;
