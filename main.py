import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageOps, ImageEnhance
import threading


class XRayConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("X-Ray Image Converter")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        self.source_folder = None
        self.image_files = []
        self.preview_image_tk = None
        self.converted_preview = None

        self._create_ui()

    def _create_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(main_frame, text="X-Ray Image Converter", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)

        self.select_folder_btn = ttk.Button(control_frame, text="Select Folder", command=self.select_folder)
        self.select_folder_btn.pack(side=tk.LEFT, padx=5)

        self.convert_btn = ttk.Button(control_frame, text="Convert to X-Ray", command=self.convert_image, state=tk.DISABLED)
        self.convert_btn.pack(side=tk.LEFT, padx=5)

        self.save_btn = ttk.Button(control_frame, text="Save All Images", command=self.save_images, state=tk.DISABLED)
        self.save_btn.pack(side=tk.LEFT, padx=5)

        self.status_label = ttk.Label(main_frame, text="No folder selected", foreground="gray")
        self.status_label.pack(pady=5)

        preview_frame = ttk.LabelFrame(main_frame, text="Preview", padding="5")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.preview_label = ttk.Label(preview_frame, text="No image loaded")
        self.preview_label.pack(fill=tk.BOTH, expand=True)

    def select_folder(self):
        folder_path = filedialog.askdirectory(title="Select Image Folder")
        if folder_path:
            self.source_folder = folder_path
            self.image_files = self._get_image_files(folder_path)
            if self.image_files:
                self._update_status(f"Selected: {len(self.image_files)} images")
                self._load_first_preview()
                self.convert_btn.configure(state=tk.NORMAL)
            else:
                self._update_status("No images found in folder")
                self.convert_btn.configure(state=tk.DISABLED)

    def _get_image_files(self, folder):
        extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')
        files = []
        for f in os.listdir(folder):
            if f.lower().endswith(extensions):
                files.append(os.path.join(folder, f))
        return sorted(files)

    def _load_first_preview(self):
        if self.image_files:
            self._load_preview(self.image_files[0])

    def _load_preview(self, image_path):
        try:
            image = Image.open(image_path)
            max_width = 700
            max_height = 450
            image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            self.preview_image_tk = ImageTk.PhotoImage(image)
            self.preview_label.configure(image=self.preview_image_tk, text="")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")

    def _update_status(self, message):
        self.status_label.configure(text=message, foreground="black")

    def convert_image(self):
        if not self.image_files:
            return

        self.convert_btn.configure(state=tk.DISABLED)
        self._update_status("Converting...")

        thread = threading.Thread(target=self._convert_in_background)
        thread.start()

    def _convert_in_background(self):
        try:
            xray_preview = self._apply_xray_effect(self.image_files[0])
            self.root.after(0, self._on_conversion_success, xray_preview)
        except Exception as e:
            self.root.after(0, self._on_conversion_error, str(e))

    def _apply_xray_effect(self, image_path):
        image = Image.open(image_path)

        if image.mode != 'RGB':
            image = image.convert('RGB')

        gray = ImageOps.grayscale(image)
        inverted = ImageOps.invert(gray)

        enhancer = ImageEnhance.Contrast(inverted)
        inverted = enhancer.enhance(2.0)

        enhancer = ImageEnhance.Brightness(inverted)
        inverted = enhancer.enhance(1.2)

        return inverted

    def _on_conversion_success(self, xray_preview):
        self.converted_preview = xray_preview
        self._show_preview(xray_preview)
        self._update_status(f"Preview ready - {len(self.image_files)} images to save")
        self.convert_btn.configure(state=tk.NORMAL)
        self.save_btn.configure(state=tk.NORMAL)

    def _show_preview(self, image):
        max_width = 700
        max_height = 450
        display_image = image.copy()
        display_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        self.preview_image_tk = ImageTk.PhotoImage(display_image)
        self.preview_label.configure(image=self.preview_image_tk, text="")

    def save_images(self):
        if not self.image_files:
            return

        save_folder = filedialog.askdirectory(title="Select Save Folder")
        if not save_folder:
            return

        self.save_btn.configure(state=tk.DISABLED)
        self._update_status("Saving...")

        thread = threading.Thread(target=self._save_all_in_background, args=(save_folder,))
        thread.start()

    def _save_all_in_background(self, save_folder):
        try:
            saved_count = 0
            for image_path in self.image_files:
                xray_image = self._apply_xray_effect(image_path)
                base_name = os.path.splitext(os.path.basename(image_path))[0]
                output_path = os.path.join(save_folder, f"{base_name}_xray.png")
                xray_image.save(output_path, "PNG")
                saved_count += 1

            self.root.after(0, self._on_save_success, saved_count, save_folder)
        except Exception as e:
            self.root.after(0, self._on_save_error, str(e))

    def _on_save_success(self, count, save_folder):
        self._update_status(f"Saved {count} images")
        self.save_btn.configure(state=tk.NORMAL)
        messagebox.showinfo("Success", f"Saved {count} images to:\n{save_folder}")

    def _on_save_error(self, error_message):
        self._update_status("Save failed")
        self.save_btn.configure(state=tk.NORMAL)
        messagebox.showerror("Error", f"Failed to save images:\n{error_message}")

    def _on_conversion_error(self, error_message):
        self._update_status("Conversion failed")
        self.convert_btn.configure(state=tk.NORMAL)
        messagebox.showerror("Error", f"Failed to convert image:\n{error_message}")


def main():
    root = tk.Tk()
    app = XRayConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()