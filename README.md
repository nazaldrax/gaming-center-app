# Gaming Center Management System - Complete Setup Guide

## 🎮 Project Overview

A modern, full-featured Gaming Center Management System built with **Flask** and **SQLite**, designed to manage consoles, track gaming sessions, handle payments, and provide detailed revenue reports.

### ✨ Key Features

- **Real-Time Dashboard**: Live console status tracking with visual indicators
- **Session Management**: Start, extend, and end gaming sessions with automatic billing
- **Payment Processing**: Track pending and completed payments with transaction logs
- **Reservations System**: Book consoles in advance with conflict detection
- **Member Management**: Register members with contact information
- **Revenue Reports**: Daily and custom date range reports with analytics
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Dark Gaming Theme**: Modern cyberpunk-inspired UI with neon colors

---

## 📋 System Requirements

- Python 3.8+
- Flask 2.0+
- SQLite3
- Modern web browser (Chrome, Firefox, Safari, Edge)

---

## 🚀 Installation & Setup

### Step 1: Clone Repository
```bash
git clone https://github.com/nazaldrax/gaming-center-app.git
cd gaming-center-app
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install flask
```

### Step 4: Run Application
```bash
python app.py
```

The application will start at `http://localhost:5000`

---

## 📁 Project Structure

```
gaming-center-app/
├── app.py                          # Main Flask application
├── database.db                     # SQLite database (created on first run)
├── templates/
│   ├── base.html                  # Base template with navigation
│   ├── dashboard.html             # Console management & sessions
│   ├── members.html               # Member management page
│   ├── reports.html               # Revenue analytics
│   └── bookings.html              # Reservations system
├── static/
│   ├── css/
│   │   └── style.css              # Gaming theme styles
│   └── js/
│       └── timer.js               # Session timer functionality
└── README.md                       # This file
```

---

## 💾 Database Schema

### Members Table
```sql
CREATE TABLE members (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    mobile TEXT NOT NULL UNIQUE,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Devices Table
```sql
CREATE TABLE devices (
    id INTEGER PRIMARY KEY,
    device_type TEXT NOT NULL,
    device_number INTEGER NOT NULL,
    status TEXT DEFAULT 'Available',
    current_member_id INTEGER,
    rate_per_hour REAL NOT NULL,
    UNIQUE(device_type, device_number)
)
```

### Sessions Table
```sql
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY,
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
)
```

### Transactions Table
```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY,
    session_id INTEGER,
    member_id INTEGER,
    member_name TEXT,
    device_name TEXT,
    amount REAL,
    payment_status TEXT,
    payment_date TIMESTAMP,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Reservations Table
```sql
CREATE TABLE reservations (
    id INTEGER PRIMARY KEY,
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
)
```

---

## 🎯 Default Devices & Rates

| Console | Quantity | Rate/Hour |
|---------|----------|-----------|
| PS5 | 8 | ₹100 |
| Gaming PC | 2 | ₹120 |
| Driving Console | 1 | ₹150 |

---

## 📡 API Endpoints

### Member Management
- `GET /api/members` - Get all members
- `POST /api/members` - Add new member
- `GET /api/members/search?q=query` - Search members

### Device Management
- `GET /api/devices` - Get all devices
- `GET /api/devices/<id>` - Get device details

### Session Management
- `POST /api/sessions/start` - Start new session
- `GET /api/sessions/active` - Get active sessions
- `GET /api/sessions/<id>` - Get session details
- `POST /api/sessions/<id>/extend` - Extend session
- `POST /api/sessions/<id>/end` - End session and record payment

### Reservations
- `GET /api/reservations` - Get upcoming reservations
- `POST /api/reservations` - Create booking
- `DELETE /api/reservations/<id>` - Cancel reservation

### Reports
- `GET /api/reports/daily?date=YYYY-MM-DD` - Daily revenue report
- `GET /api/reports/custom?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` - Custom range report

---

## 🎮 How to Use

### Dashboard

1. **View Console Status**: All consoles are displayed with real-time status (Available/Occupied)
2. **Start Session**:
   - Click "Start Session" on an available console
   - Select a registered member from dropdown
   - Choose duration (30 min, 1 hour, 2 hours)
   - Review bill amount and click "Start Session"
