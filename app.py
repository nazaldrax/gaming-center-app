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
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Create Transactions Table
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        member_id INTEGER,
        member_name TEXT,
        device_name TEXT,
        amount REAL,
        payment_status TEXT,
        payment_date TIMESTAMP,
        transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Create Reservations Table
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
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    conn.commit()
    
    # Initialize devices
    for device_type, info in DEVICES.items():
        for i in range(1, info['total'] + 1):
            try:
                c.execute('''INSERT OR IGNORE INTO devices 
                    (device_type, device_number, rate_per_hour) 
                    VALUES (?, ?, ?)''',
                    (device_type, i, info['rate']))
            except sqlite3.IntegrityError:
                pass
    
    conn.commit()
    conn.close()

# Initialize DB on startup
if not os.path.exists(DATABASE):
    init_db()

# ==================== ROUTES ====================

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/members')
def members():
    return render_template('members.html')

@app.route('/reports')
def reports():
    return render_template('reports.html')

@app.route('/bookings')
def bookings():
    return render_template('bookings.html')

# ==================== MEMBER APIs ====================

@app.route('/api/members', methods=['GET', 'POST'])
def api_members():
    conn = get_db()
    c = conn.cursor()
    
    if request.method == 'POST':
        data = request.json
        try:
            c.execute('''INSERT INTO members (name, mobile, address) 
                VALUES (?, ?, ?)''',
                (data['name'], data['mobile'], data['address']))
            conn.commit()
            return jsonify({'success': True, 'message': 'Member added successfully'})
        except sqlite3.IntegrityError:
            return jsonify({'success': False, 'error': 'Mobile number already exists'}), 400
    
    c.execute('SELECT * FROM members ORDER BY created_at DESC')
    members = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(members)

@app.route('/api/members/search')
def search_members():
    query = request.args.get('q', '').lower()
    conn = get_db()
    c = conn.cursor()
    c.execute('''SELECT * FROM members WHERE 
        LOWER(name) LIKE ? OR mobile LIKE ? 
        ORDER BY created_at DESC''',
        (f'%{query}%', f'%{query}%'))
    members = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(members)

# ==================== DEVICE APIs ====================

@app.route('/api/devices')
def api_devices():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM devices ORDER BY device_type, device_number')
    devices = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(devices)

@app.route('/api/devices/available')
def api_available_devices():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM devices WHERE status = 'Available' ORDER BY device_type, device_number")
    devices = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(devices)

# ==================== SESSION APIs ====================

