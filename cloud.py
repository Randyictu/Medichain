import grpc
from concurrent import futures
import cloudsecurity_pb2
import cloudsecurity_pb2_grpc
from utils import send_otp, verify_otp_code, hash_password, check_password
import os
import json
from datetime import datetime

# Try to import Firebase (optional)
FIREBASE_AVAILABLE = False
try:
    import firebase_admin
    from firebase_admin import credentials, auth, firestore
    FIREBASE_AVAILABLE = True
    print("[INFO] Firebase SDK available")
except ImportError:
    print("[INFO] Firebase SDK not available - using local database")

class LocalDatabase:
    """Local file-based database fallback when Firebase is not available"""
    
    def __init__(self):
        self.users_file = 'local_users.json'
        self.otps_file = 'local_otps.json'
        self._init_files()
    
    def _init_files(self):
        """Initialize local database files"""
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump({}, f)
        if not os.path.exists(self.otps_file):
            with open(self.otps_file, 'w') as f:
                json.dump({}, f)
    
    def _read_users(self):
        """Read users from file"""
        with open(self.users_file, 'r') as f:
            return json.load(f)
    
    def _write_users(self, users):
        """Write users to file"""
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)
    
    def _read_otps(self):
        """Read OTPs from file"""
        with open(self.otps_file, 'r') as f:
            return json.load(f)
    
    def _write_otps(self, otps):
        """Write OTPs to file"""
        with open(self.otps_file, 'w') as f:
            json.dump(otps, f, indent=2)
    
    def create_user(self, username, email, password, phone=''):
        """Create a new user"""
        users = self._read_users()
        
        # Check if user exists
        for uid, user in users.items():
            if user['email'] == email:
                raise Exception("Email already exists")
            if user['username'] == username:
                raise Exception("Username already taken")
        
        # Create new user
        uid = f"local_{len(users) + 1}"
        users[uid] = {
            'uid': uid,
            'username': username,
            'email': email,
            'password_hash': hash_password(password),
            'phone': phone,
            'created_at': datetime.now().isoformat(),
            'email_verified': False,
            'two_factor_enabled': True
        }
        
        self._write_users(users)
        return uid
    
    def get_user_by_email(self, email):
        """Get user by email"""
        users = self._read_users()
        for uid, user in users.items():
            if user['email'] == email:
                return user
        return None
    
    def get_user_by_username(self, username):
        """Get user by username"""
        users = self._read_users()
        for uid, user in users.items():
            if user['username'] == username:
                return user
        return None
    
    def get_user_by_uid(self, uid):
        """Get user by UID"""
        users = self._read_users()
        return users.get(uid)
    
    def verify_password(self, email, password):
        """Verify user password"""
        user = self.get_user_by_email(email)
        if not user:
            return None
        
        if check_password(password, user['password_hash']):
            return user
        return None
    
    def update_user(self, uid, **kwargs):
        """Update user data"""
        users = self._read_users()
        if uid not in users:
            raise Exception("User not found")
        
        for key, value in kwargs.items():
            if value and key != 'uid':
                users[uid][key] = value
        
        self._write_users(users)
        return True
    
    def store_otp(self, email, otp_hash, expires_at):
        """Store OTP"""
        otps = self._read_otps()
        otps[email] = {
            'otp_hash': otp_hash,
            'created_at': datetime.now().isoformat(),
            'expires_at': expires_at.isoformat(),
            'used': False
        }
        self._write_otps(otps)
    
    def get_otp(self, email):
        """Get OTP data"""
        otps = self._read_otps()
        return otps.get(email)
    
    def mark_otp_used(self, email):
        """Mark OTP as used"""
        otps = self._read_otps()
        if email in otps:
            otps[email]['used'] = True
            self._write_otps(otps)
    
    def delete_otp(self, email):
        """Delete OTP"""
        otps = self._read_otps()
        if email in otps:
            del otps[email]
            self._write_otps(otps)

def initialize_database():
    """Initialize Firebase or Local Database"""
    if FIREBASE_AVAILABLE:
        try:
            firebase_admin.get_app()
            print("[INFO] Firebase already initialized")
        except ValueError:
            if os.path.exists('firebase-credentials.json'):
                cred = credentials.Certificate('firebase-credentials.json')
                firebase_admin.initialize_app(cred)
                print("[SUCCESS] Firebase initialized")
                return 'firebase', firestore.client()
            else:
                print("[WARNING] firebase-credentials.json not found, using local database")
                return 'local', LocalDatabase()
    else:
        print("[INFO] Using local database")
        return 'local', LocalDatabase()

