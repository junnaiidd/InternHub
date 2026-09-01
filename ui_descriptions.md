# CHAPTER 7: SCREENSHOTS AND UI DESCRIPTION

This chapter provides a detailed, comprehensive description of the user interface (UI) design, visual layout, and responsive components of the Online Internship Portal Management System. Designed using a warm editorial minimalist design system, the interface leverages a Scandinavian-inspired color palette consisting of warm cream/taupe backgrounds (`#EDE7DC`), soft ivory surface cards (`#FAF7F2`), premium burnt terracotta accents (`#C85C27`), and sophisticated mossy sage green indicators (`#5B755F`), contrasted with warm dark charcoal typography (`#252422`). The frontend is built using HTML5, Bootstrap 5, custom CSS variables, and Jinja2 templating, ensuring full responsive adaptation across desktops, laptops, tablets, and mobile devices.

---

## 7.1 Home Page
The Home Page serves as the primary landing gateway and brand ambassador for the InternHub platform. It features a floating, translucent warm-cream navigation bar (`#mainNav`) at the top, embedded with a Gaussian blur filter to provide a modern glassmorphism effect, showcasing the bold editorial logo brandmark `InternHub` next to a solid terracotta briefcase icon (`bi-briefcase-fill`). The primary hero section follows a fluid asymmetric grid: the left side displays a bold, low-weight Outfit font title "Find Your Perfect **Internship**" with terracotta highlights, followed by a warm mocha-charcoal paragraph description and dual pill-shaped action buttons ("Get Started Free" in primary terracotta and "Sign In" in custom light outline). The right side of the desktop view displays an interactive floating composition containing three bento-style cards detailing active platform metrics ("500+ Companies" with a terracotta building icon, "10K+ Students" with a sage green mortarboard icon, and "2K+ Listings" with a slate blue briefcase icon) orbiting a central solid brand emblem. Below the hero section, a full-width stats bar displays key platform metrics inside a card surface with hairline separators. The page concludes with a bento grid "How It Works" step-by-step tutorial block featuring three card items with soft-colored icon backdrops (orange-soft, green-soft, and blue-soft) and large decorative numbers, leading into a centered call-to-action (CTA) jumbotron block and a sticky, minimal footer. The entire layout adapts seamlessly to mobile viewports by collapsing the floating illustrations and stacking grids vertically.

```
+-----------------------------------------------------------------------------------+
|  [icon] InternHub                     ThemeToggle   Dashboard  Browse  [Logout]   |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|   🚀 Launch Your Career                                  +-------------------+    |
|   Find Your Perfect                                      | [icon] 500+ Comp. |    |
|   Internship                                             +-------------------+    |
|                                                                                   |
|   Connect with top companies, build real-world             +---------------+      |
|   experience, and kickstart your career.                   |  [icon] 10K+  |      |
|                                                            +---------------+      |
|   [Get Started Free]   [Sign In]                                                  |
|                                                                                   |
+-----------------------------------------------------------------------------------+
|        500+ Companies  |  10K+ Placements  |  2K+ Active  |  95% Match            |
+-----------------------------------------------------------------------------------+
```
*Figure 7.1: Home Page Interface*

---

## 7.2 Login Page
    The Login Page provides a secure, minimal, and visually engaging entry interface for all registered users of the system. It is implemented using a cinematic split-screen responsive layout (`auth-split-container`) that occupies the full screen height. The left panel is a dedicated warm sand-cream branding panel (`auth-split-left`) that serves to reinforce platform value, displaying the large `InternHub` logo and the header "Elevate Your Career." in Outfit font. Below this title, a vertical stack of three custom checkmark list items with terracotta check icons outlines core platform capabilities: Curated Editorial Job Openings, Direct Communication & Fast Track Application, and a Beautiful Bento Metrics Control Panel. The background of this panel is embellished with organic, overlapping geometric line arches (`shape-arch-1`, `shape-arch-2`) that float subtly. The right panel is the primary forms workspace (`auth-split-right`), hosting a centered, borderless soft ivory card (`auth-card`) containing the login form. The form features two main input fields: Email Address and Password. Both fields are encapsulated within Bootstrap input groups prefixed with cozy mocha-colored background icon plates (a standard envelope icon for email and a padlock icon for password), and the password label includes an inline, high-contrast terracotta link for password recovery. Below the inputs, a primary terracotta submit button labeled "Sign In" with a slide-in box-arrow icon stretches across the card, followed by a hairline separator line and a secondary white outline button labeled "Create New Account" for unregistered visitors. On tablet and mobile viewports, the media queries automatically hide the left branding panel and scale the right form card to full width for a seamless touch-screen login experience.

