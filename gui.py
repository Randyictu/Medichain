import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import subprocess
import threading
import time
import sys
import os
from datetime import datetime
import queue

class ModernGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Integrated Cloud & Distributed System")
        self.root.geometry("1400x900")
        self.root.configure(bg='#0f172a')
        
        # Process tracking
        self.processes = {}
        self.output_queues = {}
        self.output_threads = {}
        
        # Color scheme - Modern Dark Theme
        self.colors = {
            'bg_primary': '#0f172a',
            'bg_secondary': '#1e293b',
            'bg_card': '#334155',
            'accent_blue': '#3b82f6',
            'accent_green': '#10b981',
            'accent_red': '#ef4444',
            'accent_yellow': '#f59e0b',
            'accent_purple': '#8b5cf6',
            'text_primary': '#f1f5f9',
            'text_secondary': '#94a3b8',
            'border': '#475569'
        }
        
        self.setup_styles()
        self.create_main_layout()
        self.update_status_loop()
        self.update_outputs_loop()
    
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Primary.TButton',
            background=self.colors['accent_blue'],
            foreground='white',
            borderwidth=0,
            focuscolor='none',
            padding=(20, 12),
            font=('Segoe UI', 10, 'bold'))
        
        style.map('Primary.TButton',
            background=[('active', '#2563eb')])
        
        style.configure('Success.TButton',
            background=self.colors['accent_green'],
            foreground='white',
            borderwidth=0,
            padding=(20, 12),
            font=('Segoe UI', 10, 'bold'))
        
        style.configure('Danger.TButton',
            background=self.colors['accent_red'],
            foreground='white',
            borderwidth=0,
            padding=(20, 12),
            font=('Segoe UI', 10, 'bold'))
        
        style.configure('Warning.TButton',
            background=self.colors['accent_yellow'],
            foreground='white',
            borderwidth=0,
            padding=(20, 12),
            font=('Segoe UI', 10, 'bold'))
    
    def create_main_layout(self):
        """Create main layout"""
        self.create_header()
        
        main_container = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left sidebar
        left_panel = tk.Frame(main_container, bg=self.colors['bg_secondary'], width=350)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 20))
        left_panel.pack_propagate(False)
        
        self.create_control_panel(left_panel)
        
        # Right panel
        right_panel = tk.Frame(main_container, bg=self.colors['bg_primary'])
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.create_status_panel(right_panel)
        self.create_output_panel(right_panel)
    
    def create_header(self):
        """Create header"""
        header = tk.Frame(self.root, bg=self.colors['bg_secondary'], height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title_frame = tk.Frame(header, bg=self.colors['bg_secondary'])
        title_frame.pack(side=tk.LEFT, padx=30, pady=20)
        
        icon_label = tk.Label(title_frame, text="🔐💾", font=('Segoe UI', 28),
                             bg=self.colors['bg_secondary'], fg=self.colors['text_primary'])
        icon_label.pack(side=tk.LEFT, padx=(0, 15))
        
        title_label = tk.Label(title_frame, text="Integrated Cloud System",
                              font=('Segoe UI', 24, 'bold'),
                              bg=self.colors['bg_secondary'],
                              fg=self.colors['text_primary'])
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = tk.Label(title_frame, text="Authentication & Distributed Storage",
                                 font=('Segoe UI', 11),
                                 bg=self.colors['bg_secondary'],
                                 fg=self.colors['text_secondary'])
        subtitle_label.pack(side=tk.LEFT, padx=(15, 0))
        
        self.time_label = tk.Label(header, font=('Segoe UI', 11),
                                  bg=self.colors['bg_secondary'],
                                  fg=self.colors['text_secondary'])
        self.time_label.pack(side=tk.RIGHT, padx=30)
        self.update_time()
    
    def create_control_panel(self, parent):
        """Create control panel"""
        title_label = tk.Label(parent, text="System Controls",
                              font=('Segoe UI', 16, 'bold'),
                              bg=self.colors['bg_secondary'],
                              fg=self.colors['text_primary'])
        title_label.pack(pady=(20, 30), padx=20, anchor='w')
        
        self.create_section(parent, "🔐 Cloud Security", [
            ("Start Auth Server", self.start_cloud_server, 'Primary.TButton'),
            ("Open Auth Client", self.open_auth_client, 'Primary.TButton'),
            ("Stop Auth Server", self.stop_cloud_server, 'Danger.TButton')
        ])
        
        self.create_section(parent, "💾 Distributed Storage", [
            ("Start Storage Server", self.start_threaded_network, 'Success.TButton'),
            ("Open Node Interface", self.open_node_interface, 'Success.TButton'),
            ("Stop Storage Server", self.stop_threaded_network, 'Danger.TButton')
        ])
        
        self.create_section(parent, "⚙️ System Management", [
            ("Refresh Status", self.refresh_status, 'Warning.TButton'),
            ("Clear Output", self.clear_output, 'Warning.TButton'),
            ("Stop Everything", self.stop_everything, 'Danger.TButton')
        ])
    
    def create_section(self, parent, title, buttons):
        """Create section with buttons"""
        section_frame = tk.Frame(parent, bg=self.colors['bg_card'])
        section_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        section_title = tk.Label(section_frame, text=title,
                                font=('Segoe UI', 13, 'bold'),
                                bg=self.colors['bg_card'],
                                fg=self.colors['text_primary'])
        section_title.pack(pady=(15, 10), padx=15, anchor='w')
        
        for btn_text, btn_command, btn_style in buttons:
            btn = ttk.Button(section_frame, text=btn_text,
                           command=btn_command, style=btn_style)
            btn.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Frame(section_frame, bg=self.colors['bg_card'], height=15).pack()
    
    def create_status_panel(self, parent):
        """Create status panel"""
        status_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], height=200)
        status_frame.pack(fill=tk.X, pady=(0, 20))
        status_frame.pack_propagate(False)
        
        title = tk.Label(status_frame, text="System Status",
                        font=('Segoe UI', 14, 'bold'),
                        bg=self.colors['bg_secondary'],
                        fg=self.colors['text_primary'])
        title.pack(pady=(15, 20), padx=20, anchor='w')
        
        cards_container = tk.Frame(status_frame, bg=self.colors['bg_secondary'])
        cards_container.pack(fill=tk.BOTH, expand=True, padx=20)
        
        self.status_cards = {}
        
        services = [
            ("Cloud Security Server", "cloud_server", "🔐"),
            ("Storage Server", "storage_server", "🖥️"),
            ("Active Processes", "processes", "⚡")
        ]
        
        for idx, (name, key, icon) in enumerate(services):
            card = self.create_status_card(cards_container, name, icon)
            self.status_cards[key] = card
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
    
    def create_status_card(self, parent, title, icon):
        """Create status card"""
        card = tk.Frame(parent, bg=self.colors['bg_card'])
        
        header = tk.Frame(card, bg=self.colors['bg_card'])
        header.pack(fill=tk.X, padx=15, pady=(15, 5))
        
        icon_label = tk.Label(header, text=icon, font=('Segoe UI', 20),
                             bg=self.colors['bg_card'], fg=self.colors['text_primary'])
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        title_label = tk.Label(header, text=title, font=('Segoe UI', 11, 'bold'),
                              bg=self.colors['bg_card'], fg=self.colors['text_primary'])
        title_label.pack(side=tk.LEFT)
        
        status_frame = tk.Frame(card, bg=self.colors['bg_card'])
        status_frame.pack(fill=tk.X, padx=15, pady=10)
        
        status_dot = tk.Label(status_frame, text="●", font=('Segoe UI', 14),
                             bg=self.colors['bg_card'], fg=self.colors['text_secondary'])
        status_dot.pack(side=tk.LEFT, padx=(0, 8))
        
        status_text = tk.Label(status_frame, text="Not Running",
                              font=('Segoe UI', 9),
                              bg=self.colors['bg_card'],
                              fg=self.colors['text_secondary'])
        status_text.pack(side=tk.LEFT)
        
        info_label = tk.Label(card, text="PID: N/A",
                            font=('Segoe UI', 8),
                            bg=self.colors['bg_card'],
                            fg=self.colors['text_secondary'])
        info_label.pack(padx=15, pady=(0, 15), anchor='w')
        
        card.status_dot = status_dot
        card.status_text = status_text
        card.info_label = info_label
        
        return card
    
    def create_output_panel(self, parent):
        """Create output panel"""
        output_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        title = tk.Label(output_frame, text="System Output & Logs",
                        font=('Segoe UI', 14, 'bold'),
                        bg=self.colors['bg_secondary'],
                        fg=self.colors['text_primary'])
        title.pack(pady=(15, 10), padx=20, anchor='w')
        
        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            font=('Consolas', 9),
            bg='#1e293b',
            fg='#e2e8f0',
            insertbackground='white',
            relief=tk.FLAT,
            padx=10,
            pady=10,
            wrap=tk.WORD
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        self.add_output("System initialized successfully", "INFO")
        self.add_output("Ready to start services...", "INFO")
    
    def add_output(self, message, level="INFO"):
        """Add output message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        level_colors = {
            "INFO": "#3b82f6",
            "SUCCESS": "#10b981",
            "ERROR": "#ef4444",
            "WARNING": "#f59e0b",
            "OUTPUT": "#94a3b8"
        }
        
        color = level_colors.get(level, "#94a3b8")
        
        self.output_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.output_text.insert(tk.END, f"[{level}] ", level)
        self.output_text.insert(tk.END, f"{message}\n")
        
        self.output_text.tag_config("timestamp", foreground="#64748b")
        self.output_text.tag_config(level, foreground=color, font=('Consolas', 9, 'bold'))
        
        self.output_text.see(tk.END)
        self.output_text.update()
    
    def read_process_output(self, process, name, output_queue):
        """Read process output in thread"""
        try:
            for line in iter(process.stdout.readline, b''):
                if line:
                    output_queue.put((name, line.decode('utf-8', errors='ignore').strip()))
        except:
            pass
    
    def update_outputs_loop(self):
        """Update outputs from all processes"""
        for name, q in self.output_queues.items():
            try:
                while not q.empty():
                    proc_name, line = q.get_nowait()
                    if line:
                        self.add_output(f"[{proc_name}] {line}", "OUTPUT")
            except:
                pass
        
        self.root.after(100, self.update_outputs_loop)
    
    def start_process_with_output(self, name, script, args=[]):
        """Start process and capture output"""
        if name in self.processes and self.processes[name].poll() is None:
            messagebox.showwarning("Warning", f"{name} is already running!")
            return False
        
        try:
            cmd = [sys.executable, script] + args
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
                universal_newlines=False
            )
            
            self.processes[name] = process
            
            # Create output queue and thread
            output_queue = queue.Queue()
            self.output_queues[name] = output_queue
            
            output_thread = threading.Thread(
                target=self.read_process_output,
                args=(process, name, output_queue),
                daemon=True
            )
            output_thread.start()
            self.output_threads[name] = output_thread
            
            self.add_output(f"Started {name} (PID: {process.pid})", "SUCCESS")
            return True
            
        except Exception as e:
            self.add_output(f"Failed to start {name}: {str(e)}", "ERROR")
            messagebox.showerror("Error", f"Failed to start {name}\n{str(e)}")
            return False
    
    def stop_process(self, name):
        """Stop a process"""
        if name not in self.processes:
            self.add_output(f"{name} is not running", "WARNING")
            return
        
        try:
            process = self.processes[name]
            process.terminate()
            try:
                process.wait(timeout=5)
            except:
                process.kill()
            
            del self.processes[name]
            if name in self.output_queues:
                del self.output_queues[name]
            if name in self.output_threads:
                del self.output_threads[name]
            
            self.add_output(f"Stopped {name}", "INFO")
            
        except Exception as e:
            self.add_output(f"Error stopping {name}: {str(e)}", "ERROR")
    
    def start_cloud_server(self):
        """Start cloud security server"""
        self.start_process_with_output("Cloud Security Server", "cloud.py")
    
    def open_auth_client(self):
        """Open authentication client in new window"""
        try:
            if os.name == 'nt':  # Windows
                subprocess.Popen([sys.executable, 'client.py'],
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:  # Linux/Mac
                terminals = [
                    ['gnome-terminal', '--', sys.executable, 'client.py'],
                    ['xterm', '-e', sys.executable, 'client.py'],
                    ['konsole', '-e', sys.executable, 'client.py'],
                ]
                launched = False
                for term_cmd in terminals:
                    try:
                        subprocess.Popen(term_cmd)
                        launched = True
                        break
                    except FileNotFoundError:
                        continue
                
                if not launched:
                    subprocess.Popen([sys.executable, 'client.py'])
            
            self.add_output("Opened Authentication Client in new window", "SUCCESS")
            
        except Exception as e:
            self.add_output(f"Failed to open client: {str(e)}", "ERROR")
            messagebox.showerror("Error", f"Failed to open client\n{str(e)}")
    
    def stop_cloud_server(self):
        """Stop cloud server"""
        self.stop_process("Cloud Security Server")
    
    def start_threaded_network(self):
        """Start threaded network server"""
        self.start_process_with_output("Threaded Network Server", "threaded.py")
    
    def open_node_interface(self):
        """Open node in new window"""
        node_id = simpledialog.askstring("Create Node", "Enter Node ID (e.g., 1, 2, 3):")
        
        if not node_id:
            return
        
        try:
            if os.name == 'nt':  # Windows
                subprocess.Popen([sys.executable, 'node.py', node_id],
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:  # Linux/Mac
                terminals = [
                    ['gnome-terminal', '--', sys.executable, 'node.py', node_id],
                    ['xterm', '-e', sys.executable, 'node.py', node_id],
                    ['konsole', '-e', sys.executable, 'node.py', node_id],
                ]
                launched = False
                for term_cmd in terminals:
                    try:
                        subprocess.Popen(term_cmd)
                        launched = True
                        break
                    except FileNotFoundError:
                        continue
                
                if not launched:
                    subprocess.Popen([sys.executable, 'node.py', node_id])
            
            self.add_output(f"Opened Storage Node {node_id} in new window", "SUCCESS")
            
        except Exception as e:
            self.add_output(f"Failed to open node: {str(e)}", "ERROR")
            messagebox.showerror("Error", f"Failed to open node\n{str(e)}")
    
    def stop_threaded_network(self):
        """Stop threaded network"""
        self.stop_process("Threaded Network Server")
    
    def stop_everything(self):
        """Stop all processes"""
        if messagebox.askyesno("Confirm", "Stop all running processes?"):
            for name in list(self.processes.keys()):
                self.stop_process(name)
            self.add_output("All processes stopped", "INFO")
    
    def refresh_status(self):
        """Refresh status"""
        self.update_status()
        self.add_output("Status refreshed", "INFO")
    
    def clear_output(self):
        """Clear output"""
        self.output_text.delete(1.0, tk.END)
        self.add_output("Output cleared", "INFO")
    
    def update_status_card(self, key, running, pid=None, extra_info=""):
        """Update status card"""
        if key not in self.status_cards:
            return
        
        card = self.status_cards[key]
        
        if running:
            card.status_dot.config(fg=self.colors['accent_green'])
            card.status_text.config(text="Running", fg=self.colors['accent_green'])
            info_text = f"PID: {pid}" if pid else "Active"
            if extra_info:
                info_text += f" | {extra_info}"
            card.info_label.config(text=info_text)
        else:
            card.status_dot.config(fg=self.colors['text_secondary'])
            card.status_text.config(text="Not Running", fg=self.colors['text_secondary'])
            card.info_label.config(text="PID: N/A")
    
    def update_status(self):
        """Update all status"""
        cloud_server = self.processes.get("Cloud Security Server")
        self.update_status_card("cloud_server",
                               cloud_server and cloud_server.poll() is None,
                               cloud_server.pid if cloud_server else None)
        
        storage_server = self.processes.get("Threaded Network Server")
        self.update_status_card("storage_server",
                               storage_server and storage_server.poll() is None,
                               storage_server.pid if storage_server else None)
        
        total_processes = len([p for p in self.processes.values() if p.poll() is None])
        self.update_status_card("processes",
                               total_processes > 0,
                               extra_info=f"{total_processes} Running")
    
    def update_status_loop(self):
        """Update status periodically"""
        self.update_status()
        self.root.after(2000, self.update_status_loop)
    
    def update_time(self):
        """Update time"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)

def main():
    root = tk.Tk()
    app = ModernGUI(root)
    
    def on_closing():
        if app.processes:
            if messagebox.askyesno("Quit", "Stop all processes and exit?"):
                for name in list(app.processes.keys()):
                    app.stop_process(name)
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()