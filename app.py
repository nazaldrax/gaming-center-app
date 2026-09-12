"""
Gaming Center Management System
Flask Backend with SQLite Database
"""

from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import sqlite3
import json
import os

app = Flask(__name__)
DATABASE = 'database.db'

# Device Categories with Default Rates (per hour in INR)
DEVICES = {
    'PS5': {'total': 8, 'rate': 100, 'color': '#00d4ff'},
    'Gaming PC': {'total': 2, 'rate': 120, 'color': '#00ff41'},
    'Driving Console': {'total': 1, 'rate': 150, 'color': '#ff006e'}
}

# ==================== DATABASE SETUP ====================
def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with required tables"""
    conn = get_db()
    c = conn.cursor()
    
    # Create Members Table
    c.execute('''CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        mobile TEXT NOT NULL UNIQUE,
        address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Create Devices Table
    c.execute('''CREATE TABLE IF NOT EXISTS devices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_type TEXT NOT NULL,
        device_number INTEGER NOT NULL,
        status TEXT DEFAULT 'Available',
        current_member_id INTEGER,
        rate_per_hour REAL NOT NULL,
        UNIQUE(device_type, device_number)
    )''')
    
    # Create Sessions Table
    c.execute('''CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        member_id INTEGER,
        member_name TEXT,
        device_id INTEGER,
        device_type TEXT,
        device_number INTEGER,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        duration_minutes INTEGER,
        rate_per_hour REAL,
        total_amount REAL,
        payment_status TEXT DEFAULT 'Pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(member_id) REFERENCES members(id),
        FOREIGN KEY(device_id) REFERENCES devices(id)
    )''')
    
    # Create Transaction Log Table
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        member_name TEXT,
        member_id INTEGER,
        device_name TEXT,
        amount REAL,
        payment_status TEXT,
        payment_date TIMESTAMP,
        transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(session_id) REFERENCES sessions(id),
        FOREIGN KEY(member_id) REFERENCES members(id)
    )''')
    
    # Create Reservations/Bookings Table
    c.execute('''CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        member_id INTEGER,
        member_name TEXT,
        device_id INTEGER,
        device_type TEXT,
        device_number INTEGER,
        reservation_date TIMESTAMP,
        start_time TIMESTAMP,
        end_time TIMESTAMP,
        duration_minutes INTEGER,
        status TEXT DEFAULT 'Confirmed',
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(member_id) REFERENCES members(id),
        FOREIGN KEY(device_id) REFERENCES devices(id)
    )''')
    
    conn.commit()
    
    # Initialize devices if not already present
    c.execute('SELECT COUNT(*) FROM devices')
    if c.fetchone()[0] == 0:
        devices_list = [
            ('PS5', 1, 100), ('PS5', 2, 100), ('PS5', 3, 100), ('PS5', 4, 100),
            ('PS5', 5, 100), ('PS5', 6, 100), ('PS5', 7, 100), ('PS5', 8, 100),
            ('Gaming PC', 1, 120), ('Gaming PC', 2, 120),
            ('Driving Console', 1, 150)
        ]
        c.executemany('INSERT INTO devices (device_type, device_number, rate_per_hour) VALUES (?, ?, ?)', devices_list)
        conn.commit()
    
    conn.close()

# Initialize database on startup
if not os.path.exists(DATABASE):
    init_db()
else:
    # Add new tables if they don't exist
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER,
            member_name TEXT,
            device_id INTEGER,
            device_type TEXT,
            device_number INTEGER,
            reservation_date TIMESTAMP,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            duration_minutes INTEGER,
            status TEXT DEFAULT 'Confirmed',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(member_id) REFERENCES members(id),
            FOREIGN KEY(device_id) REFERENCES devices(id)
        )''')
        conn.commit()
        conn.close()
    except:
        pass

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/members')
def members():
    """Members management page"""
    return render_template('members.html')

@app.route('/reports')
def reports():
    """Daily reports and analytics"""
    return render_template('reports.html')

@app.route('/bookings')
def bookings():
    """Bookings and reservations page"""
    return render_template('bookings.html')

# ==================== API ENDPOINTS ====================

# ---- MEMBERS API ----

@app.route('/api/members', methods=['GET'])
def get_members():
    """Fetch all members"""
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM members ORDER BY created_at DESC')
        members = [dict(row) for row in c.fetchall()]
        conn.close()
        return jsonify({'success': True, 'data': members})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/members/search', methods=['GET'])
def search_members():
    """Search members by name or mobile"""
    try:
        query = request.args.get('q', '').strip()
        conn = get_db()
        c = conn.cursor()
        c.execute('''SELECT * FROM members 
                     WHERE name LIKE ? OR mobile LIKE ? 
                     ORDER BY name''', (f'%{query}%', f'%{query}%'))
        members = [dict(row) for row in c.fetchall()]
        conn.close()
        return jsonify({'success': True, 'data': members})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/members', methods=['POST'])
def add_member():
    """Add new member"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        mobile = data.get('mobile', '').strip()
        address = data.get('address', '').strip()
        
        if not name or not mobile:
            return jsonify({'success': False, 'error': 'Name and Mobile are required'})
        
        conn = get_db()
        c = conn.cursor()
        c.execute('INSERT INTO members (name, mobile, address) VALUES (?, ?, ?)',
                  (name, mobile, address))
        conn.commit()
        member_id = c.lastrowid
        conn.close()
        
        return jsonify({'success': True, 'message': 'Member added successfully', 'id': member_id, 'name': name})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'error': 'Mobile number already exists'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ---- DEVICES API ----

