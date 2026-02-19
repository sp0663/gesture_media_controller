import tkinter as tk
from tkinter import messagebox
import os
import subprocess
import sys
import threading

class GestureControllerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gesture Media Controller")
        self.root.geometry("450x450")
        self.root.configure(padx=20, pady=20)
        
        self.controller_process = None

        # --- HEADER ---
        tk.Label(root, text="HCI Media Controller", font=("Arial", 16, "bold")).pack(pady=(0, 5))
        tk.Label(root, text="NVIDIA Jetson Nano Edition", font=("Arial", 10, "italic"), fg="gray").pack(pady=(0, 20))

        # --- MAIN CONTROLLER SECTION ---
        self.status_var = tk.StringVar(value="Status: INACTIVE")
        self.status_label = tk.Label(root, textvariable=self.status_var, font=("Arial", 12, "bold"), fg="red")
        self.status_label.pack(pady=(0, 10))

        self.start_btn = tk.Button(root, text="Launch Controller", width=25, height=2, 
                                   bg="#4CAF50", fg="white", font=("Arial", 10, "bold"),
                                   command=self.toggle_controller)
        self.start_btn.pack(pady=5)

        tk.Frame(root, height=2, bd=1, relief="sunken").pack(fill="x", pady=20)

        # --- CUSTOM GESTURE SECTION ---
        tk.Label(root, text="Custom Gesture ML", font=("Arial", 12, "bold")).pack(pady=(0, 5))

        # Action Mapping Dropdown
        tk.Label(root, text="Map Custom Gesture To:").pack()
        
        self.mapping_var = tk.StringVar()
        self.options = {
            "Play/Pause": "play_pause",
            "Mute": "mute",
            "Full Screen": "full_screen",
            "Next Track": "move_next",
            "Previous Track": "move_prev",
            "Volume Up": "volume_up",
            "Volume Down": "volume_down"
        }
        
        # Load saved mapping if it exists
        if os.path.exists("custom_mapping.txt"):
            with open("custom_mapping.txt", "r") as f:
                saved_val = f.read().strip()
                for k, v in self.options.items():
                    if v == saved_val:
                        self.mapping_var.set(k)
        if not self.mapping_var.get():
            self.mapping_var.set("Play/Pause")

        self.dropdown = tk.OptionMenu(root, self.mapping_var, *self.options.keys(), command=self.save_mapping)
        self.dropdown.pack(pady=(0, 15))

        self.train_btn = tk.Button(root, text="Train New Gesture", width=25, 
                                   bg="#2196F3", fg="white", font=("Arial", 10),
                                   command=self.train_gesture)
        self.train_btn.pack(pady=5)

        self.delete_btn = tk.Button(root, text="Delete Custom Gesture", width=25, 
                                    bg="#f44336", fg="white", font=("Arial", 10),
                                    command=self.delete_gesture)
        self.delete_btn.pack(pady=5)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def save_mapping(self, selected_label):
        vlc_command = self.options[selected_label]
        with open("custom_mapping.txt", "w") as f:
            f.write(vlc_command)
        print(f"Custom mapping saved: {vlc_command}")

    def toggle_controller(self):
        if self.controller_process is None or self.controller_process.poll() is not None:
            # Ensure mapping file exists before launching
            if not os.path.exists("custom_mapping.txt"):
                self.save_mapping(self.mapping_var.get())
                
            print("Launching main.py...")
            self.controller_process = subprocess.Popen([sys.executable, "main.py"])
            self.status_var.set("Status: RUNNING")
            self.status_label.config(fg="green")
            self.start_btn.config(text="Stop Controller", bg="#FF9800")
            self.train_btn.config(state="disabled") 
        else:
            print("Terminating main.py...")
            self.controller_process.terminate()
            self.controller_process = None
            self.status_var.set("Status: INACTIVE")
            self.status_label.config(fg="red")
            self.start_btn.config(text="Launch Controller", bg="#4CAF50")
            self.train_btn.config(state="normal")

    def train_gesture(self):
        messagebox.showinfo("Train Gesture", "Opening data collection script. Please follow the terminal prompts.")
        
        def run_training_pipeline():
            self.train_btn.config(state="disabled") 
            try:
                subprocess.run([sys.executable, "collect_gesture_data.py"])
                subprocess.run([sys.executable, "train_model.py"])
                self.root.after(0, lambda: messagebox.showinfo("Success", "Custom gesture model updated successfully!"))
            except Exception as e:
                print(f"Error during training: {e}")
            finally:
                self.root.after(0, lambda: self.train_btn.config(state="normal"))

        threading.Thread(target=run_training_pipeline, daemon=True).start()

    def delete_gesture(self):
        files_to_delete = ["gesture_model.pkl", "gesture_data.csv"]
        deleted_any = False
        for file in files_to_delete:
            if os.path.exists(file):
                os.remove(file)
                deleted_any = True
        if deleted_any: messagebox.showinfo("Success", "Custom gesture data and model deleted.")
        else: messagebox.showwarning("Not Found", "No custom gesture model found to delete.")

    def on_closing(self):
        if self.controller_process is not None and self.controller_process.poll() is None:
            self.controller_process.terminate()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = GestureControllerUI(root)
    root.mainloop()