```
+------------------------------------------+----------------------------------------+
|                                          |                                        |
|  [icon] InternHub                        |            Welcome Back                |
|                                          |            Sign in to your account     |
|  Elevate Your Career.                    |                                        |
|                                          |  EMAIL ADDRESS                         |
|  [check] Curated Editorial Openings      |  [ [env-icon] | you@example.com      ] |
|  [check] Direct & Fast Applications      |                                        |
|  [check] Bento Metrics Control Panel     |  PASSWORD            Forgot password?  |
|                                          |  [ [lock-icon]| Your password        ] |
|               /----\                     |                                        |
|              /      \                    |  [            Sign In               ]  |
|             |  arch  |                   |                                        |
|                                          |  ------------- or -------------------  |
|                                          |  [       Create New Account         ]  |
+------------------------------------------+----------------------------------------+
```
*Figure 7.2: Login Page Interface*

---

## 7.3 Registration Page
The Registration Page features the same cohesive, full-height cinematic split-screen architecture as the login interface, maintaining styling and aesthetic consistency. The left-hand branding panel (`auth-split-left`) welcomes users with the bold display header "Discover. Connect. Grow.", three bulleted benefit descriptions, and floating organic arch shapes. The right-hand form workspace (`auth-split-right`) features a centered soft cream card containing a dynamic, role-adaptive sign-up form. At the top of the form, the User Type Selector provides a highly intuitive choice between two account types via large, custom radio cards ("Student" displaying a mortarboard icon and "Company" displaying a building icon). These cards use custom JavaScript to dynamically update their borders to active terracotta and their backgrounds to Mocha-sand, providing instant interactive feedback. Below the role selector, the form includes three core text inputs: Email Address, Password, and Confirm Password, all styled with elegant Bootstrap input groups and icon prefixes. Below these fields, a dynamic container toggles field displays based on the chosen role: when Student is active, it reveals custom inputs for Full Name, College/University, and Degree/Major; when Company is active, it reveals fields for Company Name and Industry. The form concludes with a prominent terracotta primary button labeled "Create Account" and a secondary outline navigation button labeled "Sign In Instead". On mobile displays, the split layout collapses gracefully, displaying a unified registration card that dynamically slides fields into view as the user toggles roles.

```
+------------------------------------------+----------------------------------------+
|                                          |             Get Started                |
|  [icon] InternHub                        |                                        |
|                                          |  CHOOSE YOUR ACCOUNT TYPE              |
|  Discover. Connect.                      |  +------------------+----------------+ |
|  Grow.                                   |  |  [icon] Student  | [icon] Company | |
|                                          |  +------------------+----------------+ |
|  [check] Curated Editorial Openings      |                                        |
|  [check] Direct & Fast Applications      |  EMAIL ADDRESS                         |
|  [check] You@example.com                 |  [ [env-icon] | you@example.com      ] |
|                                          |                                        |
|                                          |  FULL NAME *                           |
|                                          |  [ [user-icon]| John Doe             ] |
|                                          |                                        |
|                                          |  [          Create Account          ]  |
+------------------------------------------+----------------------------------------+
```
*Figure 7.3: Registration Page Interface*

---

