# Arabic OCR on Windows (Tesseract + OCRmyPDF)

This repo provides a **fast, high‑accuracy, fully local** pipeline to extract **Arabic text from PDFs** on **Windows** using:
- **Tesseract 5** with the Arabic model from **tessdata_best** (highest free accuracy).
- **OCRmyPDF** as the smart wrapper that auto‑rotates, deskews, cleans pages, and produces a **searchable PDF** plus a sidecar TXT file.

> ℹ️ Reality check: *Zero* OCR errors is not realistic, especially with Arabic (fonts, scan quality, diacritics). The settings here balance **accuracy**, **speed**, and **reasonable file sizes** for long PDFs.

---

## ✅ Outputs
- Searchable PDF: `*_OCR.pdf`
- Plain text sidecar: `*_OCR.txt` — strongly recommended for search/indexing and to bypass some RTL quirks in certain PDF viewers.

---

## 🧩 Requirements (Windows)
**System (install via Chocolatey):**
- Python 3.10+
- Tesseract OCR
- Ghostscript
- (Optional) pngquant (better compression for color images)

**Python:**
- `ocrmypdf` (installed via `pip`)

> Ensure **TESSDATA_PREFIX** points to your Tesseract `tessdata` directory. You must install **Arabic model (ara)** from **tessdata_best**.

---

## ⚡️ Quick Install (PowerShell — Run as Administrator)
If you don’t have Chocolatey, install it from its official site first. Then run:

```powershell
# 1) System tools
choco install -y python3 tesseract ghostscript pngquant

# 2) Python packages
pip install --upgrade pip
pip install -r requirements.txt

# 3) Arabic model from tessdata_best
Invoke-WebRequest `
  https://github.com/tesseract-ocr/tessdata_best/raw/main/ara.traineddata `
  -OutFile "C:\Program Files\Tesseract-OCR\tessdata\ara.traineddata"

# 4) Make sure Tesseract knows where models live
[Environment]::SetEnvironmentVariable('TESSDATA_PREFIX', 'C:\Program Files\Tesseract-OCR\tessdata', 'Machine')
$env:TESSDATA_PREFIX='C:\Program Files\Tesseract-OCR\tessdata'

# 5) Sanity checks
tesseract --version
tesseract --list-langs     # "ara" should be listed
ocrmypdf --version
```

> If you see permission issues, reopen PowerShell **as Administrator**. If `ara` is missing, confirm `ara.traineddata` is in the correct `tessdata` directory and that **TESSDATA_PREFIX** is set.

---

## 🗂️ Suggested Project Layout
```
OCR/
├─ app.py           # main script
├─ requirements.txt # Python deps
└─ README.md
```

---

## ▶️ How to Run (Python script)
Place your PDF somewhere (example):
`C:\Users\waok\Downloads\ARABIC PDF PATH .pdf`

From the project folder:
```powershell
python app.py "C:\Users\waok\Downloads\ARABIC PDF PATH .pdf" "C:\Users\waok\Downloads\ARABIC PDF PATH _OCR.pdf"
```
If you omit arguments, `app.py` uses a default input path inside the script. The script also writes a sidecar TXT next to your output PDF: `..._OCR.txt`.

### Direct CLI (no Python)
```powershell
ocrmypdf -l ara --jobs 8 `
  --rotate-pages --deskew --clean --remove-background `
  --optimize 3 --output-type pdf `
  --pdf-renderer hocr `
  --sidecar "C:\Users\waok\Downloads\ARABIC PDF PATH _OCR.txt" `
  "C:\Users\waok\Downloads\ARABIC PDF PATH .pdf" `
  "C:\Users\waok\Downloads\ARABIC PDF PATH _OCR.pdf"
```
> If you see *“page already has text”* and still want to force OCR, add `--force-ocr`.

---

## 🧠 What the Script Does (Key Settings)
- **Language**: `ara` (add `+eng` if your content is mixed).
- **Preprocessing**: Auto‑rotate, deskew, and background clean **before** OCR for better accuracy.
- **Tesseract engine**: LSTM‑only (most accurate) with automatic page segmentation (PSM 3) — good default for diverse document layouts.
- **PDF rendering**: `pdf_renderer="hocr"` works better with RTL languages in many viewers.
- **Output type**: `output_type="pdf"` (smaller than PDF/A).
- **Sidecar**: `*_OCR.txt` is reliable for search/indexing and downstream NLP.
- **Parallelism**: `jobs` leverages CPU cores to speed up long PDFs.

---

## ✍️ Suggested `app.py`
> Tuned for highest free accuracy with reasonable output size on Windows.

```python
import os, sys, pathlib
import ocrmypdf

