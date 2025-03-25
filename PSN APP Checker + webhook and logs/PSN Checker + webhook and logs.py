import requests
import time
import os
import threading
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk  

# Initialiser CustomTkinter (Mode Sombre)
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")  # Thème bleu

# URL du webhook Discord
WEBHOOK_URL = "YOUR WEBHOOK"

# Fonction pour envoyer un message via Discord Webhook avec embed
def send_discord_alert(username):
    embed = {
        "embeds": [
            {
                "title": "✅ New Available PSN Username!",
                "description": f"The username `{username}` is available!",
                "color": 3066993,  # Vert
                "fields": [
                    {
                        "name": "USERNAME AVAILABLE IN 24 hours",
                        "value": username,
                        "inline": True
                    }
                ]
            }
        ]
    }
    
    # Envoyer la requête POST au webhook Discord
    response = requests.post(WEBHOOK_URL, json=embed)
    if response.status_code != 201:
        print(f"Error sending webhook: {response.status_code}, {response.text}")

# GUI Class
class PSNCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PSN Username Checker 1.0.1")
        self.root.geometry("1080x650")

        # Charger l'image de fond
        self.bg_image = Image.open("image.png")  
        self.bg_image = self.bg_image.resize((1080, 650), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        # Afficher l'image en arrière-plan
        self.bg_label = tk.Label(root, image=self.bg_photo)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)  

        # Label du fichier
        self.file_label = ctk.CTkLabel(root, text="Put your usernames files here:", font=("Arial", 16, "bold"))
        self.file_label.pack(pady=5)

        # Bouton pour sélectionner un fichier (coins carrés)
        self.file_button = ctk.CTkButton(root, text="📂 Select a file", command=self.select_file, corner_radius=0)
        self.file_button.pack(pady=5)

        # Affichage du chemin du fichier
        self.file_path = tk.StringVar()
        self.file_display = ctk.CTkLabel(root, textvariable=self.file_path, text_color="lightblue")
        self.file_display.pack()

        # Boutons Start & Stop (coins carrés)
        self.start_button = ctk.CTkButton(root, text="▶ Start Check", command=self.start_checking, state=tk.DISABLED, corner_radius=0, fg_color="green", hover_color="darkgreen")
        self.start_button.pack(pady=10)

        self.stop_button = ctk.CTkButton(root, text="⛔ Stop Check", command=self.stop_checking, state=tk.DISABLED, corner_radius=0, fg_color="red", hover_color="darkred")
        self.stop_button.pack(pady=5)

        # Barre de progression
        self.progress = ttk.Progressbar(root, length=300, mode="determinate")
        self.progress.pack(pady=10)

        # Message d'information
        self.file_label = ctk.CTkLabel(root, text="⚠️ Tips : All 3L's, 4L's, Barcode OG(-)(_) are taken !", text_color="yellow", font=("Arial", 12))
        self.file_label.pack(pady=5)

        # Zone d'affichage des résultats
        self.output_box = ctk.CTkTextbox(root, height=300, width=600, fg_color="grey", text_color="white", corner_radius=0)
        self.output_box.pack()

        # Flag pour l'arrêt sécurisé
        self.safe_exit = False

        # Flag pour activer/désactiver les notifications
        self.webhook_enabled = False

        # Liste pour garder les 150 derniers noms vérifiés
        self.recent_checks = []

        # Bouton pour activer/désactiver les notifications Webhook
        self.webhook_button = ctk.CTkButton(root, text="Discord Webhook OFF", command=self.toggle_webhook, corner_radius=0)
        self.webhook_button.pack(pady=10)

        # Bouton pour afficher les logs
        self.log_button = ctk.CTkButton(root, text="Show Log", command=self.show_log, corner_radius=0)
        self.log_button.pack(pady=5)

        # Crédits en haut à droite
        self.credit_label = ctk.CTkLabel(root, text="credit : Github @a5x", font=("Arial", 12), text_color="lightgrey")
        self.credit_label.place(x=900, y=10)  # Positionner le texte en haut à droite

    def select_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if filename:
            self.file_path.set(filename)
            self.start_button.configure(state=tk.NORMAL)

    def check_username(self, username):
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
            'Accept-Language': 'nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7',
            'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        }
        json_data = {
            'onlineId': username,
            'reserveIfAvailable': True,
        }

        try:
            response = requests.post('https://accounts.api.playstation.com/api/v1/accounts/onlineIds',
                                     headers=headers, json=json_data, timeout=10)
            if response.status_code == 201:
                self.output_box.insert(tk.END, f"✅ VALID: {username}\n")
                self.output_box.yview(tk.END)  # Défilement automatique
                self.add_to_log(username)  # Ajouter le nom validé aux logs
                # Envoi de la notification si activée
                if self.webhook_enabled:
                    send_discord_alert(username)
                return username
            elif response.status_code == 400:
                self.output_box.insert(tk.END, f"❌ TAKEN: {username}\n")
                self.output_box.yview(tk.END)  # Défilement automatique
            else:
                self.output_box.insert(tk.END, f"⚠️ ERROR {response.status_code}: {username}\n")
                self.output_box.yview(tk.END)  # Défilement automatique
        except requests.exceptions.RequestException as e:
            self.output_box.insert(tk.END, f"⚠️ Network Error: {e}\n")
            self.output_box.yview(tk.END)  # Défilement automatique

    def start_checking(self):
        file = self.file_path.get()
        if not os.path.exists(file):
            messagebox.showerror("Erreur", "File not found!")
            return

        with open(file, "r") as f:
            usernames = f.read().splitlines()

        if not usernames:
            messagebox.showerror("Erreur", "No usernames in the file!")
            return

        self.output_box.delete("1.0", tk.END)
        self.progress["maximum"] = len(usernames)
        self.progress["value"] = 0
        self.safe_exit = False

        self.start_button.configure(state=tk.DISABLED)
        self.stop_button.configure(state=tk.NORMAL)

        output_file = "available_psn_usernames.txt"
        available_usernames = []

        def run_check():
            for username in usernames:
                if self.safe_exit:
                    break  
                result = self.check_username(username)
                if result:
                    available_usernames.append(result)
                self.progress["value"] += 1
                self.root.update_idletasks()
                time.sleep(0.01)

            with open(output_file, "w") as f:
                f.write("\n".join(available_usernames) + "\n")

            messagebox.showinfo("Done", f"Finished! Available usernames saved to '{output_file}'")
            self.start_button.configure(state=tk.NORMAL)
            self.stop_button.configure(state=tk.DISABLED)

        threading.Thread(target=run_check).start()

    def stop_checking(self):
        self.safe_exit = True
        self.output_box.insert(tk.END, "🛑 Stopping process...\n")
        self.output_box.yview(tk.END)  # Défilement automatique
        self.stop_button.configure(state=tk.DISABLED)

    def toggle_webhook(self):
        # Bascule de l'état de l'envoi de notifications
        self.webhook_enabled = not self.webhook_enabled
        if self.webhook_enabled:
            self.webhook_button.configure(text="Discord Webhook ON")
        else:
            self.webhook_button.configure(text="Discord Webhook OFF")

    def add_to_log(self, username):
        # Ajouter un nom aux logs, en limitant à 150 derniers éléments
        self.recent_checks.append(username)
        if len(self.recent_checks) > 150:
            self.recent_checks.pop(0)

    def show_log(self):
        # Créer une fenêtre de logs
        log_window = tk.Toplevel(self.root)
        log_window.title("Log of Last 150 Checks")
        log_window.geometry("500x400")

        # Charger l'image de fond pour la fenêtre de log
        log_bg_image = Image.open("log_image.png")  # Remplace "image.png" par ton chemin d'image
        log_bg_image = log_bg_image.resize((500, 400), Image.Resampling.LANCZOS)  # Redimensionner l'image pour la taille de la fenêtre
        log_bg_photo = ImageTk.PhotoImage(log_bg_image)

        # Afficher l'image en arrière-plan
        log_bg_label = tk.Label(log_window, image=log_bg_photo)
        log_bg_label.place(x=0, y=0, relwidth=1, relheight=1)  # Positionner l'image en arrière-plan

        # Créer une frame avec un canvas et une scrollbar
        log_frame = tk.Frame(log_window)
        log_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        log_canvas = tk.Canvas(log_frame)
        log_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(log_frame, orient=tk.VERTICAL, command=log_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        log_canvas.configure(yscrollcommand=scrollbar.set)

        # Créer un widget Text pour afficher les logs
        log_text_frame = tk.Frame(log_canvas)
        log_text_frame.pack(fill=tk.BOTH, expand=True)

        log_text = tk.Text(log_text_frame, wrap=tk.WORD, height=15, width=50)
        log_text.pack(pady=10)

        # Afficher les derniers 150 noms
        log_text.insert(tk.END, "\n".join(self.recent_checks))
        log_text.config(state=tk.DISABLED)

        log_canvas.create_window((0, 0), window=log_text_frame, anchor="nw")

        log_text_frame.update_idletasks()
        log_canvas.config(scrollregion=log_canvas.bbox("all"))

        # Garder une référence à l'image pour qu'elle ne soit pas collectée par le garbage collector
        log_bg_label.image = log_bg_photo

# Run GUI
root = ctk.CTk()
app = PSNCheckerApp(root)
root.mainloop()