## 7.4 Student Dashboard
The Student Dashboard provides authenticated students with a highly organized, centralized control center to manage their profiles, explore active internships, and track ongoing applications. The page is introduced by a prominent page header displaying a solid terracotta mortarboard icon (`bi-mortarboard-fill`) and a customized welcome greeting displaying the logged-in student's full name. Below this header, the layout opens into a modern bento grid system consisting of a profile card and a quick stats block. The left column is a high-contrast profile summary card containing a dynamic initials bubble avatar, full name, email, college, and degree badge styled in warm student accent colors (`role-student`). The right column contains a grid of four clickable bento-style stats cards detailing key application metrics: Total Applied (slate blue icon), Accepted (moss green icon), Pending (peach icon), and Rejected (orange-soft icon). Below the bento grid is a row of pill-shaped quick action buttons allowing students to instantly "Browse Internships" (solid terracotta button), view "Saved Internships" (outline button with terracotta heart icon), or "Edit Profile" (outline button with slate blue pencil icon). The lower half of the dashboard contains a large card holding the "My Applications" table. This custom table features clean columns: Role/Company (showing a golden "Edited" badge if modified by the student), Location, Stipend, Date Applied, Last Updated, and Status (represented by emoji-prefixed status badges: pending ⏳, accepted ✅, rejected ❌), along with an Actions column containing eye and edit icons. On mobile screens, the table transforms into responsive individual cards that prevent horizontal scrolling and maintain readability.

```
+-----------------------------------------------------------------------------------+
|  [mortarboard-icon] Student Dashboard                                             |
|  Welcome back, John Doe                                                           |
+-------------------------------------+---------------------------------------------+
|                                     |  +--------------------+------------------+  |
|  +-------------------------------+  |  | [blue] Total: 12   | [green] Acc: 2   |  |
|  |             [ J ]             |  |  +--------------------+------------------+  |
|  |           John Doe            |  |  | [peach] Pend: 8    | [orange] Rej: 2  |  |
|  |  [icon] john@example.com      |  |  +--------------------+------------------+  |
|  |  [badge] B.Tech CSE           |  |                                             |
|  +-------------------------------+  |  [Browse Opportunities]  [Saved]  [Edit]    |
+-------------------------------------+---------------------------------------------+
|  MY APPLICATIONS                                                                  |
|  +-----------------------------------------------------------------------------+  |
|  | Company & Role           | Location     | Applied    | Status     | Actions |  |
|  +--------------------------+--------------+------------+------------+---------+  |
|  | TechCorp (Python Intern) | Bengaluru    | 24 May 26  | ⏳ Pending | [eye]   |  |
|  +--------------------------+--------------+------------+------------+---------+  |
+-----------------------------------------------------------------------------------+
```
*Figure 7.4: Student Dashboard Interface*

---

## 7.5 Company Dashboard
The Company Dashboard serves as a comprehensive recruiter workspace, allowing partner companies to post internship opportunities, manage listings, and review incoming candidate applications. The page is topped by a bold display header containing a terracotta building icon (`bi-building-fill`) and a subtitle indicating the authenticated recruiter's corporate profile. Below the header is a rectangular grid of four responsive metrics cards: Total Listings (with a slate blue briefcase icon), Active Listings (with a moss green check icon), Total Applicants (with a peach people-fill icon), and Headquarters Location (with an orange pin icon displaying the company's regional base). Below these cards, a row of button controls enables recruiters to immediately "Post New Internship" (solid terracotta primary button) or "Edit Profile". The primary content container is the "Your Internship Listings" card, housing a data table with columns for Listing Title, Location, Stipend, Deadline, Applicants count (represented by a cozy blue-soft badge), Listing Status (Active/Closed toggle badge), and Actions. The Actions column displays a custom green-bordered outline button labeled "View Applicants" with a people icon. When the dashboard is accessed from mobile devices, the table folds into elegant vertically-stacked blocks, allowing recruiters to quickly monitor applicant counts and listing statuses on the go.

