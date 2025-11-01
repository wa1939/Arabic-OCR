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
        
        # OCR Options frame
        options_frame = ttk.LabelFrame(self.main_frame, text="OCR Options", padding="5")
        options_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10, padx=5)
        
        # Deskew option
        self.deskew_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Deskew Pages (may increase file size)", 
                       variable=self.deskew_var).grid(row=0, column=0, sticky=tk.W, padx=5)
        
        # PDF/A option
        self.pdfa_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Create PDF/A (may increase file size)", 
                       variable=self.pdfa_var).grid(row=1, column=0, sticky=tk.W, padx=5)
        
        # Export Options frame
        export_frame = ttk.LabelFrame(self.main_frame, text="Export Options", padding="5")
        export_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10, padx=5)
        
        # Text export option
        self.text_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(export_frame, text="Export to Text file (UTF-8 with Arabic support)", 
                       variable=self.text_var).grid(row=0, column=0, sticky=tk.W, padx=5)
        
        # Word export option
        self.word_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(export_frame, text="Export to Word document", 
                       variable=self.word_var).grid(row=1, column=0, sticky=tk.W, padx=5)
        
        # Force page OCR option for better text extraction
        self.force_ocr_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(export_frame, text="Force OCR (Ensures text is properly extracted)", 
                       variable=self.force_ocr_var).grid(row=2, column=0, sticky=tk.W, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.main_frame, mode='indeterminate', length=400)
        self.progress.grid(row=4, column=0, columnspan=3, pady=20, padx=5, sticky=(tk.W, tk.E))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var)
        self.status_label.grid(row=5, column=0, columnspan=3, pady=5)
        
        # Run button
        self.run_button = ttk.Button(self.main_frame, text="Run OCR", command=self.run_ocr)
        self.run_button.grid(row=6, column=0, columnspan=3, pady=20)
        
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

        # Try to repair PDF if pikepdf is available
        try:
            import pikepdf
            try:
                temp_path = input_file + ".temp.pdf"
                with pikepdf.open(input_file) as pdf:
                    # Remove any damaged images
                    for page in pdf.pages:
                        try:
                            for name, image in page.images.items():
                                try:
                                    # Test if image can be loaded
                                    _ = image.read_bytes()
                                except Exception:
                                    # Remove damaged image
                                    del page.images[name]
                        except Exception:
                            continue
                    # Enable object stream compression for smaller file size
                    pdf.save(temp_path, object_stream_mode=pikepdf.ObjectStreamMode.generate)
                if os.path.exists(temp_path):
                    input_file = temp_path
                    self.status_var.set("PDF repaired, proceeding with OCR...")
            except Exception as e:
                self.status_var.set(f"PDF repair attempt failed: {str(e)}")
                # Repair failed; continue with original file
                pass
        except ImportError:
            # pikepdf not installed; proceed with original file
            self.status_var.set("pikepdf not available for PDF repair")

        base_output = os.path.splitext(output_file)[0]
        sidecar_path = os.path.abspath(f"{base_output}.txt") if self.text_var.get() else None

        # Primary OCR attempt
        try:
            # Progress callback to show status
            def progress_callback(progress):
                if not progress.page_count:
                    return
                self.status_var.set(f"Processing page {progress.page} of {progress.page_count}")

            # First try to process with minimal optimization
            try:
                ocrmypdf.ocr(
                    input_file,
                    output_file,
                    language="ara",
                    rotate_pages=False,
                    deskew=False,
                    optimize=0,  # Disable optimization for initial attempt
                    pdf_renderer="hocr",  # More stable than sandwich for problematic PDFs
                    output_type="pdf",
                    sidecar=sidecar_path,
                    jobs=1,  # Reduce parallel processing to avoid memory issues
                    skip_big=4,
                    force_ocr=False,  # Don't force OCR unless text isn't found
                    use_threads=False,  # Disable threading for better stability
                    remove_background=False,
                    progress_bar=progress_callback,
                    quiet=False,
                )
                
                # If successful, try to optimize the output file
                if os.path.exists(output_file):
                    temp_output = output_file + ".temp.pdf"
                    os.rename(output_file, temp_output)
                    try:
                        ocrmypdf.ocr(
                            temp_output,
                            output_file,
                            language="ara",
                            optimize=1,
                            skip_text=True,  # Don't redo OCR
                            force_ocr=False,
                            redo_ocr=False,
                            jpeg_quality=85,  # Higher quality to prevent corruption
                            progress_bar=progress_callback,
                            quiet=True,
                        )
                        try:
                            os.remove(temp_output)
                        except Exception:
                            pass
                    except Exception as opt_error:
                        # If optimization fails, keep the unoptimized version
                        os.rename(temp_output, output_file)
                        self.status_var.set("Warning: Could not optimize output file")
            except Exception as e:
                raise RuntimeError(f"OCR process failed: {str(e)}")

            # PDF/A conversion if requested
            if self.pdfa_var.get():
                temp_output = output_file + ".temp.pdf"
                os.rename(output_file, temp_output)
                ocrmypdf.ocr(
                    temp_output,
                    output_file,
                    language="ara",
                    optimize=1,
                    output_type="pdfa",
                    skip_text=True,
                    force_ocr=False,
                    redo_ocr=False,
                )
                try:
                    os.remove(temp_output)
                except Exception:
                    pass

        except Exception as exc:
            # Primary OCR failed. Try page-by-page fallback to salvage pages.
            self.status_var.set("Primary OCR failed, attempting page-by-page fallback...")
            tempdir = None
            try:
                import tempfile
                import shutil
                try:
                    import pikepdf
                except Exception:
                    pikepdf = None

                tempdir = tempfile.mkdtemp(prefix="ocr_fallback_")
                page_outputs = []
                text_parts = []

                if pikepdf is None:
                    raise RuntimeError("pikepdf is required for page-by-page fallback but not available")

                with pikepdf.open(input_file) as pdf:
                    num_pages = len(pdf.pages)
                    for i in range(num_pages):
                        self.status_var.set(f"Processing page {i+1}/{num_pages}...")
                        single_path = os.path.join(tempdir, f"page_{i+1}.pdf")
                        ocr_out = os.path.join(tempdir, f"page_{i+1}.ocr.pdf")
                        sidecar_page = None
                        try:
                            single = pikepdf.Pdf.new()
                            single.pages.append(pdf.pages[i])
                            single.save(single_path)
                            single.close()

                            if self.text_var.get():
                                sidecar_page = os.path.join(tempdir, f"page_{i+1}.txt")
                            ocrmypdf.ocr(
                                single_path,
                                ocr_out,
                                language="ara",
                                rotate_pages=False,
                                deskew=False,
                                optimize=0,
                                pdf_renderer="hocr",
                                output_type="pdf",
                                sidecar=sidecar_page,
                                jobs=1,
                                skip_big=4,
                                force_ocr=self.force_ocr_var.get(),
                                use_threads=False,
                                remove_background=False,
                                quiet=True,
                            )

                            if os.path.exists(ocr_out):
                                page_outputs.append(ocr_out)
                                if sidecar_page and os.path.exists(sidecar_page):
                                    with open(sidecar_page, 'r', encoding='utf-8', errors='ignore') as f:
                                        text_parts.append(f.read())
                        except Exception:
                            # Skip this page on failure and continue
                            continue

                # Merge successful page outputs into final PDF
                if page_outputs:
                    try:
                        merged = pikepdf.Pdf.new()
                        for p in page_outputs:
                            try:
                                with pikepdf.open(p) as doc:
                                    for pg in doc.pages:
                                        merged.pages.append(pg)
                            except Exception:
                                continue
                        merged.save(output_file)
                        merged.close()

                        # Write aggregated text sidecar
                        if self.text_var.get() and text_parts:
                            with open(sidecar_path, 'w', encoding='utf-8') as f:
                                f.write('\n\n'.join(text_parts))

                        # If Word export requested, create docx
                        if self.word_var.get() and text_parts:
                            try:
                                from docx import Document
                                doc = Document()
                                doc.add_paragraph('\n\n'.join(text_parts))
                                doc.save(f"{base_output}.docx")
                            except Exception:
                                pass
                    except Exception as e_merge:
                        raise RuntimeError(f"Failed to merge page outputs: {e_merge}")
                else:
                    raise RuntimeError("Page-by-page fallback failed: no pages could be processed")

            except Exception as fallback_exc:
                raise RuntimeError(f"Primary OCR failed: {exc}. Fallback error: {fallback_exc}")
            finally:
                try:
                    if tempdir and os.path.exists(tempdir):
                        shutil.rmtree(tempdir)
                except Exception:
                    pass


def check_dependencies():
    missing = []
    try:
        import pikepdf
    except ImportError:
        missing.append("pikepdf")
    try:
        import docx
    except ImportError:
        missing.append("python-docx")
    
    if missing:
        print("[WARNING] Some optional dependencies are missing:", ", ".join(missing))
        print("To install: pip install " + " ".join(missing))
    return True

def main():
    # Debug startup
    print("[DEBUG] main() starting")
    
    if not check_dependencies():
        return
        
    try:
        root = tk.Tk()
    except Exception as e:
        print("[ERROR] Failed to create Tk root:", e)
        return
    try:
        root.lift()
        root.attributes('-topmost', True)
        root.after(100, lambda: root.attributes('-topmost', False))
    except Exception:
        pass
    app = OCRApp(root)
    print("[DEBUG] entering mainloop")
    root.mainloop()


if __name__ == "__main__":
    main()
