import json
import os
import pickle
import subprocess
import sys
from pathlib import Path

from cryptography.fernet import Fernet
import tkinter as tk
from tkinter import messagebox, ttk
from ttkthemes import ThemedTk


class FreeRDPGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FreeRDP GUI Wrapper")
        if getattr(sys, 'frozen', False):
            icon_path = os.path.join(sys._MEIPASS, 'app_icon.png')
        else:
            icon_path = 'app_icon.png'
        self.root.iconphoto(False, tk.PhotoImage(file=icon_path))
        self.root.geometry('550x750')
        self.root.resizable(False, False)

        self.root.set_theme("arc")

        self.config_dir = os.path.expanduser("~/.config/freerdp_gui")
        self.config_file = os.path.join(self.config_dir, "config.key")

        self.load_or_initialize_cipher_suite()

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

        config_frame = ttk.LabelFrame(self.main_frame, text="Configurations", padding="10")
        config_frame.grid(row=4, column=0, sticky=tk.EW, pady=(0, 10))

        ttk.Label(config_frame, text="Config Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.config_name_entry = ttk.Entry(config_frame)
        self.config_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)

        self.load_config_btn = ttk.Button(config_frame, text="Load Config", command=self.load_config)
        self.load_config_btn.grid(row=0, column=2, padx=5, pady=5)

        self.save_config_btn = ttk.Button(config_frame, text="Save Config", command=self.export_config)
        self.save_config_btn.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(config_frame, text="Select Config:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.config_dropdown = ttk.Combobox(config_frame, values=self.get_available_configs())
        self.config_dropdown.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)

        self.delete_config_btn = ttk.Button(config_frame, text="Delete Config", command=self.delete_config)
        self.delete_config_btn.grid(row=1, column=2, padx=5, pady=5)

        config_frame.grid_columnconfigure(1, weight=1)

    def load_or_initialize_cipher_suite(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, "rb") as f:
                self.cipher_suite = pickle.load(f)
        else:
            self.initialize_cipher_suite()
            self.save_cipher_suite()

    def initialize_cipher_suite(self):
        self.key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.key)

    def save_cipher_suite(self):
        os.makedirs(self.config_dir, exist_ok=True)

        with open(self.config_file, "wb") as f:
            pickle.dump(self.cipher_suite, f)

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

    def encrypt(self, message: str) -> str:
        return self.cipher_suite.encrypt(message.encode()).decode()

    def decrypt(self, encrypted_message: str) -> str:
        return self.cipher_suite.decrypt(encrypted_message.encode()).decode()

    def get_config_path(self, config_name):
        return Path(f"~/.config/freerdp_gui/{config_name}.json").expanduser()

    def get_available_configs(self):
        config_dir = Path("~/.config/freerdp_gui").expanduser()
        return [f.stem for f in config_dir.glob("*.json")]

    def export_config(self):
        config_name = self.config_name_entry.get()
        if not config_name:
            messagebox.showwarning("Warning", "Please specify a config name!")
            return

        config_path = self.get_config_path(config_name)
        config_path = Path("~/.config/freerdp_gui").expanduser()
        config_path.mkdir(parents=True, exist_ok=True)

        data = {
            "hostname": self.hostname_entry.get(),
            "username": self.username_entry.get(),
            "password": self.encrypt(self.password_entry.get()),
            "dynamic_resolution": self.dynamic_res_var.get(),
            "ignore_certificate": self.cert_ignore_var.get(),
            "enable_clipboard": self.clipboard_var.get(),
            "resolution": self.resolution_entry.get() if self.res_checkbox_var.get() else "",
            "full_screen": self.fullscreen_var.get(),
            "audio_redirection": self.audio_var.get(),
            "drive_path": self.drive_entry.get() if self.drive_checkbox_var.get() else "",
            "printer_redirection": self.printer_var.get(),
            "multiple_monitors": self.multimon_var.get(),
            "use_rdg": self.rdg_enable_var.get(),
            "rdg_server": self.rdg_server_entry.get(),
            "rdg_user": self.rdg_user_entry.get(),
            "rdg_password": self.encrypt(self.rdg_password_entry.get())
        }

        config_filename = f"{config_name}.json"
        with open(config_path / config_filename, 'w') as file:
            json.dump(data, file)

        self.config_dropdown['values'] = self.get_available_configs()

    def clear_all_fields(self):
        entries_to_clear = [
            self.hostname_entry,
            self.username_entry,
            self.password_entry,
            self.resolution_entry,
            self.drive_entry,
            self.rdg_server_entry,
            self.rdg_user_entry,
            self.rdg_password_entry
        ]

        for entry in entries_to_clear:
            entry.delete(0, 'end')

        checkboxes_to_clear = [
            self.dynamic_res_var,
            self.cert_ignore_var,
            self.clipboard_var,
            self.res_checkbox_var,
            self.fullscreen_var,
            self.audio_var,
            self.drive_checkbox_var,
            self.printer_var,
            self.multimon_var,
            self.rdg_enable_var
        ]

        for checkbox in checkboxes_to_clear:
            checkbox.set(0)

    def load_config(self):
        self.clear_all_fields()
        config_name = self.config_dropdown.get()
        if not config_name:
            messagebox.showwarning("Warning", "Please select a config to load!")
            return

        config_path = self.get_config_path(config_name)

        if config_path.exists():
            with open(config_path, 'r') as file:
                data = json.load(file)
                self.hostname_entry.insert(0, data.get("hostname", ""))
                self.username_entry.insert(0, data.get("username", ""))
                decrypted_password = self.decrypt(data.get("password", ""))
                self.password_entry.insert(0, decrypted_password)

                self.dynamic_res_var.set(data.get("dynamic_resolution", 0))
                self.cert_ignore_var.set(data.get("ignore_certificate", 0))
                self.clipboard_var.set(data.get("enable_clipboard", 0))

                res = data.get("resolution", "")
                if res:
                    self.res_checkbox_var.set(1)
                    self.toggle_res_entry()
                    self.resolution_entry.insert(0, res)

                self.fullscreen_var.set(data.get("full_screen", 0))
                self.audio_var.set(data.get("audio_redirection", 0))

                drive_path = data.get("drive_path", "")
                if drive_path:
                    self.drive_checkbox_var.set(1)
                    self.toggle_drive_entry()
                    self.drive_entry.insert(0, drive_path)

                self.printer_var.set(data.get("printer_redirection", 0))
                self.multimon_var.set(data.get("multiple_monitors", 0))

                self.rdg_enable_var.set(data.get("use_rdg", 0))
                self.toggle_rdg()
                self.rdg_server_entry.insert(0, data.get("rdg_server", ""))
                self.rdg_user_entry.insert(0, data.get("rdg_user", ""))
                decrypted_rdg_password = self.decrypt(data.get("rdg_password", ""))
                self.rdg_password_entry.insert(0, decrypted_rdg_password)
        else:
            messagebox.showwarning("Warning", "Configuration file not found!")

    def delete_config(self):
        config_name = self.config_dropdown.get()
        if not config_name:
            messagebox.showwarning("Warning", "Please select a config to delete!")
            return

        config_path = self.get_config_path(config_name)
        if config_path.exists():
            config_path.unlink()
            self.config_dropdown['values'] = self.get_available_configs()
            self.config_dropdown.set('')
            messagebox.showinfo("Info", "Config deleted successfully!")
        else:
            messagebox.showwarning("Warning", "Config not found!")

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