@app.route('/api/devices', methods=['GET'])
def get_devices():
    """Fetch all devices with current status"""
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('''SELECT d.*, m.name as member_name 
                     FROM devices d 
                     LEFT JOIN members m ON d.current_member_id = m.id 
                     ORDER BY d.device_type, d.device_number''')
        devices = [dict(row) for row in c.fetchall()]
        conn.close()
        return jsonify({'success': True, 'data': devices})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/devices/<int:device_id>', methods=['GET'])
def get_device(device_id):
    """Get specific device details"""
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('''SELECT d.*, m.name as member_name 
                     FROM devices d 
                     LEFT JOIN members m ON d.current_member_id = m.id 
                     WHERE d.id = ?''', (device_id,))
        device = dict(c.fetchone())
        conn.close()
        return jsonify({'success': True, 'data': device})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ---- SESSIONS API ----

@app.route('/api/sessions/start', methods=['POST'])
def start_session():
    """Start a new gaming session"""
    try:
        data = request.get_json()
        device_id = data.get('device_id')
        member_id = data.get('member_id')
        member_name = data.get('member_name', 'Guest')
        duration_minutes = int(data.get('duration_minutes', 60))
        
        if not device_id:
            return jsonify({'success': False, 'error': 'Device not selected'})
        
        if not member_name or member_name.strip() == '':
            return jsonify({'success': False, 'error': 'Please select a registered member or enter guest name'})
        
        conn = get_db()
        c = conn.cursor()
        
        # Check device availability
        c.execute('SELECT * FROM devices WHERE id = ?', (device_id,))
        device = dict(c.fetchone())
        
        if device['status'] != 'Available':
            conn.close()
            return jsonify({'success': False, 'error': 'Device is not available'})
        
        # Create session
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        c.execute('''INSERT INTO sessions 
                     (member_id, member_name, device_id, device_type, device_number, 
                      start_time, end_time, duration_minutes, rate_per_hour, total_amount, payment_status)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (member_id, member_name, device_id, device['device_type'], device['device_number'],
                   start_time, end_time, duration_minutes, device['rate_per_hour'],
                   (duration_minutes / 60) * device['rate_per_hour'], 'Pending'))
        
        session_id = c.lastrowid
        
        # Update device status
        c.execute('UPDATE devices SET status = ?, current_member_id = ? WHERE id = ?',
                  ('Occupied', member_id, device_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Session started', 'session_id': session_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/sessions/active', methods=['GET'])
def get_active_sessions():
    """Fetch all active sessions"""
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('''SELECT * FROM sessions 
                     WHERE payment_status = 'Pending' 
                     ORDER BY start_time DESC''')
        sessions = []
        for row in c.fetchall():
            session = dict(row)
            start = datetime.fromisoformat(session['start_time'])
            end = datetime.fromisoformat(session['end_time'])
            now = datetime.now()
            
            elapsed = int((now - start).total_seconds() / 60)
            remaining = int((end - now).total_seconds() / 60)
            
            session['elapsed_minutes'] = max(0, elapsed)
            session['remaining_minutes'] = max(0, remaining)
            session['is_expired'] = remaining <= 0
            session['alert_5min'] = remaining <= 5 and remaining > 0
            
            sessions.append(session)
        
        conn.close()
        return jsonify({'success': True, 'data': sessions})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/sessions/<int:session_id>', methods=['GET'])
def get_session(session_id):
    """Get specific session details"""
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
        session = dict(c.fetchone())
        
        start = datetime.fromisoformat(session['start_time'])
        end = datetime.fromisoformat(session['end_time'])
        now = datetime.now()
        
        elapsed = int((now - start).total_seconds() / 60)
        remaining = int((end - now).total_seconds() / 60)
        
        session['elapsed_minutes'] = max(0, elapsed)
        session['remaining_minutes'] = max(0, remaining)
        session['is_expired'] = remaining <= 0
        
        conn.close()
        return jsonify({'success': True, 'data': session})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/sessions/<int:session_id>/extend', methods=['POST'])
def extend_session(session_id):
    """Extend session duration"""
    try:
        data = request.get_json()
        extra_minutes = int(data.get('extra_minutes', 30))
        
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
        session = dict(c.fetchone())
        
        old_end = datetime.fromisoformat(session['end_time'])
        new_end = old_end + timedelta(minutes=extra_minutes)
        new_duration = session['duration_minutes'] + extra_minutes
        new_amount = (new_duration / 60) * session['rate_per_hour']
        
        c.execute('''UPDATE sessions 
                     SET end_time = ?, duration_minutes = ?, total_amount = ? 
                     WHERE id = ?''',
                  (new_end, new_duration, new_amount, session_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Session extended', 
                       'new_end_time': str(new_end), 'new_amount': new_amount})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/sessions/<int:session_id>/end', methods=['POST'])
def end_session(session_id):
    """End session and mark payment status"""
    try:
        data = request.get_json()
        payment_status = data.get('payment_status', 'Pending')  # Can be 'Pending', 'Completed', 'Partial'
        
        conn = get_db()
        c = conn.cursor()
        
        # Get session details
        c.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
        session = dict(c.fetchone())
        
        # Update session status
        c.execute('''UPDATE sessions 
                     SET payment_status = ? 
                     WHERE id = ?''',
                  (payment_status, session_id))
        
        # Update device status only if payment is completed
        if payment_status == 'Completed':
            c.execute('UPDATE devices SET status = ?, current_member_id = NULL WHERE id = ?',
                      ('Available', session['device_id']))
        
        # Create transaction log
        payment_date = datetime.now() if payment_status == 'Completed' else None
        c.execute('''INSERT INTO transactions 
                     (session_id, member_id, member_name, device_name, amount, payment_status, payment_date)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (session_id, session['member_id'], session['member_name'], 
                   f"{session['device_type']} {session['device_number']}", 
                   session['total_amount'], payment_status, payment_date))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': f'Session payment marked as {payment_status}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ---- RESERVATIONS API ----

