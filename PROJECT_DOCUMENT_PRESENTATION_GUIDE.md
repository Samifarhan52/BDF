# 🩸 LifePulse - Blood Donor Finder Platform
## Comprehensive Academic Project Report & Presentation Guide
**Department of Computer Science & Engineering / Information Technology**  
**Course:** Final Year / Capstone Engineering Project  
**Project Title:** LifePulse — Real-Time Medical Blood Matching, Emergency Fulfillment, and Spatial Donor Network  
**GitHub Repository:** [https://github.com/Samifarhan52/BDF](https://github.com/Samifarhan52/BDF)

---

## 📑 Table of Contents
1. [Executive Summary & Abstract](#1-executive-summary--abstract)
2. [Problem Statement & Real-World Motivation](#2-problem-statement--real-world-motivation)
3. [Technology Stack & Architectural Rationale](#3-technology-stack--architectural-rationale)
4. [System Architecture & Core Modules](#4-system-architecture--core-modules)
5. [Database Design & ER Schema](#5-database-design--er-schema)
6. [Algorithms & Mathematical Formulations](#6-algorithms--mathematical-formulations)
7. [Step-by-Step Guide: How to Run in VS Code](#7-step-by-step-guide-how-to-run-in-vs-code)
8. [Slide-by-Slide Presentation Script (For College Review)](#8-slide-by-slide-presentation-script-for-college-review)
9. [Viva Voce: Top 10 Questions & Model Answers](#9-viva-voce-top-10-questions--model-answers)
10. [Future Scope & Production Roadmap](#10-future-scope--production-roadmap)

---

## 1. Executive Summary & Abstract

In acute trauma cases, surgical emergencies, and oncological therapies, blood product transfusion within the clinical "golden hour" is critical to survival. Traditional blood finding mechanisms rely on fragmented social media appeals, physical registries, or static phone directories with stale contact records and zero availability awareness.

**LifePulse** is an enterprise-grade emergency blood donor network engineered to solve this latency. Built using **Python 3, Flask, SQLite3, Tailwind CSS, Leaflet.js, and FontAwesome 6**, LifePulse provides:
- **Instant Medical Compatibility Matching**: An algorithmic engine that cross-references recipient ABO and Rh antigen compatibility (e.g. Universal Donor $O^-$, Universal Recipient $AB^+$) to eliminate wasted contact attempts.
- **Dynamic Availability Toggling**: An interactive presence beacon allowing verified donors to transition between *Available* and *Unavailable* in real time.
- **Trackable Emergency Unit Fulfillment**: A hospital broadcast board where critical cases display real-time pledge meters (e.g. *1 of 2 Units Secured*), enabling donors to volunteer and hospital coordinators to track pledges.
- **Spatial Radius & Interactive GIS Mapping**: Real-time geolocation detection paired with OpenStreetMap/Leaflet integration for geographic distance calculations using the Haversine formula.
- **Hospital Blood Bank Inventory Monitoring**: Real-time stock status across regional healthcare centers.

---

## 2. Problem Statement & Real-World Motivation

### 2.1 The Critical Healthcare Bottlenecks
1. **High Latency in Donor Outreach**: Relatives of emergency trauma patients lose valuable hours calling obsolete donor directories.
2. **Biological Incompatibility Risks**: Searching only for identical blood groups in emergencies ignores medically compatible alternatives (such as $O^-$ universal red blood cells for $A^+$ or $B^+$ recipients).
3. **Donor Burnout & Disturbance**: Volunteers receive emergency calls during work, exams, or illness because directories lack live status toggles.
4. **Lack of Fulfillment Transparency**: Multiple donors often travel to a hospital for a request that has already been resolved hours earlier.
5. **Shortage Visibility**: Surrounding clinics have no transparent insight into neighboring blood bank stock depletion.

### 2.2 Project Objectives
- Build a lightweight, cross-platform web application with zero external server dependencies.
- Implement secure, role-based authentication (**Volunteer Donor** vs **Hospital Coordinator**).
- Enable instantaneous emergency broadcast and volunteer pledge tracking.
- Provide self-screening clinical questionnaires to enforce safety intervals (56 days whole blood interval).

---

## 3. Technology Stack & Architectural Rationale

| Component | Technology Selected | Version | Academic / Technical Rationale |
| :--- | :--- | :--- | :--- |
| **Backend Framework** | **Python / Flask** | 3.1.3 | Lightweight WSGI micro-framework, low memory footprint, native REST support, fast request-response cycle. |
| **Database** | **SQLite 3** | Embedded | Zero-configuration, ACID-compliant, serverless, native to Python's standard library. Ideal for portable deployment and college demonstration. |
| **Authentication & Security** | **Werkzeug Security** | 3.1.0 | Salted password hashing via `pbkdf2:sha256` preventing rainbow table attacks; secure session cookie signing. |
| **Frontend Styling** | **Tailwind CSS** | 3.x CDN | Utility-first CSS allowing custom medical-grade responsive layouts with zero build step overhead. |
| **Official Icons** | **FontAwesome 6** | 6.5.1 CDN | Professional clinical and emergency iconography (`truck-medical`, `droplet`, `heart-pulse`, `hospital`). |
| **GIS Mapping** | **Leaflet.js & OpenStreetMap** | 1.9.4 | Open-source interactive spatial mapping without API keys, credit card billing, or rate limits. |
| **Templating Engine** | **Jinja2** | 3.1.6 | Server-side template rendering with template inheritance (`base.html`), contextual processors, and safe XSS escaping. |
| **Version Control** | **Git & GitHub** | - | Structured commits, automated `.gitignore`, cloud backup. |

---

## 4. System Architecture & Core Modules

```
                             [ WEB BROWSER / CLIENT ]
                                        │
           ┌────────────────────────────┼────────────────────────────┐
           ▼                            ▼                            ▼
   [ Desktop Browser ]          [ Mobile Drawer ]           [ Geolocation API ]
           │                            │                            │
           └────────────────────────────┼────────────────────────────┘
                                        │ HTTP Requests (REST / Jinja2)
                                        ▼
                      ┌───────────────────────────────────┐
                      │    FLASK WSGI SERVER (app.py)     │
                      ├───────────────────────────────────┤
                      │  • Session & Role Middleware      │
                      │  • Haversine Distance Engine      │
                      │  • ABO/Rh Compatibility Engine    │
                      │  • Emergency Broadcast Router     │
                      └─────────────────┬─────────────────┘
                                        │
                       ┌────────────────┴────────────────┐
                       ▼                                 ▼
             [ SQLite DATABASE ]               [ CLIENT RESPONSES ]
             • users                           • Server-rendered HTML
             • donors                          • JSON API endpoints
             • urgent_requests                 • Leaflet Map Markers
             • request_responses
             • blood_banks
```

### Module 1: Authentication & Role-Based Access Control (RBAC)
- **Donor Role**: Can access personalized dashboard, digital donor ID card, medical eligibility countdown, and view emergency commitments.
- **Hospital Coordinator Role**: Can post emergency requests with urgency levels, monitor responding donors with contact hotlines, and mark emergencies as fulfilled.
- **One-Click Demo Evaluator**: Fast-login autofill buttons (`nihil` for donor, `Dr. Sarah Jenkins` for hospital).

### Module 2: Medical ABO/Rh Compatibility Matching Engine
The system contains an embedded directed graph of human red blood cell compatibility:
- **Recipient Compatibility Map**:
  - $A^+ \leftarrow [A^+, A^-, O^+, O^-]$
  - $A^- \leftarrow [A^-, O^-]$
  - $B^+ \leftarrow [B^+, B^-, O^+, O^-]$
  - $B^- \leftarrow [B^-, O^-]$
  - $AB^+ \leftarrow [A^+, A^-, B^+, B^-, AB^+, AB^-, O^+, O^-]$ *(Universal Recipient)*
  - $AB^- \leftarrow [AB^-, A^-, B^-, O^-]$
  - $O^+ \leftarrow [O^+, O^-]$
  - $O^- \leftarrow [O^-]$ *(Universal Donor)*
- A checkbox filter allows search queries to automatically expand from exact matches to medically safe alternatives.

### Module 3: Spatial Distance & Interactive Leaflet GIS Engine
- Uses HTML5 Geolocation (`navigator.geolocation`) with fallback coordinates.
- Calculates great-circle geographic distance between coordinates in kilometers.
- Renders custom SVG map markers:
  - Red circular badges with blood groups for verified donors.
  - Dark medical pins for hospitals and emergency cases with click-to-call popups.

### Module 4: Emergency Broadcast & Real-Time Fulfillment Tracker
- Hospital staff or relatives submit urgent requests with urgency priorities:
  - **CRITICAL NEED**: Immediate surgery / trauma resuscitation ($< 2$ hours).
  - **HIGH NEED**: ICU transfusion / oncology depletion ($< 6$ hours).
  - **MEDIUM NEED**: Scheduled dialysis / pre-operative reservation ($< 24$ hours).
- **Progress Tracking**: Pledged units are updated live. When volunteers confirm commitments via the `Volunteer / I Can Donate` modal, the database increments `units_fulfilled` and the UI progress bar advances in real time.

### Module 5: Clinical Eligibility & Recovery Tracker
- Implements international Red Cross blood safety standards:
  - Age: 18 to 65 years.
  - Weight: $\ge 50$ kg (110 lbs).
  - Whole Blood Recovery Interval: 56 days between successive donations.
- Evaluates the user's `last_donation_date` and computes an automated countdown badge.

### Module 6: Hospital Blood Bank Reserves Directory
- Monitors real-time regional blood stocks across 5 blood groups ($O^-, O^+, A^+, B^+, AB^+$) with categorical inventory indicators:
  - **NORMAL** (Adequate reserves)
  - **LOW** (Targeted volunteer drive recommended)
  - **CRITICAL** (Urgent shortage broadcast)

---

## 5. Database Design & ER Schema

The database (`blood_donor.db`) is structured with 5 relational entities:

### Entity 1: `users` (Account & Authentication)
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique user identifier |
| `name` | TEXT | NOT NULL | Full name of donor or coordinator |
| `email` | TEXT | UNIQUE NOT NULL | Login credential |
| `password_hash` | TEXT | NOT NULL | Salted PBKDF2:SHA256 password hash |
| `role` | TEXT | DEFAULT 'donor' | 'donor' or 'hospital' |
| `blood_group` | TEXT | - | ABO/Rh group (e.g. 'O+', 'A-') |
| `phone` | TEXT | - | Contact telephone number |
| `city` | TEXT | - | Primary residential city |
| `state` | TEXT | - | State / province |
| `weight_kg` | REAL | DEFAULT 65.0 | Clinical screening weight |
| `last_donation_date` | TEXT | - | ISO date (YYYY-MM-DD) |
| `is_available` | INTEGER | DEFAULT 1 | 1 = Available, 0 = Offline |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |

### Entity 2: `donors` (Public Search Directory)
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique donor record ID |
| `user_id` | INTEGER | FOREIGN KEY &rarr; `users(id)` | Associated user account (optional) |
| `name` | TEXT | NOT NULL | Display name |
| `blood_group` | TEXT | NOT NULL | ABO/Rh blood type |
| `age` | INTEGER | - | Donor age |
| `gender` | TEXT | - | Gender |
| `phone` | TEXT | NOT NULL | Emergency phone number |
| `email` | TEXT | - | Email address |
| `city` | TEXT | NOT NULL | City location |
| `state` | TEXT | - | State code |
| `latitude` | REAL | - | Decimal latitude for GIS maps |
| `longitude` | REAL | - | Decimal longitude for GIS maps |
| `last_donation_date` | TEXT | - | Last donation recorded |
| `is_available` | INTEGER | DEFAULT 1 | Search filter status flag |
| `is_verified` | INTEGER | DEFAULT 1 | Identity verification badge |
| `donations_count` | INTEGER | DEFAULT 1 | Historical donation count |

### Entity 3: `urgent_requests` (Emergency Needs)
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Emergency request identifier |
| `patient_name` | TEXT | NOT NULL | Patient requiring transfusion |
| `blood_group` | TEXT | NOT NULL | Required blood type |
| `units_needed` | INTEGER | NOT NULL | Target units required |
| `units_fulfilled` | INTEGER | DEFAULT 0 | Count of units pledged by donors |
| `urgency_level` | TEXT | NOT NULL | 'CRITICAL NEED', 'HIGH NEED', 'MEDIUM NEED' |
| `hospital_name` | TEXT | NOT NULL | Receiving medical facility |
| `city` | TEXT | NOT NULL | Hospital municipality |
| `hotline` | TEXT | NOT NULL | 24/7 direct telephone line |
| `notes` | TEXT | - | Surgery or clinical trauma notes |
| `latitude` | REAL | - | Hospital GIS latitude |
| `longitude` | REAL | - | Hospital GIS longitude |
| `status` | TEXT | DEFAULT 'ACTIVE' | 'ACTIVE' or 'FULFILLED' |
| `posted_by` | TEXT | - | Coordinator or ward name |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Broadcast timestamp |

### Entity 4: `request_responses` (Fulfillment Pledges)
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Pledge transaction ID |
| `request_id` | INTEGER | FOREIGN KEY &rarr; `urgent_requests(id)` | Associated emergency request |
| `donor_name` | TEXT | NOT NULL | Volunteer name |
| `donor_email` | TEXT | NOT NULL | Contact email |
| `blood_group` | TEXT | NOT NULL | Volunteer blood type |
| `phone` | TEXT | NOT NULL | Hotline for hospital coordinator |
| `units_pledged` | INTEGER | DEFAULT 1 | Number of units committed |
| `status` | TEXT | DEFAULT 'PLEDGED' | 'PLEDGED', 'COMPLETED', 'CANCELLED' |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Pledge timestamp |

### Entity 5: `blood_banks` (Institutional Inventory)
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Institution ID |
| `name` | TEXT | NOT NULL | Hospital or blood center name |
| `city` | TEXT | NOT NULL | Municipality |
| `address` | TEXT | NOT NULL | Physical street address |
| `phone` | TEXT | NOT NULL | Blood bank direct hotline |
| `stock_o_neg` | TEXT | - | O- inventory gauge |
| `stock_o_pos` | TEXT | - | O+ inventory gauge |
| `stock_a_pos` | TEXT | - | A+ inventory gauge |
| `stock_b_pos` | TEXT | - | B+ inventory gauge |
| `stock_ab_pos` | TEXT | - | AB+ inventory gauge |
| `operating_hours` | TEXT | - | Operational schedule (e.g. 24/7) |

---

## 6. Algorithms & Mathematical Formulations

### 6.1 Haversine Distance Formula
To compute geodesic spatial distance between recipient coordinates $(\phi_1, \lambda_1)$ and donor coordinates $(\phi_2, \lambda_2)$ on a spherical Earth of radius $R = 6371.0 \text{ km}$:

$$\Delta \phi = \phi_2 - \phi_1, \quad \Delta \lambda = \lambda_2 - \lambda_1$$

$$a = \sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta \lambda}{2}\right)$$

$$c = 2 \cdot \operatorname{atan2}\left(\sqrt{a}, \sqrt{1-a}\right)$$

$$d = R \cdot c$$

In Python:
```python
def haversine_distance(lat1, lon1, lat2, lon2):
    if not (lat1 and lon1 and lat2 and lon2):
        return None
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)
```

### 6.2 Password Hashing (PBKDF2-HMAC-SHA256)
Passwords are never stored in plaintext. They undergo key derivation:
$$\text{Hash} = \operatorname{PBKDF2}(\text{HMAC-SHA256}, \text{password}, \text{salt}, c = 1000000)$$
This ensures security against brute-force attacks.

### 6.3 Clinical Recovery Interval Calculation
$$\Delta t = (\text{Last Donation Date} + 56 \text{ days}) - \text{Current Date}$$
$$\text{Is Eligible} = 
\begin{cases} 
\text{True}, & \text{if } \Delta t \le 0 \\ 
\text{False}, & \text{if } \Delta t > 0 
\end{cases}$$

---

## 7. Step-by-Step Guide: How to Run in VS Code

### 7.1 Prerequisites
- A Mac, Windows, or Linux computer.
- Python 3.9+ installed (`python3 --version`).
- Visual Studio Code installed.

### 7.2 Running via the Integrated Terminal (Recommended)
1. **Open VS Code**.
2. Go to **File** &rarr; **Open Folder...** (or press `Cmd + O` on Mac / `Ctrl + O` on Windows).
3. Select the folder: `/Users/apple/Desktop/BDF`.
4. Open the integrated terminal by pressing **`Ctrl + \``** (Backtick) or clicking **Terminal &rarr; New Terminal**.
5. Enter the startup command:
   ```bash
   ./run.sh
   ```
   *(Or if using standard python directly: `python3 app.py` or `./venv/bin/python app.py`)*
6. The terminal displays:
   ```
   ==========================================================
   🩸 LifePulse - Enterprise Blood Donor Finder Started
   Local URL: http://127.0.0.1:5000
   ==========================================================
   ```
7. Hold `Cmd` (or `Ctrl`) and click the link, or open any web browser and visit:  
   👉 **`http://127.0.0.1:5000`**

### 7.3 One-Click Debugging via VS Code UI (F5)
1. In VS Code, look at the left sidebar and click the **Run and Debug** icon (`Cmd + Shift + D`).
2. Make sure the dropdown says **"Python: LifePulse Web App"**.
3. Press **`F5`** (or click the green Play button).
4. The server launches and attaches automatically.

---

## 8. Slide-by-Slide Presentation Script (For College Review)

Use this structured 10-slide outline for your PowerPoint / viva demonstration:

### Slide 1: Title & Introduction
- **What to say:** *"Good morning respected evaluators. Today I present 'LifePulse' — an enterprise-grade real-time blood donor finder and emergency fulfillment tracking platform."*
- **Key point:** Connects critical patients with verified nearby donors within minutes.

### Slide 2: Problem Statement & Motivation
- **What to say:** *"During medical trauma and surgeries, every second counts. Traditional donor databases are static, 80% of contacts are unavailable, and biological compatibility is rarely calculated in real time, leading to fatal transfusion delays."*

### Slide 3: Proposed Solution & Core Innovations
- **What to say:** *"LifePulse solves this through three innovations: First, real-time presence toggling where donors switch between Available and Unavailable. Second, an algorithmic ABO/Rh compatibility engine. Third, trackable emergency fulfillment with live progress bars."*

### Slide 4: System Architecture & Technology Stack
- **What to say:** *"We selected Python Flask for its micro-service performance and low latency. The persistence layer uses ACID-compliant SQLite3 with salted PBKDF2 password hashing. The frontend utilizes Tailwind CSS, official FontAwesome icons, and Leaflet.js with OpenStreetMap for spatial rendering."*

### Slide 5: Live Demonstration — Homepage & Reference Matching
- **Action:** Open `http://127.0.0.1:5000`.
- **What to say:** *"Notice the emergency announcement bar and the status beacon in the navbar. When I click 'Status: Available', it issues an asynchronous AJAX request to our REST API, toggling the donor's presence without reloading the page."*

### Slide 6: Live Demonstration — Real-Time Matching & Compatibility
- **Action:** Select **`O-`** in **`New York`** and click **Find Available Donors**.
- **What to say:** *"The engine maps recipient antibodies against donor red cells. When 'Include medically compatible groups' is enabled, the search returns universal donors ($O^-$) alongside exact matches, sorted by verified status."*

### Slide 7: Live Demonstration — Emergency Board & Unit Fulfillment Tracking
- **Action:** Scroll to **Active Urgent Blood Needs** (`John Doe`, `Alice Wong`, `vijay`).
- **What to say:** *"Here we have pre-seeded critical cases from leading medical centers. Each card shows the required units and a live progress bar. Let me click 'Volunteer / I Can Donate' on John Doe's request. Upon pledging 1 unit, the progress bar updates to 100% and hospital staff are instantly alerted."*

### Slide 8: Live Demonstration — Authentication & Personal Dashboard
- **Action:** Click **Login** &rarr; click **Autofill 'nihil'** &rarr; click **Sign In**.
- **What to say:** *"The platform implements session-based RBAC. Here in the Donor Dashboard, we see the user's Digital Donor ID Card with a verification number and QR code. Below it, our clinical tracker calculates the exact days remaining until the safe 56-day whole-blood recovery interval."*

### Slide 9: Live Demonstration — Hospital Coordinator Portal & Blood Banks
- **Action:** Click **Logout** &rarr; Autofill **Dr. Sarah Jenkins** &rarr; click **Blood Banks**.
- **What to say:** *"In the Hospital Coordinator view, medical staff can broadcast new emergencies and review pledged volunteers. In the Blood Banks section, real-time inventory gauges show current reserves across regional trauma centers."*

### Slide 10: Conclusion & Future Scope
- **What to say:** *"LifePulse bridges the gap between emergency demand and community supply. Future milestones include automated SMS dispatch via Twilio and wearable biometric sync. Thank you. I am ready for questions."*

---

## 9. Viva Voce: Top 10 Questions & Model Answers

### Q1: Why did you choose Flask over Django or Node.js?
> **Answer:** Flask is a minimalist WSGI micro-framework that gives complete control over application architecture without the monolithic overhead of Django. For a healthcare emergency engine where rapid request-response turnaround is critical, Flask provides sub-millisecond route dispatching while keeping the code clean and maintainable.

### Q2: How does your compatibility engine prevent hemolytic transfusion reactions?
> **Answer:** Blood compatibility is governed by A, B antigens on red cells and antibodies in plasma. Transfusing incompatible red cells triggers acute immune hemolysis. Our backend maintains an adjacency list of safe donor-to-recipient mappings in the `COMPATIBILITY` data structure. For example, $AB^+$ patients have neither anti-A nor anti-B antibodies, so the engine identifies them as Universal Recipients, whereas $O^-$ cells have no A or B surface antigens and can be safely given to all groups.

### Q3: How is spatial distance calculated without expensive Google Maps API keys?
> **Answer:** We use the mathematical **Haversine Formula**, which determines the great-circle distance between two pairs of spherical coordinates (latitude and longitude) using Earth's mean radius ($6371 \text{ km}$). On the frontend, we render these coordinates via **Leaflet.js** and **OpenStreetMap**, an open-source GIS engine that requires zero proprietary API keys and has zero billing dependencies.

### Q4: How are passwords secured in the database?
> **Answer:** Passwords are never stored in plaintext. When a user registers, Werkzeug's `generate_password_hash` derives a cryptographic key using **PBKDF2 with HMAC-SHA256** and a 16-character random salt over 1,000,000 iterations. During login, `check_password_hash` recomputes the hash in constant time, preventing timing attacks and rainbow table lookups.

### Q5: What happens when an urgent blood need is fully pledged?
> **Answer:** In our database, the `urgent_requests` table stores `units_needed` and `units_fulfilled`. Each time a donor submits a pledge via `/api/respond-urgent`, an entry is recorded in `request_responses` and `units_fulfilled` is incremented. When `units_fulfilled >= units_needed`, the record's status automatically transitions from `'ACTIVE'` to `'FULFILLED'`, updating the progress bar to 100% green.

### Q6: Why did you choose SQLite over MySQL or PostgreSQL?
> **Answer:** SQLite is an ACID-compliant, self-contained relational database embedded directly inside the host process. It requires no standalone database server daemon, eliminating network latency for local reads. This makes the project portable and reliable for university evaluation, while supporting full SQL querying, indexing, and foreign key constraints.

### Q7: How does the system enforce donor health safety?
> **Answer:** The platform implements standard clinical blood banking protocols:
> 1. Donors must be 18–65 years old and weigh at least 50 kg.
> 2. The system enforces a mandatory **56-day recovery interval** between successive whole blood donations. The dashboard calculates the difference between `today` and `last_donation_date` and displays an eligibility countdown timer.
> 3. Donors must complete a self-screening health declaration (no recent tattoos, piercings, or fever within 48 hours).

### Q8: How does the presence toggle work without refreshing the page?
> **Answer:** The `Status: Available` button uses client-side JavaScript (`fetch('/api/toggle-status', { method: 'POST' })`). The server toggles the boolean `is_available` flag in the SQLite database and returns a JSON payload `{ success: true, new_status: 'Available' }`. The DOM updates the button color, text, and glowing beacon without any page reload.

### Q9: Can hospital staff see who volunteered for an emergency?
> **Answer:** Yes. When logged in under the Hospital Coordinator role (`sarah@mountsinai.org`), the dashboard aggregates records from the `request_responses` table joined with `urgent_requests`, showing the volunteer's name, blood group, contact telephone, and timestamp.

### Q10: How can this application be deployed to production?
> **Answer:** In production, Flask can be served behind **Gunicorn** (a WSGI HTTP server) with 4 worker processes reverse-proxied by **Nginx** for SSL/TLS termination. The SQLite file can either be hosted on persistent storage or migrated to PostgreSQL by changing the database connection string.

---

## 10. Future Scope & Production Roadmap

1. **Automated SMS & WhatsApp Webhook Dispatch**: Integration with Twilio / WhatsApp Business API to broadcast instant push notifications to donors within a 15 km radius.
2. **Real-Time Drone Blood Delivery Tracking**: Visualizing blood product transit from central blood banks to rural clinics via WebSockets.
3. **Biometric Integration**: Syncing with smartwatches (Apple HealthKit / Google Fit) to verify donor resting heart rate and hemoglobin estimates prior to donation.
4. **Decentralized Transfusion Ledger**: Recording donation records on a permissioned blockchain to eliminate counterfeit donor certification.

---
**Report Prepared for:** Final Year Engineering Presentation & Project Evaluation  
**Author:** Sami Farhan (`Samifarhan52`)  
**Repository:** [https://github.com/Samifarhan52/BDF](https://github.com/Samifarhan52/BDF)
