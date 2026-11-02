import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import shutil
import threading

# Default Extension Categories
DEFAULT_CATEGORIES = {
    "Programming": [".py", ".java", ".cpp", ".cs", ".js", ".html", ".css", ".ipynb", ".php", ".rb"],
    "Lab Reports & Docs": [".pdf", ".docx", ".doc", ".txt", ".odt", ".tex", ".rtf"],
    "Presentations": [".pptx", ".ppt", ".key"],
    "Spreadsheets & Data": [".csv", ".xlsx", ".xls", ".json", ".xml"],
    "Images & Diagrams": [".png", ".jpg", ".jpeg", ".svg", ".gif", ".webp", ".bmp"],
    "Archives": [".zip", ".rar", ".tar", ".gz", ".7z"],
}

class FileOrganizerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart File Organizer")
        self.geometry("620x550")
        self.minsize(580, 500)
        
        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        self.source_dir = Path.home() / "Downloads"
        self.dest_dir = Path.home() / "Organized_Files"

        self._create_widgets()

    def _create_widgets(self):
        # Header Frame
        header_frame = ttk.Frame(self, padding=15)
        header_frame.pack(fill=tk.X)
        
        title_label = ttk.Label(header_frame, text="📂 Smart File Organizer", font=("Helvetica", 16, "bold"))
        title_label.pack(anchor=tk.W)
        subtitle_label = ttk.Label(header_frame, text="Automatically organize files by categories using Python", font=("Helvetica", 10))
        subtitle_label.pack(anchor=tk.W, pady=(2, 0))

        # Path Configuration Frame
        path_frame = ttk.LabelFrame(self, text=" Directory Selection ", padding=15)
        path_frame.pack(fill=tk.X, padx=15, pady=5)

        # Source Path
        ttk.Label(path_frame, text="Source Directory (Files to organize):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.source_entry = ttk.Entry(path_frame)
        self.source_entry.insert(0, str(self.source_dir))
        self.source_entry.grid(row=1, column=0, sticky=tk.EW, padx=(0, 5), pady=(0, 10))
        
        browse_src_btn = ttk.Button(path_frame, text="Browse...", command=self._browse_source)
        browse_src_btn.grid(row=1, column=1, pady=(0, 10))

        # Destination Path
        ttk.Label(path_frame, text="Destination Directory (Target folder):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.dest_entry = ttk.Entry(path_frame)
        self.dest_entry.insert(0, str(self.dest_dir))
        self.dest_entry.grid(row=3, column=0, sticky=tk.EW, padx=(0, 5))
        
        browse_dest_btn = ttk.Button(path_frame, text="Browse...", command=self._browse_dest)
        browse_dest_btn.grid(row=3, column=1)

        path_frame.columnconfigure(0, weight=1)

        # Progress / Output Log Area
        log_frame = ttk.LabelFrame(self, text=" Activity Log ", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        self.log_text = tk.Text(log_frame, state=tk.DISABLED, font=("Consolas", 9), wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)

        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Action Buttons Frame
        btn_frame = ttk.Frame(self, padding=10)
        btn_frame.pack(fill=tk.X, padx=15, pady=(0, 10))

        self.organize_btn = ttk.Button(btn_frame, text="🚀 Start Organizing", command=self._start_organizing_thread)
        self.organize_btn.pack(side=tk.RIGHT)

    def _browse_source(self):
        selected = filedialog.askdirectory(initialdir=self.source_entry.get())
        if selected:
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, selected)

    def _browse_dest(self):
        selected = filedialog.askdirectory(initialdir=self.dest_entry.get())
        if selected:
            self.dest_entry.delete(0, tk.END)
            self.dest_entry.insert(0, selected)

    def log(self, message):
        """Append log message into the GUI text area thread-safely."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _start_organizing_thread(self):
        """Runs organization in a separate thread to keep the GUI responsive."""
        src_path = Path(self.source_entry.get().strip())
        dest_path = Path(self.dest_entry.get().strip())

        if not src_path.exists():
            messagebox.showerror("Error", f"Source directory does not exist:\n{src_path}")
            return

        self.organize_btn.config(state=tk.DISABLED)
        threading.Thread(target=self._run_organizer, args=(src_path, dest_path), daemon=True).start()

    def _run_organizer(self, source_dir, dest_dir):
        self.log(f"--- Starting File Organization ---")
        self.log(f"Source: {source_dir}")
        self.log(f"Destination: {dest_dir}\n")

        moved_count = 0

        try:
            for file_path in source_dir.iterdir():
                if file_path.is_file():
                    ext = file_path.suffix.lower()
                    moved = False

                    for category, extensions in DEFAULT_CATEGORIES.items():
                        if ext in extensions:
                            target_folder = dest_dir / category
                            target_folder.mkdir(parents=True, exist_ok=True)
                            
                            target_path = self._get_unique_path(target_folder, file_path)
                            shutil.move(str(file_path), str(target_path))
                            
                            self.log(f" Moved: {file_path.name}  ➔  {category}/")
                            moved = True
                            moved_count += 1
                            break

                    if not moved:
                        other_folder = dest_dir / "Others"
                        other_folder.mkdir(parents=True, exist_ok=True)
                        
                        target_path = self._get_unique_path(other_folder, file_path)
                        shutil.move(str(file_path), str(target_path))
                        
                        self.log(f" Moved: {file_path.name}  ➔  Others/")
                        moved_count += 1

            self.log(f"\n Done! Successfully organized {moved_count} file(s).")
            messagebox.showinfo("Success", f"Finished organizing {moved_count} files!")

        except Exception as e:
            self.log(f"\n Error encountered: {str(e)}")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")

        finally:
            self.organize_btn.config(state=tk.NORMAL)

    @staticmethod
    def _get_unique_path(folder: Path, file_path: Path) -> Path:
        """Avoid overwriting existing files with duplicate names."""
        target = folder / file_path.name
        counter = 1
        while target.exists():
            target = folder / f"{file_path.stem}_{counter}{file_path.suffix}"
            counter += 1
        return target


if __name__ == "__main__":
    app = FileOrganizerApp()
    app.mainloop()