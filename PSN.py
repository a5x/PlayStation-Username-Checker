import os
import time
import threading
import requests
import customtkinter as ctk
from tkinter import filedialog, messagebox

# START TKINTER CODE OMG
ctk.set_appearance_mode("dark")  # color1
ctk.set_default_color_theme("blue")  # color2

WEBHOOK_URL = "YOUR WEBHOOK"

class PSNCheckerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PSN Username Checker 2.0")
        self.geometry("1080x650")
        self.minsize(800, 500)

     
        self.file_path = ctk.StringVar()
        self.safe_exit = False
        self.webhook_enabled = False
        self.recent_checks = []

      
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ui sections
        self._build_header()
        self._build_controls()
        self._build_output()
        self._build_footer()

    def _build_header(self):
        header = ctk.CTkFrame(self, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        title = ctk.CTkLabel(header, text="📘 PSN Username Checker", font=ctk.CTkFont(size=24, weight="bold"))
        title.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        appearance = ctk.CTkOptionMenu(header, values=["Light","Dark","System"], command=self._change_appearance)
        appearance.set("Dark")
        appearance.grid(row=0, column=1, padx=20, pady=10, sticky="e")

    def _build_controls(self):
        controls = ctk.CTkFrame(self)
        controls.grid(row=1, column=0, sticky="ew", padx=20, pady=5)
        controls.grid_columnconfigure((0,1,2,3), weight=1)

        # for username path
        file_lbl = ctk.CTkLabel(controls, text="Usernames File:", font=ctk.CTkFont(size=14))
        file_lbl.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        file_entry = ctk.CTkEntry(controls, textvariable=self.file_path, placeholder_text=".txt file with usernames...")
        file_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        browse = ctk.CTkButton(controls, text="📂 Browse", command=self._select_file, corner_radius=8)
        browse.grid(row=0, column=2, padx=5, pady=5)

        # Webhook discord on/off
        self.webhook_switch = ctk.CTkSwitch(controls, text="Webhook OFF", command=self._toggle_webhook)
        self.webhook_switch.grid(row=0, column=3, padx=5, pady=5)

        # Start/Stop buttons
        btn_frame = ctk.CTkFrame(controls, fg_color="transparent")
        btn_frame.grid(row=1, column=0, columnspan=4, pady=(10,0))
        btn_frame.grid_columnconfigure((0,1), weight=1)

        self.start_btn = ctk.CTkButton(btn_frame, text="Start Check ▶", command=self._start_check, fg_color="green", hover_color="#00aa00", state="disabled", corner_radius=8)
        self.start_btn.grid(row=0, column=0, padx=10, sticky="ew")
        self.stop_btn = ctk.CTkButton(btn_frame, text="Stop ⛔", command=self._stop_check, fg_color="red", hover_color="#aa0000", state="disabled", corner_radius=8)
        self.stop_btn.grid(row=0, column=1, padx=10, sticky="ew")

    def _build_output(self):
        output_frame = ctk.CTkFrame(self)
        output_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        output_frame.grid_rowconfigure(0, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)

        self.output_box = ctk.CTkTextbox(output_frame, wrap="word", font=ctk.CTkFont(size=14))
        self.output_box.grid(row=0, column=0, sticky="nsew", padx=(0,10), pady=5)

        self.progress = ctk.CTkProgressBar(output_frame)
        self.progress.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5,0))

    def _build_footer(self):
        footer = ctk.CTkFrame(self, corner_radius=0)
        footer.grid(row=3, column=0, sticky="ew", padx=20, pady=(0,10))
        footer.grid_columnconfigure(1, weight=1)

        tip = ctk.CTkLabel(footer, text=" Tips: All 3L, 4L, Barcode OG(-)(_) are taken ! ⚠️⚠️⚠️", font=ctk.CTkFont(size=12), text_color="yellow")
        tip.grid(row=0, column=0, sticky="w")

        log_btn = ctk.CTkButton(footer, text="Show Log", command=self._show_log, corner_radius=8)
        log_btn.grid(row=0, column=1, sticky="e")

        credit = ctk.CTkLabel(footer, text="© Github @a5x", font=ctk.CTkFont(size=12), text_color="gray")
        credit.grid(row=0, column=2, sticky="e", padx=10)

    
    def _change_appearance(self, choice):
        ctk.set_appearance_mode(choice.lower())

    def _select_file(self):
        file = filedialog.askopenfilename(filetypes=[("Text Files","*.txt")])
        if file:
            self.file_path.set(file)
            self.start_btn.configure(state="normal")

    def _toggle_webhook(self):
        self.webhook_enabled = not self.webhook_enabled
        self.webhook_switch.configure(text="Webhook ON" if self.webhook_enabled else "Webhook OFF")

    def _start_check(self):
        path = self.file_path.get()
        if not os.path.exists(path):
            messagebox.showerror("Error","File not found!")
            return
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            self.usernames = [u.strip() for u in f if u.strip()]
        if not self.usernames:
            messagebox.showerror("Error","No usernames in file!")
            return

        self.output_box.delete("1.0","end")
        self.progress.set(0)
        self.progress_steps = len(self.usernames)

        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.safe_exit = False

        threading.Thread(target=self._run_check, daemon=True).start()

    def _run_check(self):
        available = []
        for idx, user in enumerate(self.usernames,1):
            if self.safe_exit:
                break
            result = self._check_username(user)
            if result:
                available.append(result)
            self.progress.set(idx/self.progress_steps)
            time.sleep(0.01)

        with open("available_psn_usernames.txt","w",encoding='utf-8') as f:
            f.write("\n".join(available))
        messagebox.showinfo("Done","Finished! Saved to available_psn_usernames.txt")
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")

    def _check_username(self, username):
        headers = {
            'Accept': '*/*',
            'Sec-Fetch-Mode': 'cors',
            'sec-ch-ua-mobile': '?0',
            'Sec-Fetch-Dest': 'empty',
            'Connection': 'keep-alive',
            'Sec-Fetch-Site': 'cross-site',
            'sec-ch-ua-platform': '"Windows"',
            'Content-Type': 'application/json; charset=UTF-8',
            'Origin': 'https://id.sonyentertainmentnetwork.com',
            'Referer': 'https://id.sonyentertainmentnetwork.com/',
            'Accept-Language': 'en-US,en;q=0.9',
            'sec-ch-ua': '"Chromium";v="111", "Not(A:Brand";v="8", "Google Chrome";v="111"',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }
        payload = {'onlineId':username,'reserveIfAvailable':True}
        try:
            resp = requests.post(
                'https://accounts.api.playstation.com/api/v1/accounts/onlineIds',
                headers=headers,
                json=payload,
                timeout=10
            )
            if resp.status_code == 201:
                self.output_box.insert("end",f"VALID ✅ : {username}\n")
                self.output_box.yview("end")
                self._log(username)
                if self.webhook_enabled:
                    self._send_alert(username)
                return username
            elif resp.status_code == 400:
                self.output_box.insert("end",f"TAKEN: {username} ❌\n")
                self.output_box.yview("end")
            else:
                self.output_box.insert("end",f"ERROR⚠️⚠️⚠️ {resp.status_code}: {username}\n")
                self.output_box.yview("end")
        except Exception as e:
            self.output_box.insert("end",f"Network Error try again please⚠️ : {e}\n")
            self.output_box.yview("end")
        return None

    def _send_alert(self, username):
        embed = {
            "embeds": [
                {
                    "title": "New PSN Username ✅✅!",
                    "description": f"The PSN `{username}` is available!",
                    "color": 3066993,
                    "fields": [
                        {"name": "USERNAME AVAILABLE", "value": username, "inline": True}
                    ]
                }
            ]
        }
        try:
            requests.post(WEBHOOK_URL, json=embed)
        except:
            pass

    def _stop_check(self):
        self.safe_exit = True
        self.output_box.insert("end","STOP...\n")
        self.output_box.yview("end")

    def _log(self, user):
        self.recent_checks.append(user)
        if len(self.recent_checks) > 150:
            self.recent_checks.pop(0)

    def _show_log(self):
        log_win = ctk.CTkToplevel(self)
        log_win.title("Last Checks Log")
        log_win.geometry("400x300")
        box = ctk.CTkTextbox(log_win, font=ctk.CTkFont(size=14))
        box.pack(fill="both", expand=True, padx=10, pady=10)
        box.insert("end", "\n".join(self.recent_checks))
        box.configure(state="disabled")

if __name__ == "__main__":
    app = PSNCheckerApp()
    app.mainloop()
