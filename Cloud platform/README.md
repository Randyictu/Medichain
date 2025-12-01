# Cloud Security System with Firebase & OTP Authentication

A complete gRPC-based cloud security system with dual-mode support (Firebase Cloud or Local JSON), featuring two-factor authentication via email OTP.

## 📋 Table of Contents

- [Features](#features)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Guide](#usage-guide)
- [Firebase Setup](#firebase-setup)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)
- [File Structure](#file-structure)

---

## ✨ Features

### Core Features
- ✅ **User Registration (Signup)** - Create accounts with email and password
- ✅ **User Authentication (Login)** - Secure login with username or email
- ✅ **Two-Factor Authentication** - OTP verification via email
- ✅ **Password Reset** - Email-based password recovery
- ✅ **User Profile Management** - View and update user information
- ✅ **Hybrid Database Support** - Works with or without Firebase

### Security Features
- 🔐 **Bcrypt Password Hashing** - Industry-standard password encryption
- 🔑 **OTP Generation** - 6-digit one-time passwords
- ⏱️ **OTP Expiration** - 5-minute validity window
- 🔒 **SHA-256 OTP Hashing** - Secure OTP storage
- 🚫 **One-time Use** - OTPs cannot be reused
- ✉️ **Email Verification** - SMTP-based email delivery

### Architecture Features
- 🔄 **Dual Mode Operation** - Firebase Cloud or Local JSON
- 🚀 **gRPC Protocol** - High-performance RPC framework
- 📦 **Protocol Buffers** - Efficient data serialization
- 🌐 **Client-Server Architecture** - Scalable design
- 📊 **Real-time Data Sync** - When using Firebase mode

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     CLIENT APPLICATION                  │
│  (client.py - Interactive & Command Line Interface)     │
└───────────────────────┬─────────────────────────────────┘
                        │ gRPC
                        ▼
┌─────────────────────────────────────────────────────────┐
│                   SERVER APPLICATION                    │
│            (cloud.py - gRPC Server)                     │
└───────────────────────┬─────────────────────────────────┘
                        │
          ┌─────────────┴─────────────┐
          ▼                           ▼
┌──────────────────┐        ┌──────────────────┐
│  FIREBASE MODE   │        │   LOCAL MODE     │
│  - Firebase Auth │        │  - JSON Files    │
│  - Firestore DB  │        │  - Bcrypt Hash   │
└──────────────────┘        └──────────────────┘
          │                           │
          └─────────────┬─────────────┘
                        ▼
              ┌──────────────────┐
              │  EMAIL (SMTP)    │
              │  OTP Delivery    │
              └──────────────────┘
```

---

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- Gmail account (for OTP emails)
- Firebase account (optional, only for cloud mode)

### Basic Installation (Local Mode)

```bash
# Install required packages
pip install grpcio grpcio-tools bcrypt

# Generate Protocol Buffer files
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. cloudsecurity.proto
```

### Full Installation (Firebase Mode)

```bash
# Install all packages including Firebase
pip install grpcio grpcio-tools bcrypt firebase-admin requests

# Generate Protocol Buffer files
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. cloudsecurity.proto
```

---

## ⚡ Quick Start

### Local Mode (No Firebase Required)

**Terminal 1 - Start Server:**
```bash
python cloud.py
```

**Terminal 2 - Run Client:**
```bash
python client.py
```

**Expected Output (Server):**
```
[INFO] Firebase SDK not available - using local database
[INFO] Using local database
[INFO] Database mode: LOCAL

======================================================================
  CLOUD SECURITY SERVER
======================================================================
  Starting Server on port 51234 ............[OK]
  Server Status: Running
======================================================================
```

**Data Storage:** 
- `local_users.json` - User accounts
- `local_otps.json` - OTP codes

---

## 📖 Usage Guide

### Interactive Mode (Recommended)

```bash
python client.py
```

**Menu Options:**
```
======================================================================
  CLOUD SECURITY CLIENT
======================================================================
  1. Signup          - Create new account
  2. Login           - Authenticate user (sends OTP)
  3. Verify OTP      - Complete login with OTP code
  4. Reset Password  - Request password reset
  5. Get Profile     - View user information
  6. Update Profile  - Modify user data
  7. Exit            - Close application
======================================================================
```

### Command Line Mode

#### 1. Create Account (Signup)
```bash
python client.py signup john john@example.com SecurePass123! +1234567890
```

**Response:**
```
Result: Success: Account created! UID: local_1
```

#### 2. Login (Sends OTP)
```bash
python client.py login john@example.com SecurePass123!
```

**Response:**
```
Result: OTP sent to john@example.com. Please verify.
```

**Check your email for the OTP!** 📧

#### 3. Verify OTP
```bash
python client.py verify_otp john@example.com 123456
```

**Response:**
```
Result: Success: Login complete! Token: local_token_local_1
```

#### 4. Get User Profile
```bash
python client.py get_profile local_1
```

**Response:**
```
Result: Success: {"uid":"local_1","email":"john@example.com","username":"john"...}
```

#### 5. Update Profile
```bash
python client.py update_profile local_1 john_updated new@email.com +9876543210
```

**Response:**
```
Result: Success: Profile updated
```

#### 6. Reset Password
```bash
python client.py reset_password john@example.com
```

**Response:**
```
Result: Success: Password reset link sent to john@example.com
```

---

## 🔥 Firebase Setup

### Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **"Add project"**
3. Project name: `cloud-security-app`
4. Disable Google Analytics (optional)
5. Click **"Create project"**

### Step 2: Enable Authentication

1. Click **"Authentication"** → **"Get started"**
2. Go to **"Sign-in method"** tab
3. Enable **"Email/Password"**
4. Click **"Save"**

### Step 3: Create Firestore Database

1. Click **"Firestore Database"** → **"Create database"**
2. Select **"Start in test mode"**
3. Choose location (e.g., `us-central`)
4. Click **"Enable"**

### Step 4: Get Service Account Key

1. Click ⚙️ **Settings** → **"Project settings"**
2. Go to **"Service accounts"** tab
3. Click **"Generate new private key"**
4. Save as `firebase-credentials.json` in project folder

### Step 5: Get Web API Key

1. In **"Project settings"** → **"General"** tab
2. Find **"Web API Key"** (looks like `AIzaSy...`)
3. Set environment variable:

**Windows (CMD):**
```bash
set FIREBASE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXX
```

**Windows (PowerShell):**
```powershell
$env:FIREBASE_API_KEY="AIzaSyXXXXXXXXXXXXXXXXXXXX"
```

**Linux/Mac:**
```bash
export FIREBASE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXX
```

**Or update `params.py`:**
```python
firebase_api_key = "AIzaSyXXXXXXXXXXXXXXXXXXXX"
```

### Step 6: Install Firebase Packages

```bash
pip install firebase-admin requests
```

### Step 7: Verify Setup

```bash
python params.py
```

**Expected Output:**
```
======================================================================
  CONFIGURATION SUMMARY
======================================================================
  Email From: your-email@gmail.com
  Firebase API Key: SET
  Firebase Credentials: firebase-credentials.json
  Server: localhost:51234
======================================================================

Configuration Validation:
  ✓ Email configured
  ✓ Gmail App Password configured
  ✓ Firebase API Key configured
  ✓ Firebase credentials file found
```

### Step 8: Run in Firebase Mode

```bash
python cloud.py
```

**Expected Output:**
```
[INFO] Firebase SDK available
[SUCCESS] Firebase initialized
[INFO] Database mode: FIREBASE

======================================================================
  CLOUD SECURITY SERVER
======================================================================
  Starting Server on port 51234 ............[OK]
  Server Status: Running
======================================================================
```

---

## 📡 API Reference

### gRPC Services

#### 1. signup (SignupRequest) → Response

Creates a new user account.

**Request:**
```protobuf
message SignupRequest {
  string login = 1;      // username
  string email = 2;      // email address
  string password = 3;   // password (min 8 chars)
  string phone = 4;      // optional phone number
}
```

**Example:**
```bash
python client.py signup alice alice@example.com MyPass123! +1234567890
```

**Response:**
```
Success: Account created! UID: local_1
```

---

#### 2. login (LoginRequest) → Response

Authenticates user and sends OTP to email.

**Request:**
```protobuf
message LoginRequest {
  string login = 1;      // username or email
  string password = 2;   // password
}
```

**Example:**
```bash
python client.py login alice@example.com MyPass123!
```

**Response:**
```
OTP sent to alice@example.com. Please verify.
```

---

#### 3. verify_otp (OTPRequest) → Response

Verifies the OTP code and completes login.

**Request:**
```protobuf
message OTPRequest {
  string email = 1;      // user email
  string otp = 2;        // 6-digit OTP code
}
```

**Example:**
```bash
python client.py verify_otp alice@example.com 123456
```

**Response:**
```
Success: Login complete! Token: local_token_local_1
```

---

#### 4. reset_password (EmailRequest) → Response

Sends password reset link to email.

**Request:**
```protobuf
message EmailRequest {
  string email = 1;
}
```

**Example:**
```bash
python client.py reset_password alice@example.com
```

**Response:**
```
Success: Password reset link sent to alice@example.com
```

---

#### 5. get_user_profile (UIDRequest) → Response

Retrieves user profile information.

**Request:**
```protobuf
message UIDRequest {
  string uid = 1;
}
```

**Example:**
```bash
python client.py get_profile local_1
```

**Response:**
```json
{
  "uid": "local_1",
  "email": "alice@example.com",
  "username": "alice",
  "phone": "+1234567890",
  "email_verified": false
}
```

---

#### 6. update_user_profile (UpdateProfileRequest) → Response

Updates user profile information.

**Request:**
```protobuf
message UpdateProfileRequest {
  string uid = 1;        // user ID
  string login = 2;      // new username (optional)
  string email = 3;      // new email (optional)
  string phone = 4;      // new phone (optional)
}
```

**Example:**
```bash
python client.py update_profile local_1 alice_new new@email.com +9876543210
```

**Response:**
```
Success: Profile updated
```

---

## 🔍 Data Storage

### Local Mode

**local_users.json:**
```json
{
  "local_1": {
    "uid": "local_1",
    "username": "alice",
    "email": "alice@example.com",
    "password_hash": "$2b$12$...",
    "phone": "+1234567890",
    "created_at": "2024-11-29T10:30:00",
    "email_verified": false,
    "two_factor_enabled": true
  }
}
```

**local_otps.json:**
```json
{
  "alice@example.com": {
    "otp_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "created_at": "2024-11-29T10:35:00",
    "expires_at": "2024-11-29T10:40:00",
    "used": false
  }
}
```

### Firebase Mode

**Firestore Collections:**

**users/** collection:
```javascript
{
  uid: "xYz123AbC",
  username: "alice",
  email: "alice@example.com",
  phone: "+1234567890",
  created_at: Timestamp,
  two_factor_enabled: true
}
```

**otps/** collection:
```javascript
{
  email: "alice@example.com",
  otp_hash: "e3b0c44...",
  created_at: Timestamp,
  expires_at: Timestamp,
  used: false
}
```

---

## 🐛 Troubleshooting

### Issue 1: "Couldn't parse file content!"

**Error:**
```
TypeError: Couldn't parse file content!
```

**Solution:**
```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. cloudsecurity.proto
```

---

### Issue 2: "Connection refused"

**Error:**
```
[ERROR] RPC failed: UNAVAILABLE - failed to connect to all addresses
```

**Solution:**
- Make sure `cloud.py` is running
- Check port 51234 is not in use
- Verify firewall settings

---

### Issue 3: "OTP not received in email"

**Problem:** Email doesn't arrive

**Solutions:**
1. **Check server terminal** - OTP is printed there for debugging:
   ```
   [DEBUG] Generated OTP: 123456
   ```

2. **Verify email configuration** in `params.py`:
   ```python
   from_email = "your-email@gmail.com"
   app_password = "your-app-password"  # Not regular password!
   ```

3. **Get Gmail App Password:**
   - Go to Google Account Settings
   - Security → 2-Step Verification (enable it)
   - App Passwords → Generate
   - Use the 16-character password

---

### Issue 4: "Invalid credentials"

**Error:**
```
Result: Unauthorized: Invalid credentials
```

**Solutions:**
- Check email/password are correct
- Verify account exists (try signup first)
- For Firebase mode: Check Firebase API key

---

### Issue 5: "OTP expired"

**Error:**
```
Result: Error: Invalid or expired OTP
```

**Solution:**
- OTPs expire after 5 minutes
- Request new login to get fresh OTP
- Check system time is correct

---

### Issue 6: "Firebase already initialized"

**Error:**
```
ValueError: The default Firebase app already exists
```

**Solution:**
- Restart the server (`Ctrl+C` then run again)
- Firebase can only be initialized once per process

---

### Issue 7: "Module not found"

**Error:**
```
ModuleNotFoundError: No module named 'firebase_admin'
```

**Solution:**
```bash
pip install firebase-admin requests
```

---

## 📁 File Structure

```
project/
├── client.py                    # Client application
├── cloud.py                     # Server application
├── utils.py                     # Utility functions
├── params.py                    # Configuration
├── cloudsecurity.proto          # Protocol definition
├── cloudsecurity_pb2.py        # Generated protobuf (auto)
├── cloudsecurity_pb2_grpc.py   # Generated gRPC (auto)
├── firebase-credentials.json    # Firebase key (optional)
├── local_users.json            # Local mode user DB (auto-created)
├── local_otps.json             # Local mode OTP storage (auto-created)
└── README.md                    # This file
```

---

## ⚙️ Configuration

### Email Configuration (params.py)

```python
# Gmail SMTP Settings
from_email = "your-email@gmail.com"
app_password = "xxxx xxxx xxxx xxxx"  # Gmail App Password

# SMTP Server
smtp_server = "smtp.gmail.com"
smtp_port = 587
```

### Firebase Configuration (params.py)

```python
# Firebase API Key (from Firebase Console)
firebase_api_key = "AIzaSyXXXXXXXXXXXXXXXXXXXX"

# Firebase Credentials File
firebase_credentials_path = "firebase-credentials.json"
```

### Server Configuration (params.py)

```python
# Server Settings
server_host = "localhost"
server_port = 51234

# OTP Settings
otp_expiry_minutes = 5
otp_length = 6

# Security Settings
min_password_length = 8
two_factor_enabled_by_default = True
```

---

## 🔄 Switching Modes

### Use Local Mode

```bash
# Remove or rename Firebase credentials
mv firebase-credentials.json firebase-credentials.json.backup

# Run server
python cloud.py
# Output: [INFO] Database mode: LOCAL
```

### Use Firebase Mode

```bash
# Ensure firebase-credentials.json exists
# Run server
python cloud.py
# Output: [INFO] Database mode: FIREBASE
```

---

## 📊 Feature Comparison

| Feature | Local Mode | Firebase Mode |
|---------|-----------|---------------|
| **Setup Time** | 2 minutes | 15 minutes |
| **Internet Required** | Only for email | Yes |
| **Data Storage** | JSON files | Firestore Cloud |
| **Authentication** | Bcrypt | Firebase Auth |
| **Scalability** | Single machine | Cloud scale |
| **Cost** | Free | Free tier available |
| **Backup** | Manual | Automatic |
| **Multi-device** | No | Yes |
| **View Data** | Text editor | Firebase Console |

---

## 🔐 Security Best Practices

### Development

- ✅ OTP printed to console for debugging
- ✅ Test mode Firestore rules
- ✅ Local file storage acceptable

### Production

1. **Use Environment Variables:**
   ```bash
   export FIREBASE_API_KEY="your-key"
   export GMAIL_APP_PASSWORD="your-password"
   ```

2. **Update Firestore Rules:**
   ```javascript
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       match /users/{userId} {
         allow read, write: if request.auth.uid == userId;
       }
     }
   }
   ```

3. **Enable SSL/TLS:**
   ```python
   credentials = grpc.ssl_channel_credentials()
   channel = grpc.secure_channel('server:port', credentials)
   ```

4. **Add Rate Limiting**
5. **Implement CAPTCHA**
6. **Enable logging and monitoring**

---

## 🧪 Testing

### Test Workflow

```bash
# 1. Start server
python cloud.py

# 2. Create account
python client.py signup testuser test@example.com TestPass123!

# 3. Login (sends OTP)
python client.py login test@example.com TestPass123!

# 4. Check email for OTP (or check server terminal)

# 5. Verify OTP
python client.py verify_otp test@example.com 123456

# 6. Get profile
python client.py get_profile local_1

# 7. Update profile
python client.py update_profile local_1 newuser new@email.com +9999999999
```

---

## 📚 Additional Resources

- [gRPC Documentation](https://grpc.io/docs/)
- [Protocol Buffers Guide](https://developers.google.com/protocol-buffers)
- [Firebase Documentation](https://firebase.google.com/docs)
- [Bcrypt Guide](https://pypi.org/project/bcrypt/)

---

## 📝 License

This project is for educational purposes.

---

## 👥 Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review the [Usage Guide](#usage-guide)
3. Verify all [configuration](#configuration) settings

---

## 🎯 Quick Commands Reference

```bash
# Setup
pip install grpcio grpcio-tools bcrypt
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. cloudsecurity.proto

# Run
python cloud.py              # Terminal 1 - Server
python client.py             # Terminal 2 - Client

# Command Line Usage
python client.py signup <user> <email> <pass> [phone]
python client.py login <email> <password>
python client.py verify_otp <email> <otp>
python client.py reset_password <email>
python client.py get_profile <uid>
python client.py update_profile <uid> <user> <email> <phone>

# Check Configuration
python params.py

# Firebase Setup (Optional)
pip install firebase-admin requests
# Place firebase-credentials.json in project folder
export FIREBASE_API_KEY="your-key"
```

---

**Built with ❤️ using gRPC, Protocol Buffers, and Firebase**

**Ready to secure your cloud! 🚀🔐**
