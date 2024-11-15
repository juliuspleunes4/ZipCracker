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
    # Thread starten voor de zware taak
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
    log_text.see(tk.END)  # Scroll automatisch naar de laatste regel


def create_gui():
    root = TkinterDnD.Tk()  # Gebruik TkinterDnD in plaats van standaard Tk
    root.title("ZipCracker")
    root.geometry("500x400")

    global archive_label, log_text, status_label, archive_path

    # Bestand drag-and-drop
    archive_label = tk.Label(root, text="Drag and drop your archive here", relief="sunken", height=3, width=40)
    archive_label.pack(pady=10)

    # Bind drag-and-drop functionaliteit
    root.drop_target_register(DND_FILES)
    root.dnd_bind('<<Drop>>', on_drop)

    # Statuslabel
    status_label = ttk.Label(root, text="Idle", relief="groove")
    status_label.pack(pady=5, fill="x")

    # Tekstvak voor logs
    log_text = tk.Text(root, wrap="word", height=15, width=60)
    log_text.pack(pady=10)

    # Knop om te starten
    crack_button = tk.Button(
        root, text="Start Cracking",
        command=lambda: start_cracking_thread(archive_path.get())
    )
    crack_button.pack(pady=10)

    # Variabel voor archiefpad
    archive_path = tk.StringVar()

    root.mainloop()


if __name__ == "__main__":
    create_gui()
