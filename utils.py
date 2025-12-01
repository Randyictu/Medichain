import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from param import from_email, app_password
from datetime import datetime, timedelta
import hashlib
import bcrypt

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), 
                         bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    """Check password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def generate_otp():
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))

def hash_otp(otp):
    """Hash OTP for secure storage"""
    return hashlib.sha256(otp.encode()).hexdigest()

def store_otp_in_db(email, otp, otps_ref=None, local_db=None):
    """
    Store OTP in Firebase Firestore or Local Database
    
    Args:
        email: User's email
        otp: Generated OTP
        otps_ref: Firestore collection reference (for Firebase)
        local_db: Local database instance (for local mode)
    """
    try:
        hashed_otp = hash_otp(otp)
        expiration = datetime.now() + timedelta(minutes=5)
        
        if otps_ref:
            # Firebase mode
            from google.cloud.firestore import SERVER_TIMESTAMP
            
            otp_doc = {
                'email': email,
                'otp_hash': hashed_otp,
                'created_at': SERVER_TIMESTAMP,
                'expires_at': expiration,
                'used': False
            }
            
            otps_ref.document(email).set(otp_doc)
            print(f"[INFO] OTP stored in Firebase for {email}")
        elif local_db:
            # Local mode
            local_db.store_otp(email, hashed_otp, expiration)
            print(f"[INFO] OTP stored locally for {email}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to store OTP: {e}")
        return False

def verify_otp_code(email, otp, otps_ref=None, local_db=None):
    """
    Verify OTP from Firebase Firestore or Local Database
    
    Args:
        email: User's email
        otp: OTP to verify
        otps_ref: Firestore collection reference (for Firebase)
        local_db: Local database instance (for local mode)
    
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        if otps_ref:
            # Firebase mode
            otp_doc = otps_ref.document(email).get()
            
            if not otp_doc.exists:
                print(f"[ERROR] No OTP found for {email}")
                return False
            
            otp_data = otp_doc.to_dict()
            
            if otp_data.get('used', False):
                print(f"[ERROR] OTP already used")
                return False
            
            expires_at = otp_data.get('expires_at')
            if expires_at and datetime.now() > expires_at:
                print(f"[ERROR] OTP expired")
                otps_ref.document(email).delete()
                return False
            
            stored_hash = otp_data.get('otp_hash')
            provided_hash = hash_otp(otp)
            
            if stored_hash == provided_hash:
                otps_ref.document(email).update({'used': True})
                print(f"[SUCCESS] OTP verified")
                return True
            else:
                print(f"[ERROR] Invalid OTP")
                return False
                
        elif local_db:
            # Local mode
            otp_data = local_db.get_otp(email)
            
            if not otp_data:
                print(f"[ERROR] No OTP found for {email}")
                return False
            
            if otp_data.get('used', False):
                print(f"[ERROR] OTP already used")
                return False
            
            expires_at = datetime.fromisoformat(otp_data['expires_at'])
            if datetime.now() > expires_at:
                print(f"[ERROR] OTP expired")
                local_db.delete_otp(email)
                return False
            
            stored_hash = otp_data.get('otp_hash')
            provided_hash = hash_otp(otp)
            
            if stored_hash == provided_hash:
                local_db.mark_otp_used(email)
                print(f"[SUCCESS] OTP verified")
                return True
            else:
                print(f"[ERROR] Invalid OTP")
                return False
                
    except Exception as e:
        print(f"[ERROR] OTP verification failed: {e}")
        return False

def send_otp(to_email, otps_ref=None, local_db=None) -> str:
    """
    Generate and send OTP via email
    
    Args:
        to_email: Recipient email
        otps_ref: Firestore collection reference (for Firebase, optional)
        local_db: Local database instance (for local mode, optional)
    
    Returns:
        str: Success or error message
    """
    try:
        otp = generate_otp()
        print(f"[DEBUG] Generated OTP: {otp}")
        
        subject = "Your OTP Code for Cloud Security"
        body = f"""
Hello,

Your One-Time Password (OTP) for login verification is:

    {otp}

This OTP is valid for 5 minutes. Do not share this code with anyone.

If you did not request this code, please ignore this email.

Best regards,
Cloud Security Team
"""
        
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        print(f"Starting tls session on smtp.gmail.com:587 .........", end='')
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            print('[OK]')
            
            print(f"login to the server with {from_email} .........", end='')
            server.login(from_email, app_password)
            print('[OK]')
            
            print(f"Sending OTP data to {to_email}  .........", end='')
            server.send_message(msg)
            print('[OK]')
            
            print(f"OTP data sent to {to_email} successfully!")
            
            # Store OTP
            store_otp_in_db(to_email, otp, otps_ref, local_db)
            
            return f"OTP sent to your email: {to_email} successfully!"
            
    except Exception as e:
        error_msg = f"Failed to send email: {e}"
        print(f"[ERROR] {error_msg}")
        return f"Error: {error_msg}"

def send_welcome_email(to_email, username):
    """Send welcome email to new users"""
    try:
        subject = "Welcome to Cloud Security Platform!"
        body = f"""
Hello {username},

Welcome to the Cloud Security Platform!

Your account has been successfully created. You can now:
- Access secure cloud storage
- Enable two-factor authentication
- Manage your profile settings

Thank you for joining us!

Best regards,
Cloud Security Team
"""
        
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(from_email, app_password)
            server.send_message(msg)
        
        print(f"[SUCCESS] Welcome email sent to {to_email}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send welcome email: {e}")
        return False

def is_valid_email(email):
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_strong_password(password):
    """
    Validate password strength
    Returns: (bool, str) - (is_valid, message)
    """
    import re
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain digit"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain special character"
    
    return True, "Password is strong"

if __name__ == '__main__':
    print("Testing utility functions...\n")
    
    print("Email validation:")
    print(f"  test@example.com: {is_valid_email('test@example.com')}")
    print(f"  invalid-email: {is_valid_email('invalid-email')}")
    
    print("\nPassword strength:")
    strong, msg = is_strong_password("Weak123")
    print(f"  Weak123: {strong} - {msg}")
    strong, msg = is_strong_password("Strong@Pass123")
    print(f"  Strong@Pass123: {strong} - {msg}")
    
    print(f"\nGenerated OTP: {generate_otp()}")
    
    print("\nPassword hashing:")
    password = "TestPass123!"
    hashed = hash_password(password)
    print(f"  Original: {password}")
    print(f"  Hashed: {hashed[:30]}...")
    print(f"  Verification: {check_password(password, hashed)}")