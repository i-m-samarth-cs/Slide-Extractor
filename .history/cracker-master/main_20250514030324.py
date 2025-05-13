import os
import shutil
import tkinter as tk
from tkinter import messagebox, filedialog, Label
from tkinter.ttk import Progressbar, Style, Button, Entry
import threading
from slide_extractor import SlideExtractor
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


class SlideExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎞️ YouTube Slide Extractor")
        self.root.geometry("850x650")
        self.root.configure(bg="#1e1e2f")

        self.style = Style()
        self.style.theme_use("clam")
        self.style.configure("Accent.TButton",
                             font=("Helvetica", 14, "bold"),
                             padding=10,
                             background="#00b894",
                             foreground="white")
        self.style.map("Accent.TButton",
                       background=[("active", "#019875")])

        self.create_widgets()

    def create_widgets(self):
        self.center_frame = tk.Frame(self.root, bg="#1e1e2f")
        self.center_frame.pack(expand=True, padx=30, pady=30)

        # Header Label
        header = Label(self.center_frame, text="🎞️ YouTube Slide Extractor",
                       font=("Helvetica", 24, "bold"), fg="white", bg="#1e1e2f")
        header.grid(row=0, column=0, columnspan=2, pady=(10, 30))

        # URL Entry
        Label(self.center_frame, text="YouTube URL:",
              font=("Helvetica", 16), fg="white", bg="#1e1e2f").grid(row=1, column=0, sticky="e", padx=10, pady=10)
        self.url_entry = Entry(self.center_frame, width=50, font=("Helvetica", 14))
        self.url_entry.grid(row=1, column=1, padx=10, pady=10)

        # Frame Interval
        Label(self.center_frame, text="Frame Interval (seconds):",
              font=("Helvetica", 16), fg="white", bg="#1e1e2f").grid(row=2, column=0, sticky="e", padx=10, pady=10)
        self.interval_entry = Entry(self.center_frame, width=10, font=("Helvetica", 14))
        self.interval_entry.insert(0, "5")
        self.interval_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        # Similarity Threshold
        Label(self.center_frame, text="Similarity Threshold (0.0 to 1.0):",
              font=("Helvetica", 16), fg="white", bg="#1e1e2f").grid(row=3, column=0, sticky="e", padx=10, pady=10)
        self.threshold_entry = Entry(self.center_frame, width=10, font=("Helvetica", 14))
        self.threshold_entry.insert(0, "0.9")
        self.threshold_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        # Output Info
        Label(self.center_frame, text="Output Directory: slides/",
              font=("Helvetica", 14), fg="#dfe6e9", bg="#1e1e2f").grid(row=4, column=0, columnspan=2, pady=10)

        # Progress Label
        self.progress_label = Label(self.center_frame, text="Status: Ready",
                                    font=("Helvetica", 14), fg="white", bg="#1e1e2f")
        self.progress_label.grid(row=5, column=0, pady=10, sticky="e")
        self.progress_bar = Progressbar(self.center_frame, orient="horizontal", length=400, mode="indeterminate")
        self.progress_bar.grid(row=5, column=1, pady=10, padx=10)

        # Extract Button
        self.extract_button = Button(self.center_frame, text="🎬 Extract Slides", style="Accent.TButton",
                                     command=self.extract_slides)
        self.extract_button.grid(row=6, column=0, columnspan=2, pady=(30, 10))

        # PDF Button
        self.pdf_button = Button(self.center_frame, text="📄 Generate PDF", style="Accent.TButton",
                                 command=self.generate_pdf)
        self.pdf_button.grid(row=7, column=0, columnspan=2, pady=(10, 10))

    def extract_slides(self):
        url = self.url_entry.get()
        try:
            interval = int(self.interval_entry.get())
            threshold = float(self.threshold_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for interval and threshold.")
            return

        self.toggle_inputs(state="disabled")
        self.progress_label.config(text="Status: Downloading and processing video...")
        self.progress_bar.start()

        threading.Thread(target=self.start_slide_extraction, args=(url, interval, threshold), daemon=True).start()

    def start_slide_extraction(self, url, interval, threshold):
        try:
            slide_folder = "slides"
            if os.path.exists(slide_folder):
                shutil.rmtree(slide_folder)
            os.makedirs(slide_folder)

            extractor = SlideExtractor(video_url=url, interval=interval, similarity_threshold=threshold)
            success = extractor.extract_slides()
            status = "✅ Extraction Complete!" if success else "❌ Extraction Failed!"
            self.progress_label.config(text=f"Status: {status}")
        except Exception as e:
            self.progress_label.config(text=f"⚠️ Error: {str(e)}")
        finally:
            self.progress_bar.stop()
            self.toggle_inputs(state="normal")

    def toggle_inputs(self, state):
        self.url_entry.config(state=state)
        self.interval_entry.config(state=state)
        self.threshold_entry.config(state=state)
        self.extract_button.config(state=state)
        self.pdf_button.config(state=state)

    def generate_pdf(self):
        slide_folder = "slides"
        pdf_filename = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])

        if not pdf_filename:
            return

        try:
            slide_images = sorted(f for f in os.listdir(slide_folder) if f.endswith(".png"))
            if not slide_images:
                messagebox.showerror("No Slides", "No slides found. Please extract slides first.")
                return

            c = canvas.Canvas(pdf_filename, pagesize=letter)
            y = 750
            for slide in slide_images:
                slide_path = os.path.join(slide_folder, slide)
                img = Image.open(slide_path)
                img_width, img_height = img.size
                aspect_ratio = (img_height * 500) / img_width
                c.drawImage(slide_path, 50, y - aspect_ratio, width=500, height=aspect_ratio)

                y -= (aspect_ratio + 50)
                if y < 150:
                    c.showPage()
                    y = 750

            c.save()
            messagebox.showinfo("Success", f"PDF generated successfully at:\n{pdf_filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Error generating PDF: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = SlideExtractorApp(root)
    root.mainloop()
