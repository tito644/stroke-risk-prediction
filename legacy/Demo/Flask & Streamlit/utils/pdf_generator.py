
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


try:
    import arabic_reshaper
    from bidi.algorithm import get_display
except Exception:
    arabic_reshaper = None
    get_display = None



AR = {
    "title": "تقرير تقييم خطر السكتة الدماغية",
    "name": "الاسم",
    "age": "العمر",
    "gender": "النوع",
    "male": "ذكر",
    "female": "أنثى",
    "risk": "الحالة",
    "prob": "النسبة",
    "threshold": "العتبة",
    "symptoms": "الأعراض",
    "yes": "نعم",
    "no": "لا",
    "ai_title": "تحليل الحالة باستخدام الذكاء الاصطناعي",
    "risk_map": {"low": "منخفضة", "medium": "متوسطة", "high": "عالية"},
}

EN = {
    "title": "Stroke Risk Assessment Report",
    "name": "Name",
    "age": "Age",
    "gender": "Gender",
    "male": "male",
    "female": "female",
    "risk": "Risk",
    "prob": "Probability",
    "threshold": "Threshold",
    "symptoms": "Symptoms",
    "yes": "Yes",
    "no": "No",
    "ai_title": "AI-based case analysis",
    "risk_map": {"low": "low", "medium": "medium", "high": "high"},
}


SYMPTOMS_EN = {
    "ألم في الصدر": "Chest Pain",
    "ضيق في التنفس": "Shortness of Breath",
    "اضطراب نبضات القلب": "Irregular Heartbeat",
    "التعب و ضعط مرتفع": "Fatigue & Weakness",
    "دوخة": "Dizziness",
    "تورم (وذمة)": "Swelling (Edema)",
    "ألم في الرقبة / العد / الكتف / الظهر": "Pain in Neck/Jaw/Shoulder/Back",
    "التعرق الزائد": "Excessive Sweating",
    "السعال المستمر": "Persistent Cough",
    "الغثيان/القيء": "Nausea/Vomiting",
    "ضعط دم مرتفع": "High Blood Pressure",
    "أرتجاع في الصدر (النساط)": "Chest Discomfort (Activity)",
    "الأيدي الباردة / القدمين": "Cold Hands/Feet",
    "الشخير/توقف التنفس أثناء النوم": "Snoring/Sleep Apnea",
    "الغلق / الشعور بالهلاك": "Anxiety/Feeling of Doom",
}


def _safe_filename(name: str) -> str:
    bad = r'<>:"/\|?*'
    out = ''.join('_' if ch in bad else ch for ch in (name or '').strip())
    out = out.replace(' ', '_')
    return out or "patient"


