"""
CloudSync Pro - Enhanced Web API with VIP Support
Email-only OTP, VIP accounts, improved security
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import time
import hashlib
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Configuration
ADMIN_EMAIL = 'admin@cloudsync.com'
ADMIN_PASSWORD = 'AdminSecure123!'

# Email configuration (update with your credentials)
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
FROM_EMAIL = 'sasbergson@gmail.com'  # UPDATE THIS
APP_PASSWORD = 'tgnwazxwlfjrjsuz'   # UPDATE THIS - Gmail App Password

# In-memory storage
users_storage = {}
otp_storage = {}

# Helper functions
def generate_otp():
    """Generate 6-digit OTP"""
    return str(random.randint(100000, 999999))

def hash_otp(otp):
    """Hash OTP for secure storage"""
    return hashlib.sha256(otp.encode()).hexdigest()

def send_email_otp(to_email, otp):
    """Send OTP via email - EMAIL ONLY"""
    try:
        subject = "Your OTP Code for CloudSync Pro"
        body = f"""
Hello,

Your One-Time Password (OTP) for login verification is:

    {otp}

This OTP is valid for 5 minutes. Do not share this code with anyone.

If you did not request this code, please ignore this email.

Best regards,
CloudSync Pro Team
"""
        
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        # Send via SMTP
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
        server.starttls()
        server.login(FROM_EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"[SUCCESS] ✅ OTP sent to {to_email}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send OTP email: {e}")
        return False

def send_welcome_email(to_email, username):
    """Send welcome email"""
    try:
        subject = "Welcome to CloudSync Pro!"
        body = f"""
Hello {username},

Welcome to CloudSync Pro!

Your account has been successfully created. You can now:
- Access 30GB secure cloud storage
- Upload files with automatic replication
- Manage your files securely

To upgrade to VIP (100GB storage), contact support.

Best regards,
CloudSync Pro Team
"""
        
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
        server.starttls()
        server.login(FROM_EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"[SUCCESS] Welcome email sent to {to_email}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send welcome email: {e}")
        return False

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Serve index.html"""
    try:
        if os.path.exists('index.html'):
            return send_file('index.html')
        else:
            return "<h1>Error: index.html not found</h1>", 404
    except Exception as e:
        return f"<h1>Error: {e}</h1>", 500

@app.route('/<path:filename>')
def serve_static_files(filename):
    """Serve static files"""
    try:
        if filename.startswith('api/'):
            return jsonify({'error': 'Not found'}), 404
        
        if os.path.exists(filename):
            return send_file(filename)
        else:
            return index()
    except Exception as e:
        return jsonify({'error': str(e)}), 404

