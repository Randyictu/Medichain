import React, { useState, useEffect } from 'react';
import { Upload, Cloud, Server, Users, Settings, TrendingUp, HardDrive, Activity, AlertCircle, CheckCircle, Trash2, Plus, LogOut, File, Download, Search, Bot, Bell, Menu, X } from 'lucide-react';

const CloudStoragePlatform = () => {
  const [currentView, setCurrentView] = useState('login');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userRole, setUserRole] = useState('user');
  const [currentUser, setCurrentUser] = useState(null);
  
  // Auth states
  const [authForm, setAuthForm] = useState({ username: '', email: '', password: '', phone: '' });
  const [otpForm, setOtpForm] = useState({ email: '', otp: '' });
  const [showOtpModal, setShowOtpModal] = useState(false);
  
  // Storage states - 30GB per user
  const [userStorage, setUserStorage] = useState({ 
    used: 0, 
    total: 30 * 1024 * 1024 * 1024 
  });
  const [files, setFiles] = useState([]);
  const [uploadProgress, setUploadProgress] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Nodes - starts with 3 active nodes
  const [nodes, setNodes] = useState([
    { id: 1, name: 'Node 1', ip: '10.0.1.1', mac: '02:1a:2b:3c:4d:5e', status: 'active', storage: { used: 0, total: 10 * 1024 * 1024 * 1024 }, files: [], bandwidth: '100 Mbps' },
    { id: 2, name: 'Node 2', ip: '10.0.1.2', mac: '02:2a:3b:4c:5d:6e', status: 'active', storage: { used: 0, total: 10 * 1024 * 1024 * 1024 }, files: [], bandwidth: '100 Mbps' },
    { id: 3, name: 'Node 3', ip: '10.0.1.3', mac: '02:3a:4b:5c:6d:7e', status: 'active', storage: { used: 0, total: 10 * 1024 * 1024 * 1024 }, files: [], bandwidth: '100 Mbps' }
  ]);
  
  // AI Chat states
  const [showAiChat, setShowAiChat] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  
  // Notifications
  const [notifications, setNotifications] = useState([
    { id: 1, message: 'System started successfully', time: new Date().toISOString(), read: false }
  ]);

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // Authentication handlers
  const handleSignup = async () => {
    if (!authForm.username || !authForm.email || !authForm.password) {
      alert('Please fill all required fields');
      return;
    }
    
    // Simulate backend call to cloud.py signup endpoint
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    setNotifications(prev => [...prev, {
      id: Date.now(),
      message: `Signup successful for ${authForm.email}`,
      time: new Date().toISOString(),
      read: false
    }]);

    // Signup does not send OTP. Prompt user to login.
    alert('✅ Signup successful! You may now login.');
    setCurrentView('login');
  };

  const handleLogin = async () => {
    if (!authForm.email || !authForm.password) {
      alert('Please enter email and password');
      return;
    }
    
    // Simulate backend call to cloud.py login endpoint
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    alert('✅ Login successful! OTP sent to ' + authForm.email);
    setOtpForm({ ...otpForm, email: authForm.email });
    setShowOtpModal(true);
  };

  const handleVerifyOtp = async () => {
    if (otpForm.otp.length !== 6) {
      alert('Please enter a valid 6-digit OTP');
      return;
    }
    
    // Simulate backend call to cloud.py verify_otp endpoint
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const user = {
      username: authForm.username || authForm.email.split('@')[0],
      email: otpForm.email,
      role: otpForm.email.includes('admin') ? 'admin' : 'user',
      uid: 'local_' + Date.now()
    };
    
    setCurrentUser(user);
    setUserRole(user.role);
    setIsAuthenticated(true);
    setShowOtpModal(false);
    setCurrentView('dashboard');
    
    setNotifications(prev => [...prev, {
      id: Date.now(),
      message: `Welcome ${user.username}! Login successful`,
      time: new Date().toISOString(),
      read: false
    }]);
  };

  // File upload with replication across nodes
  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const fileSize = file.size;
    const availableSpace = userStorage.total - userStorage.used;

    if (fileSize > availableSpace) {
      alert('❌ Insufficient storage space!');
      return;
    }

    // Check if at least 3 nodes are available
    const activeNodes = nodes.filter(n => n.status === 'active');
    if (activeNodes.length < 3) {
      alert('⚠️ Need at least 3 active nodes for replication');
      return;
    }

    const newFile = {
      id: Date.now(),
      name: file.name,
      size: fileSize,
      uploadedAt: new Date().toISOString(),
      replicas: [],
      type: file.type || 'unknown'
    };

    // Start upload with progress tracking
    setUploadProgress({ 
      fileName: file.name, 
      progress: 0, 
      currentNode: null,
      totalNodes: 3,
      completedNodes: 0
    });

    // Replicate to 3 nodes
    const replicationNodes = activeNodes.slice(0, 3);
    
    for (let i = 0; i < replicationNodes.length; i++) {
      const node = replicationNodes[i];
      
      setUploadProgress(prev => ({ 
        ...prev, 
        currentNode: node.name,
        progress: ((i + 0.5) / 3) * 100,
        completedNodes: i
      }));
      
      // Simulate network upload time (proportional to file size)
      const uploadTime = Math.min(2000, (fileSize / (1024 * 1024)) * 500);
      await new Promise(resolve => setTimeout(resolve, uploadTime));
      
      // Update node storage and file list
      setNodes(prevNodes => prevNodes.map(n => 
        n.id === node.id 
          ? { 
              ...n, 
              storage: { ...n.storage, used: n.storage.used + fileSize },
              files: [...n.files, newFile.id]
            }
          : n
      ));
      
      newFile.replicas.push({ 
        nodeId: node.id, 
        nodeName: node.name,
        nodeIp: node.ip 
      });
      
      setUploadProgress(prev => ({ 
        ...prev, 
        progress: ((i + 1) / 3) * 100,
        completedNodes: i + 1
      }));
    }

    // Update user storage
    setUserStorage(prev => ({ ...prev, used: prev.used + fileSize }));
    setFiles(prev => [...prev, newFile]);
    
    setNotifications(prev => [...prev, {
      id: Date.now(),
      message: `File "${file.name}" uploaded successfully (replicated to 3 nodes)`,
      time: new Date().toISOString(),
      read: false
    }]);

    setTimeout(() => setUploadProgress(null), 2000);
  };

  // Delete file from all nodes
  const handleDeleteFile = (fileId) => {
    const file = files.find(f => f.id === fileId);
    if (!file) return;

    if (confirm(`🗑️ Delete "${file.name}" from all nodes?`)) {
      // Remove from all nodes
      file.replicas.forEach(replica => {
        setNodes(prevNodes => prevNodes.map(node => 
          node.id === replica.nodeId
            ? {
                ...node,
                storage: { ...node.storage, used: node.storage.used - file.size },
                files: node.files.filter(fid => fid !== fileId)
              }
            : node
        ));
      });

      // Update user storage
      setUserStorage(prev => ({ ...prev, used: prev.used - file.size }));
      setFiles(prev => prev.filter(f => f.id !== fileId));
      
      setNotifications(prev => [...prev, {
        id: Date.now(),
        message: `File "${file.name}" deleted from all nodes`,
        time: new Date().toISOString(),
        read: false
      }]);
    }
  };

  // Download file (simulated)
  const handleDownloadFile = (file) => {
    setNotifications(prev => [...prev, {
      id: Date.now(),
      message: `Downloading "${file.name}" from ${file.replicas[0].nodeName}`,
      time: new Date().toISOString(),
      read: false
    }]);
    alert(`📥 Downloading "${file.name}" from ${file.replicas[0].nodeName}`);
  };

  // Admin: Add new node
  const handleAddNode = () => {
    const nodeId = nodes.length + 1;
    const newNode = {
      id: nodeId,
      name: `Node ${nodeId}`,
      ip: `10.0.1.${nodeId}`,
      mac: `02:${nodeId}a:4b:5c:6d:7e`,
      status: 'active',
      storage: { used: 0, total: 10 * 1024 * 1024 * 1024 },
      files: [],
      bandwidth: '100 Mbps'
    };
    setNodes(prev => [...prev, newNode]);
    
    setNotifications(prev => [...prev, {
      id: Date.now(),
      message: `Node ${nodeId} added successfully`,
      time: new Date().toISOString(),
      read: false
    }]);
  };

  // Admin: Delete node
  const handleDeleteNode = (nodeId) => {
    const node = nodes.find(n => n.id === nodeId);
    if (!node) return;
    
    if (node.files.length > 0) {
      alert(`⚠️ Warning: This node contains ${node.files.length} file(s). Files will need re-replication!`);
    }
    
    if (confirm(`🗑️ Delete ${node.name}? This action cannot be undone.`)) {
      setNodes(prev => prev.filter(n => n.id !== nodeId));
      
      setNotifications(prev => [...prev, {
        id: Date.now(),
        message: `${node.name} removed from cluster`,
        time: new Date().toISOString(),
        read: false
      }]);
    }
  };

  // AI Assistant
  const handleAiChat = async () => {
    if (!chatInput.trim()) return;

    const userMessage = { role: 'user', content: chatInput };
    setChatMessages(prev => [...prev, userMessage]);
    setChatInput('');
    setAiLoading(true);

    try {
      const systemContext = `You are a helpful AI assistant for CloudSync Pro, a distributed cloud storage platform.

Current System Status:
- User: ${currentUser?.username}
- Storage Used: ${formatBytes(userStorage.used)} / ${formatBytes(userStorage.total)}
- Files: ${files.length} total
- Active Nodes: ${nodes.filter(n => n.status === 'active').length} / ${nodes.length}
- Replication Factor: 3x per file

Help the user with questions about storage management, file operations, node status, or system features.`;

      const response = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: 'claude-sonnet-4-20250514',
          max_tokens: 1000,
          messages: [
            { role: 'user', content: systemContext + '\n\nUser question: ' + chatInput }
          ]
        })
      });

      const data = await response.json();
      const aiResponse = { 
        role: 'assistant', 
        content: data.content?.[0]?.text || 'I apologize, but I encountered an error. Please try again.' 
      };
      setChatMessages(prev => [...prev, aiResponse]);
    } catch (error) {
      setChatMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'I apologize, but I encountered an error connecting to the AI service. Please check your connection and try again.' 
      }]);
    } finally {
      setAiLoading(false);
    }
  };

  // Filter files based on search
  const filteredFiles = files.filter(file => 
    file.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Login/Signup UI
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center p-4">
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl p-8 w-full max-w-md border border-white/20">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full mb-4 shadow-lg">
              <Cloud className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-white mb-2">CloudSync Pro</h1>
            <p className="text-blue-200">Distributed Cloud Storage Platform</p>
            <p className="text-sm text-blue-300 mt-2">30GB Free Storage • 3x Replication</p>
          </div>

          <div className="flex mb-6 bg-white/5 rounded-lg p-1">
            <button
              onClick={() => setCurrentView('login')}
              className={`flex-1 py-2 rounded-md transition-all ${currentView === 'login' ? 'bg-blue-500 text-white shadow-lg' : 'text-white/70 hover:text-white'}`}
            >
              Login
            </button>
            <button
              onClick={() => setCurrentView('signup')}
              className={`flex-1 py-2 rounded-md transition-all ${currentView === 'signup' ? 'bg-blue-500 text-white shadow-lg' : 'text-white/70 hover:text-white'}`}
            >
              Sign Up
            </button>
          </div>

          {currentView === 'signup' && (
            <div className="space-y-4">
              <input
                type="text"
                placeholder="Username"
                value={authForm.username}
                onChange={(e) => setAuthForm({ ...authForm, username: e.target.value })}
                className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <input
                type="email"
                placeholder="Email"
                value={authForm.email}
                onChange={(e) => setAuthForm({ ...authForm, email: e.target.value })}
                className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <input
                type="password"
                placeholder="Password (min 8 characters)"
                value={authForm.password}
                onChange={(e) => setAuthForm({ ...authForm, password: e.target.value })}
                className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <input
                type="tel"
                placeholder="Phone (optional)"
                value={authForm.phone}
                onChange={(e) => setAuthForm({ ...authForm, phone: e.target.value })}
                className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button
                onClick={handleSignup}
                className="w-full py-3 bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white rounded-lg font-semibold transition-all shadow-lg"
              >
                Create Account
              </button>
              <p className="text-xs text-white/60 text-center">
                By signing up, you agree to receive OTP via email
              </p>
            </div>
          )}

          {currentView === 'login' && (
            <div className="space-y-4">
              <input
                type="email"
                placeholder="Email"
                value={authForm.email}
                onChange={(e) => setAuthForm({ ...authForm, email: e.target.value })}
                className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <input
                type="password"
                placeholder="Password"
                value={authForm.password}
                onChange={(e) => setAuthForm({ ...authForm, password: e.target.value })}
                className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button
                onClick={handleLogin}
                className="w-full py-3 bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white rounded-lg font-semibold transition-all shadow-lg"
              >
                Login
              </button>
              <p className="text-xs text-white/60 text-center">
                Two-factor authentication with OTP enabled
              </p>
            </div>
          )}
        </div>

        {/* OTP Modal */}
        {showOtpModal && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-2xl p-8 w-full max-w-md shadow-2xl">
              <div className="text-center mb-6">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
                  <AlertCircle className="w-8 h-8 text-blue-500" />
                </div>
                <h2 className="text-2xl font-bold mb-2">Verify OTP</h2>
                <p className="text-gray-600">Enter the 6-digit code sent to</p>
                <p className="font-semibold text-gray-900">{otpForm.email}</p>
              </div>
              <input
                type="text"
                maxLength="6"
                placeholder="000000"
                value={otpForm.otp}
                onChange={(e) => setOtpForm({ ...otpForm, otp: e.target.value.replace(/\D/g, '') })}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg text-center text-2xl tracking-widest mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <div className="flex gap-3">
                <button
                  onClick={() => setShowOtpModal(false)}
                  className="flex-1 py-3 bg-gray-200 hover:bg-gray-300 rounded-lg font-semibold transition-all"
                >
                  Cancel
                </button>
                <button
                  onClick={handleVerifyOtp}
                  className="flex-1 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-semibold transition-all"
                >
                  Verify
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  // Main Dashboard
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-40 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg flex items-center justify-center shadow-lg">
              <Cloud className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">CloudSync Pro</h1>
              <p className="text-xs text-gray-500">{currentUser?.username} • {userRole === 'admin' ? '👑 Admin' : '👤 User'}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="relative">
              <button className="p-2 hover:bg-gray-100 rounded-lg transition-all relative">
                <Bell className="w-5 h-5 text-gray-600" />
                {notifications.filter(n => !n.read).length > 0 && (
                  <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
                )}
              </button>
            </div>
            <button
              onClick={() => setShowAiChat(!showAiChat)}
              className="flex items-center gap-2 px-3 py-2 hover:bg-gray-100 rounded-lg transition-all"
              title="AI Assistant"
            >
              <Bot className="w-5 h-5 text-blue-500" />
              <span className="text-sm font-medium">AI Help</span>
            </button>
            <button
              onClick={() => {
                if (confirm('Are you sure you want to logout?')) {
                  setIsAuthenticated(false);
                  setCurrentUser(null);
                  setCurrentView('login');
                  setFiles([]);
                  setUserStorage({ used: 0, total: 30 * 1024 * 1024 * 1024 });
                }
              }}
              className="flex items-center gap-2 px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-all"
            >
              <LogOut className="w-4 h-4" />
              Logout
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Navigation Tabs */}
        <div className="flex gap-2 mb-6 bg-white p-2 rounded-lg shadow-sm overflow-x-auto">
          <button
            onClick={() => setCurrentView('dashboard')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all whitespace-nowrap ${currentView === 'dashboard' ? 'bg-blue-500 text-white' : 'hover:bg-gray-100'}`}
          >
            <TrendingUp className="w-4 h-4" />
            Dashboard
          </button>
          <button
            onClick={() => setCurrentView('files')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all whitespace-nowrap ${currentView === 'files' ? 'bg-blue-500 text-white' : 'hover:bg-gray-100'}`}
          >
            <File className="w-4 h-4" />
            My Files ({files.length})
          </button>
          <button
            onClick={() => setCurrentView('nodes')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all whitespace-nowrap ${currentView === 'nodes' ? 'bg-blue-500 text-white' : 'hover:bg-gray-100'}`}
          >
            <Server className="w-4 h-4" />
            Nodes ({nodes.filter(n => n.status === 'active').length}/{nodes.length})
          </button>
          {userRole === 'admin' && (
            <button
              onClick={() => setCurrentView('admin')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all whitespace-nowrap ${currentView === 'admin' ? 'bg-blue-500 text-white' : 'hover:bg-gray-100'}`}
            >
              <Settings className="w-4 h-4" />
              Admin Panel
            </button>
          )}
        </div>

        {/* Dashboard View */}
        {currentView === 'dashboard' && (
          <div className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-xl shadow-lg p-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-blue-100 text-sm">Storage Used</span>
                  <HardDrive className="w-5 h-5 text-blue-200" />
                </div>
                <p className="text-2xl font-bold">{formatBytes(userStorage.used)}</p>
                <p className="text-xs text-blue-200">of {formatBytes(userStorage.total)}</p>
                <div className="mt-3 bg-blue-400 rounded-full h-2">
                  <div 
                    className="bg-white rounded-full h-2 transition-all"
                    style={{ width: `${(userStorage.used / userStorage.total) * 100}%` }}
                  />
                </div>
              </div>
              
              <div className="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-xl shadow-lg p-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-green-100 text-sm">Total Files</span>
                  <File className="w-5 h-5 text-green-200" />
                </div>
                <p className="text-2xl font-bold">{files.length}</p>
                <p className="text-xs text-green-200">Across all nodes</p>
              </div>
              
              <div className="bg-gradient-to-br from-purple-500 to-purple-600 text-white rounded-xl shadow-lg p-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-purple-100 text-sm">Active Nodes</span>
                  <Activity className="w-5 h-5 text-purple-200" />
                </div>
                <p className="text-2xl font-bold">{nodes.filter(n => n.status === 'active').length}</p>
                <p className="text-xs text-purple-200">of {nodes.length} total</p>
              </div>
              
              <div className="bg-gradient-to-br from-orange-500 to-orange-600 text-white rounded-xl shadow-lg p-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-orange-100 text-sm">Replication</span>
                  <CheckCircle className="w-5 h-5 text-orange-200" />
                </div>
                <p className="text-2xl font-bold">3x</p>
                <p className="text-xs text-orange-200">Per file backup</p>
              </div>
            </div>

            {/* Quick Upload */}
            <div className="bg-gradient-to-br from-indigo-50 to-purple-50 border-2 border-dashed border-indigo-300 rounded-xl p-8 text-center">
              <Upload className="w-12 h-12 text-indigo-500 mx-auto mb-3" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Quick Upload</h3>
              <p className="text-gray-600 mb-4">Upload files with automatic 3x replication</p>
              <label className="inline-flex items-center gap-2 px-6 py-3 bg-indigo-500 hover:bg-indigo-600 text-white rounded-lg cursor-pointer transition-all shadow-lg">
                <Upload className="w-5 h-5" />
                Choose Files
                <input
                  type="file"
                  onChange={handleFileUpload}
                  className="hidden"
                  multiple
                />
              </label>
            </div>

            {/* Upload Progress */}
            {uploadProgress && (
              <div className="bg-white border-2 border-blue-500 rounded-xl p-6 shadow-lg">
                <div className="flex items-center gap-3 mb-4">
                  <Upload className="w-6 h-6 text-blue-500 animate-pulse" />
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-900">{uploadProgress.fileName}</h4>
                    <p className="text-sm text-gray-600">
                      Uploading to {uploadProgress.currentNode} ({uploadProgress.completedNodes}/{uploadProgress.totalNodes} nodes)
                    </p>
                  </div>
                </div>
                <div className="relative">
                  <div className="w-full bg-gray-200 rounded-full h-4">
                    <div
                      className="bg-gradient-to-r from-blue-500 to-purple-500 h-4 rounded-full transition-all flex items-center justify-center"
                      style={{ width: `${uploadProgress.progress}%` }}
                    >
                      <span className="text-xs text-white font-bold">{uploadProgress.progress.toFixed(0)}%</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Node Status Grid */}
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
              <h3 className="text-lg font-semibold mb-4">Live Node Status</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {nodes.map(node => (
                  <div key={node.id} className="border-2 border-gray-200 rounded-lg p-4 hover:border-blue-400 transition-all">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <div className={`w-3 h-3 rounded-full ${node.status === 'active' ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
                        <span className="font-semibold">{node.name}</span>
                      </div>
                      <Server className="w-5 h-5 text-gray-400" />
                    </div>
                    <div className="space-y-2 text-sm">
                      <p className="text-gray-600">IP: {node.ip}</p>
                      <p className="text-gray-600">Files: {node.files.length}</p>
                      <div>
                        <div className="flex justify-between text-xs mb-1">
                          <span>Storage</span>
                          <span className="font-semibold">{((node.storage.used / node.storage.total) * 100).toFixed(1)}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-gradient-to-r from-green-400 to-blue-500 h-2 rounded-full"
                            style={{ width: `${(node.storage.used / node.storage.total) * 100}%` }}
                          />
                        </div>
                        <p className="text-xs text-gray-500 mt-1">
                          {formatBytes(node.storage.total - node.storage.used)} available
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Files */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200">
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-semibold">Recent Files</h3>
              </div>
              <div className="divide-y divide-gray-200">
                {files.slice(-5).reverse().map(file => (
                  <div key={file.id} className="p-4 hover:bg-gray-50 flex items-center gap-3">
                    <File className="w-5 h-5 text-blue-500" />
                    <div className="flex-1">
                      <p className="font-medium">{file.name}</p>
                      <p className="text-sm text-gray-500">{formatBytes(file.size)} • {file.replicas.length} replicas</p>
                    </div>
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  </div>
                ))}
                {files.length === 0 && (
                  <div className="p-8 text-center text-gray-500">
                    <File className="w-12 h-12 mx-auto mb-2 opacity-30" />
                    <p>No files uploaded yet</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Files View */}
        {currentView === 'files' && (
          <div className="space-y-6">
            {/* Upload Section */}
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">File Management</h3>
                <div className="flex gap-2">
                  <label className="flex items-center gap-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg cursor-pointer transition-all">
                    <Upload className="w-4 h-4" />
                    Upload File
                    <input
                      type="file"
                      onChange={handleFileUpload}
                      className="hidden"
                    />
                  </label>
                </div>
              </div>

              {uploadProgress && (
                <div className="border-2 border-blue-500 bg-blue-50 rounded-lg p-4 mb-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Upload className="w-5 h-5 text-blue-500 animate-bounce" />
                    <span className="font-semibold text-blue-900">{uploadProgress.fileName}</span>
                  </div>
                  {uploadProgress.currentNode && (
                    <p className="text-sm text-blue-700 mb-2">
                      📡 Replicating to {uploadProgress.currentNode}... ({uploadProgress.completedNodes}/{uploadProgress.totalNodes} complete)
                    </p>
                  )}
                  <div className="w-full bg-blue-200 rounded-full h-3 mb-2">
                    <div
                      className="bg-blue-600 h-3 rounded-full transition-all"
                      style={{ width: `${uploadProgress.progress}%` }}
                    />
                  </div>
                  <p className="text-sm text-blue-700 font-semibold">{uploadProgress.progress.toFixed(0)}% complete</p>
                </div>
              )}

              {/* Storage Info */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-blue-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-1">Used Space</p>
                  <p className="text-2xl font-bold text-blue-600">{formatBytes(userStorage.used)}</p>
                </div>
                <div className="bg-green-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600 mb-1">Available Space</p>
                  <p className="text-2xl font-bold text-green-600">{formatBytes(userStorage.total - userStorage.used)}</p>
                </div>
              </div>
            </div>

            {/* Search Bar */}
            <div className="bg-white rounded-xl shadow-sm p-4 border border-gray-200">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search files..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* Files List */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200">
              <div className="p-6 border-b border-gray-200 flex items-center justify-between">
                <h3 className="text-lg font-semibold">My Files ({filteredFiles.length})</h3>
                <span className="text-sm text-gray-500">{formatBytes(userStorage.used)} used</span>
              </div>
              <div className="divide-y divide-gray-200">
                {filteredFiles.length === 0 ? (
                  <div className="p-12 text-center text-gray-500">
                    <File className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p>No files found</p>
                  </div>
                ) : (
                  filteredFiles.map(file => (
                    <div key={file.id} className="p-4 hover:bg-gray-50 transition-all">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3 flex-1">
                          <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                            <File className="w-5 h-5 text-blue-500" />
                          </div>
                          <div className="flex-1">
                            <p className="font-semibold text-gray-900">{file.name}</p>
                            <p className="text-sm text-gray-500">
                              {formatBytes(file.size)} • Replicated on {file.replicas.length} nodes
                            </p>
                            <div className="flex gap-2 mt-1">
                              {file.replicas.map((replica, idx) => (
                                <span key={idx} className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                                  {replica.nodeName}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => handleDownloadFile(file)}
                            className="p-2 hover:bg-blue-100 rounded-lg transition-all"
                            title="Download"
                          >
                            <Download className="w-4 h-4 text-blue-600" />
                          </button>
                          <button
                            onClick={() => handleDeleteFile(file.id)}
                            className="p-2 hover:bg-red-100 rounded-lg transition-all"
                            title="Delete"
                          >
                            <Trash2 className="w-4 h-4 text-red-500" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}

        {/* Nodes View */}
        {currentView === 'nodes' && (
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200">
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-lg font-semibold">Network Nodes</h3>
                <p className="text-sm text-gray-500 mt-1">Distributed storage cluster status</p>
              </div>
              <div className="divide-y divide-gray-200">
                {nodes.map(node => (
                  <div key={node.id} className="p-6 hover:bg-gray-50 transition-all">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <div className={`w-4 h-4 rounded-full ${node.status === 'active' ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
                        <div>
                          <h4 className="font-semibold text-lg">{node.name}</h4>
                          <p className="text-sm text-gray-500">IP: {node.ip} • MAC: {node.mac}</p>
                        </div>
                      </div>
                      <span className={`px-4 py-1 rounded-full text-sm font-semibold ${node.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                        {node.status}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-3 gap-4 mb-4">
                      <div className="bg-gray-50 rounded-lg p-3">
                        <p className="text-xs text-gray-600 mb-1">Storage Used</p>
                        <p className="font-semibold">{formatBytes(node.storage.used)}</p>
                      </div>
                      <div className="bg-gray-50 rounded-lg p-3">
                        <p className="text-xs text-gray-600 mb-1">Available</p>
                        <p className="font-semibold">{formatBytes(node.storage.total - node.storage.used)}</p>
                      </div>
                      <div className="bg-gray-50 rounded-lg p-3">
                        <p className="text-xs text-gray-600 mb-1">Bandwidth</p>
                        <p className="font-semibold">{node.bandwidth}</p>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Storage Capacity</span>
                        <span className="font-semibold">{formatBytes(node.storage.used)} / {formatBytes(node.storage.total)}</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-3">
                        <div
                          className="bg-gradient-to-r from-purple-500 to-blue-500 h-3 rounded-full transition-all"
                          style={{ width: `${(node.storage.used / node.storage.total) * 100}%` }}
                        />
                      </div>
                      <div className="flex justify-between text-xs text-gray-500">
                        <span>{((node.storage.used / node.storage.total) * 100).toFixed(1)}% used</span>
                        <span>{node.files.length} files stored</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Admin View */}
        {currentView === 'admin' && userRole === 'admin' && (
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="text-lg font-semibold">Node Management</h3>
                  <p className="text-sm text-gray-500 mt-1">Add, remove, or monitor cluster nodes</p>
                </div>
                <button
                  onClick={handleAddNode}
                  className="flex items-center gap-2 px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-all shadow-lg"
                >
                  <Plus className="w-4 h-4" />
                  Add Node
                </button>
              </div>

              <div className="space-y-4">
                {nodes.map(node => (
                  <div key={node.id} className="border-2 border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-all">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4 flex-1">
                        <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
                          <Server className="w-6 h-6 text-white" />
                        </div>
                        <div className="flex-1">
                          <h4 className="font-semibold">{node.name}</h4>
                          <p className="text-sm text-gray-500">IP: {node.ip} • MAC: {node.mac}</p>
                          <p className="text-xs text-gray-400 mt-1">
                            {node.files.length} files • {formatBytes(node.storage.used)} used
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${node.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                          {node.status}
                        </span>
                        <button
                          onClick={() => handleDeleteNode(node.id)}
                          className="p-2 hover:bg-red-100 rounded-lg transition-all"
                          title="Delete node"
                        >
                          <Trash2 className="w-4 h-4 text-red-500" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* System Statistics */}
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
              <h3 className="text-lg font-semibold mb-4">System Statistics</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="border border-gray-200 rounded-lg p-4 bg-gradient-to-br from-blue-50 to-blue-100">
                  <p className="text-sm text-gray-600 mb-1">Total Users</p>
                  <p className="text-3xl font-bold text-blue-600">1</p>
                </div>
                <div className="border border-gray-200 rounded-lg p-4 bg-gradient-to-br from-green-50 to-green-100">
                  <p className="text-sm text-gray-600 mb-1">Total Storage</p>
                  <p className="text-3xl font-bold text-green-600">{formatBytes(nodes.reduce((sum, n) => sum + n.storage.total, 0))}</p>
                </div>
                <div className="border border-gray-200 rounded-lg p-4 bg-gradient-to-br from-purple-50 to-purple-100">
                  <p className="text-sm text-gray-600 mb-1">Files Stored</p>
                  <p className="text-3xl font-bold text-purple-600">{files.length}</p>
                </div>
                <div className="border border-gray-200 rounded-lg p-4 bg-gradient-to-br from-orange-50 to-orange-100">
                  <p className="text-sm text-gray-600 mb-1">Active Nodes</p>
                  <p className="text-3xl font-bold text-orange-600">{nodes.filter(n => n.status === 'active').length}</p>
                </div>
              </div>
            </div>

            {/* Admin Controls */}
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
              <h3 className="text-lg font-semibold mb-4">Admin Controls</h3>
              <div className="grid grid-cols-2 gap-4">
                <button className="p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-all text-left">
                  <Users className="w-6 h-6 text-blue-500 mb-2" />
                  <p className="font-semibold">User Management</p>
                  <p className="text-sm text-gray-500">Manage user accounts</p>
                </button>
                <button className="p-4 border-2 border-gray-200 rounded-lg hover:border-green-500 hover:bg-green-50 transition-all text-left">
                  <Settings className="w-6 h-6 text-green-500 mb-2" />
                  <p className="font-semibold">System Settings</p>
                  <p className="text-sm text-gray-500">Configure platform</p>
                </button>
                <button className="p-4 border-2 border-gray-200 rounded-lg hover:border-purple-500 hover:bg-purple-50 transition-all text-left">
                  <Activity className="w-6 h-6 text-purple-500 mb-2" />
                  <p className="font-semibold">Activity Logs</p>
                  <p className="text-sm text-gray-500">View system logs</p>
                </button>
                <button className="p-4 border-2 border-gray-200 rounded-lg hover:border-red-500 hover:bg-red-50 transition-all text-left">
                  <AlertCircle className="w-6 h-6 text-red-500 mb-2" />
                  <p className="font-semibold">System Health</p>
                  <p className="text-sm text-gray-500">Monitor cluster</p>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* AI Chat Assistant */}
      {showAiChat && (
        <div className="fixed bottom-4 right-4 w-96 h-[600px] bg-white rounded-2xl shadow-2xl border border-gray-200 flex flex-col z-50">
          <div className="p-4 border-b border-gray-200 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-t-2xl">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Bot className="w-6 h-6" />
                <div>
                  <h3 className="font-semibold">AI Assistant</h3>
                  <p className="text-xs text-blue-100">Powered by Claude</p>
                </div>
              </div>
              <button
                onClick={() => setShowAiChat(false)}
                className="p-1 hover:bg-white/20 rounded transition-all"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50">
            {chatMessages.length === 0 && (
              <div className="text-center text-gray-500 mt-12">
                <Bot className="w-16 h-16 mx-auto mb-3 opacity-30" />
                <p className="text-sm font-medium">Ask me anything!</p>
                <p className="text-xs mt-2">I can help you with:</p>
                <div className="mt-2 text-xs space-y-1">
                  <p>• Storage management</p>
                  <p>• File operations</p>
                  <p>• Node status</p>
                  <p>• System optimization</p>
                </div>
              </div>
            )}
            {chatMessages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] p-3 rounded-lg shadow-sm ${
                    msg.role === 'user'
                      ? 'bg-blue-500 text-white'
                      : 'bg-white text-gray-900 border border-gray-200'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>
            ))}
            {aiLoading && (
              <div className="flex justify-start">
                <div className="bg-white border border-gray-200 p-3 rounded-lg shadow-sm">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="p-4 border-t border-gray-200 bg-white rounded-b-2xl">
            <div className="flex gap-2">
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && !aiLoading && handleAiChat()}
                placeholder="Type your question..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                disabled={aiLoading}
              />
              <button
                onClick={handleAiChat}
                disabled={aiLoading || !chatInput.trim()}
                className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Send
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CloudStoragePlatform;