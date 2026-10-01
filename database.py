import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'blood_donor.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_pwd(password):
    return generate_password_hash(password, method='pbkdf2:sha256')

def init_db(force_reseed=False):
    db_exists = os.path.exists(DB_PATH)
    if db_exists and not force_reseed:
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    if force_reseed:
        cursor.execute("DROP TABLE IF EXISTS users")
        cursor.execute("DROP TABLE IF EXISTS donors")
        cursor.execute("DROP TABLE IF EXISTS urgent_requests")
        cursor.execute("DROP TABLE IF EXISTS request_responses")
        cursor.execute("DROP TABLE IF EXISTS blood_banks")
        cursor.execute("DROP TABLE IF EXISTS blood_inventory")
        cursor.execute("DROP TABLE IF EXISTS app_settings")

    # 1. Users Table (Authentication)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'donor',
        blood_group TEXT,
        phone TEXT,
        city TEXT,
        state TEXT,
        weight_kg REAL DEFAULT 65.0,
        last_donation_date TEXT,
        is_available INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 2. Donors Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS donors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT NOT NULL,
        blood_group TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        phone TEXT NOT NULL,
        email TEXT,
        city TEXT NOT NULL,
        state TEXT,
        zip_code TEXT,
        last_donation_date TEXT,
        is_available INTEGER DEFAULT 1,
        is_verified INTEGER DEFAULT 1,
        donations_count INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')

    # 3. Blood Banks Table (Add Blood Banks feature)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS blood_banks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        hospital_name TEXT,
        city TEXT NOT NULL,
        address TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT,
        operating_hours TEXT DEFAULT '24/7 Emergency Transfusion',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 4. Blood Inventory Table (Add Items in Blood Bank feature)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS blood_inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        blood_bank_id INTEGER NOT NULL,
        blood_group TEXT NOT NULL,
        component_type TEXT DEFAULT 'Whole Blood',
        units_available INTEGER DEFAULT 0,
        expiry_date TEXT,
        status TEXT DEFAULT 'In Stock',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (blood_bank_id) REFERENCES blood_banks(id)
    )
    ''')

    # 5. Urgent Requests Table (with blood_bank_id foreign key & dropdown method)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS urgent_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT NOT NULL,
        blood_group TEXT NOT NULL,
        component_type TEXT DEFAULT 'Whole Blood',
        units_needed INTEGER NOT NULL,
        units_fulfilled INTEGER DEFAULT 0,
        urgency_level TEXT NOT NULL,
        blood_bank_id INTEGER,
        hospital_name TEXT NOT NULL,
        city TEXT NOT NULL,
        hotline TEXT NOT NULL,
        notes TEXT,
        status TEXT DEFAULT 'ACTIVE',
        posted_by TEXT DEFAULT 'Emergency Ward',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (blood_bank_id) REFERENCES blood_banks(id)
    )
    ''')

    # 6. Request Responses (Volunteer Pledges)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS request_responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        request_id INTEGER NOT NULL,
        donor_name TEXT NOT NULL,
        donor_email TEXT NOT NULL,
        blood_group TEXT NOT NULL,
        phone TEXT NOT NULL,
        units_pledged INTEGER DEFAULT 1,
        status TEXT DEFAULT 'PLEDGED',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (request_id) REFERENCES urgent_requests(id)
    )
    ''')

    # 7. Global App Settings
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS app_settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    ''')

    # Seed Demo Users
    demo_users = [
        ("nihil", "nihil@lifepulse.org", hash_pwd("password123"), "donor", "O+", "555-0199", "New York", "NY", 70.0, "2024-01-14", 1),
        ("Dr. Sarah Jenkins", "sarah@mountsinai.org", hash_pwd("hospital123"), "hospital", "A+", "555-9001", "New York", "NY", 62.0, None, 1),
        ("Michael Chen", "m.chen@example.com", hash_pwd("donor123"), "donor", "O-", "555-0122", "New York", "NY", 68.0, "2024-01-15", 1),
        ("Priya Sharma", "priya@lifepulse.org", hash_pwd("donor123"), "donor", "A+", "+91 98401 23456", "Chennai", "TN", 58.0, "2024-02-10", 1)
    ]
    cursor.executemany('''
    INSERT OR IGNORE INTO users (name, email, password_hash, role, blood_group, phone, city, state, weight_kg, last_donation_date, is_available)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', demo_users)

    # Seed Donors
    sample_donors = [
        (1, "nihil", "O+", 22, "Male", "555-0199", "nihil@lifepulse.org", "New York", "NY", "10025", "2024-01-14", 1, 1, 3),
        (3, "Michael Chen", "O-", 29, "Male", "555-0122", "m.chen@example.com", "New York", "NY", "10001", "2024-01-15", 1, 1, 4),
        (4, "Priya Sharma", "A+", 26, "Female", "+91 98401 23456", "priya@lifepulse.org", "Chennai", "TN", "600001", "2024-02-10", 1, 1, 3),
        (None, "David Miller", "B+", 34, "Male", "555-0144", "david.m@example.com", "San Francisco", "CA", "94102", "2023-11-20", 1, 1, 6),
        (None, "Elena Rostova", "AB+", 31, "Female", "555-0155", "elena.r@example.com", "New York", "NY", "10021", "2024-01-05", 1, 1, 2),
        (None, "Karthik Raman", "O-", 28, "Male", "+91 98402 88899", "karthik.r@example.com", "Chennai", "TN", "600028", "2023-12-14", 1, 1, 5),
        (None, "Jessica Taylor", "A-", 24, "Female", "555-0188", "jtaylor@example.com", "Chicago", "IL", "60601", "2024-02-01", 1, 1, 2),
        (None, "Marcus Johnson", "B-", 38, "Male", "555-0177", "marcus.j@example.com", "San Francisco", "CA", "94110", "2023-10-18", 0, 1, 7),
        (None, "Sophia Patel", "AB-", 27, "Female", "555-0133", "spatel@example.com", "New York", "NY", "10003", "2024-01-25", 1, 1, 1),
        (None, "Rajesh Kumar", "O+", 32, "Male", "+91 98403 11223", "rajesh.k@example.com", "Chennai", "TN", "600004", "2024-01-18", 1, 1, 8)
    ]
    cursor.executemany('''
    INSERT OR IGNORE INTO donors (user_id, name, blood_group, age, gender, phone, email, city, state, zip_code, last_donation_date, is_available, is_verified, donations_count)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_donors)

    # Seed Blood Banks
    sample_banks = [
        (1, "Mount Sinai Hospital Blood Bank", "Mount Sinai Hospital", "New York", "One Gustave L. Levy Place, New York, NY 10029", "555-9001", "bloodbank@mountsinai.org", "24/7 Emergency Transfusion"),
        (2, "UCSF Medical Center Transfusion Service", "UCSF Medical Center", "San Francisco", "505 Parnassus Ave, San Francisco, CA 94143", "555-9002", "transfusion@ucsf.edu", "24/7 Emergency Transfusion"),
        (3, "Apollo Hospitals Central Blood Bank", "hm (chennai)", "Chennai", "21 Greams Lane, Thousand Lights, Chennai, TN 600006", "1234567891", "blood@apollohospitals.com", "24/7 Emergency Transfusion"),
        (4, "Northwestern Memorial Blood Donor Center", "Northwestern Memorial Hospital", "Chicago", "251 E Huron St, Chicago, IL 60611", "555-9004", "blooddonor@nm.org", "24/7 Emergency Transfusion")
    ]
    cursor.executemany('''
    INSERT OR IGNORE INTO blood_banks (id, name, hospital_name, city, address, phone, email, operating_hours)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_banks)

    # Seed Blood Bank Items (Inventory for each blood bank)
    sample_inventory = [
        # Mount Sinai (Bank 1)
        (1, "O-", "Whole Blood", 5, "2026-11-15", "In Stock"),
        (1, "O-", "Packed Red Blood Cells (PRBC)", 4, "2026-11-20", "In Stock"),
        (1, "O+", "Whole Blood", 14, "2026-11-18", "In Stock"),
        (1, "A+", "Packed Red Blood Cells (PRBC)", 9, "2026-11-22", "In Stock"),
        (1, "B+", "Platelets", 3, "2026-10-10", "Low Stock"),
        (1, "AB+", "Fresh Frozen Plasma (FFP)", 6, "2026-12-01", "In Stock"),
        # UCSF (Bank 2)
        (2, "A+", "Whole Blood", 8, "2026-11-14", "In Stock"),
        (2, "O-", "Packed Red Blood Cells (PRBC)", 2, "2026-10-25", "Low Stock"),
        (2, "B+", "Whole Blood", 6, "2026-11-19", "In Stock"),
        (2, "O+", "Platelets", 4, "2026-10-12", "In Stock"),
        # Apollo Chennai (Bank 3)
        (3, "O-", "Whole Blood", 3, "2026-11-10", "In Stock"),
        (3, "O+", "Whole Blood", 18, "2026-11-25", "In Stock"),
        (3, "A+", "Packed Red Blood Cells (PRBC)", 11, "2026-11-28", "In Stock"),
        (3, "B+", "Fresh Frozen Plasma (FFP)", 7, "2026-12-05", "In Stock"),
        # Northwestern (Bank 4)
        (4, "B+", "Whole Blood", 6, "2026-11-16", "In Stock"),
        (4, "O-", "Whole Blood", 1, "2026-10-20", "Low Stock"),
        (4, "A-", "Platelets", 3, "2026-10-15", "In Stock")
    ]
    cursor.executemany('''
    INSERT OR IGNORE INTO blood_inventory (blood_bank_id, blood_group, component_type, units_available, expiry_date, status)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', sample_inventory)

    # Seed Urgent Requests (Matching reference screenshots with blood_bank_id linked!)
    sample_urgent = [
        (1, "John Doe", "O-", "Whole Blood", 2, 1, "CRITICAL NEED", 1, "Mount Sinai Hospital (New York)", "New York", "555-9001", "Urgent surgery requirement", "ACTIVE", "Dr. Sarah Jenkins"),
        (2, "Alice Wong", "A+", "Whole Blood", 3, 2, "HIGH NEED", 2, "UCSF Medical Center (San Francisco)", "San Francisco", "555-9002", "Trauma unit request", "ACTIVE", "Emergency Triage Team"),
        (3, "vijay", "O-", "Whole Blood", 1, 0, "MEDIUM NEED", 3, "hm (chennai)", "Chennai", "1234567891", "Dialysis and severe anemia support", "ACTIVE", "Apollo Care Unit"),
        (4, "Sarah Jenkins", "B+", "Whole Blood", 2, 0, "HIGH NEED", 4, "Northwestern Memorial Hospital", "Chicago", "555-9004", "Pediatric cardiac emergency", "ACTIVE", "ICU Floor 4")
    ]
    cursor.executemany('''
    INSERT OR IGNORE INTO urgent_requests (id, patient_name, blood_group, component_type, units_needed, units_fulfilled, urgency_level, blood_bank_id, hospital_name, city, hotline, notes, status, posted_by)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_urgent)

    conn.commit()
    conn.close()
    print("Database schema upgraded with Blood Banks, Items Inventory, and Dropdown foreign keys successfully.")

if __name__ == '__main__':
    init_db(force_reseed=True)