class PDFGenerator:
    def __init__(self, out_dir="reports", fonts_dir=None):
        
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.out_dir = os.path.join(base_dir, out_dir) if not os.path.isabs(out_dir) else out_dir
        self.fonts_dir = fonts_dir or os.path.join(base_dir, "assets", "fonts")
        os.makedirs(self.out_dir, exist_ok=True)
        self._register_fonts()

    
    def _register_fonts(self):
        ar_path = os.path.join(self.fonts_dir, "NotoNaskhArabic-Regular.ttf")
        en_path = os.path.join(self.fonts_dir, "Noto Sans Regular.ttf")

        if not os.path.exists(ar_path):
            raise FileNotFoundError(f"Arabic font not found: {ar_path}")
        if not os.path.exists(en_path):
            raise FileNotFoundError(f"English font not found: {en_path}")

        pdfmetrics.registerFont(TTFont("NotoNaskhArabic", ar_path))
        pdfmetrics.registerFont(TTFont("Noto Sans Regular", en_path))
        self.ar_font = "NotoNaskhArabic"
        self.en_font = "Noto Sans Regular"

    def _shape_ar(self, text: str) -> str:
        if not text:
            return ""
        if arabic_reshaper and get_display:
            return get_display(arabic_reshaper.reshape(text))
        return text

    
    def _draw_ltr(self, c, x, y, text, size=12):
        c.setFont(self.en_font, size)
        c.drawString(x, y, text)

    def _draw_rtl(self, c, right_x, y, text, size=12):
        c.setFont(self.ar_font, size)
        c.drawRightString(right_x, y, self._shape_ar(text))

    def _draw_kv(self, c, x_ltr, x_rtl, y, k, v, lang):
        if lang == "ar":
            self._draw_rtl(c, x_rtl, y, f"{k}: {v}", 12)
        else:
            self._draw_ltr(c, x_ltr, y, f"{k}: {v}", 12)

    
    def _wrap_lines(self, font_name, size, text, max_width):
        """
        يقسم النص لأسطر بحيث كل سطر لا يتعدى max_width
        """
        all_out_lines = []
        for raw_line in (text or "").splitlines():
            words = raw_line.split()
            if not words:
                all_out_lines.append("")
                continue

            current = words[0]
            for w in words[1:]:
                test = current + " " + w
                w_px = pdfmetrics.stringWidth(test, font_name, size)
                if w_px <= max_width:
                    current = test
                else:
                    all_out_lines.append(current)
                    current = w
            all_out_lines.append(current)
        return all_out_lines

    
    def _draw_multiline_ltr(self, c, x, y, text, size=12, line_h=16, max_width=None):
        if max_width is None:
            max_width = 10000 
        lines = self._wrap_lines(self.en_font, size, text, max_width)
        c.setFont(self.en_font, size)
        for line in lines:
            if line.strip():
                c.drawString(x, y, line)
            y -= line_h
        return y

    
    def _draw_multiline_rtl(self, c, right_x, y, text, size=12, line_h=16, max_width=None):
        if max_width is None:
            max_width = 10000
        logical_lines = self._wrap_lines(self.ar_font, size, text, max_width)
        c.setFont(self.ar_font, size)
        for line in logical_lines:
            if line.strip():
                shaped = self._shape_ar(line)
                c.drawRightString(right_x, y, shaped)
            y -= line_h
        return y

    
    def _draw_bullets_two_cols(self, c, items, lang, page_w, margin, y_start, line_h=16):
        half = (len(items) + 1) // 2
        col1 = items[:half]
        col2 = items[half:]

        col_gap = 40
        col_w = (page_w - 2 * margin - col_gap) / 2.0
        y1 = y_start
        y2 = y_start

        def draw_item_ltr(x, y, txt):
            self._draw_ltr(c, x, y, f"• {txt}", 12)

        def draw_item_rtl(right_x, y, txt):
            
            self._draw_rtl(c, right_x, y, f"• {txt}", 12)

        if lang == "ar":
            
            right_x = margin + col_w + col_gap + col_w  
            left_x_end = margin + col_w  
            for t in col2:
                draw_item_rtl(right_x, y2, t)
                y2 -= line_h
            for t in col1:
                draw_item_rtl(left_x_end, y1, t)
                y1 -= line_h
        else:
            
            left_x = margin
            right_x = margin + col_w + col_gap
            for t in col1:
                draw_item_ltr(left_x, y1, t)
                y1 -= line_h
            for t in col2:
                draw_item_ltr(right_x, y2, t)
                y2 -= line_h

        return min(y1, y2)

    def generate_report(self, patient_info, symptoms, prediction_result, language="ar"):
        lang = (language or "ar").lower()
        L = AR if lang == "ar" else EN

        safe_name = _safe_filename(patient_info.get("name", "patient"))
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_name}_{ts}.pdf"
        path = os.path.join(self.out_dir, filename)

        c = canvas.Canvas(path, pagesize=A4)
        w, h = A4
        margin = 48
        y = h - margin

        
        try:
            logos_dir = os.path.join(self.fonts_dir, "..", "logos")
            right_logo = os.path.join(logos_dir, "right_logo.png")
            left_logo  = os.path.join(logos_dir, "leftt_logo.ico")

            logo_h = 60
            logo_w = 60

            if os.path.exists(right_logo):
                c.drawImage(
                    right_logo,
                    w - margin - logo_w,
                    h - margin - logo_h / 2,
                    width=logo_w,
                    height=logo_h,
                    preserveAspectRatio=True,
                    mask="auto",
                )
            if os.path.exists(left_logo):
                c.drawImage(
                    left_logo,
                    margin,
                    h - margin - logo_h / 2,
                    width=logo_w,
                    height=logo_h,
                    preserveAspectRatio=True,
                    mask="auto",
                )
        except Exception as e:
            print("Logo draw error:", e)

        
        risk_raw = str(prediction_result.get("risk_level", "")).lower()
        risk_disp = L["risk_map"].get(risk_raw, risk_raw)
        prob = float(prediction_result.get("probability", 0.0))
        #thr = prediction_result.get("threshold", 0.5)

        center_x = w / 2
        title_y = h - margin - (60 / 2 + 8)   # 60 = logo_h
        header_y = title_y - 20

        if lang == "ar":
            c.setFont(self.ar_font, 16)
            c.drawCentredString(center_x, title_y, self._shape_ar(L["title"]))
        else:
            c.setFont(self.en_font, 16)
            c.drawCentredString(center_x, title_y, L["title"])

        if lang == "ar":
            line_txt = f"{L['risk']}: {risk_disp}    —    {L['prob']}: {prob:.2f}    )"
            c.setFont(self.ar_font, 12)
            c.drawCentredString(center_x, header_y, self._shape_ar(line_txt))
        else:
            line_txt = f"{L['risk']}: {risk_disp}    —    {L['prob']}: {prob:.2f}    )"
            c.setFont(self.en_font, 12)
            c.drawCentredString(center_x, header_y, line_txt)

        y = header_y - 26

        
        g = str(patient_info.get("gender", ""))
        if g:
            g_disp = L["male"] if g.lower().startswith("m") else L["female"]
        else:
            g_disp = ""

        self._draw_kv(c, margin, w - margin, y, L["name"], f"{patient_info.get('name','')}", lang); y -= 18
        self._draw_kv(c, margin, w - margin, y, L["age"], f"{patient_info.get('age','')}", lang); y -= 18
        self._draw_kv(c, margin, w - margin, y, L["gender"], g_disp, lang); y -= 22

        
        if lang == "ar":
            self._draw_rtl(c, w - margin, y, f"{L['symptoms']}:", 13)
        else:
            self._draw_ltr(c, margin, y, f"{L['symptoms']}:", 13)
        y -= 18

        items = []
        for ar_label, val in (symptoms or {}).items():
            is_yes = str(val).lower() in ("yes", "true", "1", "on", "نعم")
            yn_disp = L["yes"] if is_yes else L["no"]
            txt = (
                f"{ar_label}: {yn_disp}"
                if lang == "ar"
                else f"{SYMPTOMS_EN.get(ar_label, ar_label)}: {yn_disp}"
            )
            items.append(txt)

        y = self._draw_bullets_two_cols(c, items, lang, w, margin, y)

       
        y -= 28
        ai_text = (prediction_result or {}).get("ai_analysis", "") or ""
        ai_text = ai_text.strip()

        if ai_text:
            max_width = w - 2 * margin

            if lang == "ar":
                self._draw_rtl(c, w - margin, y, L["ai_title"], 13)
            else:
                self._draw_ltr(c, margin, y, L["ai_title"], 13)
            y -= 20

            if lang == "ar":
                y = self._draw_multiline_rtl(
                    c,
                    w - margin,
                    y,
                    ai_text,
                    size=11,
                    line_h=15,
                    max_width=max_width,
                )
            else:
                y = self._draw_multiline_ltr(
                    c,
                    margin,
                    y,
                    ai_text,
                    size=11,
                    line_h=15,
                    max_width=max_width,
                )

        c.showPage()
        c.save()
        return path, filename
