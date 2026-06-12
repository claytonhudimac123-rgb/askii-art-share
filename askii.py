import os
import time
import json
import subprocess
import tkinter as tk
import threading
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- CONFIGURATION ---
WEBSITE_PROJECT_DIR = r"E:\askii art gen" # <-- PASTE YOUR LOCAL FOLDER PATH HERE
ASCII_CHARS = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]

class AsciiArtApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ASCII Folder-Sync Studio")
        self.geometry("1350x900")
        self.filepath = None
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure((0, 1), weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        self.top_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.top_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        self.upload_btn = ctk.CTkButton(self.top_frame, text="📁 Upload Image", font=("Arial", 13, "bold"), command=self.upload_image)
        self.upload_btn.pack(side="left", padx=10)

        self.file_label = ctk.CTkLabel(self.top_frame, text="No file selected", font=("Arial", 12, "italic"))
        self.file_label.pack(side="left", padx=10)

        self.res_label = ctk.CTkLabel(self.top_frame, text="Width Res:", font=("Arial", 12))
        self.res_label.pack(side="left", padx=(20, 5))
        
        self.res_entry = ctk.CTkEntry(self.top_frame, width=70)
        self.res_entry.insert(0, "100")
        self.res_entry.pack(side="left", padx=5)

        self.slider_label = ctk.CTkLabel(self.top_frame, text="Text Size (6):", font=("Arial", 12))
        self.slider_label.pack(side="left", padx=(20, 5))

        self.size_slider = ctk.CTkSlider(self.top_frame, from_=2, to=20, number_of_steps=18, command=self.update_font_size)
        self.size_slider.set(6)
        self.size_slider.pack(side="left", padx=5)

        self.generate_btn = ctk.CTkButton(self.top_frame, text="⚡ Convert to ASCII", state="disabled", command=self.start_conversion)
        self.generate_btn.pack(side="right", padx=10)

        self.left_frame = ctk.CTkFrame(self.main_frame)
        self.left_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.left_frame.grid_rowconfigure(1, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)

        self.preview_box = ctk.CTkTextbox(self.left_frame, font=("Courier New", 6), wrap="none")
        self.preview_box.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.right_frame = ctk.CTkFrame(self.main_frame)
        self.right_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        self.tab_view = ctk.CTkTabview(self.right_frame)
        self.tab_view.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.tab_text = self.tab_view.add("📝 Built-in Text Editor")

        self.tab_text.grid_rowconfigure(0, weight=1)
        self.tab_text.grid_columnconfigure(0, weight=1)
        self.editor_box = ctk.CTkTextbox(self.tab_text, font=("Courier New", 6), wrap="none")
        self.editor_box.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.bottom_dock = ctk.CTkFrame(self.main_frame, height=60)
        self.bottom_dock.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        self.share_btn = ctk.CTkButton(self.bottom_dock, text="🚀 Save & Push Globally", fg_color="#2b7a78", hover_color="#174d4c", command=self.publish_to_folder)
        self.share_btn.pack(side="left", padx=15, pady=10)

        self.copy_btn = ctk.CTkButton(self.bottom_dock, text="📋 Copy Shareable Link", state="disabled", command=self.copy_to_clipboard)
        self.copy_btn.pack(side="left", padx=5, pady=10)

        self.status_lbl = ctk.CTkLabel(self.bottom_dock, text="Ready.", font=("Arial", 12), text_color="#a1a1aa")
        self.status_lbl.pack(side="left", padx=20, pady=10)
        self.current_generated_url = ""

    def update_font_size(self, value):
        size = int(value)
        self.slider_label.configure(text=f"Text Size ({size}):")
        self.preview_box.configure(font=("Courier New", size))
        self.editor_box.configure(font=("Courier New", size))

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.webp")])
        if file_path:
            self.filepath = file_path
            self.file_label.configure(text=file_path.split("/")[-1])
            self.generate_btn.configure(state="normal")

    def start_conversion(self):
        threading.Thread(target=self.process_image_live, daemon=True).start()

    def process_image_live(self):
        try:
            width = int(self.res_entry.get())
            if width < 10 or width > 700: raise ValueError
        except ValueError:
            messagebox.showwarning("Error", "Enter a width between 10 and 700!")
            return

        self.generate_btn.configure(state="disabled")
        self.preview_box.delete("1.0", tk.END)
        self.editor_box.delete("1.0", tk.END)

        img = Image.open(self.filepath)
        height = int(width * (img.height / img.width) * 0.5)
        img = img.resize((width, height)).convert("L")
        
        pixels = list(img.getdata())
        lines = []
        for r in range(height):
            row = "".join([ASCII_CHARS[pixels[r * width + c] // 24] for c in range(width)])
            lines.append(row)
            self.preview_box.insert(tk.END, row + "\n")
        
        self.editor_box.insert("1.0", "\n".join(lines))
        self.generate_btn.configure(state="normal")

    def publish_to_folder(self):
        art_content = self.editor_box.get("1.0", tk.END).strip()
        if not art_content:
            messagebox.showwarning("Empty", "Generate some artwork first!")
            return

        if not os.path.exists(WEBSITE_PROJECT_DIR):
            messagebox.showerror("Folder Error", f"Could not find website folder directory at:\n{WEBSITE_PROJECT_DIR}\nPlease verify your path configuration setup.")
            return

        self.status_lbl.configure(text="⏳ Syncing local files & pushing updates...", text_color="#3b82f6")
        threading.Thread(target=self.sync_pipeline, args=(art_content,), daemon=True).start()

    def sync_pipeline(self, content):
        import base64
        
        # 1. Create fallback separate share string link
        b64_string = base64.b64encode(content.encode('utf-8')).decode('utf-8').replace('+', '-').replace('/', '_')
        base_site = "https://askiiartshare.netlify.app/"
        self.current_generated_url = f"{base_site}#view_{b64_string}"

        art_dir = os.path.join(WEBSITE_PROJECT_DIR, "art")
        os.makedirs(art_dir, exist_ok=True)

        timestamp = int(time.time())
        filename = f"ascii_{timestamp}.txt"
        filepath = os.path.join(art_dir, filename)

        try:
            # Save the raw text artwork file
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            # Update index database manifest catalog
            manifest_path = os.path.join(art_dir, "manifest.json")
            manifest_data = []
            
            if os.path.exists(manifest_path):
                try:
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        manifest_data = json.load(f)
                except: pass

            manifest_data.append({
                "title": f"Submission #{timestamp}",
                "filename": filename
            })

            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(manifest_data, f, indent=4)

            # Run automated background Git command pushes
            subprocess.run(["git", "add", "."], cwd=WEBSITE_PROJECT_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["git", "commit", "-m", f"Auto-added ASCII artwork {timestamp}"], cwd=WEBSITE_PROJECT_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["git", "push"], cwd=WEBSITE_PROJECT_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            self.status_lbl.configure(text="✅ Saved locally & pushed to Git repository!", text_color="#10b981")
        except Exception as e:
            self.status_lbl.configure(text=f"❌ Error during file write operations.", text_color="#ef4444")
            print(e)
            
        self.copy_btn.configure(state="normal")
        self.clipboard_clear()
        self.clipboard_append(self.current_generated_url)
        self.update()

    def copy_to_clipboard(self):
        if self.current_generated_url:
            self.clipboard_clear()
            self.clipboard_append(self.current_generated_url)
            self.update()
            messagebox.showinfo("Copied!", "Standalone direct link copied!")

if __name__ == "__main__":
    app = AsciiArtApp()
    app.mainloop()