class UserServiceSkeleton(cloudsecurity_pb2_grpc.UserServiceServicer):
    def __init__(self):
        self.db_type, self.db = initialize_database()
        print(f"[INFO] Database mode: {self.db_type.upper()}")
        
        if self.db_type == 'firebase':
            self.users_ref = self.db.collection('users')
            self.otps_ref = self.db.collection('otps')
    
    def signup(self, request, context) -> cloudsecurity_pb2.Response:
        """Register a new user"""
        print(f'\n[SIGNUP] New registration request')
        print(f'  Username: {request.login}')
        print(f'  Email: {request.email}')
        
        try:
            if self.db_type == 'firebase':
                return self._signup_firebase(request)
            else:
                return self._signup_local(request)
        except Exception as e:
            print(f'[ERROR] Signup failed: {e}')
            return cloudsecurity_pb2.Response(result=f"Error: {str(e)}")
    
    def _signup_firebase(self, request):
        """Signup using Firebase"""
        # Check username
        existing_user = self.users_ref.where('username', '==', request.login).limit(1).get()
        if len(list(existing_user)) > 0:
            return cloudsecurity_pb2.Response(result="Error: Username already taken")
        
        # Create user in Firebase Auth
        user = auth.create_user(
            email=request.email,
            password=request.password,
            display_name=request.login,
            email_verified=False
        )
        
        print(f'[SUCCESS] Firebase user created: {user.uid}')
        
        # Store in Firestore
        user_data = {
            'uid': user.uid,
            'username': request.login,
            'email': request.email,
            'phone': request.phone if hasattr(request, 'phone') else '',
            'created_at': firestore.SERVER_TIMESTAMP,
            'two_factor_enabled': True
        }
        
        self.users_ref.document(user.uid).set(user_data)
        
        return cloudsecurity_pb2.Response(
            result=f"Success: Account created! UID: {user.uid}"
        )
    
    def _signup_local(self, request):
        """Signup using local database"""
        uid = self.db.create_user(
            request.login,
            request.email,
            request.password,
            request.phone if hasattr(request, 'phone') else ''
        )
        
        print(f'[SUCCESS] Local user created: {uid}')
        
        return cloudsecurity_pb2.Response(
            result=f"Success: Account created! UID: {uid}"
        )
    
    def login(self, request, context) -> cloudsecurity_pb2.Response:
        """Authenticate user and send OTP"""
        print(f'\n[LOGIN] Authentication request')
        print(f'  Login: {request.login}')
        
        try:
            if self.db_type == 'firebase':
                return self._login_firebase(request)
            else:
                return self._login_local(request)
        except Exception as e:
            print(f'[ERROR] Login failed: {e}')
            return cloudsecurity_pb2.Response(result=f"Error: {str(e)}")
    
    def _login_firebase(self, request):
        """Login using Firebase"""
        user_email = request.login
        
        if '@' not in request.login:
            user_docs = self.users_ref.where('username', '==', request.login).limit(1).get()
            user_list = list(user_docs)
            
            if len(user_list) == 0:
                return cloudsecurity_pb2.Response(result="Unauthorized: User not found")
            
            user_data = user_list[0].to_dict()
            user_email = user_data['email']
        
        # Verify credentials
        result = self.verify_firebase_credentials(user_email, request.password)
        
        if result['success']:
            otp_result = send_otp(user_email, self.otps_ref if self.db_type == 'firebase' else None, self.db)
            
            if 'successfully' in otp_result:
                return cloudsecurity_pb2.Response(
                    result=f"OTP sent to {user_email}. Please verify."
                )
            else:
                return cloudsecurity_pb2.Response(result="Error: Failed to send OTP")
        else:
            return cloudsecurity_pb2.Response(result="Unauthorized: Invalid credentials")
    
    def _login_local(self, request):
        """Login using local database"""
        user_email = request.login
        
        # Check if login is username
        if '@' not in request.login:
            user = self.db.get_user_by_username(request.login)
            if not user:
                return cloudsecurity_pb2.Response(result="Unauthorized: User not found")
            user_email = user['email']
        
        # Verify password
        user = self.db.verify_password(user_email, request.password)
        
        if user:
            otp_result = send_otp(user_email, None, self.db)
            
            if 'successfully' in otp_result:
                return cloudsecurity_pb2.Response(
                    result=f"OTP sent to {user_email}. Please verify."
                )
            else:
                return cloudsecurity_pb2.Response(result="Error: Failed to send OTP")
        else:
            return cloudsecurity_pb2.Response(result="Unauthorized: Invalid credentials")
    
    def verify_firebase_credentials(self, email, password):
        """Verify credentials using Firebase REST API"""
        import requests
        from param import firebase_api_key
        
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={firebase_api_key}"
        
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        try:
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                return {'success': True, 'uid': data['localId'], 'token': data['idToken']}
            else:
                return {'success': False}
        except Exception as e:
            print(f'[ERROR] Credential verification failed: {e}')
            return {'success': False}
    
    def verify_otp(self, request, context) -> cloudsecurity_pb2.Response:
        """Verify OTP code"""
        print(f'\n[OTP VERIFICATION] Verifying OTP for {request.email}')
        
        try:
            result = verify_otp_code(
                request.email,
                request.otp,
                self.otps_ref if self.db_type == 'firebase' else None,
                self.db
            )
            
            if result:
                print(f'[SUCCESS] OTP verified for {request.email}')
                
                if self.db_type == 'firebase':
                    user = auth.get_user_by_email(request.email)
                    custom_token = auth.create_custom_token(user.uid)
                    token = custom_token.decode('utf-8')
                else:
                    user = self.db.get_user_by_email(request.email)
                    token = f"local_token_{user['uid']}"
                
                return cloudsecurity_pb2.Response(
                    result=f"Success: Login complete! Token: {token}"
                )
            else:
                return cloudsecurity_pb2.Response(result="Error: Invalid or expired OTP")
        except Exception as e:
            print(f'[ERROR] {e}')
            return cloudsecurity_pb2.Response(result=f"Error: {str(e)}")
    
    def reset_password(self, request, context) -> cloudsecurity_pb2.Response:
        """Send password reset email"""
        print(f'\n[PASSWORD RESET] Request for {request.email}')
        
        try:
            if self.db_type == 'firebase':
                link = auth.generate_password_reset_link(request.email)
                print(f'[SUCCESS] Reset link: {link}')
            else:
                print(f'[INFO] Local mode: Password reset link would be sent')
            
            return cloudsecurity_pb2.Response(
                result=f"Success: Password reset link sent to {request.email}"
            )
        except Exception as e:
            print(f'[ERROR] {e}')
            return cloudsecurity_pb2.Response(result=f"Error: {str(e)}")
    
    def get_user_profile(self, request, context) -> cloudsecurity_pb2.Response:
        """Get user profile"""
        print(f'\n[GET PROFILE] Request for UID: {request.uid}')
        
        try:
            if self.db_type == 'firebase':
                user = auth.get_user(request.uid)
                user_doc = self.users_ref.document(request.uid).get()
                
                if user_doc.exists:
                    user_data = user_doc.to_dict()
                    profile = {
                        'uid': user.uid,
                        'email': user.email,
                        'username': user_data.get('username', ''),
                        'phone': user_data.get('phone', ''),
                        'email_verified': user.email_verified
                    }
                else:
                    return cloudsecurity_pb2.Response(result="Error: Profile not found")
            else:
                user = self.db.get_user_by_uid(request.uid)
                if user:
                    profile = {
                        'uid': user['uid'],
                        'email': user['email'],
                        'username': user['username'],
                        'phone': user.get('phone', ''),
                        'email_verified': user.get('email_verified', False)
                    }
                else:
                    return cloudsecurity_pb2.Response(result="Error: User not found")
            
            import json
            return cloudsecurity_pb2.Response(result=f"Success: {json.dumps(profile)}")
        except Exception as e:
            print(f'[ERROR] {e}')
            return cloudsecurity_pb2.Response(result=f"Error: {str(e)}")
    
    def update_user_profile(self, request, context) -> cloudsecurity_pb2.Response:
        """Update user profile"""
        print(f'\n[UPDATE PROFILE] Request for UID: {request.uid}')
        
        try:
            if self.db_type == 'firebase':
                update_params = {}
                if request.email:
                    update_params['email'] = request.email
                if request.phone:
                    update_params['phone_number'] = request.phone
                
                if update_params:
                    auth.update_user(request.uid, **update_params)
                
                update_data = {}
                if request.login:
                    update_data['username'] = request.login
                if request.email:
                    update_data['email'] = request.email
                if request.phone:
                    update_data['phone'] = request.phone
                
                if update_data:
                    self.users_ref.document(request.uid).update(update_data)
            else:
                update_data = {}
                if request.login:
                    update_data['username'] = request.login
                if request.email:
                    update_data['email'] = request.email
                if request.phone:
                    update_data['phone'] = request.phone
                
                if update_data:
                    self.db.update_user(request.uid, **update_data)
            
            return cloudsecurity_pb2.Response(result="Success: Profile updated")
        except Exception as e:
            print(f'[ERROR] {e}')
            return cloudsecurity_pb2.Response(result=f"Error: {str(e)}")

def run():
    """Start the gRPC server"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    cloudsecurity_pb2_grpc.add_UserServiceServicer_to_server(
        UserServiceSkeleton(), server
    )
    server.add_insecure_port('[::]:51234')
    
    print('\n' + '='*70)
    print('  CLOUD SECURITY SERVER')
    print('='*70)
    print('  Starting Server on port 51234 ............', end='')
    server.start()
    print('[OK]')
    print('  Server Status: Running')
    print('='*70 + '\n')
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print('\n[INFO] Shutting down server...')
        server.stop(0)

if __name__ == '__main__':
    run()