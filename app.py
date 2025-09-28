import sys
try:
    import ocrmypdf
except Exception as e:
    print("ocrmypdf is not available:", e)
    sys.exit(1)


def main(input_path: str, output_path: str = "output_ocr.pdf"):
    """Run OCR on a PDF using ocrmypdf with sensible defaults.

    Inputs:
      - input_path: path to the input PDF file
      - output_path: path for the OCRed PDF output
    """
    # ensure the input path string is handled correctly on Windows
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


if __name__ == "__main__":
    # default input file — use a raw string or escaped backslashes
    default_input = r"C:\Users\path.pdf"
    in_path = sys.argv[1] if len(sys.argv) > 1 else default_input
    out_path = sys.argv[2] if len(sys.argv) > 2 else "output_ocr.pdf"
    try:
        main(in_path, out_path)
    except Exception as exc:
        print("Failed to run ocrmypdf:", exc)
        sys.exit(2)
