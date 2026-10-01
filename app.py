import os
import sqlite3
import math
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_file
from werkzeug.security import check_password_hash
from database import get_db_connection, init_db, hash_pwd

app = Flask(__name__)
app.secret_key = 'lifepulse-enterprise-college-project-secure-key-2026'

# Ensure database tables exist
init_db(force_reseed=False)

# Medical Blood Compatibility Matrix
COMPATIBILITY = {
    'recipient_can_receive_from': {
        'A+': ['A+', 'A-', 'O+', 'O-'],
        'A-': ['A-', 'O-'],
        'B+': ['B+', 'B-', 'O+', 'O-'],
        'B-': ['B-', 'O-'],
        'AB+': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
        'AB-': ['AB-', 'A-', 'B-', 'O-'],
        'O+': ['O+', 'O-'],
        'O-': ['O-']
    },
    'donor_can_give_to': {
        'A+': ['A+', 'AB+'],
        'A-': ['A+', 'A-', 'AB+', 'AB-'],
        'B+': ['B+', 'AB+'],
        'B-': ['B+', 'B-', 'AB+', 'AB-'],
        'AB+': ['AB+'],
        'AB-': ['AB+', 'AB-'],
        'O+': ['O+', 'A+', 'B+', 'AB+'],
        'O-': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    }
}

BLOOD_COMPONENTS = ['Whole Blood', 'Packed Red Blood Cells (PRBC)', 'Platelets', 'Fresh Frozen Plasma (FFP)', 'Cryoprecipitate']

def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

def get_stats():
    conn = get_db_connection()
    donors_count = conn.execute("SELECT COUNT(*) FROM donors WHERE is_available = 1").fetchone()[0]
    urgent_count = conn.execute("SELECT COUNT(*) FROM urgent_requests WHERE status = 'ACTIVE'").fetchone()[0]
    blood_banks_count = conn.execute("SELECT COUNT(*) FROM blood_banks").fetchone()[0]
    total_stock_units = conn.execute("SELECT SUM(units_available) FROM blood_inventory").fetchone()[0] or 0
    total_donations = conn.execute("SELECT SUM(donations_count) FROM donors").fetchone()[0] or 10
    lives_impacted = total_donations * 3 + total_stock_units
    conn.close()
    return {
        'available_donors': donors_count,
        'urgent_requests': urgent_count,
        'blood_banks_count': blood_banks_count,
        'total_stock_units': total_stock_units,
        'lives_impacted': lives_impacted
    }

@app.context_processor
def inject_global_data():
    current_user = get_current_user()
    conn = get_db_connection()
    active_urgent_count = conn.execute("SELECT COUNT(*) FROM urgent_requests WHERE status = 'ACTIVE'").fetchone()[0]
    all_blood_banks = [dict(b) for b in conn.execute("SELECT id, name, hospital_name, city, phone FROM blood_banks ORDER BY name ASC").fetchall()]
    conn.close()

    display_status = current_user['is_available'] if current_user else 1
    status_text = 'Available' if display_status == 1 else 'Unavailable'
    display_name = current_user['name'] if current_user else 'nihil'

    return {
        'current_user': current_user,
        'is_authenticated': current_user is not None,
        'status_text': status_text,
        'display_name': display_name,
        'stats': get_stats(),
        'active_urgent_count': active_urgent_count,
        'all_blood_banks': all_blood_banks,
        'blood_groups': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
        'blood_components': BLOOD_COMPONENTS
    }

