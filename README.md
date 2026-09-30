# 🩸 LifePulse - Enterprise Blood Donor Finder Platform
> **College Final Year / Engineering Project**  
> **Topic:** Real-World Blood Donor Finder Website (Role-Based Authentication, Medical Compatibility Engine, Emergency Tracking & Spatial Search)

---

## 🌟 Overview & Real-World Capabilities

**LifePulse** is an enterprise-grade emergency blood donation and hospital transfusion coordination platform. It combines **secure role-based authentication** (Donors & Hospitals), **real-time emergency unit fulfillment tracking**, a **biological ABO/Rh compatibility engine**, an **interactive Leaflet spatial map**, and a **live regional blood bank inventory**.

### 🔑 Key Real-World Highlights:
1. **Fully Functional Authentication & Sessions**:
   - Secure login & signup with salted password hashing (`pbkdf2:sha256`) and encrypted session cookies.
   - Dual-role support: **Volunteer Donor** vs **Hospital Emergency Coordinator**.
   - **One-Click Demo Accounts** for instant presentation in viva without manual typing.
2. **End-to-End Emergency Tracking & Volunteer System**:
   - Every urgent blood request has a live **progress bar** (e.g. *1 of 2 Units Secured*).
   - Donors can click **"Volunteer / I Can Donate"** &rarr; records their pledge in SQLite (`request_responses`), alerts the hospital, and updates the emergency status.
3. **Personalized User Dashboards (`/dashboard`)**:
   - **Digital Donor ID Card** with QR code simulation and verification number.
   - **Medical Eligibility Countdown Tracker** (calculates exact days until safe next donation based on the standard 56-day whole blood interval).
   - **Pledge History** tracking all hospital emergencies volunteered for.
   - **Hospital Portal**: Hospital coordinators can post emergencies, monitor donor pledges, and mark requests as fulfilled.
4. **Regional Blood Bank Stock Tracker (`/blood-banks`)**:
   - Real-world directory of hospital blood banks with live inventory gauges (Normal, Low, Critical) across all 5 major blood groups.
5. **Mobile-Responsive Enterprise Navigation**:
   - Mobile hamburger drawer menu, active route indicators, user profile dropdown with digital ID badge, and real-time urgent request counter.

---

## 🖥️ How to Run in VS Code (Step-by-Step)

### Option A: Using the VS Code Terminal (Fastest)

1. **Open the Project in VS Code**:
   - Open VS Code &rarr; **File** &rarr; **Open Folder...** (or `Cmd + O` / `Ctrl + O`).
   - Select `/Users/apple/Desktop/BDF`.

2. **Open the Integrated Terminal**:
   - Press **`Ctrl + \``** (or menu: **Terminal** &rarr; **New Terminal**).

3. **Start the Application**:
   - Run:
     ```bash
     ./run.sh
     ```
     *(Or: `python3 app.py` / `./venv/bin/python app.py`)*

4. **Open in Browser**:
   - Visit: 👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

### Option B: One-Click F5 Debugging in VS Code

1. Open `/Users/apple/Desktop/BDF` in VS Code.
2. Press **`F5`** (or go to **Run & Debug** and click the green Play button).
3. The server starts automatically and you can open `http://127.0.0.1:5000`.

---

## 👥 Demo Accounts (For Viva Evaluation)

On the **Login page (`/login`)**, one-click **Autofill** buttons are provided so your professors can test without typing:

| Role | Name | Email | Password | Features to Demonstrate |
| :--- | :--- | :--- | :--- | :--- |
| **Donor (O+)** | **nihil** | `nihil@lifepulse.org` | `password123` | Digital Donor ID Card, Eligibility Tracker, Pledging to Emergencies |
| **Hospital Staff** | **Dr. Sarah Jenkins** | `sarah@mountsinai.org` | `hospital123` | Hospital Broadcast Portal, Tracking Donor Volunteers, Marking Fulfilled |
| **Universal Donor (O-)** | **Michael Chen** | `m.chen@example.com` | `donor123` | Universal donor search, emergency response |

---

## 📸 Reference Design vs Implemented System