```
+-----------------------------------------------------------------------------------+
|  [building-icon] Company Dashboard                                                |
|  Manage your listings for TechCorp Solutions                                      |
+-------------------+--------------------+--------------------+---------------------+
| [blue] Listings: 5| [green] Active: 4  | [peach] Applicants | [orange] HQ: Blr    |
+-------------------+--------------------+--------------------+---------------------+
|                                                                                   |
|  [Post New Internship]  [Edit Company Profile]                                    |
|                                                                                   |
|  YOUR INTERNSHIP LISTINGS                                                         |
|  +-----------------------------------------------------------------------------+  |
|  | Title                    | Stipend      | Deadline   | Applicants | Actions |  |
|  +--------------------------+--------------+------------+------------+---------+  |
|  | Python developer Intern  | INR 15k/mo   | 30 Jun 26  | 12 applied | [View]  |  |
|  +--------------------------+--------------+------------+------------+---------+  |
+-----------------------------------------------------------------------------------+
```
*Figure 7.5: Company Dashboard Interface*

---

## 7.6 Internship Listings Page
The Internship Listings Page serves as the primary discovery search engine for students seeking new opportunities. It begins with a prominent, full-width search card ("Find Your Future") styled with thick borders, a warm ivory background, and generous padding. The card houses an inline search form containing a keyword search field (with a magnifying glass icon), a location text field, a duration selection dropdown, and a solid terracotta "Filter" submit button. When active filters are applied, a dynamic summary bar appears below the search card, displaying active criteria tags (e.g. Location: Remote) alongside an outline button to "Clear Filters". Below the filters is a two-column bento-style responsive grid displaying active internships. Each internship card (`internship-card`) features a clean header displaying a circular initials avatar of the company, the internship title in bold Outfit font, a clickable building icon link to the company's profile, and a custom terracotta heart bookmark icon in the upper-right corner that scales dynamically on hover. Underneath the header, a horizontal row of rounded badges displays key metadata: Location, Duration, and Stipend (highlighted in moss green). A short description snippet follows, along with a row of required skills badges in soft peach. The card footer, separated by a light border, displays the application deadline date on the left and a "Apply Now" button on the right (or a "Applied" check badge if the student has already submitted an application).

```
+-----------------------------------------------------------------------------------+
|  Find Your Future                                                                 |
|  [ [search-icon] | Title/skills...  ] [ Location... ] [ Any Duration v] [Filter]  |
+-----------------------------------------------------------------------------------+
|  Active Filters: "Python" [x] Remote [x]                        [Clear Filters]   |
+-----------------------------------+-----------------------------------------------+
|  +-----------------------------+  |  +-----------------------------+              |
|  | [T] Python Developer Intern |  |  | [T] Backend Engineer Intern |              |
|  | TechCorp Solutions    [heart]  |  |  | TechCorp Solutions    [heart]  |              |
|  |                             |  |  |                             |              |
|  | [loc] Remote  [dur] 3 mos   |  |  | [loc] Delhi   [dur] 6 mos   |              |
|  | [stipend] INR 15k/mo        |  |  | [stipend] Unpaid            |              |
|  |                             |  |  |                             |              |
|  | [Python] [Flask] [SQL]      |  |  | [Django] [Postgres] [Git]   |              |
|  | --------------------------- |  |  | --------------------------- |              |
|  | Deadline: 30 Jun   [Applied]|  |  | Deadline: 15 Jul [Apply Now]|              |
|  +-----------------------------+  |  +-----------------------------+              |
+-----------------------------------+-----------------------------------------------+
```
*Figure 7.6: Internship Listings Page Interface*

---

