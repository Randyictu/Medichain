"""
Configuration file for Cloud Security System
"""

import os

# Email Configuration for OTP delivery
from_email = "sasbergson@gmail.com"
app_password = "tgnwazxwlfjrjsuz"  # Gmail App Password (16-characters)

# Firebase Configuration (optional)
firebase_api_key = os.getenv('FIREBASE_API_KEY', 'YOUR_FIREBASE_API_KEY')

# Firebase Credentials File Path
firebase_credentials_path = 'firebase-credentials.json'

# Server Configuration
server_host = 'localhost'
server_port = 51234

# OTP Configuration
otp_expiry_minutes = 5
otp_length = 6

# Security Settings
min_password_length = 8
require_special_char = True
require_uppercase = True
require_lowercase = True
require_digit = True

# Two-Factor Authentication
two_factor_enabled_by_default = True

# Admin Dashboard Configuration
admin_email = "admin@cloudsync.com"
admin_password = "AdminSecure123!"
admin_username = "admin"

# Storage Configuration
TOTAL_STORAGE = 60 * 1024 * 1024 * 1024  # 60GB
NODE_COUNT = 6
NODE_STORAGE = 10 * 1024 * 1024 * 1024  # 10GB per node
REPLICATION_FACTOR = "ALL_NODES"  # Replicate across ALL active nodes

# Development/Debug Settings
debug_mode = False
print_otp_to_console = True  # For debugging - also prints to console

# SMTP Configuration
smtp_server = 'smtp.gmail.com'
smtp_port = 587
smtp_use_tls = True

# Bandwidth configurations for nodes (Mbps)
NODE_BANDWIDTHS = ["100 Mbps", "150 Mbps", "200 Mbps", "200 Mbps", "250 Mbps", "300 Mbps"]

def print_config():
    """Print current configuration"""
    print("\n" + "="*70)
    print("  CONFIGURATION SUMMARY")
    print("="*70)
    print(f"  Email From: {from_email}")
    print(f"  Admin Email: {admin_email}")
    print(f"  Total Storage: {TOTAL_STORAGE / (1024**3):.0f} GB")
    print(f"  Nodes: {NODE_COUNT} x {NODE_STORAGE / (1024**3):.0f} GB")
    print(f"  Replication: Across ALL active nodes")
    print(f"  OTP Delivery: Via Email")
    print(f"  Server: {server_host}:{server_port}")
    print("="*70 + "\n")

if __name__ == '__main__':
    print_config()