| Reference Requirement | Implementation in LifePulse |
| :--- | :--- |
| **Top Alert Bar** | Crimson banner with alert icon + "+ Post Urgent Need" button |
| **Brand & Header** | LifePulse blood drop logo + live **`Status: Available / Unavailable`** toggle + User menu |
| **Real-Time Matching Engine** | Blood group dropdown, City/Zip input, **"Use GPS Location"**, and compatibility toggle |
| **Stats Counters** | Available Verified Donors, Active Urgent Requests, Estimated Lives Impacted |
| **Active Urgent Blood Needs** | Exact cards: **John Doe** (Mount Sinai), **Alice Wong** (UCSF), **vijay** (hm chennai) with urgency badges and circular blood group icons |
| **Real-Time Tracking** | **Progress Bar on every card** (Pledged: X of Y Units) + **"Volunteer / I Can Donate"** button |
| **Donor Directory** | Filter by group, compatibility, city, distance sort, and Grid/Map toggle |
| **Blood Banks** | Real-time clinical inventory directory with live stock gauges (Normal/Low/Critical) |
| **Compatibility Engine** | Interactive ABO/Rh matrix with visual highlights + 30-sec donor eligibility quiz |

---

## 🗄️ Database Architecture (SQLite `blood_donor.db`)

### 1. `users` Table
Stores registered donors and hospital coordinators with hashed passwords.
- `id`, `name`, `email`, `password_hash`, `role` (`donor` / `hospital`), `blood_group`, `phone`, `city`, `state`, `weight_kg`, `last_donation_date`, `is_available`, `created_at`

### 2. `donors` Table
Searchable donor directory linked with geolocation coordinates and verified badges.
- `id`, `user_id`, `name`, `blood_group`, `age`, `gender`, `phone`, `email`, `city`, `state`, `latitude`, `longitude`, `last_donation_date`, `is_available`, `is_verified`, `donations_count`

### 3. `urgent_requests` Table
Critical emergency cases posted by hospitals with live fulfillment progress tracking.
- `id`, `patient_name`, `blood_group`, `units_needed`, `units_fulfilled`, `urgency_level`, `hospital_name`, `city`, `hotline`, `notes`, `status` (`ACTIVE` / `FULFILLED`), `posted_by`

### 4. `request_responses` Table
Logs each donor's commitment/pledge when volunteering for an emergency.
- `id`, `request_id`, `donor_name`, `donor_email`, `blood_group`, `phone`, `units_pledged`, `status` (`PLEDGED`), `created_at`

### 5. `blood_banks` Table
Hospital blood inventory reserves across major groups.
- `id`, `name`, `city`, `address`, `phone`, `stock_o_neg`, `stock_o_pos`, `stock_a_pos`, `stock_b_pos`, `stock_ab_pos`, `operating_hours`

---

## 🎓 Recommended 5-Minute Presentation Flow for Professors

1. **Homepage & UI Authenticity**:
   - Show the emergency announcement bar, LifePulse branding, and click the **`Status: Available`** toggle in the navbar to show live donor availability updates.
   - Point to the live counters (Verified Donors, Active Requests, Lives Impacted).
2. **Search Engine & Spatial Matching**:
   - Search for **`O-`** in **`New York`**. Show verified donor results with contact options and the Leaflet interactive map.
3. **Emergency Tracking & Volunteer Pledge (Key Feature)**:
   - Scroll down to **"Active Urgent Blood Needs"** (`John Doe`, `Alice Wong`, `vijay`).
   - Notice the live progress bar: e.g. *1 of 2 Units Secured (50%)*.
   - Click **"Volunteer / I Can Donate"** on a card, confirm the pledge, and watch the progress bar and unit count increase in real time!
4. **Authentication & Dashboard**:
   - Go to **Login** &rarr; click **Autofill "nihil"** &rarr; click **Sign In**.
   - Show the **Digital Donor ID Card**, the **Medical Eligibility Countdown Tracker** (56-day rule), and the list of pledged emergency commitments.
   - Logout &rarr; click **Autofill "Dr. Sarah Jenkins"** &rarr; show the **Hospital Coordinator Portal** with broadcast management and one-click fulfillment.
5. **Hospital Blood Banks & Inventory**:
   - Click **Blood Banks** in the navigation. Show the live stock meters (O- Critical, A+ Normal, etc.) across regional medical centers.
6. **Medical Compatibility Engine & Viva Answers**:
   - Open **Compatibility Matrix**. Click **O-** (Universal Donor) and **AB+** (Universal Recipient) to explain the biological rules to the evaluators.

---

## 👨‍💻 Author & Credits
- **Project Topic:** Blood Donor Finder Website
- **Technologies:** Python 3, Flask, SQLite3, Werkzeug Security, Tailwind CSS, Leaflet.js, FontAwesome 6
- **Status:** Complete, Fully Tested, Enterprise-Grade, and Ready to Demonstrate