3. **Monitor Active Sessions**:
   - Active sessions auto-refresh every 5 seconds
   - View elapsed time, remaining time, and total bill
   - 5-minute warning alert triggers automatically
4. **End Session**:
   - Click "End & Pay" to close the session
   - Choose payment status: Pending, Completed, or Partial
   - Device automatically becomes available when payment is completed

### Members Page

1. **Add Member**:
   - Enter name, mobile number, and address
   - Mobile number must be unique
2. **Search Members**:
   - Quick search by name or mobile
   - View all registered members
3. **View Details**:
   - Check member profile and contact info

### Bookings Page

1. **Create Reservation**:
   - Select member and device
   - Choose date and time
   - Set duration and add notes
   - Click "Create Booking"
2. **View Reservations**:
   - See all upcoming bookings in table
   - Cancel bookings if needed
3. **Conflict Detection**:
   - System automatically prevents double-booking
   - Shows time slot availability

### Reports Page

1. **Daily Report**:
   - Select date to view that day's revenue
   - See total revenue, session count, and most used console
   - View detailed transaction list
2. **Custom Report**:
   - Choose start and end dates
   - Get aggregated data for period
   - Export-ready transaction details

---

## 💳 Payment Workflow

### Session End Options

1. **End Session (Pending)**
   - Session ends but device remains unavailable
   - Payment marked as "Pending"
   - Device can be freed later after payment
   - Useful for installment payments or cash collection

2. **Payment Completed**
   - Session ends and device becomes available immediately
   - Payment marked as "Completed"
   - Transaction logged with payment date
   - Amount appears in daily/custom reports

3. **Partial Payment**
   - Session ends and device becomes available
   - Payment marked as "Partial"
   - Partial amount recorded in transactions
   - Outstanding amount tracked separately

---

## 🔒 Data Validation

- **Member Names**: Required, validated for empty input
- **Mobile Numbers**: Required, must be unique, validated for duplicates
- **Device Selection**: Only available devices can be selected
- **Session Duration**: Minimum 30 minutes, maximum 180 minutes
- **Reservation Dates**: Cannot book in the past
- **Time Slot Conflicts**: Automatic detection and prevention

---

## ⚙️ Configuration

### Device Setup (in app.py)

To add or modify devices, edit the `DEVICES` dictionary:

```python
DEVICES = {
    'PS5': {'total': 8, 'rate': 100, 'color': '#00d4ff'},
    'Gaming PC': {'total': 2, 'rate': 120, 'color': '#00ff41'},
    'Driving Console': {'total': 1, 'rate': 150, 'color': '#ff006e'}
}
```

### Database Location

Default: `database.db` in project root

To change, modify in `app.py`:
```python
DATABASE = 'path/to/database.db'
```

### Server Settings

Default port: `5000`

To change, modify last line of `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=YOUR_PORT)
```

---

## 🐛 Troubleshooting

### Issue: "Address already in use"
**Solution**: Change port in app.py or kill process on port 5000

### Issue: Database locked error
**Solution**: Close all database connections and restart Flask

### Issue: Members not loading
**Solution**: Ensure database.db exists and is not corrupted. Delete it and restart to recreate.

### Issue: Sessions not updating in real-time
**Solution**: Refresh browser or check browser console for errors

---

## 🔐 Security Notes

- Store in secure environment (not production)
- Use HTTPS in production deployment
- Add authentication/authorization layer for multi-user
- Regularly backup database
- Validate all user inputs

---

## 📊 Future Enhancements

- [ ] User authentication and roles
- [ ] Online payment integration (Razorpay, Stripe)
- [ ] SMS/Email notifications
- [ ] Advance booking with deposits
- [ ] Loyalty programs
- [ ] Staff management
- [ ] Inventory management
- [ ] Analytics dashboard with charts
- [ ] Mobile app
- [ ] Multi-location support

---

## 🤝 Support & Contact

For issues, suggestions, or contributions:
- GitHub Issues: [Create an issue](https://github.com/nazaldrax/gaming-center-app/issues)
- Email: nazaldrax@example.com

---

## 📝 License

This project is open source and available for personal and commercial use.

---

## 🎊 Happy Gaming!

Manage your gaming center efficiently with this modern, feature-rich management system!

**Last Updated**: September 12, 2026
**Version**: 1.0.0
