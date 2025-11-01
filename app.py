import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os

try:
    import ocrmypdf
except Exception as e:
    print("ocrmypdf is not available:", e)
    sys.exit(1)

class OCRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Arabic OCR Application")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input file selection
        ttk.Label(self.main_frame, text="Input PDF File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.input_path = tk.StringVar()
        ttk.Entry(self.main_frame, textvariable=self.input_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.main_frame, text="Browse", command=self.browse_input).grid(row=0, column=2, pady=5)
        
        # Output file selection
        ttk.Label(self.main_frame, text="Output PDF File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.output_path = tk.StringVar(value="output_ocr.pdf")
        ttk.Entry(self.main_frame, textvariable=self.output_path, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(self.main_frame, text="Browse", command=self.browse_output).grid(row=1, column=2, pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.main_frame, mode='indeterminate', length=400)
        self.progress.grid(row=2, column=0, columnspan=3, pady=20, padx=5, sticky=(tk.W, tk.E))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var)
        self.status_label.grid(row=3, column=0, columnspan=3, pady=5)
        
        # Run button
        self.run_button = ttk.Button(self.main_frame, text="Run OCR", command=self.run_ocr)
        self.run_button.grid(row=4, column=0, columnspan=3, pady=20)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)

    def browse_input(self):
        filename = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.input_path.set(filename)
    
    def browse_output(self):
        filename = filedialog.asksaveasfilename(
            title="Save OCR Result As",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.output_path.set(filename)
    
    def run_ocr(self):
        input_file = self.input_path.get()
        output_file = self.output_path.get()
        
        if not input_file or not output_file:
            messagebox.showerror("Error", "Please select both input and output files")
            return
        
        if not os.path.exists(input_file):
            messagebox.showerror("Error", "Input file does not exist")
            return
        
        # Disable the run button and start progress bar
        self.run_button.state(['disabled'])
        self.progress.start(10)
        self.status_var.set("Processing...")
        
        # Run OCR in a separate thread
        thread = threading.Thread(target=self._run_ocr_thread, args=(input_file, output_file))
        thread.daemon = True
        thread.start()
    
    def _run_ocr_thread(self, input_path, output_path):
        try:
            ocrmypdf.ocr(
                input_path,
                output_path,
                language="ara",
                rotate_pages=True,
                deskew=True,
                optimize=1,
                pdf_renderer="hocr",
                oversample=300,
                sidecar="output.txt",
                jobs=8,
            )
            self.root.after(0, self._ocr_complete, True)
        except Exception as exc:
            self.root.after(0, self._ocr_complete, False, str(exc))
    
    def _ocr_complete(self, success, error_message=None):
        self.progress.stop()
        self.run_button.state(['!disabled'])
        
        if success:
            self.status_var.set("OCR completed successfully!")
            messagebox.showinfo("Success", "OCR process completed successfully!")
        else:
            self.status_var.set("Error: " + error_message)
            messagebox.showerror("Error", f"Failed to run OCR:\n{error_message}")


def main():
    root = tk.Tk()
    app = OCRApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
