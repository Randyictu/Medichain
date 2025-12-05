# CloudSync Pro

**Enterprise-grade distributed cloud storage platform with advanced authentication, real-time monitoring, and AI assistance.**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com)
[![gRPC](https://img.shields.io/badge/gRPC-1.x-orange.svg)](https://grpc.io)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🌟 Features

### Core Functionality
- **Distributed Storage**: Automatic file replication across 6 storage nodes
- **30GB Free Storage**: Standard users get 30GB, VIP users get 100GB
- **Two-Factor Authentication**: Email-based OTP for enhanced security
- **Real-time Monitoring**: Live node status, bandwidth, CPU, memory, and temperature tracking
- **AI Assistant**: Claude-powered helper for storage management and system queries
- **Admin Dashboard**: Comprehensive node management and system monitoring

### Storage Architecture
- **6-Node Cluster**: Distributed storage across multiple nodes (10GB each)
- **All-Node Replication**: Files replicated to ALL active nodes for maximum redundancy
- **Dynamic Node Management**: Add/remove nodes on the fly
- **Class A IP Allocation**: Automatic IP assignment (10.0.x.x)
- **Bandwidth Monitoring**: Real-time network performance tracking

### Security Features
- **Email-Only OTP**: Secure one-time passwords sent via email (not console)
- **Password Hashing**: bcrypt-based password security
- **gRPC Authentication**: Secure service communication
- **Session Management**: Token-based authentication
- **Admin Controls**: Separate admin authentication flow

### User Roles
- **Standard Users**: 30GB storage, full file management
- **VIP Users**: 100GB storage, priority features
- **Admin**: Full system control, node management, user administration

## 📋 Architecture

```
CloudSync Pro Architecture
┌─────────────────────────────────────────────────────────┐
│                    Web Interface                        │
│              (React + Tailwind CSS)                     │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Web API Server                         │
│              (Flask + CORS)                             │
│    • Authentication  • File Upload  • User Management   │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
┌───────▼───────┐ ┌──▼──────┐ ┌──▼────────────────┐
│  Cloud Server │ │ Threaded│ │   Storage Nodes   │
│    (gRPC)     │ │ Network │ │  (Node 1-6)       │
│  • Auth       │ │ Server  │ │  • 10GB each      │
│  • OTP        │ │         │ │  • Replication    │
│  • Firebase   │ │         │ │  • Mini OS        │
└───────────────┘ └─────────┘ └───────────────────┘
```

## 🚀 Quick Start

### Prerequisites

```bash
# Required packages
pip install flask flask-cors grpcio grpcio-tools
pip install firebase-admin bcrypt python-dotenv
```

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/cloudsync-pro.git
cd cloudsync-pro
```

2. **Configure email settings**
Edit `param.py`:
```python
from_email = "your_email@gmail.com"
app_password = "your_app_password"  # Gmail App Password
```

3. **Generate Protocol Buffers**
```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. cloudsecurity.proto
```

4. **Launch the platform**
```bash
python simple_start.py
```

The web interface will automatically open at `http://localhost:5000`

### Default Admin Credentials
```
Email: admin@cloudsync.com
Password: AdminSecure123!
```

## 📁 Project Structure

```
cloudsync-pro/
├── client.py              # gRPC client for authentication
├── cloud.py               # Cloud security server (gRPC)
├── web_api.py             # Web API server (Flask)
├── threaded.py            # Threaded network server
├── node.py                # Storage node mini-OS
├── index.html             # Web interface (React)
├── utils.py               # OTP and email utilities
├── param.py               # Configuration file
├── simple_start.py        # Quick launcher
├── main.py                # Full system launcher
├── cloudsecurity.proto    # Protocol buffer definitions
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🔧 Configuration

### Email Configuration (param.py)
```python
# Gmail SMTP settings
from_email = "your_email@gmail.com"
app_password = "xxxx xxxx xxxx xxxx"  # 16-char app password

smtp_server = 'smtp.gmail.com'
smtp_port = 587
smtp_use_tls = True
```

### Storage Configuration
```python
# Storage limits
TOTAL_STORAGE = 60 * 1024 * 1024 * 1024  # 60GB total
NODE_COUNT = 6                             # 6 nodes
NODE_STORAGE = 10 * 1024 * 1024 * 1024   # 10GB per node
REPLICATION_FACTOR = "ALL_NODES"          # Replicate to all
```

### Firebase (Optional)
Place `firebase-credentials.json` in the root directory to enable Firebase authentication.

## 💡 Usage

### User Workflow

1. **Sign Up**
   - Create account with username, email, password
   - Receive welcome email
   - No OTP required for signup

2. **Login**
   - Enter email and password
   - Receive 6-digit OTP via email
   - Enter OTP to complete login

3. **Upload Files**
   - Drag and drop or click to upload
   - Files automatically replicated to all 6 nodes
   - Real-time upload progress tracking

4. **Manage Files**
   - View all uploaded files
   - Download from any node
   - Delete files (removes from all nodes)

### Admin Workflow

1. **Admin Login**
   - Use admin credentials (no OTP required)
   - Access admin dashboard

2. **Node Management**
   - Monitor all 6 nodes in real-time
   - View CPU, memory, temperature, bandwidth
   - Add/remove nodes dynamically
   - Check storage capacity per node

3. **User Management**
   - View registered users
   - Upgrade users to VIP (100GB)
   - Monitor system statistics

### Storage Node Operations

Each node runs a mini operating system with commands:

```bash
# File operations
addfile <filename> <content>  # Create file locally
upload <filename>              # Upload to cloud
download <filename>            # Download from cloud
localfiles                     # List local files
cloudfiles                     # List cloud files

# Network operations
send <file> <ip>               # Send to another node
bandwidth                      # Show bandwidth info
network                        # Show network config

# System info
status                         # Node status
storage                        # Storage information
help                          # Show all commands
quit                          # Disconnect
```

## 🔐 Security Features

### Authentication Flow
1. **Signup**: Password + Email confirmation
2. **Login**: Password → Email OTP → Token
3. **Session**: JWT token-based sessions
4. **Admin**: Direct password authentication (no OTP)

### OTP System
- 6-digit random code
- SHA-256 hashing for storage
- 5-minute expiration
- Single-use only
- Email delivery only (not console)

### Password Requirements
- Minimum 8 characters
- Uppercase letter required
- Lowercase letter required
- Digit required
- Special character required

## 🌐 API Endpoints

### Authentication
```
POST /api/auth/signup          # Create new account
POST /api/auth/login           # Login (sends OTP)
POST /api/auth/verify-otp      # Verify OTP code
```

### User Management
```
GET  /api/profile              # Get user profile
POST /api/admin/upgrade-vip    # Upgrade to VIP (admin)
```

### Health Check
```
GET  /api/health               # API health status
```

## 🎨 Web Interface

### Technology Stack
- **Frontend**: React 18
- **Styling**: Tailwind CSS 3
- **Icons**: Lucide React
- **State Management**: React Hooks
- **API Communication**: Fetch API

### Key Components
- **Authentication Pages**: Login/Signup with OTP modal
- **Dashboard**: Stats cards, quick upload, recent files
- **Files View**: File management with search
- **Nodes View**: Real-time node monitoring
- **Admin Panel**: System management and controls
- **AI Chat**: Claude-powered assistance

## 🤖 AI Assistant

Powered by Claude (Anthropic), the AI assistant helps with:
- Storage management questions
- File operation guidance
- Node status interpretation
- System optimization tips
- Troubleshooting support

Access via the "AI Help" button in the header.

## 📊 System Requirements

### Minimum Requirements
- Python 3.8+
- 2GB RAM
- 100GB disk space
- Internet connection (for email)

### Recommended Requirements
- Python 3.10+
- 4GB RAM
- 200GB disk space
- Stable internet connection
- Gmail account for email

## 🐛 Troubleshooting

### Email OTP Not Sending
1. Check Gmail App Password in `param.py`
2. Enable "Less secure app access" (if needed)
3. Verify SMTP settings
4. Check console for error messages

### gRPC Connection Failed
```bash
# Regenerate protocol buffers
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. cloudsecurity.proto
```

### Port Already in Use
```bash
# Change ports in configuration
# Web API: port 5000 (web_api.py)
# gRPC: port 51234 (cloud.py)
# Network: port 9000 (threaded.py)
```

### Firebase Issues
- Ensure `firebase-credentials.json` is present
- Check Firebase project settings
- Verify API key in `param.py`
- System falls back to local database if Firebase unavailable

## 🔄 Update Process

### Adding New Nodes
```bash
# In admin panel or via command
python node.py 7  # Start node 7
```

### Upgrading to VIP
```python
# Via API or admin panel
POST /api/admin/upgrade-vip
{
  "admin_email": "admin@cloudsync.com",
  "admin_password": "AdminSecure123!",
  "target_email": "user@example.com"
}
```

## 📝 Development

### Running Tests
```bash
# Test OTP flow
python test_otp_flow.py

# Test individual components
python cloud.py      # Test gRPC server
python web_api.py    # Test web API
python node.py 1     # Test storage node
```

### Adding Features
1. Update protocol buffers if needed (`cloudsecurity.proto`)
2. Regenerate Python files
3. Update server logic (`cloud.py`, `web_api.py`)
4. Update web interface (`index.html`)
5. Test thoroughly

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Initial Development** - CloudSync Pro Team
- **Contributors** - See [CONTRIBUTORS.md](CONTRIBUTORS.md)

## 🙏 Acknowledgments

- gRPC for efficient service communication
- Flask for web API framework
- React for frontend framework
- Anthropic Claude for AI assistance
- Firebase for optional authentication backend
- Tailwind CSS for beautiful UI components

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/cloudsync-pro/issues)
- **Email**: support@cloudsync.com
- **Documentation**: [Wiki](https://github.com/yourusername/cloudsync-pro/wiki)

## 🗺️ Roadmap

- [ ] Mobile app (React Native)
- [ ] End-to-end encryption
- [ ] File versioning
- [ ] Shared folders
- [ ] WebDAV support
- [ ] S3-compatible API
- [ ] Docker containerization
- [ ] Kubernetes deployment
- [ ] Advanced analytics dashboard
- [ ] Multi-region support

---

**Made with ❤️ by the CloudSync Pro Team**
