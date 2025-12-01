"""
Configuration file for Cloud Security System
Store sensitive credentials as environment variables in production
"""

import os

# Email Configuration for OTP delivery
# IMPORTANT: Use Gmail App Password, not your regular password
# How to get App Password:
# 1. Go to Google Account Settings
# 2. Security → 2-Step Verification (enable it)
# 3. App Passwords → Generate new app password
# 4. Copy the 16-character password

from_email = "sasbergson@gmail.com"
from_password = "Them0stw@ntedm@n"  # Regular password (deprecated)
app_password = "tgnw azxw lfjr jsuz"  # App-specific password (USE THIS)

# Firebase Configuration
# Get this from Firebase Console → Project Settings → General → Web API Key
# Required only if using Firebase mode
firebase_api_key = os.getenv('FIREBASE_API_KEY', 'YOUR_FIREBASE_API_KEY')

# Firebase Credentials File Path
# This is the service account JSON file downloaded from Firebase Console
# Required only if using Firebase mode
firebase_credentials_path = 'firebase-credentials.json'

# Server Configuration
server_host = 'localhost'
server_port = 51234

# OTP Configuration
otp_expiry_minutes = 5  # OTP validity duration
otp_length = 6  # Number of digits in OTP

# Security Settings
min_password_length = 8
require_special_char = True
require_uppercase = True
require_lowercase = True
require_digit = True

# Two-Factor Authentication
two_factor_enabled_by_default = True

# Development/Debug Settings
debug_mode = False
print_otp_to_console = True  # For development only - prints OTP to console

# SMTP Configuration
smtp_server = 'smtp.gmail.com'
smtp_port = 587
smtp_use_tls = True

# Display configuration summary (for debugging)
def print_config():
    """Print current configuration (excluding sensitive data)"""
    print("\n" + "="*70)
    print("  CONFIGURATION SUMMARY")
    print("="*70)
    print(f"  Email From: {from_email}")
    print(f"  Firebase API Key: {'SET' if firebase_api_key != 'YOUR_FIREBASE_API_KEY' else 'NOT SET'}")
    print(f"  Firebase Credentials: {firebase_credentials_path}")
    print(f"  Server: {server_host}:{server_port}")
    print(f"  OTP Expiry: {otp_expiry_minutes} minutes")
    print(f"  OTP Length: {otp_length} digits")
    print(f"  2FA Enabled by Default: {two_factor_enabled_by_default}")
    print(f"  Debug Mode: {debug_mode}")
    print(f"  Print OTP to Console: {print_otp_to_console}")
    print("="*70 + "\n")

if __name__ == '__main__':
    print_config()
    
    # Validation checks
    print("Configuration Validation:")
    
    # Check email configuration
    if not from_email or from_email == 'your-email@gmail.com':
        print("  ⚠️  WARNING: Email address not configured!")
    else:
        print(f"  ✓ Email configured: {from_email}")
    
    # Check Gmail App Password
    if not app_password or len(app_password) < 10:
        print("  ⚠️  WARNING: Gmail App Password not configured!")
    else:
        print("  ✓ Gmail App Password configured")
    
    # Check Firebase API Key (optional for local mode)
    if firebase_api_key == 'YOUR_FIREBASE_API_KEY':
        print("  ℹ️  INFO: Firebase API Key not set (using local mode)")
    else:
        print("  ✓ Firebase API Key configured")
    
    # Check Firebase credentials file (optional for local mode)
    if os.path.exists(firebase_credentials_path):
        print(f"  ✓ Firebase credentials file found: {firebase_credentials_path}")
    else:
        print(f"  ℹ️  INFO: Firebase credentials not found (using local mode)")
    
    print("\n" + "="*70)
    print("  MODE SELECTION")
    print("="*70)
    print("  The system will automatically choose:")
    print("  - FIREBASE MODE: If firebase-admin installed & credentials exist")
    print("  - LOCAL MODE: Otherwise (uses JSON files)")
    print("="*70)
    
    print("\n" + "="*70)
    print("  SETUP INSTRUCTIONS")
    print("="*70)
    print("\n  Gmail Configuration (REQUIRED):")
    print("     1. Enable 2-Step Verification in Google Account")
    print("     2. Generate App Password")
    print("     3. Update 'app_password' in this file")
    
    print("\n  Firebase Setup (OPTIONAL - for cloud mode):")
    print("     1. Create project at console.firebase.google.com")
    print("     2. Enable Email/Password authentication")
    print("     3. Create Firestore database")
    print("     4. Download service account key (firebase-credentials.json)")
    print("     5. Get Web API Key and set FIREBASE_API_KEY env variable")
    
    print("\n  Local Mode (NO FIREBASE NEEDED):")
    print("     1. Just run: python cloud.py")
    print("     2. Data stored in: local_users.json & local_otps.json")
    
    print("\n" + "="*70 + "\n")