@app.route('/api/reservations', methods=['GET'])
def get_reservations():
    """Fetch all reservations"""
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('''SELECT * FROM reservations 
                     WHERE status = 'Confirmed' AND reservation_date >= DATE('now')
                     ORDER BY reservation_date, start_time''')
        reservations = [dict(row) for row in c.fetchall()]
        conn.close()
        return jsonify({'success': True, 'data': reservations})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/reservations', methods=['POST'])
def create_reservation():
    """Create new reservation/booking"""
    try:
        data = request.get_json()
        member_id = data.get('member_id')
        member_name = data.get('member_name')
        device_id = data.get('device_id')
        device_type = data.get('device_type')
        device_number = data.get('device_number')
        reservation_date = data.get('reservation_date')
        start_time = data.get('start_time')
        duration_minutes = int(data.get('duration_minutes', 60))
        notes = data.get('notes', '')
        
        if not all([member_id, device_id, reservation_date, start_time]):
            return jsonify({'success': False, 'error': 'Missing required fields'})
        
        conn = get_db()
        c = conn.cursor()
        
        # Parse times
        start_datetime = datetime.fromisoformat(f"{reservation_date}T{start_time}")
        end_datetime = start_datetime + timedelta(minutes=duration_minutes)
        
        # Check for conflicts
        c.execute('''SELECT COUNT(*) as count FROM reservations 
                     WHERE device_id = ? AND reservation_date = ? 
                     AND status = 'Confirmed'
                     AND ((start_time < ? AND end_time > ?)
                          OR (start_time < ? AND end_time > ?)
                          OR (start_time >= ? AND end_time <= ?))''',
                  (device_id, reservation_date, end_datetime, start_datetime,
                   end_datetime, start_datetime, end_datetime, start_datetime))
        
        if c.fetchone()['count'] > 0:
            conn.close()
            return jsonify({'success': False, 'error': 'Time slot not available'})
        
        c.execute('''INSERT INTO reservations 
                     (member_id, member_name, device_id, device_type, device_number,
                      reservation_date, start_time, end_time, duration_minutes, notes)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (member_id, member_name, device_id, device_type, device_number,
                   reservation_date, start_datetime, end_datetime, duration_minutes, notes))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Reservation created successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/reservations/<int:reservation_id>', methods=['DELETE'])
def cancel_reservation(reservation_id):
    """Cancel a reservation"""
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('UPDATE reservations SET status = ? WHERE id = ?', ('Cancelled', reservation_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Reservation cancelled'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ---- REPORTS API ----

@app.route('/api/reports/daily', methods=['GET'])
def get_daily_report():
    """Get daily revenue report"""
    try:
        date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        conn = get_db()
        c = conn.cursor()
        
        # Total Revenue
        c.execute('''SELECT SUM(amount) as total_revenue 
                     FROM transactions 
                     WHERE payment_status = 'Completed' 
                     AND DATE(payment_date) = ?''', (date,))
        total_revenue = c.fetchone()['total_revenue'] or 0
        
        # Total Sessions
        c.execute('''SELECT COUNT(*) as total_sessions 
                     FROM transactions 
                     WHERE payment_status = 'Completed' 
                     AND DATE(payment_date) = ?''', (date,))
        total_sessions = c.fetchone()['total_sessions']
        
        # Most Used Console
        c.execute('''SELECT device_name, COUNT(*) as count 
                     FROM transactions 
                     WHERE payment_status = 'Completed' 
                     AND DATE(payment_date) = ? 
                     GROUP BY device_name 
                     ORDER BY count DESC 
                     LIMIT 1''', (date,))
        most_used = c.fetchone()
        most_used_console = most_used['device_name'] if most_used else 'N/A'
        
        # Detailed Transactions
        c.execute('''SELECT s.member_name, s.device_type, s.device_number, s.duration_minutes, 
                            s.start_time, s.end_time, t.amount, t.payment_status, t.payment_date
                     FROM transactions t
                     JOIN sessions s ON t.session_id = s.id
                     WHERE t.payment_status = 'Completed' 
                     AND DATE(t.payment_date) = ? 
                     ORDER BY t.payment_date DESC''', (date,))
        transactions = []
        for row in c.fetchall():
            trans = dict(row)
            trans['device_name'] = f"{trans['device_type']} #{trans['device_number']}"
            trans['duration'] = f"{trans['duration_minutes'] // 60}h {trans['duration_minutes'] % 60}m"
            transactions.append(trans)
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'date': date,
                'total_revenue': round(total_revenue, 2),
                'total_sessions': total_sessions,
                'most_used_console': most_used_console,
                'transactions': transactions
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/reports/custom', methods=['GET'])
def get_custom_report():
    """Get custom date range report"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        conn = get_db()
        c = conn.cursor()
        
        # Total Revenue
        c.execute('''SELECT SUM(amount) as total_revenue 
                     FROM transactions 
                     WHERE payment_status = 'Completed' 
                     AND DATE(payment_date) BETWEEN ? AND ?''', (start_date, end_date))
        total_revenue = c.fetchone()['total_revenue'] or 0
        
        # Total Sessions
        c.execute('''SELECT COUNT(*) as total_sessions 
                     FROM transactions 
                     WHERE payment_status = 'Completed' 
                     AND DATE(payment_date) BETWEEN ? AND ?''', (start_date, end_date))
        total_sessions = c.fetchone()['total_sessions']
        
        # Detailed Transactions
        c.execute('''SELECT s.member_name, s.device_type, s.device_number, s.duration_minutes, 
                            s.start_time, s.end_time, t.amount, t.payment_status, t.payment_date
                     FROM transactions t
                     JOIN sessions s ON t.session_id = s.id
                     WHERE t.payment_status = 'Completed' 
                     AND DATE(t.payment_date) BETWEEN ? AND ? 
                     ORDER BY t.payment_date DESC''', (start_date, end_date))
        transactions = []
        for row in c.fetchall():
            trans = dict(row)
            trans['device_name'] = f"{trans['device_type']} #{trans['device_number']}"
            trans['duration'] = f"{trans['duration_minutes'] // 60}h {trans['duration_minutes'] % 60}m"
            transactions.append(trans)
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'start_date': start_date,
                'end_date': end_date,
                'total_revenue': round(total_revenue, 2),
                'total_sessions': total_sessions,
                'transactions': transactions
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Page not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

# ==================== RUN APPLICATION ====================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
