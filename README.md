# OCR العربي على ويندوز (Tesseract + OCRmyPDF)

هذا المشروع يقدّم سكربت بسيط وعملي لـ **استخراج النص العربي من ملفات PDF** بدقّة عالية على نظام **Windows** بالاعتماد على:
- **Tesseract 5** مع نموذج العربية **tessdata_best** (أعلى دقّة مجانية).
- **OCRmyPDF** كغلاف ذكي يقوم بتنظيف الصور، تدوير الصفحات، تصحيح الميل، وإنتاج **PDF قابل للبحث** + ملف نصي جانبي (sidecar).

> ⚠️ ملاحظة واقعية: الوصول إلى *صفر أخطاء* في OCR غير ممكن، خصوصًا مع العربية (خطوط/جودة مسح/تشكيل). الإعدادات هنا تعطيك مزيجًا ممتازًا من **الدقّة** و**السرعة** و**حجم ملف معقول**.

---

## ✅ المخرجات
- ملف PDF قابل للبحث: `*_OCR.pdf`
- ملف نص خام موثوق: `*_OCR.txt` (مهم جدًا للسيرش/الفهرسة ولتجاوز قيود عرض RTL في بعض قارئات الـPDF).

---

## 🧩 المتطلبات (Windows)
- **Python 3.10+** (مُفضّل عبر Chocolatey).
- **Tesseract OCR** (مع لغة العربية `ara` من **tessdata_best**).
- **Ghostscript** (يعتمد عليه OCRmyPDF).
- **OCRmyPDF** (تُثبت عبر pip).
- (اختياري) **pngquant** لضغط الصور الملونة أكثر.

> سيتم تثبيت Python/Tesseract/Ghostscript وpngquant عبر **Chocolatey**، و OCRmyPDF عبر **pip**.  
> **TESSDATA_PREFIX** يجب أن يشير إلى مجلد `tessdata` الخاص بتيسراكت.

---

## ⚡️ تثبيت سريع (PowerShell - كمسؤول)
> إن لم يكن لديك Chocolatey مسبقًا، ثبّته أولًا من موقعه الرسمي. ثم نفّذ:

```powershell
# 1) ثبّت الأدوات النظامية
choco install -y python3 tesseract ghostscript pngquant

# 2) ثبّت باقة بايثون
pip install --upgrade pip
pip install -r requirements.txt

# 3) أضف نموذج العربية من tessdata_best
Invoke-WebRequest `
  https://github.com/tesseract-ocr/tessdata_best/raw/main/ara.traineddata `
  -OutFile "C:\Program Files\Tesseract-OCR\tessdata\ara.traineddata"

# 4) عرّف مسار نماذج تيسراكت (مرة واحدة)
[Environment]::SetEnvironmentVariable('TESSDATA_PREFIX', 'C:\Program Files\Tesseract-OCR\tessdata', 'Machine')
$env:TESSDATA_PREFIX='C:\Program Files\Tesseract-OCR\tessdata'

# 5) تحقق أن كل شيء تمام
tesseract --version
tesseract --list-langs     # تأكد أن "ara" موجودة
ocrmypdf --version
```

> إذا ظهرت لك مشكلة صلاحيات، افتح PowerShell **كـمسؤول**.  
> إذا لم تظهر `ara` ضمن اللغات، تأكد من أن `ara.traineddata` موجود في مسار `tessdata` الصحيح، وأن **TESSDATA_PREFIX** مضبوط.

---

## 🗂️ بنية المشروع المقترحة
```
OCR/
├─ app.py           # سكربت التشغيل
├─ requirements.txt # تبع pip
└─ README.md
```

---

## ▶️ طريقة التشغيل (بايثون)
- ضع ملفك مثلًا هنا: `C:\Users\waok\Downloads\سياسة شركة علم.pdf`
- ثم شغّل (من داخل مجلد المشروع):
```powershell
python app.py "C:\Users\waok\Downloads\سياسة شركة علم.pdf" "C:\Users\waok\Downloads\سياسة شركة علم_OCR.pdf"
```
> إذا لم تمرّر مسارًا، السكربت يستخدم قيمة افتراضية داخل `app.py`.  
> سيُنتج أيضًا ملفًا نصيًا جانبيًا بجانب الـPDF: `..._OCR.txt`.

### مثال مباشر (سطر أوامر OCRmyPDF بدون بايثون)
```powershell
ocrmypdf -l ara --jobs 8 `
  --rotate-pages --deskew --clean --remove-background `
  --optimize 3 --output-type pdf `
  --pdf-renderer hocr `
  --sidecar "C:\Users\waok\Downloads\سياسة شركة علم_OCR.txt" `
  "C:\Users\waok\Downloads\سياسة شركة علم.pdf" `
  "C:\Users\waok\Downloads\سياسة شركة علم_OCR.pdf"
```
> إن ظهرت رسالة *page already has text* وتريد إجبار الـOCR: أضف `--force-ocr`.

---

## 🧠 ماذا يفعل السكربت؟ (ملخّص الإعدادات)
- **لغة العربية**: `language="ara"` (يمكن إضافة `+eng` إذا عندك نص مختلط).
- **تحسين الصور**: تدوير تلقائي/تصحيح الميل/تنظيف الخلفية قبل الـOCR.
- **محرّك Tesseract**: LSTM-only (أدق)، وتقسيم صفحة تلقائي (PSM=3) مناسب لمعظم الوثائق.
- **إخراج PDF**: `pdf_renderer="hocr"` أنسب للـRTL، و`output_type="pdf"` لحجم أصغر من PDF/A.
- **ملف نصي جانبي**: `sidecar="*.txt"` نص خام موثوق للفهرسة/التحليل.
- **تعدد الأنوية**: `jobs` لاستغلال المعالج وتسريع المعالجة.

---

## ✍️ كود `app.py` المقترح
> مهيأ لأعلى دقّة مجانية مع حجم ملف منطقي على ويندوز.

```python
import os, sys, pathlib
import ocrmypdf

