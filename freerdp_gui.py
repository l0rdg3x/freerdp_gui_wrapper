import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import subprocess
from ttkthemes import ThemedTk
import sys

class FreeRDPGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FreeRDP GUI Wrapper")
        if getattr(sys, 'frozen', False):
            icon_path = os.path.join(sys._MEIPASS, 'app_icon.png')
        else:
            icon_path = 'app_icon.png'
        self.root.iconphoto(False, tk.PhotoImage(file=icon_path))
        self.root.geometry('550x650')
        self.root.resizable(True, True)

        self.root.set_theme("arc")

        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        server_frame = ttk.LabelFrame(self.main_frame, text="Server Information", padding="10")
        server_frame.grid(row=0, column=0, sticky=tk.EW, pady=(0, 10))
        
        ttk.Label(server_frame, text="Hostname/IP:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.hostname_entry = ttk.Entry(server_frame)
        self.hostname_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(server_frame, text="Username:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.username_entry = ttk.Entry(server_frame)
        self.username_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(server_frame, text="Password:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.password_entry = ttk.Entry(server_frame, show='*')
        self.password_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)

        server_frame.grid_columnconfigure(1, weight=1)

        checkbox_frame = ttk.Frame(self.main_frame)
        checkbox_frame.grid(row=1, column=0, sticky=tk.EW, pady=(0, 10))

        self.dynamic_res_var = tk.IntVar()
        self.dynamic_res_chk = ttk.Checkbutton(checkbox_frame, text="Dynamic Resolution", variable=self.dynamic_res_var)
        self.dynamic_res_chk.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)

        self.cert_ignore_var = tk.IntVar()
        self.cert_ignore_chk = ttk.Checkbutton(checkbox_frame, text="Ignore Certificate", variable=self.cert_ignore_var)
        self.cert_ignore_chk.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

        self.clipboard_var = tk.IntVar()
        self.clipboard_chk = ttk.Checkbutton(checkbox_frame, text="Enable Clipboard", variable=self.clipboard_var)
        self.clipboard_chk.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)

        self.res_checkbox_var = tk.IntVar()
        self.resolution_checkbox = ttk.Checkbutton(checkbox_frame, text="Resolution (WxH):", variable=self.res_checkbox_var, command=self.toggle_res_entry)
        self.resolution_checkbox.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
        self.resolution_entry = ttk.Entry(checkbox_frame, state=tk.DISABLED)
        self.resolution_entry.grid(row=1, column=2, padx=5, pady=5, sticky=tk.EW)

        self.fullscreen_var = tk.IntVar()
        self.fullscreen_chk = ttk.Checkbutton(checkbox_frame, text="Full Screen", variable=self.fullscreen_var)
        self.fullscreen_chk.grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)

        self.audio_var = tk.IntVar()
        self.audio_chk = ttk.Checkbutton(checkbox_frame, text="Audio Redirection", variable=self.audio_var)
        self.audio_chk.grid(row=2, column=1, padx=10, pady=5, sticky=tk.W)

        self.drive_checkbox_var = tk.IntVar()
        self.drive_checkbox = ttk.Checkbutton(checkbox_frame, text="Drive Path:", variable=self.drive_checkbox_var, command=self.toggle_drive_entry)
        self.drive_checkbox.grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        self.drive_entry = ttk.Entry(checkbox_frame, state=tk.DISABLED)
        self.drive_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.EW)

        self.printer_var = tk.IntVar()
        self.printer_chk = ttk.Checkbutton(checkbox_frame, text="Printer Redirection", variable=self.printer_var)
        self.printer_chk.grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)

        self.multimon_var = tk.IntVar()
        self.multimon_chk = ttk.Checkbutton(checkbox_frame, text="Multiple Monitors", variable=self.multimon_var)
        self.multimon_chk.grid(row=4, column=1, padx=10, pady=5, sticky=tk.W)

        rdg_frame = ttk.LabelFrame(self.main_frame, text="Remote Desktop Gateway", padding="10")
        rdg_frame.grid(row=2, column=0, sticky=tk.EW, pady=(0, 10))
        
        self.rdg_enable_var = tk.IntVar()
        self.rdg_enable_chk = ttk.Checkbutton(rdg_frame, text="Use RD Gateway", variable=self.rdg_enable_var, command=self.toggle_rdg)
        self.rdg_enable_chk.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

        ttk.Label(rdg_frame, text="Server:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.rdg_server_entry = ttk.Entry(rdg_frame, state=tk.DISABLED)
        self.rdg_server_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)

        ttk.Label(rdg_frame, text="User:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.rdg_user_entry = ttk.Entry(rdg_frame, state=tk.DISABLED)
        self.rdg_user_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)

        ttk.Label(rdg_frame, text="Password:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.rdg_password_entry = ttk.Entry(rdg_frame, show='*', state=tk.DISABLED)
        self.rdg_password_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.EW)

        rdg_frame.grid_columnconfigure(1, weight=1)

        self.connect_btn = ttk.Button(self.main_frame, text="Connect", command=self.connect)
        self.connect_btn.grid(row=3, column=0, pady=20)

    def toggle_res_entry(self):
        state = tk.NORMAL if self.res_checkbox_var.get() else tk.DISABLED
        self.resolution_entry.config(state=state)

    def toggle_drive_entry(self):
        state = tk.NORMAL if self.drive_checkbox_var.get() else tk.DISABLED
        self.drive_entry.config(state=state)

    def toggle_rdg(self):
        if self.rdg_enable_var.get():
            self.rdg_server_entry.config(state=tk.NORMAL)
            self.rdg_user_entry.config(state=tk.NORMAL)
            self.rdg_password_entry.config(state=tk.NORMAL)
        else:
            self.rdg_server_entry.config(state=tk.DISABLED)
            self.rdg_user_entry.config(state=tk.DISABLED)
            self.rdg_password_entry.config(state=tk.DISABLED)

    def connect(self):
        cmd = ["xfreerdp"]
        cmd.extend([f"/v:{self.hostname_entry.get()}"])
        cmd.extend([f"/u:{self.username_entry.get()}"])
        cmd.extend([f"/p:{self.password_entry.get()}"])

        if self.dynamic_res_var.get():
            cmd.append("/dynamic-resolution")

        if self.cert_ignore_var.get():
            cmd.append("/cert-ignore")

        if self.clipboard_var.get():
            cmd.append("/clipboard")

        if self.res_checkbox_var.get() and self.resolution_entry.get():
            cmd.extend([f"/size:{self.resolution_entry.get()}"])

        if self.fullscreen_var.get():
            cmd.append("/f")

        if self.audio_var.get():
            cmd.append("/sound")

        if self.drive_checkbox_var.get() and self.drive_entry.get():
            cmd.extend([f"/drive:my_drive,{self.drive_entry.get()}"])

        if self.printer_var.get():
            cmd.append("/printer")

        if self.multimon_var.get():
            cmd.append("/multimon")

        if self.rdg_enable_var.get():
            cmd.extend([f"/g:{self.rdg_server_entry.get()}"])
            cmd.extend([f"/gu:{self.rdg_user_entry.get()}"])
            cmd.extend([f"/gp:{self.rdg_password_entry.get()}"])

        try:
            subprocess.run(cmd)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run FreeRDP: {e}")

if __name__ == "__main__":
    root = ThemedTk(theme="arc")
    gui = FreeRDPGUI(root)
    root.mainloop()
