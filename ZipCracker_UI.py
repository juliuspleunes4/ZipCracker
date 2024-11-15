import os
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
from pathlib import Path

def crack_archive(archive_path, wordlist_dir, seven_zip_path, update_status, log_attempt, callback):
    wordlist_files = list(Path(wordlist_dir).glob("*.txt"))
    if not wordlist_files:
        callback("Error", "No wordlists found in the passlists directory!")
        return

    for wordlist in wordlist_files:
        update_status(f"Trying wordlist: {wordlist.name}")
        with open(wordlist, 'r') as file:
            for line in file:
                password = line.strip()
                log_attempt(f"Attempting: {password}")
                if attempt_crack(seven_zip_path, archive_path, password):
                    callback("Success", f"Password Found: {password}")
                    return
    callback("Failure", "No password found in any wordlist.")

def attempt_crack(seven_zip_path, archive, password):
    try:
        result = subprocess.run(
            [seven_zip_path, 'x', f"-p{password}", archive, '-o"cracked"', '-y'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error: {e}")
        return False

def on_drop(event):
    archive_path.set(event.data.strip('{}'))  # Verwijder accolades
    archive_label.config(text=f"Selected: {archive_path.get()}")

def verify_7zip():
    path = r"C:\Program Files\7-Zip\7z.exe"
    if not os.path.exists(path):
        messagebox.showerror("Error", "7-Zip not installed in the default location!")
        return None
    return path

def start_cracking_thread(archive):
    if not archive or not os.path.exists(archive):
        messagebox.showerror("Error", "No archive selected or file does not exist!")
        return

    seven_zip_path = verify_7zip()
    if not seven_zip_path:
        return

    status_label.config(text="Starting...")
    threading.Thread(
        target=crack_archive,
        args=(archive, Path("passlists"), seven_zip_path, update_status, log_attempt, handle_result),
        daemon=True
    ).start()

def handle_result(status, message):
    if status == "Success":
        messagebox.showinfo("Success", message)
    elif status == "Error":
        messagebox.showerror("Error", message)
    elif status == "Failure":
        messagebox.showwarning("Failure", message)
    status_label.config(text="Idle")

def update_status(message):
    status_label.config(text=message)

def log_attempt(attempt):
    log_text.insert(tk.END, attempt + "\n")
    log_text.see(tk.END)

def create_gui():
    root = TkinterDnD.Tk()
    root.title("ZipCracker")
    root.geometry("600x500")
    root.config(bg="#2E2E2E")  # Donkere achtergrondkleur voor een moderner uiterlijk

    # Styling voor ttk widgets
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TLabel", background="#2E2E2E", foreground="#FFFFFF", font=("Arial", 10))
    style.configure("TButton", font=("Arial", 12, "bold"), padding=6, anchor="center",
                    background="#4CAF50", foreground="#FFFFFF")
    style.map("TButton", background=[("active", "#45A049")])

    global archive_label, log_text, status_label, archive_path

    # Titel label
    title_label = ttk.Label(root, text="ZipCracker", font=("Arial", 16, "bold"))
    title_label.pack(pady=(10, 5))

    # Bestand drag-and-drop label
    archive_label = ttk.Label(root, text="Drag and drop your archive here", relief="groove", padding=10, anchor="center")
    archive_label.pack(pady=(10, 5), fill="x", padx=20)
    root.drop_target_register(DND_FILES)
    root.dnd_bind('<<Drop>>', on_drop)

    # Status label
    status_label = ttk.Label(root, text="Idle", relief="sunken", padding=5)
    status_label.pack(pady=(10, 5), fill="x", padx=20)

    # Tekstvak voor logs
    log_text_frame = ttk.Frame(root)
    log_text_frame.pack(pady=(10, 5), fill="both", expand=True, padx=20)
    log_text = tk.Text(log_text_frame, wrap="word", height=15, width=60, bg="#1E1E1E", fg="#FFFFFF", insertbackground="#FFFFFF")
    log_text.pack(fill="both", expand=True)

    # Scrollbar voor het log-venster
    scrollbar = ttk.Scrollbar(log_text_frame, command=log_text.yview)
    scrollbar.pack(side="right", fill="y")
    log_text.config(yscrollcommand=scrollbar.set)

    # Start-knop
    crack_button = ttk.Button(root, text="Start Cracking", command=lambda: start_cracking_thread(archive_path.get()))
    crack_button.pack(pady=(0, 10))  # Voeg extra padding onderaan toe om de knop iets omhoog te verplaatsen

    # Variabel voor archiefpad
    archive_path = tk.StringVar()

    root.mainloop()

if __name__ == "__main__":
    create_gui()