## 7.7 Internship Application Page
The Internship Application Page features a highly specialized dual-panel workspace layout (`page-shell`) designed to streamline the application process. 
*   **Left-Hand Panel (Job Sidebar Summary):** Contains a prominent "Back to Internships" outline button at the top. Below this, a job details card displays the company's circular avatar, job title, and company profile link. A modern metric grid displays four detailed metadata boxes with custom icons (Location, Duration, Stipend, and Openings), followed by sections for "About the Role" and "Skills Required" badges.
*   **Right-Hand Panel (Primary Workspace):** Serves as the application form container, headed by a custom title block displaying a solid terracotta send icon (`bi-send-fill`). If the student is editing a previously submitted application, a highlighted orange alert banner is displayed to notify them. 
The form itself is organized in a two-column grid layout containing responsive text inputs: Full Name, College/University, Degree, Phone Number, CGPA/Percentage, Skills Highlighted, and Preferred Location. The Portfolio & Social Links input, Certifications textarea, and PDF Resume file input occupy two columns. If a resume is already linked, a green badge and a "View Current" link are displayed above the file input. The form concludes with a large Cover Letter textarea and a bottom button row containing a "Submit Application" button (or a "Save Changes" button that triggers a confirmation modal) and a "Cancel" button.

```
+-----------------------------------+-----------------------------------------------+
|  [<- Back to Internships]         |  [send-icon] Submit Your Application          |
+-----------------------------------+-----------------------------------------------+
|  +-----------------------------+  |  FULL NAME *            COLLEGE *             |
|  | [T] Python Developer Intern |  |  [ John Doe          ]  [ IIT Bombay        ] |
|  | TechCorp Solutions          |  |                                               |
|  |                             |  |  DEGREE *               PHONE NUMBER *        |
|  | Location:    Duration:      |  |  [ B.Tech CSE        ]  [ 9876543210        ] |
|  | [ Remote ]   [ 3 Months ]   |  |                                               |
|  |                             |  |  PORTFOLIO & SOCIAL LINKS                     |
|  | Stipend:     Openings:      |  |  [ github.com/johndoe, linkedin.com/in/doe  ] |
|  | [ 15k/mo ]   [ 3 openings ] |  |                                               |
|  |                             |  |  RESUME (PDF ONLY)                            |
|  | About: Work on real-world   |  |  [Choose File] No file chosen                 |
|  | Flask and Django projects.. |  |                                               |
|  +-----------------------------+  |  [Submit Application]           [Cancel]      |
+-----------------------------------+-----------------------------------------------+
```
*Figure 7.7: Internship Application Page Interface*

---

## 7.8 View Applications Page
The View Applications Page provides companies with a detailed candidate management dashboard. It includes a back navigation button and a page header titled "Applicants Overview", which displays a terracotta people icon and a count of current applicants. Below the header, a two-column responsive grid displays applicants in individual cards. Each card features:
*   **Header:** Dynamic initials avatar bubble, applicant's full name (with a golden "Edited" badge if modified by the student), email address, and a role-colored status badge (pending ⏳, accepted ✅, rejected ❌).
*   **Body:** A vertical list of applicant credentials (college, degree, telephone, CGPA, and preferred location with map pin), followed by a list of skills badges and custom tags for portfolio links with hyperlink icons. The certifications list is displayed inside a custom mocha card, and the cover letter is enclosed in a stylized container with a terracotta left border.
*   **Footer:** A wide "View Resume (PDF)" outline button with a terracotta PDF icon. Below this, dynamic action buttons allow recruiters to manage the application: pending applications display an olive-green "Accept" button and an outline "Reject" button; accepted or rejected applications display status confirmation messages alongside a "Revoke" or "Move to Pending" button.