@app.route('/api/sessions/start', methods=['POST'])
def start_session():
    data = request.json
    conn = get_db()
    c = conn.cursor()
    
    # Get member info
    c.execute('SELECT * FROM members WHERE id = ?', (data['member_id'],))
    member = c.fetchone()
    if not member:
        return jsonify({'success': False, 'error': 'Member not found'}), 400
    
    # Get device info
    c.execute('SELECT * FROM devices WHERE id = ?', (data['device_id'],))
    device = c.fetchone()
    if not device or device['status'] != 'Available':
        return jsonify({'success': False, 'error': 'Device not available'}), 400
    
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=int(data['duration']))
    total_amount = (int(data['duration']) / 60) * device['rate_per_hour']
    
    try:
        c.execute('''INSERT INTO sessions 
            (member_id, member_name, device_id, device_type, device_number, 
             start_time, end_time, duration_minutes, rate_per_hour, total_amount, payment_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (member['id'], member['name'], device['id'], device['device_type'], 
             device['device_number'], start_time, end_time, data['duration'],
             device['rate_per_hour'], total_amount, 'Active'))
        
        # Update device status
        c.execute('UPDATE devices SET status = ?, current_member_id = ? WHERE id = ?',
            ('Occupied', member['id'], device['id']))
        
        conn.commit()
        session_id = c.lastrowid
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'Session started successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/sessions/active')
def active_sessions():
    conn = get_db()
    c = conn.cursor()
    c.execute('''SELECT * FROM sessions WHERE payment_status = 'Active' 
        ORDER BY start_time DESC''')
    sessions = [dict(row) for row in c.fetchall()]
    
    # Calculate remaining time for each session
    for session in sessions:
        end_time = datetime.fromisoformat(session['end_time'])
        remaining = (end_time - datetime.now()).total_seconds() / 60
        session['remaining_minutes'] = max(0, int(remaining))
        session['elapsed_minutes'] = session['duration_minutes'] - session['remaining_minutes']
    
    conn.close()
    return jsonify(sessions)

@app.route('/api/sessions/<int:session_id>/extend', methods=['POST'])
def extend_session(session_id):
    data = request.json
    extend_minutes = int(data.get('extend_minutes', 30))
    
    conn = get_db()
    c = conn.cursor()
    
    c.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
    session = c.fetchone()
    if not session or session['payment_status'] != 'Active':
        return jsonify({'success': False, 'error': 'Session not found or not active'}), 400
    
    # Calculate new values
    old_end_time = datetime.fromisoformat(session['end_time'])
    new_end_time = old_end_time + timedelta(minutes=extend_minutes)
    new_duration = session['duration_minutes'] + extend_minutes
    new_total_amount = (new_duration / 60) * session['rate_per_hour']
    
    try:
        c.execute('''UPDATE sessions SET 
            end_time = ?, duration_minutes = ?, total_amount = ?
            WHERE id = ?''',
            (new_end_time, new_duration, new_total_amount, session_id))
        
        conn.commit()
        return jsonify({
            'success': True,
            'new_end_time': new_end_time.isoformat(),
            'new_total_amount': new_total_amount,
            'message': f'Session extended by {extend_minutes} minutes'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/sessions/<int:session_id>/end', methods=['POST'])
def end_session(session_id):
    data = request.json
    payment_status = data.get('payment_status', 'Pending')
    
    conn = get_db()
    c = conn.cursor()
    
    c.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
    session = c.fetchone()
    if not session:
        return jsonify({'success': False, 'error': 'Session not found'}), 400
    
    try:
        # Update session
        c.execute('''UPDATE sessions SET 
            payment_status = ?, end_time = ?
            WHERE id = ?''',
            (payment_status, datetime.now(), session_id))
        
        # Create transaction
        if payment_status in ['Completed', 'Partial']:
            c.execute('''INSERT INTO transactions 
                (session_id, member_id, member_name, device_name, 
                 amount, payment_status, payment_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (session_id, session['member_id'], session['member_name'],
                 f"{session['device_type']} {session['device_number']}",
                 session['total_amount'], payment_status, datetime.now()))
        
        # Update device status - only mark as Available if payment is Completed
        if payment_status == 'Completed':
            c.execute('UPDATE devices SET status = ?, current_member_id = NULL WHERE id = ?',
                ('Available', session['device_id']))
        else:
            c.execute('UPDATE devices SET status = ? WHERE id = ?',
                ('Pending Payment', session['device_id']))
        
        conn.commit()
        return jsonify({
            'success': True,
            'message': f'Session ended - Payment: {payment_status}'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/sessions/<int:session_id>/complete-payment', methods=['POST'])
def complete_payment(session_id):
    conn = get_db()
    c = conn.cursor()
    
    c.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
    session = c.fetchone()
    if not session:
        return jsonify({'success': False, 'error': 'Session not found'}), 400
    
    try:
        # Update session payment status
        c.execute('''UPDATE sessions SET payment_status = ? WHERE id = ?''',
            ('Completed', session_id))
        
        # Create or update transaction
        c.execute('SELECT * FROM transactions WHERE session_id = ?', (session_id,))
        transaction = c.fetchone()
        
        if transaction:
            c.execute('''UPDATE transactions SET 
                payment_status = 'Completed', payment_date = ? 
                WHERE session_id = ?''',
                (datetime.now(), session_id))
        else:
            c.execute('''INSERT INTO transactions 
                (session_id, member_id, member_name, device_name, 
                 amount, payment_status, payment_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (session_id, session['member_id'], session['member_name'],
                 f"{session['device_type']} {session['device_number']}",
                 session['total_amount'], 'Completed', datetime.now()))
        
        # Mark device as Available
        c.execute('UPDATE devices SET status = ?, current_member_id = NULL WHERE id = ?',
            ('Available', session['device_id']))
        
        conn.commit()
        return jsonify({
            'success': True,
            'message': 'Payment completed and device is now available'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

# ==================== REPORTS APIs ====================

@app.route('/api/reports/daily')
def daily_report():
    date_str = request.args.get('date')
    if not date_str:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    try:
        report_date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid date format'}), 400
    
    start_of_day = report_date.replace(hour=0, minute=0, second=0)
    end_of_day = report_date.replace(hour=23, minute=59, second=59)
    
    conn = get_db()
    c = conn.cursor()
    
    # Get all transactions for the day
    c.execute('''SELECT * FROM transactions WHERE 
        payment_date BETWEEN ? AND ? AND payment_status = 'Completed'
        ORDER BY payment_date DESC''',
        (start_of_day, end_of_day))
    transactions = [dict(row) for row in c.fetchall()]
    
    # Calculate summary
    total_revenue = sum(t['amount'] for t in transactions) if transactions else 0
    total_sessions = len(transactions)
    
    # Most used console
    device_counts = {}
    for t in transactions:
        device = t['device_name']
        device_counts[device] = device_counts.get(device, 0) + 1
    
    most_used_console = max(device_counts, key=device_counts.get) if device_counts else 'N/A'
    most_used_count = device_counts.get(most_used_console, 0) if device_counts else 0
    
    conn.close()
    
    return jsonify({
        'success': True,
        'date': date_str,
        'total_revenue': total_revenue,
        'total_sessions': total_sessions,
        'most_used_console': most_used_console,
        'most_used_count': most_used_count,
        'transactions': transactions
    })

@app.route('/api/reports/custom')
def custom_report():
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    if not start_date_str or not end_date_str:
        return jsonify({'success': False, 'error': 'Missing date parameters'}), 400
    
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid date format'}), 400
    
    conn = get_db()
    c = conn.cursor()
    
    c.execute('''SELECT * FROM transactions WHERE 
        payment_date BETWEEN ? AND ? AND payment_status = 'Completed'
        ORDER BY payment_date DESC''',
        (start_date, end_date))
    transactions = [dict(row) for row in c.fetchall()]
    
    total_revenue = sum(t['amount'] for t in transactions) if transactions else 0
    total_sessions = len(transactions)
    
    device_counts = {}
    for t in transactions:
        device = t['device_name']
        device_counts[device] = device_counts.get(device, 0) + 1
    
    most_used_console = max(device_counts, key=device_counts.get) if device_counts else 'N/A'
    
    conn.close()
    
    return jsonify({
        'success': True,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'total_revenue': total_revenue,
        'total_sessions': total_sessions,
        'most_used_console': most_used_console,
        'transactions': transactions
    })

# ==================== RESERVATIONS APIs ====================

@app.route('/api/reservations', methods=['GET', 'POST'])
def api_reservations():
    conn = get_db()
    c = conn.cursor()
    
    if request.method == 'POST':
        data = request.json
        
        # Check for conflicts
        c.execute('''SELECT * FROM reservations WHERE 
            device_id = ? AND status = 'Confirmed' AND
            (start_time < ? AND end_time > ?)''',
            (data['device_id'], data['end_time'], data['start_time']))
        
        if c.fetchone():
            return jsonify({'success': False, 'error': 'Time slot already booked'}), 400
        
        try:
            c.execute('''INSERT INTO reservations 
                (member_id, member_name, device_id, device_type, device_number,
                 reservation_date, start_time, end_time, duration_minutes, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (data['member_id'], data['member_name'], data['device_id'],
                 data['device_type'], data['device_number'], datetime.now(),
                 data['start_time'], data['end_time'], data['duration_minutes'],
                 data.get('notes', '')))
            
            conn.commit()
            return jsonify({'success': True, 'message': 'Reservation created'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # GET - fetch upcoming reservations
    c.execute('''SELECT * FROM reservations WHERE 
        status = 'Confirmed' AND start_time >= ? 
        ORDER BY start_time ASC''',
        (datetime.now(),))
    reservations = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(reservations)

@app.route('/api/reservations/<int:reservation_id>', methods=['DELETE'])
def delete_reservation(reservation_id):
    conn = get_db()
    c = conn.cursor()
    
    try:
        c.execute('UPDATE reservations SET status = ? WHERE id = ?',
            ('Cancelled', reservation_id))
        conn.commit()
        return jsonify({'success': True, 'message': 'Reservation cancelled'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
