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

    # Drop existing tables if force_reseed
    if force_reseed:
        cursor.execute("DROP TABLE IF EXISTS users")
        cursor.execute("DROP TABLE IF EXISTS donors")
        cursor.execute("DROP TABLE IF EXISTS urgent_requests")
        cursor.execute("DROP TABLE IF EXISTS request_responses")
        cursor.execute("DROP TABLE IF EXISTS blood_banks")
        cursor.execute("DROP TABLE IF EXISTS app_settings")

    # 1. Users table (for real authentication)
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

    # 2. Donors table
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
        latitude REAL,
        longitude REAL,
        last_donation_date TEXT,
        is_available INTEGER DEFAULT 1,
        is_verified INTEGER DEFAULT 1,
        donations_count INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')

    # 3. Urgent Blood Requests table (with trackable units_fulfilled)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS urgent_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT NOT NULL,
        blood_group TEXT NOT NULL,
        units_needed INTEGER NOT NULL,
        units_fulfilled INTEGER DEFAULT 0,
        urgency_level TEXT NOT NULL,
        hospital_name TEXT NOT NULL,
        city TEXT NOT NULL,
        hotline TEXT NOT NULL,
        notes TEXT,
        latitude REAL,
        longitude REAL,
        status TEXT DEFAULT 'ACTIVE',
        posted_by TEXT DEFAULT 'Hospital Emergency Ward',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 4. Request Responses / Volunteer Pledges (Trackable Emergency Fulfillment)
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

    # 5. Regional Blood Banks & Hospital Inventory
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS blood_banks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        city TEXT NOT NULL,
        address TEXT NOT NULL,
        phone TEXT NOT NULL,
        stock_o_neg TEXT DEFAULT 'LOW',
        stock_o_pos TEXT DEFAULT 'NORMAL',
        stock_a_pos TEXT DEFAULT 'NORMAL',
        stock_b_pos TEXT DEFAULT 'LOW',
        stock_ab_pos TEXT DEFAULT 'NORMAL',
        operating_hours TEXT DEFAULT '24/7 Emergency Transfusion',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 6. Global app settings
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS app_settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    ''')

    # Default Demo Users
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

    # Pre-seed Donors
    sample_donors = [
        (1, "nihil", "O+", 22, "Male", "555-0199", "nihil@lifepulse.org", "New York", "NY", "10025", 40.8075, -73.9626, "2024-01-14", 1, 1, 3),
        (3, "Michael Chen", "O-", 29, "Male", "555-0122", "m.chen@example.com", "New York", "NY", "10001", 40.7128, -74.0060, "2024-01-15", 1, 1, 4),
        (4, "Priya Sharma", "A+", 26, "Female", "+91 98401 23456", "priya@lifepulse.org", "Chennai", "TN", "600001", 13.0827, 80.2707, "2024-02-10", 1, 1, 3),
        (None, "David Miller", "B+", 34, "Male", "555-0144", "david.m@example.com", "San Francisco", "CA", "94102", 37.7749, -122.4194, "2023-11-20", 1, 1, 6),
        (None, "Elena Rostova", "AB+", 31, "Female", "555-0155", "elena.r@example.com", "New York", "NY", "10021", 40.7736, -73.9566, "2024-01-05", 1, 1, 2),
        (None, "Karthik Raman", "O-", 28, "Male", "+91 98402 88899", "karthik.r@example.com", "Chennai", "TN", "600028", 13.0280, 80.2500, "2023-12-14", 1, 1, 5),
        (None, "Jessica Taylor", "A-", 24, "Female", "555-0188", "jtaylor@example.com", "Chicago", "IL", "60601", 41.8781, -87.6298, "2024-02-01", 1, 1, 2),
        (None, "Marcus Johnson", "B-", 38, "Male", "555-0177", "marcus.j@example.com", "San Francisco", "CA", "94110", 37.7599, -122.4148, "2023-10-18", 0, 1, 7),
        (None, "Sophia Patel", "AB-", 27, "Female", "555-0133", "spatel@example.com", "New York", "NY", "10003", 40.7306, -73.9926, "2024-01-25", 1, 1, 1),
        (None, "Rajesh Kumar", "O+", 32, "Male", "+91 98403 11223", "rajesh.k@example.com", "Chennai", "TN", "600004", 13.0368, 80.2676, "2024-01-18", 1, 1, 8)
    ]

    cursor.executemany('''
    INSERT OR IGNORE INTO donors (user_id, name, blood_group, age, gender, phone, email, city, state, zip_code, latitude, longitude, last_donation_date, is_available, is_verified, donations_count)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_donors)

    # Pre-seed Urgent Requests (Exact matches from the user reference screenshots)
    sample_urgent_requests = [
        (
            1,
            "John Doe",
            "O-",
            2,
            1, # 1 unit already pledged/fulfilled!
            "CRITICAL NEED",
            "Mount Sinai Hospital (New York)",
            "New York",
            "555-9001",
            "Urgent surgery requirement",
            40.7903,
            -73.9530,
            "Dr. Sarah Jenkins"
        ),
        (
            2,
            "Alice Wong",
            "A+",
            3,
            2, # 2 units pledged
            "HIGH NEED",
            "UCSF Medical Center (San Francisco)",
            "San Francisco",
            "555-9002",
            "Trauma unit request",
            37.7631,
            -122.4582,
            "Emergency Triage Team"
        ),
        (
            3,
            "vijay",
            "O-",
            1,
            0, # 0 units pledged
            "MEDIUM NEED",
            "hm (chennai)",
            "Chennai",
            "1234567891",
            "Dialysis and severe anemia support",
            13.0827,
            80.2707,
            "Apollo Care Unit"
        ),
        (
            4,
            "Sarah Jenkins",
            "B+",
            2,
            0,
            "HIGH NEED",
            "Northwestern Memorial Hospital",
            "Chicago",
            "555-9004",
            "Pediatric cardiac emergency",
            41.8953,
            -87.6214,
            "ICU Floor 4"
        )
    ]

    cursor.executemany('''
    INSERT OR IGNORE INTO urgent_requests (id, patient_name, blood_group, units_needed, units_fulfilled, urgency_level, hospital_name, city, hotline, notes, latitude, longitude, posted_by)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_urgent_requests)

    # Pre-seed sample volunteer response
    sample_responses = [
        (1, "Michael Chen", "m.chen@example.com", "O-", "555-0122", 1, "PLEDGED"),
        (2, "Priya Sharma", "priya@lifepulse.org", "A+", "+91 98401 23456", 1, "PLEDGED"),
        (2, "David Miller", "david.m@example.com", "A+", "555-0144", 1, "PLEDGED")
    ]
    cursor.executemany('''
    INSERT OR IGNORE INTO request_responses (request_id, donor_name, donor_email, blood_group, phone, units_pledged, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', sample_responses)

    # Pre-seed Regional Blood Banks
    sample_blood_banks = [
        ("Mount Sinai Transfusion & Blood Bank", "New York", "One Gustave L. Levy Place, New York, NY", "(212) 241-6500", "CRITICAL", "NORMAL", "NORMAL", "LOW", "NORMAL", "24 Hours / 7 Days"),
        ("Apollo Main Hospital Blood Bank", "Chennai", "21 Greams Lane, Thousand Lights, Chennai, TN", "+91 44 2829 0200", "LOW", "NORMAL", "NORMAL", "NORMAL", "LOW", "24 Hours / 7 Days"),
        ("UCSF Transfusion Service Center", "San Francisco", "505 Parnassus Ave, San Francisco, CA", "(415) 353-1000", "CRITICAL", "LOW", "NORMAL", "NORMAL", "NORMAL", "8:00 AM - 10:00 PM"),
        ("Northwestern Medicine Blood Donor Center", "Chicago", "251 E Huron St, Feinberg Pavilion, Chicago, IL", "(312) 926-2000", "LOW", "NORMAL", "NORMAL", "LOW", "NORMAL", "7:00 AM - 9:00 PM")
    ]
    cursor.executemany('''
    INSERT OR IGNORE INTO blood_banks (name, city, address, phone, stock_o_neg, stock_o_pos, stock_a_pos, stock_b_pos, stock_ab_pos, operating_hours)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_blood_banks)

    conn.commit()
    conn.close()
    print("Database schema upgraded and initialized successfully.")

if __name__ == '__main__':
    init_db(force_reseed=True)