def main(input_path: str, output_path: str | None = None):
    # تأكيد مسار نماذج تيسراكت (tessdata_best)
    os.environ.setdefault("TESSDATA_PREFIX", r"C:\Program Files\Tesseract-OCR\tessdata")

    p_in = pathlib.Path(input_path)
    if output_path is None:
        output_path = str(p_in.with_name(p_in.stem + "_OCR.pdf"))
    sidecar = str(pathlib.Path(output_path).with_suffix(".txt"))

    # ملاحظة: إذا كانت صور الـPDF أصلًا 300dpi+ احذف oversample=300
    ocrmypdf.ocr(
        str(p_in),
        output_path,
        language="ara",                 # أضف +eng إذا فيه إنجليزي/أرقام
        rotate_pages=True,
        deskew=True,
        clean=True,
        remove_background=True,
        optimize=3,
        output_type="pdf",
        pdf_renderer="hocr",
        tesseract_oem=1,                # LSTM only
        tesseract_pagesegmode=3,        # تقسيم تلقائي
        oversample=300,                 # احذفها لو ملفاتك عالية الـDPI
        sidecar=sidecar,
        jobs=max(1, (os.cpu_count() or 8) - 1),
    )
    print(f"✅ Done:\nPDF : {output_path}\nTXT : {sidecar}")

if __name__ == "__main__":
    default_input = r"C:\Users\waok\Downloads\سياسة شركة علم.pdf"
    in_path = sys.argv[1] if len(sys.argv) > 1 else default_input
    out_path = sys.argv[2] if len(sys.argv) > 2 else None
    try:
        main(in_path, out_path)
    except Exception as exc:
        print("Failed to run ocrmypdf:", exc)
        sys.exit(2)
```

---

## 🛠️ ضبط الجودة/السرعة (Tesseract)
- **PSM (تقسيم الصفحة)**:  
  - `tesseract_pagesegmode=3` (تلقائي) جيد لمعظم الوثائق.  
  - `=6` ممتاز لصفحة نصية موحّدة الفقرات.  
- **OEM (المحرّك)**:  
  - `tesseract_oem=1` (LSTM) هو الأكثر دقّة عمومًا.
- **لغة إضافية**:  
  - `language="ara+eng"` إذا المحتوى مختلط؛ تجنّب إضافة لغات لا تحتاجها كي لا تنخفض الدقّة.
- **Oversample**:  
  - استخدم `oversample=300` فقط إذا الـPDF أقل من 300dpi. Otherwise احذفه لتقليل الحجم.

---

## 🧰 مشاكل شائعة وحلول سريعة
- **`WinError 2 / command not found`**: أضف مسارات Tesseract/Ghostscript إلى PATH أو أعد فتح PowerShell كمسؤول.  
- **`Tesseract couldn’t load any languages`**: تأكد من `TESSDATA_PREFIX` والملف `ara.traineddata` في مجلد `tessdata`.  
- **حجم إخراج ضخم**:  
  - استخدم `output_type="pdf"` بدل PDF/A الافتراضي.  
  - اجعل `optimize=3`.  
  - احذف `oversample` إن لم تكن بحاجة له.  
  - وجود `jbig2` غير متاح عادة على ويندوز؛ تجاهله آمن (فقط تفقد ضغط B/W).  
- **تحذير `lots of diacritics`**: تحذير معلوماتي يظهر مع العربية. حسّن جودة المصدر، وحافظ على 300dpi فعلي.  
- **RTL داخل PDF**: بعض القارئات لا تتعامل تمامًا مع العربية داخل طبقة النص. اعتمد على `*_OCR.txt` للبحث والتحليل، أو جرّب قارئًا آخر.

---

## 🧽 (اختياري) تصدير نص **بدون تشكيل**
```python
import re, io
in_txt  = r"C:\path\to\file_OCR.txt"
out_txt = r"C:\path\to\file_OCR_no_diac.txt"

with io.open(in_txt, "r", encoding="utf-8") as f:
    txt = f.read()

# إزالة الحركات العربية الشائعة
txt_no_diac = re.sub(r"[\u064B-\u065F\u0670\u06D6-\u06ED]", "", txt)

with io.open(out_txt, "w", encoding="utf-8") as f:
    f.write(txt_no_diac)

print("Saved:", out_txt)
```

---

## 🧪 اختبار سريع
```powershell
# بدّل المسار بالملف لديك
python app.py "C:\Users\...\سياسة شركة علم.pdf"
# راجع ناتج:
#   ...\سياسة شركة علم_OCR.pdf
#   ...\سياسة شركة علم_OCR.txt
```

---

## 📄 الترخيص
حرّ/استخدم كما تشاء داخل شركتك. احترم تراخيص البرامج التابعة (Tesseract, OCRmyPDF).

---

## 💬 ملاحظات
إذا رغبت في ملف Batch (.bat) يطلب منك المسار ويشغّل الإعدادات تلقائيًا، أخبرني لأضيفه لك بسرعة.