```
+-----------------------------------------------------------------------------------+
|  [<- Back to Dashboard]                                                           |
|  [people-icon] Applicants Overview                                                |
|  Role: Python Developer Intern &mdash; [ 2 applicants ]                           |
+-----------------------------------+-----------------------------------------------+
|  +-----------------------------+  |  +-----------------------------+              |
|  | [ J ] John Doe   [⏳ Pending]|  |  | [ S ] Sarah Smith  [✅ Accepted]            |
|  | john@example.com            |  |  | sarah@example.com           |              |
|  |                             |  |  |                             |              |
|  | [build] IIT Bombay (B.Tech) |  |  | [build] NIT Trichy (M.Tech) |              |
|  | [phone] 9876543210  [cg] 9.1|  |  | [phone] 9988776655  [cg] 9.5|              |
|  |                             |  |  |                             |              |
|  | Skills: [Python] [SQL]      |  |  | Skills: [Django] [Postgres] |              |
|  | Portfolio: [git] [linkedin] |  |  | Portfolio: [git]            |              |
|  |                             |  |  |                             |              |
|  | Cover Letter: "I am..."     |  |  | Cover Letter: "Excited..."  |              |
|  |                             |  |  |                             |              |
|  | [ [icon] View Resume (PDF) ]|  |  | [ [icon] View Resume (PDF) ]|              |
|  | --------------------------- |  |  | --------------------------- |              |
|  | [  Accept  ]  [  Reject  ]  |  |  | [✅ Accepted]      [Revoke] |              |
|  +-----------------------------+  |  +-----------------------------+              |
+-----------------------------------+-----------------------------------------------+
```
*Figure 7.8: View Applications Page Interface*

---

## 7.9 Admin Dashboard
The Admin Dashboard serves as the central control room for administrators, providing platform-wide oversight and analytics. The page is introduced by a page header displaying a shield-check icon (`bi-shield-fill-check`) and a subtitle. Below this, a stats bar features four admin metrics cards: Students (slate blue icon), Companies (green icon), Active Listings (peach icon), and Total Applications (orange icon). Below these cards, a row of action buttons provides options to "Manage Users", "Manage Internships", or trigger platform simulations ("Simulate Weekly Digest" and "Simulate Deadline Alerts"). The central section of the dashboard features a two-column charts block:
*   **User Distribution Card:** Displays a Chart.js doughnut chart comparing students and companies using slate blue and moss green slices.
*   **Application Status Card:** Displays a Chart.js bar chart showing status counts with soft-colored, rounded bars. 
The charts are styled with custom typography and dynamically update their grid lines and color schemes to match the system-wide light/dark mode theme. The page concludes with a card displaying a "Recently Registered Users" table, which lists the latest 10 signups (ID, Email, Role badge, and Join timestamp).

```
+-----------------------------------------------------------------------------------+
|  [shield-icon] Admin Dashboard                                                    |
|  Platform management and insights overview                                        |
+-------------------+--------------------+--------------------+---------------------+
| [blue] Stud: 120  | [green] Comp: 15   | [peach] Active: 45 | [orange] Apps: 210  |
+-------------------+--------------------+--------------------+---------------------+
|                                                                                   |
|  [Manage Users]  [Manage Internships]  |  [Sim. Digest]  [Sim. Alerts]            |
|                                                                                   |
|  +-----------------------------+  |  +-----------------------------+              |
|  | USER DISTRIBUTION           |  |  | APPLICATION STATUS          |              |
|  |        /-----\              |  |  |  |                           |              |
|  |       /  o    \             |  |  |  | [peach]                   |              |
|  |      |   o     |            |  |  |  | [peach] [green]           |              |
|  |       \       /             |  |  |  | [peach] [green] [orange]  |              |
|  |        \-----/              |  |  |  +-------------------------  |              |
|  +-----------------------------+  |  +-----------------------------+              |
+-----------------------------------+-----------------------------------------------+
|  RECENT REGISTRATIONS                                                             |
|  +-----------------------------------------------------------------------------+  |
|  | ID  | Email                 | Role               | Joined                   |  |
|  +-----+-----------------------+--------------------+--------------------------+  |
|  | 241 | student@example.com   | Student            | 25 May 2026, 15:42       |  |
|  +-----+-----------------------+--------------------+--------------------------+  |
+-----------------------------------------------------------------------------------+
```
*Figure 7.9: Admin Dashboard Interface*