# ==================== AUTHENTICATION ====================

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """Signup - Send welcome email"""
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        phone = data.get('phone', '')
        
        if not all([username, email, password]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if email in users_storage:
            return jsonify({'error': 'Email already registered'}), 400
        
        # Store user (default: standard account)
        users_storage[email] = {
            'username': username,
            'email': email,
            'password': password,
            'phone': phone,
            'role': 'user',  # Can be upgraded to 'vip'
            'uid': f'user_{int(time.time() * 1000)}',
            'created_at': datetime.now().isoformat()
        }
        
        print(f"\n✅ USER REGISTERED")
        print(f"  Username: {username}")
        print(f"  Email: {email}")
        print(f"  Role: Standard User")
        print("="*70 + "\n")
        
        # Send welcome email
        send_welcome_email(email, username)
        
        return jsonify({
            'success': True,
            'message': 'Account created! Check your email for welcome message.',
            'email': email
        }), 200
        
    except Exception as e:
        print(f"❌ Signup error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login - Admin direct, Users get OTP via email"""
    try:
        data = request.json
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        print(f"\n🔐 LOGIN ATTEMPT: {email}")
        
        if not email or not password:
            return jsonify({'error': 'Missing credentials'}), 400
        
        # Check for ADMIN
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            print("✅ ADMIN LOGIN SUCCESSFUL\n")
            
            return jsonify({
                'success': True,
                'message': 'Admin login successful',
                'user': {
                    'email': ADMIN_EMAIL,
                    'uid': 'admin_001',
                    'role': 'admin',
                    'username': 'Administrator'
                },
                'requires_otp': False
            }), 200
        
        # Check regular user credentials
        if email not in users_storage:
            print(f"❌ User not found: {email}\n")
            return jsonify({'error': 'Invalid credentials'}), 401
        
        user = users_storage[email]
        
        if user['password'] != password:
            print(f"❌ Invalid password: {email}\n")
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate OTP and send via EMAIL
        otp = generate_otp()
        otp_hash = hash_otp(otp)
        
        # Store OTP
        otp_storage[email] = {
            'otp': otp,
            'hash': otp_hash,
            'expires': time.time() + 300,
            'used': False
        }
        
        print(f"📧 Sending OTP to {email}...")
        
        # Send OTP via email (not console!)
        if send_email_otp(email, otp):
            print(f"✅ OTP sent successfully\n")
            return jsonify({
                'success': True,
                'message': f'OTP sent to your email!',
                'email': email,
                'requires_otp': True
            }), 200
        else:
            print(f"❌ Failed to send OTP email\n")
            return jsonify({'error': 'Failed to send OTP. Check email configuration.'}), 500
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP and complete login"""
    try:
        data = request.json
        email = data.get('email')
        otp = data.get('otp')
        
        print(f"\n🔐 OTP VERIFICATION: {email}")
        
        if not email or not otp:
            return jsonify({'error': 'Missing email or OTP'}), 400
        
        # Check if OTP exists
        if email not in otp_storage:
            print(f"❌ No OTP found\n")
            return jsonify({'error': 'No OTP found. Please login again.'}), 401
        
        stored_otp_data = otp_storage[email]
        
        # Check expiration
        if time.time() > stored_otp_data['expires']:
            del otp_storage[email]
            print(f"❌ OTP expired\n")
            return jsonify({'error': 'OTP expired. Please login again.'}), 401
        
        # Check if used
        if stored_otp_data['used']:
            print(f"❌ OTP already used\n")
            return jsonify({'error': 'OTP already used'}), 401
        
        # Verify OTP
        provided_hash = hash_otp(otp)
        
        if stored_otp_data['hash'] != provided_hash:
            print(f"❌ Invalid OTP\n")
            return jsonify({'error': 'Invalid OTP'}), 401
        
        # Mark as used
        stored_otp_data['used'] = True
        
        # Get user
        if email not in users_storage:
            users_storage[email] = {
                'username': email.split('@')[0],
                'email': email,
                'role': 'user',
                'uid': f'user_{int(time.time() * 1000)}'
            }
        
        user = users_storage[email]
        
        print(f"✅ OTP VERIFIED")
        print(f"  User: {user['username']}")
        print(f"  Role: {user.get('role', 'user')}\n")
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'email': user['email'],
                'uid': user['uid'],
                'role': user.get('role', 'user'),
                'username': user.get('username', email.split('@')[0])
            }
        }), 200
        
    except Exception as e:
        print(f"❌ OTP verification error: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== VIP MANAGEMENT ====================

@app.route('/api/admin/upgrade-vip', methods=['POST'])
def upgrade_to_vip():
    """Admin: Upgrade user to VIP"""
    try:
        data = request.json
        admin_email = data.get('admin_email')
        admin_password = data.get('admin_password')
        target_email = data.get('target_email')
        
        # Verify admin
        if admin_email != ADMIN_EMAIL or admin_password != ADMIN_PASSWORD:
            return jsonify({'error': 'Unauthorized'}), 401
        
        if target_email not in users_storage:
            return jsonify({'error': 'User not found'}), 404
        
        # Upgrade to VIP
        users_storage[target_email]['role'] = 'vip'
        
        print(f"\n⭐ VIP UPGRADE")
        print(f"  User: {users_storage[target_email]['username']}")
        print(f"  Email: {target_email}")
        print("="*70 + "\n")
        
        return jsonify({
            'success': True,
            'message': f'User {target_email} upgraded to VIP'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'message': 'CloudSync Pro API',
        'users': len(users_storage),
        'vip_users': len([u for u in users_storage.values() if u.get('role') == 'vip'])
    }), 200

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(e):
    return index()

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print('\n' + '='*70)
    print('  CLOUDSYNC PRO - WEB API SERVER (Enhanced)')
    print('='*70)
    print(f'  Server: http://localhost:5000')
    print(f'  Admin: {ADMIN_EMAIL} / {ADMIN_PASSWORD}')
    print(f'  OTP: Via email only (check {FROM_EMAIL})')
    print(f'  Features: VIP accounts, Email OTP, Enhanced security')
    print('='*70)
    
    if FROM_EMAIL == 'your_email@gmail.com':
        print('\n  ⚠️  WARNING: Update email credentials in web_api.py!')
        print('      FROM_EMAIL and APP_PASSWORD need to be configured\n')
    
    if os.path.exists('index.html'):
        print('  ✅ index.html found')
    else:
        print('  ❌ WARNING: index.html not found!')
    
    print('='*70 + '\n')
    
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)