# Gaming Center Management System

## 🎮 Complete Web Application for Managing a Gaming Center

A modern, responsive, and user-friendly web application built with **Flask** (Python), **SQLite**, and **Bootstrap 5** for managing gaming consoles, customer sessions, and revenue analytics.

---

## ✨ Features

### 🖥️ **Core System Features**

#### A. Inventory & Device Setup
- **Multi-device Support:**
  - PS5 Consoles: 8 units (₹100/hr)
  - Gaming PCs: 2 units (₹120/hr)
  - Driving Console: 1 unit (₹150/hr)
- **Real-time Device Status Dashboard** with visual indicators (Available, Occupied, Expiring Soon)
- Grid-based responsive layout showing all devices

#### B. Customer & Member Management
- **Member Registration Form** with fields:
  - Full Name
  - Mobile Number (10 digits)
  - Address
- **Quick Search** functionality by name or mobile number
- **Guest/Walk-in Support** for non-registered users
- **Member List** with creation date and contact details

#### C. Session Allocation & Billing
- **Session Start** with device and duration selection
- **Flexible Duration Options:** 30 min, 1 hour, 2 hours (customizable)
- **Auto-calculated Bill Amount** based on hourly rates
- **Active Timer Display** showing elapsed and remaining time
- **Session Extension** with +30 min option
- **Instant Payment Completion**

#### D. Real-Time Notifications
- **Visual Alerts** when 5 minutes remaining
- **Audio Alerts** using Web Audio API
- **Browser Notifications** with optional permission
- **Toast Notifications** for all session events

#### E. Daily Reports & Revenue Analytics
- **Summary Dashboard** with:
  - Total Revenue Today
  - Total Sessions Played
  - Most Used Console Type
- **Detailed Transaction Table** showing:
  - Customer Name
  - Device Name & Number
  - Session Duration
  - Start/End Time
  - Total Amount Paid
- **Date Range Filtering:**
  - Today
  - Yesterday
  - Custom Date Range

---

## 🏗️ Project Structure

```
gaming_center_app/
├── app.py                          # Flask backend & database logic
├── database.db                     # SQLite database (auto-created)
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── templates/
│   ├── base.html                  # Main layout with navbar
│   ├── dashboard.html             # Real-time console grid & timers
│   ├── members.html               # Member registration & list
│   └── reports.html               # Revenue reports & analytics
└── static/
    ├── css/
    │   └── style.css              # Dark gaming theme CSS
    └── js/
        └── timer.js               # Timer & notification system
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser (Chrome, Firefox, Edge, Safari)

### Step 1: Clone the Repository
```bash
git clone https://github.com/nazaldrax/gaming-center-app.git
cd gaming-center-app
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python app.py
```

The application will start on `http://localhost:5000`

### Step 5: Access the Application
Open your web browser and navigate to:
```
http://localhost:5000
```

---

## 📱 Usage Guide

### Dashboard
1. **View All Devices** - See real-time status of all consoles
2. **Start a Session:**
   - Click "Start Session" on an available device
   - Search for and select a registered member (or enter guest name)
   - Select session duration
   - Confirm total bill amount
   - Click "Start Session"
3. **Monitor Active Sessions** - View elapsed/remaining time with live countdown
4. **Extend Session** - Add extra time during active play
5. **End Session** - Mark as completed and trigger payment

### Members Management
1. **Register New Member:**
   - Click "Add New Member" button
   - Fill in name, mobile number, and address
   - Save to database
2. **Search Members** - Find existing members by name or phone
3. **View Member History** - Check past sessions (coming soon)

### Reports & Analytics
1. **Daily Reports:**
   - Click "Reports" in navigation
   - Select "Today" or "Yesterday"
   - View summary cards and transaction details
2. **Custom Date Range:**
   - Select "Custom"
   - Pick start and end dates
   - Generate detailed report
3. **Export Data** - Transaction data can be copied for external use

---

## 🎨 Design & UI