# ----------------- Authentication Routes ----------------- #

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not email or not password:
            flash('Please enter both your email address and password.', 'danger')
            return render_template('login.html')

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email = ? COLLATE NOCASE", (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['name']
            session['role'] = user['role']
            session['email'] = user['email']
            session['blood_group'] = user['blood_group']

            flash(f'Welcome back, {user["name"]}! You are now logged in.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Invalid email or password. Please verify your credentials or use a demo login button below.', 'danger')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', 'donor').strip()
        blood_group = request.form.get('blood_group', '').strip()
        phone = request.form.get('phone', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        weight_kg = request.form.get('weight_kg', type=float) or 60.0

        if not name or not email or not password or not phone or not city:
            flash('Please fill in all mandatory fields to create your account.', 'danger')
            return render_template('signup.html')

        conn = get_db_connection()
        existing = conn.execute("SELECT id FROM users WHERE email = ? COLLATE NOCASE", (email,)).fetchone()
        if existing:
            conn.close()
            flash('An account with this email address already exists. Please log in.', 'danger')
            return redirect(url_for('login'))

        pwd_hash = hash_pwd(password)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, role, blood_group, phone, city, state, weight_kg, is_available)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        ''', (name, email, pwd_hash, role, blood_group, phone, city, state, weight_kg))
        new_user_id = cursor.lastrowid

        if role == 'donor':
            cursor.execute('''
                INSERT INTO donors (user_id, name, blood_group, age, gender, phone, email, city, state, is_available, is_verified, donations_count)
                VALUES (?, ?, ?, 25, 'Not specified', ?, ?, ?, ?, 1, 1, 0)
            ''', (new_user_id, name, blood_group, phone, email, city, state))

        conn.commit()
        conn.close()

        session['user_id'] = new_user_id
        session['username'] = name
        session['role'] = role
        session['email'] = email
        session['blood_group'] = blood_group

        flash(f'Account created successfully! Welcome to LifePulse, {name}.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been securely logged out. Thank you for being part of LifePulse.', 'info')
    return redirect(url_for('index'))

# ----------------- Dashboard & Profile ----------------- #

@app.route('/dashboard')
def dashboard():
    user = get_current_user()
    if not user:
        flash('Please log in to access your personal dashboard.', 'info')
        return redirect(url_for('login', next=url_for('dashboard')))

    conn = get_db_connection()

    pledges = []
    eligibility_info = {}
    if user['role'] == 'donor':
        pledges = conn.execute('''
            SELECT rr.*, ur.patient_name, ur.hospital_name, ur.urgency_level, ur.city, ur.hotline
            FROM request_responses rr
            JOIN urgent_requests ur ON rr.request_id = ur.id
            WHERE rr.donor_email = ? OR rr.donor_name = ?
            ORDER BY rr.created_at DESC
        ''', (user['email'], user['name'])).fetchall()

        if user.get('last_donation_date'):
            try:
                last_dt = datetime.strptime(user['last_donation_date'], '%Y-%m-%d')
                next_eligible_dt = last_dt + timedelta(days=56)
                days_left = (next_eligible_dt - datetime.now()).days
                eligibility_info = {
                    'is_eligible': days_left <= 0,
                    'days_left': max(0, days_left),
                    'next_date': next_eligible_dt.strftime('%B %d, %Y')
                }
            except Exception:
                eligibility_info = {'is_eligible': True, 'days_left': 0, 'next_date': 'Available now'}
        else:
            eligibility_info = {'is_eligible': True, 'days_left': 0, 'next_date': 'Available now'}

    hospital_requests = []
    if user['role'] == 'hospital':
        hospital_requests = conn.execute('''
            SELECT ur.*, COUNT(rr.id) as volunteers_count
            FROM urgent_requests ur
            LEFT JOIN request_responses rr ON ur.id = rr.request_id
            GROUP BY ur.id
            ORDER BY ur.created_at DESC
        ''').fetchall()

    conn.close()

    return render_template(
        'dashboard.html',
        user=user,
        pledges=pledges,
        eligibility=eligibility_info,
        hospital_requests=hospital_requests
    )

@app.route('/profile/edit', methods=['POST'])
def edit_profile():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    phone = request.form.get('phone', '').strip()
    city = request.form.get('city', '').strip()
    state = request.form.get('state', '').strip()
    blood_group = request.form.get('blood_group', '').strip()
    last_donation_date = request.form.get('last_donation_date', '').strip()

    conn = get_db_connection()
    conn.execute('''
        UPDATE users
        SET phone = ?, city = ?, state = ?, blood_group = ?, last_donation_date = ?
        WHERE id = ?
    ''', (phone, city, state, blood_group, last_donation_date or None, user['id']))

    conn.execute('''
        UPDATE donors
        SET phone = ?, city = ?, state = ?, blood_group = ?, last_donation_date = ?
        WHERE user_id = ? OR email = ?
    ''', (phone, city, state, blood_group, last_donation_date or None, user['id'], user['email']))
    conn.commit()
    conn.close()

    flash('Your profile and contact information have been updated.', 'success')
    return redirect(url_for('dashboard'))

# ----------------- Blood Banks & Items Inventory Management ----------------- #

@app.route('/blood-banks')
def blood_banks_page():
    city = request.args.get('city', '').strip()
    conn = get_db_connection()
    
    if city:
        banks = conn.execute("SELECT * FROM blood_banks WHERE city LIKE ? ORDER BY name ASC", (f"%{city}%",)).fetchall()
    else:
        banks = conn.execute("SELECT * FROM blood_banks ORDER BY city ASC, name ASC").fetchall()
        
    bank_list = []
    for b in banks:
        b_dict = dict(b)
        items = conn.execute("SELECT * FROM blood_inventory WHERE blood_bank_id = ? ORDER BY blood_group ASC", (b['id'],)).fetchall()
        item_list = [dict(it) for it in items]
        b_dict['items'] = item_list
        b_dict['inventory_items'] = item_list
        b_dict['total_units'] = sum(it['units_available'] for it in item_list)
        bank_list.append(b_dict)

    conn.close()
    return render_template('blood_banks.html', blood_banks=bank_list, selected_city=city)

@app.route('/add-blood-bank', methods=['POST'])
def add_blood_bank():
    name = request.form.get('name', '').strip()
    hospital_name = request.form.get('hospital_name', '').strip() or name
    city = request.form.get('city', '').strip()
    address = request.form.get('address', '').strip()
    phone = request.form.get('phone', '').strip()
    email = request.form.get('email', '').strip()
    operating_hours = request.form.get('operating_hours', '24/7 Emergency Transfusion').strip()

    if not name or not city or not phone:
        flash('Please fill in required fields: Blood Bank Name, City, and Phone Number.', 'danger')
        return redirect(url_for('blood_banks_page'))

    conn = get_db_connection()
    conn.execute('''
        INSERT INTO blood_banks (name, hospital_name, city, address, phone, email, operating_hours)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, hospital_name, city, address, phone, email, operating_hours))
    conn.commit()
    conn.close()

    flash(f'New Blood Bank "{name}" successfully registered into the system!', 'success')
    return redirect(url_for('blood_banks_page'))