def main(input_path: str, output_path: str | None = None):
    # Ensure Tesseract models path (tessdata_best) is known
    os.environ.setdefault("TESSDATA_PREFIX", r"C:\Program Files\Tesseract-OCR\tessdata")

    p_in = pathlib.Path(input_path)
    if output_path is None:
        output_path = str(p_in.with_name(p_in.stem + "_OCR.pdf"))
    sidecar = str(pathlib.Path(output_path).with_suffix(".txt"))

    # NOTE: If your PDF is truly 300 dpi or higher, remove oversample=300
    ocrmypdf.ocr(
        str(p_in),
        output_path,
        language="ara",                 # add +eng if you have mixed Arabic/English
        rotate_pages=True,
        deskew=True,
        clean=True,
        remove_background=True,
        optimize=3,
        output_type="pdf",
        pdf_renderer="hocr",
        tesseract_oem=1,                # LSTM only
        tesseract_pagesegmode=3,        # automatic page segmentation
        oversample=300,                 # drop this if input is already >=300 dpi
        sidecar=sidecar,
        jobs=max(1, (os.cpu_count() or 8) - 1),
    )
    print(f"✅ Done:\nPDF : {output_path}\nTXT : {sidecar}")

if __name__ == "__main__":
    default_input = r"C:\Users\waok\Downloads\ARABIC PDF PATH .pdf"
    in_path = sys.argv[1] if len(sys.argv) > 1 else default_input
    out_path = sys.argv[2] if len(sys.argv) > 2 else None
    try:
        main(in_path, out_path)
    except Exception as exc:
        print("Failed to run ocrmypdf:", exc)
        sys.exit(2)
```

---

## 🔧 Quality & Speed Tuning
- **PSM (page segmentation):**
  - `tesseract_pagesegmode=3` is a strong default for varied layouts.
  - `=6` is great for uniform text blocks (paragraph pages).
- **OEM (engine):**
  - `tesseract_oem=1` (LSTM‑only) is typically the most accurate.
- **Languages:**
  - Use `ara+eng` only if needed; adding more languages can sometimes degrade accuracy.
- **Oversample:**
  - Keep `oversample=300` only when scans are below 300 dpi. Otherwise remove it to reduce output size.

---

## 🧰 Troubleshooting
- **`WinError 2` / “command not found”**: Add Tesseract and Ghostscript to your PATH or reopen PowerShell as Admin after install.
- **“Tesseract couldn’t load any languages”**: Confirm `TESSDATA_PREFIX` and that `ara.traineddata` exists in the `tessdata` folder.
- **Large output size**:
  - Prefer `output_type="pdf"` (smaller than default PDF/A).
  - Use `optimize=3`.
  - Remove `oversample` if scans are already 300+ dpi.
  - `jbig2` is commonly missing on Windows; it’s safe to ignore (only affects B/W compression).
- **Warning `lots of diacritics`**: Informational; common with Arabic. Improve source quality and keep effective dpi around 300.
- **RTL quirks in PDF viewers**: Some viewers struggle with Arabic text selection/search. Rely on the sidecar TXT or try another viewer.

---

## 🧽 (Optional) Export TXT **without diacritics**
```python
import re, io
in_txt  = r"C:\path\to\file_OCR.txt"
out_txt = r"C:\path\to\file_OCR_no_diac.txt"

with io.open(in_txt, "r", encoding="utf-8") as f:
    txt = f.read()

# Remove common Arabic diacritics
txt_no_diac = re.sub(r"[\u064B-\u065F\u0670\u06D6-\u06ED]", "", txt)

with io.open(out_txt, "w", encoding="utf-8") as f:
    f.write(txt_no_diac)

print("Saved:", out_txt)
```

---

## 🧪 Quick Test
```powershell
# Replace the path with your PDF
python app.py "C:\Users\...\ARABIC PDF PATH .pdf"
# Check outputs:
#   ...\ARABIC PDF PATH _OCR.pdf
#   ...\ARABIC PDF PATH _OCR.txt
```

---

## 📄 License
Free to use internally. Respect the upstream licenses (Tesseract, OCRmyPDF).

---

## 💬 Need a one‑click `.bat`?
I can include a Windows **Batch (.bat)** that asks for a PDF path and runs the same settings automatically (and writes the TXT next to it). Just say the word.