### Dark Gaming Theme
- **Modern Neon Color Scheme:**
  - Primary: Neon Blue (#00d4ff)
  - Secondary: Neon Green (#00ff41)
  - Accent: Neon Pink (#ff006e)
- **Responsive Grid Layout** - Works on desktop, tablet, and mobile
- **Smooth Animations** - Hover effects and transitions
- **Glass Morphism Cards** - Modern card design with shadows
- **Accessibility** - High contrast, readable fonts, ARIA labels

---

## 🛠️ Technical Stack

### Backend
- **Framework:** Flask 3.0.0
- **Database:** SQLite3 (built-in Python module)
- **Server:** Werkzeug 3.0.1

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Custom dark theme with animations
- **Bootstrap 5** - Responsive grid system
- **Vanilla JavaScript** - Timer system, notifications, API calls

### APIs Provided
- RESTful endpoints for all CRUD operations
- JSON request/response format
- Session management
- Real-time data fetching

---

## 📊 Database Schema

### Tables

**members**
```sql
id (INTEGER, PRIMARY KEY)
name (TEXT)
mobile (TEXT, UNIQUE)
address (TEXT)
created_at (TIMESTAMP)
```

**devices**
```sql
id (INTEGER, PRIMARY KEY)
device_type (TEXT)
device_number (INTEGER)
status (TEXT: Available/Occupied)
current_member_id (INTEGER, FOREIGN KEY)
rate_per_hour (REAL)
```

**sessions**
```sql
id (INTEGER, PRIMARY KEY)
member_id (INTEGER, FOREIGN KEY)
member_name (TEXT)
device_id (INTEGER, FOREIGN KEY)
device_type (TEXT)
device_number (INTEGER)
start_time (TIMESTAMP)
end_time (TIMESTAMP)
duration_minutes (INTEGER)
rate_per_hour (REAL)
total_amount (REAL)
payment_status (TEXT: Pending/Completed)
created_at (TIMESTAMP)
```

**transactions**
```sql
id (INTEGER, PRIMARY KEY)
session_id (INTEGER, FOREIGN KEY)
member_name (TEXT)
device_name (TEXT)
amount (REAL)
payment_status (TEXT)
transaction_date (TIMESTAMP)
```

---

## 🔗 API Endpoints

### Members
- `GET /api/members` - Get all members
- `GET /api/members/search?q=query` - Search members
- `POST /api/members` - Add new member

### Devices
- `GET /api/devices` - Get all devices with status
- `GET /api/devices/<id>` - Get specific device

### Sessions
- `POST /api/sessions/start` - Start new session
- `GET /api/sessions/active` - Get active sessions
- `GET /api/sessions/<id>` - Get session details
- `POST /api/sessions/<id>/extend` - Extend session
- `POST /api/sessions/<id>/end` - End session

### Reports
- `GET /api/reports/daily?date=YYYY-MM-DD` - Daily report
- `GET /api/reports/custom?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` - Custom report

---

## ⚙️ Configuration

### Device Rates
To modify device types or hourly rates, edit the `DEVICES` dictionary in `app.py`:

```python
DEVICES = {
    'PS5': {'total': 8, 'rate': 100, 'color': '#00d4ff'},
    'Gaming PC': {'total': 2, 'rate': 120, 'color': '#00ff41'},
    'Driving Console': {'total': 1, 'rate': 150, 'color': '#ff006e'}
}
```

### Alert Settings
To change alert threshold, modify in `static/js/timer.js`:

```javascript
const ALERT_THRESHOLD = 5 * 60; // 5 minutes in seconds
```

---

## 🐛 Troubleshooting

### Application won't start
- Ensure Python 3.8+ is installed: `python --version`
- Check Flask is installed: `pip list | grep Flask`
- Port 5000 might be in use: `python app.py` (Flask will suggest alternative)

### Database errors
- Delete `database.db` to reset (will be auto-created)
- Ensure write permissions in application directory

### Timer not working
- Check browser console for JavaScript errors
- Ensure JavaScript is enabled in browser
- Clear browser cache and reload

### Notifications not showing
- Grant notification permission when prompted
- Check browser notification settings
- Some browsers require HTTPS for notifications

---

## 📝 Future Enhancements

- [ ] User authentication & admin roles
- [ ] Payment gateway integration
- [ ] SMS notifications to members
- [ ] Email reports
- [ ] Advanced analytics with charts
- [ ] Member loyalty program
- [ ] Multi-location support
- [ ] Mobile app (React Native/Flutter)
- [ ] Dark/Light mode toggle
- [ ] Backup & restore functionality

---

## 📄 License

This project is provided as-is for educational and commercial use.

---

## 👨‍💻 Author

**Your Gaming Center Management Solution**
- GitHub: [nazaldrax](https://github.com/nazaldrax)
- Repository: [gaming-center-app](https://github.com/nazaldrax/gaming-center-app)

---

## 💬 Support

For issues, questions, or suggestions:
1. Check existing GitHub issues
2. Create a new issue with detailed description
3. Include error messages and screenshots

---

## 🎯 Quick Start Summary

```bash
# 1. Clone
git clone https://github.com/nazaldrax/gaming-center-app.git
cd gaming-center-app

# 2. Setup virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run application
python app.py

# 5. Open browser
http://localhost:5000
```

---

**Happy Gaming! 🎮✨**