@app.route('/add-inventory-item', methods=['POST'])
def add_inventory_item():
    blood_bank_id = request.form.get('blood_bank_id', type=int)
    blood_group = request.form.get('blood_group', '').strip()
    component_type = request.form.get('component_type', 'Whole Blood').strip()
    units = request.form.get('units_available', type=int) or 1
    expiry_date = request.form.get('expiry_date', '').strip()

    if not blood_bank_id or not blood_group:
        flash('Please select a Blood Bank and Blood Group to add items.', 'danger')
        return redirect(url_for('blood_banks_page'))

    status = 'In Stock' if units > 3 else ('Low Stock' if units > 0 else 'Out of Stock')

    conn = get_db_connection()
    # Check if this group and component already exists for this bank
    existing = conn.execute('''
        SELECT id, units_available FROM blood_inventory
        WHERE blood_bank_id = ? AND blood_group = ? AND component_type = ?
    ''', (blood_bank_id, blood_group, component_type)).fetchone()

    if existing:
        new_units = existing['units_available'] + units
        new_status = 'In Stock' if new_units > 3 else 'Low Stock'
        conn.execute('''
            UPDATE blood_inventory
            SET units_available = ?, status = ?, expiry_date = COALESCE(?, expiry_date)
            WHERE id = ?
        ''', (new_units, new_status, expiry_date or None, existing['id']))
    else:
        conn.execute('''
            INSERT INTO blood_inventory (blood_bank_id, blood_group, component_type, units_available, expiry_date, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (blood_bank_id, blood_group, component_type, units, expiry_date or None, status))

    bank_name = conn.execute("SELECT name FROM blood_banks WHERE id = ?", (blood_bank_id,)).fetchone()
    conn.commit()
    conn.close()

    bname = bank_name['name'] if bank_name else 'Blood Bank'
    flash(f'Successfully added {units} unit(s) of {blood_group} ({component_type}) to {bname}!', 'success')
    return redirect(request.referrer or url_for('blood_banks_page'))

# ----------------- Availability & Needs Dashboard ----------------- #

@app.route('/availability-and-needs')
def availability_and_needs():
    conn = get_db_connection()

    # 1. Total blood units available grouped by blood group across all banks
    stock_by_group = {}
    for bg in ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']:
        stock_by_group[bg] = 0

    stock_rows = conn.execute('''
        SELECT blood_group, SUM(units_available) as total_units
        FROM blood_inventory
        GROUP BY blood_group
    ''').fetchall()
    for r in stock_rows:
        stock_by_group[r['blood_group']] = r['total_units'] or 0

    # 2. Donors count available per blood group
    donors_by_group = {}
    for bg in ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']:
        donors_by_group[bg] = 0

    donor_rows = conn.execute('''
        SELECT blood_group, COUNT(*) as count
        FROM donors
        WHERE is_available = 1
        GROUP BY blood_group
    ''').fetchall()
    for r in donor_rows:
        donors_by_group[r['blood_group']] = r['count'] or 0

    # 3. Active Urgent Needs
    needs = conn.execute('''
        SELECT ur.*, bb.name as bank_name
        FROM urgent_requests ur
        LEFT JOIN blood_banks bb ON ur.blood_bank_id = bb.id
        WHERE ur.status = 'ACTIVE'
        ORDER BY
            CASE ur.urgency_level
                WHEN 'CRITICAL NEED' THEN 1
                WHEN 'HIGH NEED' THEN 2
                ELSE 3
            END,
            ur.created_at DESC
    ''').fetchall()

    # Match each need against live availability
    needs_matched = []
    for n in needs:
        n_dict = dict(n)
        bg = n['blood_group']
        needed = n['units_needed'] - (n['units_fulfilled'] or 0)
        
        # Check stock in assigned blood bank
        bank_stock = 0
        if n['blood_bank_id']:
            b_row = conn.execute('''
                SELECT SUM(units_available) as units
                FROM blood_inventory
                WHERE blood_bank_id = ? AND blood_group = ?
            ''', (n['blood_bank_id'], bg)).fetchone()
            bank_stock = b_row['units'] or 0

        city_stock_row = conn.execute('''
            SELECT SUM(bi.units_available) as units
            FROM blood_inventory bi
            JOIN blood_banks bb ON bi.blood_bank_id = bb.id
            WHERE bb.city LIKE ? AND bi.blood_group = ?
        ''', (f"%{n['city']}%", bg)).fetchone()
        city_stock = city_stock_row['units'] or 0

        n_dict['bank_stock'] = bank_stock
        n_dict['city_stock'] = city_stock
        n_dict['units_remaining'] = needed
        n_dict['can_fulfill_from_bank'] = bank_stock >= needed
        n_dict['can_fulfill_from_city'] = city_stock >= needed
        needs_matched.append(n_dict)

    # 4. Detailed items table per blood bank
    detailed_inventory = conn.execute('''
        SELECT bi.*, bb.name as bank_name, bb.city as bank_city
        FROM blood_inventory bi
        JOIN blood_banks bb ON bi.blood_bank_id = bb.id
        ORDER BY bb.name ASC, bi.blood_group ASC
    ''').fetchall()

    conn.close()

    return render_template(
        'availability_needs.html',
        stock_by_group=stock_by_group,
        donors_by_group=donors_by_group,
        needs=needs_matched,
        detailed_inventory=detailed_inventory
    )

@app.route('/fulfill-from-stock', methods=['POST'])
def fulfill_from_stock():
    request_id = request.form.get('request_id', type=int)
    blood_bank_id = request.form.get('blood_bank_id', type=int)
    units_to_fulfill = request.form.get('units', type=int) or 1

    conn = get_db_connection()
    req = conn.execute("SELECT * FROM urgent_requests WHERE id = ?", (request_id,)).fetchone()
    if not req:
        conn.close()
        flash('Urgent request record not found.', 'danger')
        return redirect(url_for('availability_and_needs'))

    bg = req['blood_group']
    
    # Check inventory
    inv = conn.execute('''
        SELECT id, units_available FROM blood_inventory
        WHERE blood_bank_id = ? AND blood_group = ? AND units_available >= ?
        LIMIT 1
    ''', (blood_bank_id, bg, units_to_fulfill)).fetchone()

    if not inv:
        # Fallback to any inventory item of that blood group with at least 1 unit
        inv = conn.execute('''
            SELECT id, units_available FROM blood_inventory
            WHERE blood_bank_id = ? AND blood_group = ? AND units_available > 0
            LIMIT 1
        ''', (blood_bank_id, bg)).fetchone()

    if not inv:
        conn.close()
        flash(f'Insufficient {bg} units in selected Blood Bank inventory.', 'danger')
        return redirect(url_for('availability_and_needs'))

    deduct = min(units_to_fulfill, inv['units_available'])
    new_stock = inv['units_available'] - deduct
    conn.execute("UPDATE blood_inventory SET units_available = ? WHERE id = ?", (new_stock, inv['id']))

    new_fulfilled = (req['units_fulfilled'] or 0) + deduct
    new_status = 'FULFILLED' if new_fulfilled >= req['units_needed'] else 'ACTIVE'
    conn.execute("UPDATE urgent_requests SET units_fulfilled = ?, status = ? WHERE id = ?", (new_fulfilled, new_status, request_id))
    
    conn.commit()
    conn.close()

    flash(f'Success! Dispensed {deduct} unit(s) of {bg} from inventory for Patient {req["patient_name"]}. Status: {new_status}!', 'success')
    return redirect(url_for('availability_and_needs'))

# ----------------- Web Page Routes ----------------- #

@app.route('/')
def index():
    blood_group = request.args.get('blood_group', '').strip()
    location = request.args.get('location', '').strip()
    compatible_mode = request.args.get('compatible', 'true') == 'true'

    conn = get_db_connection()

    urgent_requests = conn.execute('''
        SELECT ur.*, COUNT(rr.id) as response_count, bb.name as blood_bank_name
        FROM urgent_requests ur
        LEFT JOIN request_responses rr ON ur.id = rr.request_id
        LEFT JOIN blood_banks bb ON ur.blood_bank_id = bb.id
        WHERE ur.status = 'ACTIVE'
        GROUP BY ur.id
        ORDER BY
            CASE ur.urgency_level
                WHEN 'CRITICAL NEED' THEN 1
                WHEN 'HIGH NEED' THEN 2
                WHEN 'MEDIUM NEED' THEN 3
                ELSE 4
            END,
            ur.created_at DESC
        LIMIT 6
    ''').fetchall()

    donors = []
    search_performed = bool(blood_group or location)

    if search_performed:
        query = "SELECT * FROM donors WHERE 1=1"
        params = []

        if blood_group:
            if compatible_mode and blood_group in COMPATIBILITY['recipient_can_receive_from']:
                compatible_groups = COMPATIBILITY['recipient_can_receive_from'][blood_group]
                placeholders = ','.join(['?'] * len(compatible_groups))
                query += f" AND blood_group IN ({placeholders})"
                params.extend(compatible_groups)
            else:
                query += " AND blood_group = ?"
                params.append(blood_group)

        if location:
            query += " AND (city LIKE ? OR state LIKE ? OR zip_code LIKE ?)"
            loc_pattern = f"%{location}%"
            params.extend([loc_pattern, loc_pattern, loc_pattern])

        query += " ORDER BY is_available DESC, donations_count DESC"
        donors = conn.execute(query, params).fetchall()
    else:
        donors = conn.execute("SELECT * FROM donors WHERE is_available = 1 ORDER BY donations_count DESC LIMIT 6").fetchall()

    conn.close()

    return render_template(
        'index.html',
        urgent_requests=urgent_requests,
        donors=donors,
        search_performed=search_performed,
        selected_group=blood_group,
        search_location=location,
        compatible_mode=compatible_mode
    )

@app.route('/donors')
def donors_page():
    blood_group = request.args.get('blood_group', '').strip()
    location = request.args.get('location', '').strip()
    available_only = request.args.get('available_only', '1') == '1'
    compatible_mode = request.args.get('compatible', 'false') == 'true'

    conn = get_db_connection()
    query = "SELECT * FROM donors WHERE 1=1"
    params = []

    if available_only:
        query += " AND is_available = 1"

    if blood_group:
        if compatible_mode and blood_group in COMPATIBILITY['recipient_can_receive_from']:
            compatible_groups = COMPATIBILITY['recipient_can_receive_from'][blood_group]
            placeholders = ','.join(['?'] * len(compatible_groups))
            query += f" AND blood_group IN ({placeholders})"
            params.extend(compatible_groups)
        else:
            query += " AND blood_group = ?"
            params.append(blood_group)

    if location:
        query += " AND (city LIKE ? OR state LIKE ? OR zip_code LIKE ?)"
        loc_pattern = f"%{location}%"
        params.extend([loc_pattern, loc_pattern, loc_pattern])

    query += " ORDER BY is_available DESC, donations_count DESC"
    donors = conn.execute(query, params).fetchall()
    conn.close()

    return render_template(
        'donors.html',
        donors=donors,
        selected_group=blood_group,
        search_location=location,
        available_only=available_only,
        compatible_mode=compatible_mode
    )

@app.route('/urgent-needs')
def urgent_needs_page():
    urgency_filter = request.args.get('urgency', '').strip()
    blood_group = request.args.get('blood_group', '').strip()
    bank_id = request.args.get('blood_bank_id', type=int)
    city = request.args.get('city', '').strip()

    conn = get_db_connection()
    query = '''
        SELECT ur.*, COUNT(rr.id) as response_count, bb.name as blood_bank_name
        FROM urgent_requests ur
        LEFT JOIN request_responses rr ON ur.id = rr.request_id
        LEFT JOIN blood_banks bb ON ur.blood_bank_id = bb.id
        WHERE ur.status = 'ACTIVE'
    '''
    params = []

    if urgency_filter:
        query += " AND ur.urgency_level = ?"
        params.append(urgency_filter)

    if blood_group:
        query += " AND ur.blood_group = ?"
        params.append(blood_group)

    if bank_id:
        query += " AND ur.blood_bank_id = ?"
        params.append(bank_id)

    if city:
        query += " AND ur.city LIKE ?"
        params.append(f"%{city}%")

    query += '''
        GROUP BY ur.id
        ORDER BY
        CASE ur.urgency_level
            WHEN 'CRITICAL NEED' THEN 1
            WHEN 'HIGH NEED' THEN 2
            WHEN 'MEDIUM NEED' THEN 3
            ELSE 4
        END,
        ur.created_at DESC
    '''
    requests_list = conn.execute(query, params).fetchall()
    conn.close()

    return render_template(
        'urgent_needs.html',
        requests=requests_list,
        selected_urgency=urgency_filter,
        selected_group=blood_group,
        selected_bank=bank_id,
        selected_city=city
    )

@app.route('/register-donor', methods=['GET', 'POST'])
def register_donor():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        blood_group = request.form.get('blood_group', '').strip()
        age = request.form.get('age', type=int)
        gender = request.form.get('gender', '')
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        zip_code = request.form.get('zip_code', '').strip()
        last_donation_date = request.form.get('last_donation_date', '')
        is_available = 1 if request.form.get('is_available') == 'on' else 0

        if not name or not blood_group or not phone or not city:
            flash('Please fill in all required fields (Name, Blood Group, Phone, City).', 'danger')
            return redirect(url_for('register_donor'))

        conn = get_db_connection()
        user_id = session.get('user_id')
        conn.execute('''
            INSERT INTO donors (user_id, name, blood_group, age, gender, phone, email, city, state, zip_code, last_donation_date, is_available, is_verified, donations_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 1)
        ''', (user_id, name, blood_group, age, gender, phone, email, city, state, zip_code, last_donation_date, is_available))
        conn.commit()
        conn.close()

        flash(f'Thank you, {name}! You have been registered as a verified blood donor.', 'success')
        return redirect(url_for('donors_page', location=city))

    return render_template('register_donor.html')

@app.route('/compatibility')
def compatibility_page():
    return render_template('compatibility.html', compatibility=COMPATIBILITY)

@app.route('/post-urgent-need', methods=['POST'])
def post_urgent_need():
    patient_name = request.form.get('patient_name', '').strip()
    blood_group = request.form.get('blood_group', '').strip()
    component_type = request.form.get('component_type', 'Whole Blood').strip()
    units_needed = request.form.get('units_needed', type=int) or 1
    urgency_level = request.form.get('urgency_level', 'HIGH NEED').strip()
    blood_bank_id = request.form.get('blood_bank_id', type=int)
    custom_hospital = request.form.get('hospital_name', '').strip()
    city = request.form.get('city', '').strip()
    hotline = request.form.get('hotline', '').strip()
    notes = request.form.get('notes', '').strip()

    conn = get_db_connection()
    hospital_name = custom_hospital
    if blood_bank_id:
        bank = conn.execute("SELECT name, hospital_name, city, phone FROM blood_banks WHERE id = ?", (blood_bank_id,)).fetchone()
        if bank:
            hospital_name = bank['name']
            if not city:
                city = bank['city']
            if not hotline:
                hotline = bank['phone']

    if not patient_name or not blood_group or not hospital_name or not hotline:
        conn.close()
        flash('Please fill in required fields: Patient Name, Blood Group, Blood Bank/Hospital, and Hotline.', 'danger')
        return redirect(request.referrer or url_for('urgent_needs_page'))

    current_user = get_current_user()
    posted_by = current_user['name'] if current_user else 'Emergency Coordinator'

    conn.execute('''
        INSERT INTO urgent_requests (patient_name, blood_group, component_type, units_needed, units_fulfilled, urgency_level, blood_bank_id, hospital_name, city, hotline, notes, posted_by)
        VALUES (?, ?, ?, ?, 0, ?, ?, ?, ?, ?, ?, ?)
    ''', (patient_name, blood_group, component_type, units_needed, urgency_level, blood_bank_id, hospital_name, city, hotline, notes, posted_by))
    conn.commit()
    conn.close()

    flash(f'Urgent emergency request for {patient_name} ({blood_group}) posted successfully! Donors and Blood Banks alerted.', 'success')
    return redirect(url_for('urgent_needs_page'))

# ----------------- RESTful APIs ----------------- #

@app.route('/api/toggle-status', methods=['POST'])
def api_toggle_status():
    user = get_current_user()
    conn = get_db_connection()

    if user:
        new_avail = 0 if user['is_available'] == 1 else 1
        new_status = 'Available' if new_avail == 1 else 'Unavailable'
        conn.execute("UPDATE users SET is_available = ? WHERE id = ?", (new_avail, user['id']))
        conn.execute("UPDATE donors SET is_available = ? WHERE user_id = ? OR email = ?", (new_avail, user['id'], user['email']))
    else:
        current = conn.execute("SELECT is_available FROM donors WHERE name LIKE 'nihil%' LIMIT 1").fetchone()
        new_avail = 0 if current and current['is_available'] == 1 else 1
        new_status = 'Available' if new_avail == 1 else 'Unavailable'
        conn.execute("UPDATE donors SET is_available = ? WHERE name LIKE 'nihil%'", (new_avail,))
        conn.execute("UPDATE users SET is_available = ? WHERE name LIKE 'nihil%'", (new_avail,))

    conn.commit()
    conn.close()

    return jsonify({'success': True, 'new_status': new_status, 'is_available': new_avail})

@app.route('/api/respond-urgent', methods=['POST'])
def api_respond_urgent():
    req_id = request.form.get('request_id', type=int)
    donor_name = request.form.get('donor_name', '').strip()
    donor_email = request.form.get('donor_email', '').strip()
    phone = request.form.get('phone', '').strip()
    blood_group = request.form.get('blood_group', '').strip()

    current_user = get_current_user()
    if current_user:
        donor_name = donor_name or current_user['name']
        donor_email = donor_email or current_user['email']
        phone = phone or current_user['phone']
        blood_group = blood_group or current_user['blood_group']

    if not req_id or not donor_name or not phone:
        return jsonify({'success': False, 'message': 'Please provide your name and contact phone number.'}), 400

    conn = get_db_connection()
    req_row = conn.execute("SELECT * FROM urgent_requests WHERE id = ?", (req_id,)).fetchone()
    if not req_row:
        conn.close()
        return jsonify({'success': False, 'message': 'Urgent request not found.'}), 404

    conn.execute('''
        INSERT INTO request_responses (request_id, donor_name, donor_email, blood_group, phone, units_pledged, status)
        VALUES (?, ?, ?, ?, ?, 1, 'PLEDGED')
    ''', (req_id, donor_name, donor_email, blood_group, phone))

    new_fulfilled = (req_row['units_fulfilled'] or 0) + 1
    new_status = 'FULFILLED' if new_fulfilled >= req_row['units_needed'] else 'ACTIVE'

    conn.execute('''
        UPDATE urgent_requests
        SET units_fulfilled = ?, status = ?
        WHERE id = ?
    ''', (new_fulfilled, new_status, req_id))
    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'message': f'Thank you {donor_name}! Your commitment to donate has been recorded.',
        'units_fulfilled': new_fulfilled,
        'units_needed': req_row['units_needed'],
        'status': new_status
    })

@app.route('/report')
def project_report():
    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'LifePulse_Project_Report.html')
    return send_file(report_path)

@app.route('/download-report')
def download_project_report():
    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'LifePulse_Project_Report.html')
    return send_file(report_path, as_attachment=True, download_name='LifePulse_College_Project_Report.html')

@app.route('/download-pdf')
def download_pdf_report():
    pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'LifePulse_College_Project_Report.pdf')
    if os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=True, download_name='LifePulse_College_Project_Report.pdf')
    return redirect(url_for('download_project_report'))

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  🩸 LifePulse - Pure HTML/CSS/SQLite Blood Donor Finder")
    print("  Local URL: http://localhost:5000 or http://127.0.0.1:5000")
    print("="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
