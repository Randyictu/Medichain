import sys
import grpc
import cloudsecurity_pb2
import cloudsecurity_pb2_grpc
import getpass

class CloudSecurityClient:
    def __init__(self, host='localhost', port=51234):
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = cloudsecurity_pb2_grpc.UserServiceStub(self.channel)
        self.current_user = None
    
    def signup(self):
        """Handle user signup"""
        print("\n" + "="*60)
        print("  USER SIGNUP")
        print("="*60)
        
        username = input("Enter username: ").strip()
        email = input("Enter email: ").strip()
        password = getpass.getpass("Enter password: ")
        confirm_password = getpass.getpass("Confirm password: ")
        
        if password != confirm_password:
            print("\n[ERROR] Passwords do not match!")
            return
        
        phone = input("Enter phone (optional): ").strip()
        
        try:
            print("\n[INFO] Creating account...")
            request = cloudsecurity_pb2.SignupRequest(
                login=username,
                email=email,
                password=password,
                phone=phone
            )
            
            response = self.stub.signup(request)
            print(f"\n[RESULT] {response.result}")
            
            if "Success" in response.result:
                print("\n[INFO] You can now login with your credentials")
                
        except grpc.RpcError as e:
            print(f"\n[ERROR] RPC failed: {e.code()} - {e.details()}")
        except Exception as e:
            print(f"\n[ERROR] {str(e)}")
    
    def login(self):
        """Handle user login"""
        print("\n" + "="*60)
        print("  USER LOGIN")
        print("="*60)
        
        login = input("Enter username or email: ").strip()
        password = getpass.getpass("Enter password: ")
        
        try:
            print("\n[INFO] Authenticating...")
            request = cloudsecurity_pb2.LoginRequest(
                login=login,
                password=password
            )
            
            response = self.stub.login(request)
            print(f"\n[RESULT] {response.result}")
            
            if "OTP sent" in response.result:
                print("\n[INFO] Please check your email for the OTP code")
                print("[INFO] Use 'verify_otp' command to complete login")
                
        except grpc.RpcError as e:
            print(f"\n[ERROR] RPC failed: {e.code()} - {e.details()}")
        except Exception as e:
            print(f"\n[ERROR] {str(e)}")
    
    def verify_otp(self):
        """Handle OTP verification"""
        print("\n" + "="*60)
        print("  OTP VERIFICATION")
        print("="*60)
        
        email = input("Enter your email: ").strip()
        otp = input("Enter the 6-digit OTP: ").strip()
        
        try:
            print("\n[INFO] Verifying OTP...")
            request = cloudsecurity_pb2.OTPRequest(
                email=email,
                otp=otp
            )
            
            response = self.stub.verify_otp(request)
            print(f"\n[RESULT] {response.result}")
            
            if "Success" in response.result:
                self.current_user = email
                print(f"\n[SUCCESS] You are now logged in as {email}")
                
        except grpc.RpcError as e:
            print(f"\n[ERROR] RPC failed: {e.code()} - {e.details()}")
        except Exception as e:
            print(f"\n[ERROR] {str(e)}")
    
    def reset_password(self):
        """Handle password reset"""
        print("\n" + "="*60)
        print("  PASSWORD RESET")
        print("="*60)
        
        email = input("Enter your email: ").strip()
        
        try:
            print("\n[INFO] Requesting password reset...")
            request = cloudsecurity_pb2.EmailRequest(email=email)
            
            response = self.stub.reset_password(request)
            print(f"\n[RESULT] {response.result}")
            
        except grpc.RpcError as e:
            print(f"\n[ERROR] RPC failed: {e.code()} - {e.details()}")
        except Exception as e:
            print(f"\n[ERROR] {str(e)}")
    
    def get_profile(self):
        """Get user profile"""
        print("\n" + "="*60)
        print("  USER PROFILE")
        print("="*60)
        
        uid = input("Enter user UID: ").strip()
        
        try:
            print("\n[INFO] Fetching profile...")
            request = cloudsecurity_pb2.UIDRequest(uid=uid)
            
            response = self.stub.get_user_profile(request)
            print(f"\n[RESULT] {response.result}")
            
        except grpc.RpcError as e:
            print(f"\n[ERROR] RPC failed: {e.code()} - {e.details()}")
        except Exception as e:
            print(f"\n[ERROR] {str(e)}")
    
    def update_profile(self):
        """Update user profile"""
        print("\n" + "="*60)
        print("  UPDATE PROFILE")
        print("="*60)
        
        uid = input("Enter your UID: ").strip()
        
        print("\nLeave fields empty to keep current values:")
        username = input("New username: ").strip()
        email = input("New email: ").strip()
        phone = input("New phone: ").strip()
        
        try:
            print("\n[INFO] Updating profile...")
            request = cloudsecurity_pb2.UpdateProfileRequest(
                uid=uid,
                login=username,
                email=email,
                phone=phone
            )
            
            response = self.stub.update_user_profile(request)
            print(f"\n[RESULT] {response.result}")
            
        except grpc.RpcError as e:
            print(f"\n[ERROR] RPC failed: {e.code()} - {e.details()}")
        except Exception as e:
            print(f"\n[ERROR] {str(e)}")
    
    def show_menu(self):
        """Display main menu"""
        print("\n" + "="*60)
        print("  CLOUD SECURITY CLIENT")
        print("="*60)
        print("  1. Signup")
        print("  2. Login")
        print("  3. Verify OTP")
        print("  4. Reset Password")
        print("  5. Get User Profile")
        print("  6. Update Profile")
        print("  7. Exit")
        print("="*60)
    
    def run_interactive(self):
        """Run interactive client"""
        print("\n" + "="*60)
        print("  WELCOME TO CLOUD SECURITY PLATFORM")
        print("="*60)
        
        while True:
            self.show_menu()
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == '1':
                self.signup()
            elif choice == '2':
                self.login()
            elif choice == '3':
                self.verify_otp()
            elif choice == '4':
                self.reset_password()
            elif choice == '5':
                self.get_profile()
            elif choice == '6':
                self.update_profile()
            elif choice == '7':
                print("\n[INFO] Exiting... Goodbye!")
                break
            else:
                print("\n[ERROR] Invalid choice! Please try again.")
            
            input("\nPress Enter to continue...")
    
    def close(self):
        """Close the gRPC channel"""
        self.channel.close()

