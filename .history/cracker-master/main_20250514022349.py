import os
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter.ttk import Progressbar, Style, Button, Label, Entry, Frame
import threading
from slide_extractor import SlideExtractor
from PIL import Image, ImageTk
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class SlideExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Slide Extractor")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Set app theme colors
        self.primary_color = "#2c3e50"  # Dark blue
        self.secondary_color = "#3498db"  # Bright blue
        self.accent_color = "#e74c3c"  # Red accent
        self.bg_color = "#ecf0f1"  # Light gray
        self.text_color = "#2c3e50"  # Dark blue
        
        self.root.configure(bg=self.bg_color)
        
        # Configure custom styles
        self.setup_styles()
        
        # Create header
        self.create_header()
        
        # Create main content
        self.create_main_content()
        
        # Create footer
        self.create_footer()
        
        # Load dummy preview image
        self.load_dummy_preview()

    def setup_styles(self):
        """Configure custom styles for widgets"""
        self.style = Style()
        self.style.theme_use('clam')
        
        # Configure main button style
        self.style.configure(
            "Accent.TButton",
            font=("Arial", 14, "bold"),
            padding=12,
            background=self.secondary_color,
            foreground="white"
        )
        self.style.map(
            "Accent.TButton",
            background=[("active", self.accent_color), ("pressed", self.accent_color)]
        )
        
        # Configure secondary button style
        self.style.configure(
            "Secondary.TButton",
            font=("Arial", 13),
            padding=10,
            background="#95a5a6",
            foreground="white"
        )
        self.style.map(
            "Secondary.TButton",
            background=[("active", "#7f8c8d"), ("pressed", "#7f8c8d")]
        )
        
        # Configure label style
        self.style.configure(
            "TLabel",
            font=("Arial", 13),
            background=self.bg_color,
            foreground=self.text_color
        )
        
        # Configure heading label style
        self.style.configure(
            "Heading.TLabel",
            font=("Arial", 22, "bold"),
            background=self.primary_color,
            foreground="white",
            padding=10
        )
        
        # Configure progress bar
        self.style.configure(
            "TProgressbar",
            thickness=20,
            background=self.secondary_color
        )
        
        # Configure frame style
        self.style.configure(
            "TFrame",
            background=self.bg_color
        )

    def create_header(self):
        """Create application header"""
        header_frame = tk.Frame(self.root, bg=self.primary_color, height=70)
        header_frame.pack(fill=tk.X)
        
        # App title
        title_label = tk.Label(
            header_frame,
            text="YouTube Slide Extractor",
            font=("Arial", 22, "bold"),
            bg=self.primary_color,
            fg="white",
            pady=15
        )
        title_label.pack()

    def create_main_content(self):
        """Create the main content area"""
        # Main container with padding
        main_container = Frame(self.root, style="TFrame")
        main_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        # Form frame (left side)
        form_frame = Frame(main_container, style="TFrame")
        form_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Form title
        form_title = tk.Label(
            form_frame,
            text="Extraction Settings",
            font=("Arial", 16, "bold"),
            bg=self.bg_color,
            fg=self.text_color,
            pady=10
        )
        form_title.grid(row=0, column=0, columnspan=2, sticky="w")
        
        # YouTube URL field
        Label(form_frame, text="YouTube URL:", style="TLabel").grid(
            row=1, column=0, pady=(20, 10), padx=5, sticky="w"
        )
        
        url_frame = Frame(form_frame, style="TFrame")
        url_frame.grid(row=1, column=1, pady=(20, 10), padx=5, sticky="ew")
        
        self.url_entry = Entry(url_frame, width=40, font=("Arial", 12))
        self.url_entry.pack(fill=tk.X, ipady=5)
        
        # Frame interval field
        Label(form_frame, text="Frame Interval (seconds):", style="TLabel").grid(
            row=2, column=0, pady=15, padx=5, sticky="w"
        )
        
        interval_frame = Frame(form_frame, style="TFrame")
        interval_frame.grid(row=2, column=1, pady=15, padx=5, sticky="w")
        
        self.interval_entry = Entry(interval_frame, width=10, font=("Arial", 12))
        self.interval_entry.insert(0, "5")
        self.interval_entry.pack(ipady=5)
        
        # Similarity threshold field
        Label(form_frame, text="Similarity Threshold:", style="TLabel").grid(
            row=3, column=0, pady=15, padx=5, sticky="w"
        )
        
        threshold_frame = Frame(form_frame, style="TFrame")
        threshold_frame.grid(row=3, column=1, pady=15, padx=5, sticky="w")
        
        self.threshold_entry = Entry(threshold_frame, width=10, font=("Arial", 12))
        self.threshold_entry.insert(0, "0.9")
        self.threshold_entry.pack(ipady=5)
        
        # Output directory info
        output_info = tk.Label(
            form_frame,
            text="Output Directory: slides/",
            font=("Arial", 13, "italic"),
            bg=self.bg_color,
            fg="#7f8c8d"
        )
        output_info.grid(row=4, column=0, columnspan=2, pady=15, sticky="w")
        
        # Progress section
        progress_frame = Frame(form_frame, style="TFrame")
        progress_frame.grid(row=5, column=0, columnspan=2, pady=15, sticky="ew")
        
        self.progress_label = tk.Label(
            progress_frame,
            text="Status: Ready",
            font=("Arial", 13),
            bg=self.bg_color,
            fg=self.text_color
        )
        self.progress_label.pack(anchor="w", pady=(0, 10))
        
        self.progress_bar = Progressbar(
            progress_frame,
            orient="horizontal",
            length=400,
            mode="indeterminate",
            style="TProgressbar"
        )
        self.progress_bar.pack(fill=tk.X, ipady=5)
        
        # Buttons
        button_frame = Frame(form_frame, style="TFrame")
        button_frame.grid(row=6, column=0, columnspan=2, pady=20, sticky="ew")
        
        self.extract_button = Button(
            button_frame,
            text="Extract Slides",
            style="Accent.TButton",
            command=self.extract_slides
        )
        self.extract_button.pack(side=tk.LEFT, padx=(0, 15))
        
        self.pdf_button = Button(
            button_frame,
            text="Generate PDF",
            style="Secondary.TButton",
            command=self.generate_pdf
        )
        self.pdf_button.pack(side=tk.LEFT)
        
        # Preview frame (right side)
        self.preview_frame = tk.Frame(main_container, bg="white", bd=1, relief=tk.SOLID)
        self.preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(20, 0))
        
        preview_title = tk.Label(
            self.preview_frame,
            text="Slide Preview",
            font=("Arial", 16, "bold"),
            bg="white",
            fg=self.text_color,
            pady=10
        )
        preview_title.pack(anchor="center")
        
        self.preview_content = tk.Label(self.preview_frame, bg="white")
        self.preview_content.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)

    def create_footer(self):
        """Create application footer"""
        footer_frame = tk.Frame(self.root, bg=self.primary_color, height=40)
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        footer_text = tk.Label(
            footer_frame,
            text="© 2025 Slide Extractor by Samarth Shendre | Extract valuable slides from any YouTube video",
            font=("Arial", 10),
            bg=self.primary_color,
            fg="white",
            pady=10
        )
        footer_text.pack()

    def load_dummy_preview(self):
        """Load a dummy preview image"""
        # Create a blank gray canvas as placeholder
        placeholder = Image.new('RGB', (300, 200), '#e0e0e0')
        
        # Add some text to the placeholder
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(placeholder)
        text = "Slide Preview"
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
            
        text_width = draw.textlength(text, font=font)
        position = ((300-text_width)/2, 80)
        draw.text(position, text, fill="#7f8c8d", font=font)
        
        # Convert to PhotoImage
        self.preview_image = ImageTk.PhotoImage(placeholder)
        self.preview_content.config(image=self.preview_image)

    def extract_slides(self):
        """Start the slide extraction process"""
        url = self.url_entry.get()
        if not url:
            messagebox.showwarning("Missing Input", "Please enter a YouTube URL")
            return
            
        try:
            interval = int(self.interval_entry.get())
            threshold = float(self.threshold_entry.get())
            
            if interval <= 0:
                messagebox.showwarning("Invalid Input", "Frame interval must be positive")
                return
                
            if not 0 <= threshold <= 1:
                messagebox.showwarning("Invalid Input", "Threshold must be between 0.0 and 1.0")
                return
                
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter valid numeric values")
            return

        self.toggle_inputs(state="disabled")
        self.progress_label.config(text="Status: Downloading video...")
        self.progress_bar.start()

        threading.Thread(target=self.start_slide_extraction, args=(url, interval, threshold), daemon=True).start()

    def start_slide_extraction(self, url, interval, threshold):
        """Run the slide extraction in a separate thread"""
        try:
            extractor = SlideExtractor(video_url=url, interval=interval, similarity_threshold=threshold)
            success = extractor.extract_slides()
            
            if success:
                self.root.after(0, self.update_preview)
                status_text = "Extraction Complete!"
            else:
                status_text = "Extraction Failed!"
                
            self.root.after(0, lambda: self.progress_label.config(text=f"Status: {status_text}"))
            
        except Exception as e:
            self.root.after(0, lambda: self.progress_label.config(text=f"Error: {str(e)}"))
            
        finally:
            self.root.after(0, self.progress_bar.stop)
            self.root.after(0, lambda: self.toggle_inputs(state="normal"))

    def update_preview(self):
        """Update the preview with the first extracted slide"""
        try:
            slide_folder = "slides"
            slide_images = sorted(f for f in os.listdir(slide_folder) if f.endswith(".png"))
            
            if slide_images:
                first_slide = os.path.join(slide_folder, slide_images[0])
                img = Image.open(first_slide)
                
                # Resize to fit preview area
                width, height = img.size
                max_width = 350
                
                if width > max_width:
                    ratio = max_width / width
                    new_height = int(height * ratio)
                    img = img.resize((max_width, new_height), Image.LANCZOS)
                
                # Convert to PhotoImage
                self.preview_image = ImageTk.PhotoImage(img)
                self.preview_content.config(image=self.preview_image)
                
        except Exception as e:
            print(f"Error updating preview: {e}")

    def toggle_inputs(self, state):
        """Enable or disable input fields and buttons"""
        self.url_entry.config(state=state)
        self.interval_entry.config(state=state)
        self.threshold_entry.config(state=state)
        self.extract_button.config(state=state)

    def generate_pdf(self):
        """Generate a PDF from the extracted slides"""
        slide_folder = "slides"
        
        # Check if slides exist
        if not os.path.exists(slide_folder) or not os.listdir(slide_folder):
            messagebox.showwarning("No Slides", "No slides found. Please extract slides first.")
            return
            
        pdf_filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save PDF As"
        )

        if not pdf_filename:
            return

        try:
            # Show progress indicator
            self.progress_label.config(text="Status: Generating PDF...")
            self.progress_bar.start()
            
            # Start PDF generation in a separate thread
            threading.Thread(
                target=self.create_pdf_document,
                args=(pdf_filename, slide_folder),
                daemon=True
            ).start()
            
        except Exception as e:
            self.progress_bar.stop()
            self.progress_label.config(text="Status: Ready")
            messagebox.showerror("Error", f"Error generating PDF: {str(e)}")

    def create_pdf_document(self, pdf_filename, slide_folder):
        """Create the PDF document in a separate thread"""
        try:
            c = canvas.Canvas(pdf_filename, pagesize=letter)
            c.setFont("Helvetica", 16)

            slide_images = sorted(f for f in os.listdir(slide_folder) if f.endswith(".png"))

            y = 750
            for slide in slide_images:
                slide_path = os.path.join(slide_folder, slide)
                img = Image.open(slide_path)
                img_width, img_height = img.size
                
                # Calculate aspect ratio for display
                aspect_ratio = img_height / img_width
                display_width = 500
                display_height = display_width * aspect_ratio
                
                c.drawImage(slide_path, 50, y - display_height, width=display_width, height=display_height)

                y -= (display_height + 50)  # Add some spacing between slides
                if y < 100:
                    c.showPage()
                    y = 750

            c.save()
            
            self.root.after(0, self.progress_bar.stop)
            self.root.after(0, lambda: self.progress_label.config(text="Status: PDF Generated"))
            self.root.after(0, lambda: messagebox.showinfo(
                "Success",
                f"PDF generated successfully at:\n{pdf_filename}"
            ))
            
        except Exception as e:
            self.root.after(0, self.progress_bar.stop)
            self.root.after(0, lambda: self.progress_label.config(text="Status: Ready"))
            self.root.after(0, lambda: messagebox.showerror(
                "Error",
                f"Error generating PDF: {str(e)}"
            ))

if __name__ == "__main__":
    root = tk.Tk()
    app = SlideExtractorApp(root)
    root.mainloop()