def run_command_line(args):
    """Run client with command line arguments"""
    client = CloudSecurityClient()
    
    try:
        request_type = args[0].lower()
        
        if request_type == "signup":
            if len(args) < 4:
                print("Usage: python client.py signup <username> <email> <password> [phone]")
                return
            
            request = cloudsecurity_pb2.SignupRequest(
                login=args[1],
                email=args[2],
                password=args[3],
                phone=args[4] if len(args) > 4 else ""
            )
            response = client.stub.signup(request)
            print(f"Result: {response.result}")
            
        elif request_type == "login":
            if len(args) < 3:
                print("Usage: python client.py login <username/email> <password>")
                return
            
            request = cloudsecurity_pb2.LoginRequest(
                login=args[1],
                password=args[2]
            )
            response = client.stub.login(request)
            print(f"Result: {response.result}")
            
        elif request_type == "verify_otp":
            if len(args) < 3:
                print("Usage: python client.py verify_otp <email> <otp>")
                return
            
            request = cloudsecurity_pb2.OTPRequest(
                email=args[1],
                otp=args[2]
            )
            response = client.stub.verify_otp(request)
            print(f"Result: {response.result}")
            
        elif request_type == "reset_password":
            if len(args) < 2:
                print("Usage: python client.py reset_password <email>")
                return
            
            request = cloudsecurity_pb2.EmailRequest(email=args[1])
            response = client.stub.reset_password(request)
            print(f"Result: {response.result}")
            
        elif request_type == "get_profile":
            if len(args) < 2:
                print("Usage: python client.py get_profile <uid>")
                return
            
            request = cloudsecurity_pb2.UIDRequest(uid=args[1])
            response = client.stub.get_user_profile(request)
            print(f"Result: {response.result}")
            
        elif request_type == "update_profile":
            if len(args) < 5:
                print("Usage: python client.py update_profile <uid> <username> <email> <phone>")
                return
            
            request = cloudsecurity_pb2.UpdateProfileRequest(
                uid=args[1],
                login=args[2],
                email=args[3],
                phone=args[4]
            )
            response = client.stub.update_user_profile(request)
            print(f"Result: {response.result}")
            
        else:
            print(f"Unknown request type: {request_type}")
            print("\nAvailable commands:")
            print("  signup <username> <email> <password> [phone]")
            print("  login <username/email> <password>")
            print("  verify_otp <email> <otp>")
            print("  reset_password <email>")
            print("  get_profile <uid>")
            print("  update_profile <uid> <username> <email> <phone>")
            
    except grpc.RpcError as e:
        print(f"RPC Error: {e.code()} - {e.details()}")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client.close()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Command line mode
        run_command_line(sys.argv[1:])
    else:
        # Interactive mode
        client = CloudSecurityClient()
        try:
            client.run_interactive()
        except KeyboardInterrupt:
            print("\n\n[INFO] Interrupted by user")
        finally:
            client.close()