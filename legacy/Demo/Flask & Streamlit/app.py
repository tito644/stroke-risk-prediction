import os
import requests
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS

try:
    from dotenv import load_dotenv

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ENV_PATH = os.path.join(BASE_DIR, ".env")

    print("DEBUG BASE_DIR:", BASE_DIR)
    print("DEBUG ENV_PATH:", ENV_PATH)
    print("DEBUG .env exists?:", os.path.exists(ENV_PATH))

    load_dotenv(dotenv_path=ENV_PATH)

    print("DEBUG GROQ_API_KEY after load:", repr(os.getenv("GROQ_API_KEY")))
except Exception as e:
    print("DEBUG load_dotenv error:", e)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE = "https://api.groq.com/openai/v1"
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")

FLASK_SECRET = os.getenv("FLASK_SECRET", "dev-secret")

USE_GROQ = bool(GROQ_API_KEY)
if USE_GROQ:
    print("Using Groq LLM provider:", GROQ_BASE, "model:", GROQ_MODEL)
else:
    print("No GROQ_API_KEY configured. AI analysis will be disabled.")

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.config["SECRET_KEY"] = FLASK_SECRET
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
CORS(app)

from utils.model_handler import ModelHandler
from utils.pdf_generator import PDFGenerator
from utils.language import TRANSLATIONS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# NEW regression model path
MODEL_PATH = os.path.join(BASE_DIR, "models", "stroke_regression_model.joblib")

model_handler = ModelHandler(MODEL_PATH)
pdf_gen = PDFGenerator(out_dir=os.path.join(BASE_DIR, "reports"))

# Keep Arabic labels exactly as used by the UI where possible
SYMPTOMS_AR = [
    "ألم في الصدر",
    "ضيق في التنفس",
    "اضطراب نبضات القلب",
    "التعب و ضعط مرتفع",
    "دوخة",
    "تورم (وذمة)",
    "ألم في الرقبة / الكتف / الظهر",
    "التعرق الزائد",
    "السعال المستمر",
    "الغثيان/القيء",
    "ضعط دم مرتفع",
    "أرتجاع في الصدر",
    "الأيدي الباردة / القدمين",
    "الشخير/توقف التنفس أثناء النوم",
    "القلق / الشعور بالهلاك",
]


def _normalize_threshold_display(threshold):
    """
    UI may send threshold as:
    - 0.5  => means 50%
    - 50   => means 50%
    This helper normalizes it for display only.
    """
    try:
        threshold = float(threshold)
    except Exception:
        threshold = 0.5

    if 0 <= threshold <= 1:
        return threshold * 100.0
    return threshold


def generate_ai_analysis(patient_info, symptoms, prediction_result, language="ar"):
    """
    Generate a patient-friendly explanation based on regression output.
    The model now predicts Stroke Risk (%) directly.
    """
    if not USE_GROQ:
        return (
            "خدمة التحليل بالذكاء الاصطناعي غير مفعّلة (لا يوجد GROQ_API_KEY على الخادم)."
            if language == "ar"
            else "AI analysis is disabled because GROQ_API_KEY is not configured on the server."
        )

    lang = (language or "ar").lower()

    positive_symptoms = []
    for label, val in (symptoms or {}).items():
        if str(val).strip().lower() in ("yes", "true", "1", "on", "نعم"):
            positive_symptoms.append(label)

    risk_level = prediction_result.get("risk_level", "")
    risk_percent = float(prediction_result.get("probability", 0.0))
    threshold = _normalize_threshold_display(prediction_result.get("threshold", 50))

    at_risk = "نعم" if risk_percent >= threshold and lang == "ar" else "Yes" if risk_percent >= threshold else "No"
    if lang == "ar":
        system_msg = {
            "role": "system",
            "content": (
                "أنت مساعد طبي افتراضي يتحدث العربية. اشرح نتيجة تقييم خطر السكتة الدماغية "
                "بأسلوب مبسط للمريض اعتمادًا على العمر والنوع والأعراض ونسبة الخطر ومستوى الخطر. "
                "لا تعطي تشخيصًا أكيدًا ولا خطة علاج، فقط توعية عامة. "
                "اشرح النتيجة بشكل واضح ومطمئن وغير مرعب. "
                "اختتم الرسالة بجملة واضحة أن هذا التقرير لا يغني عن زيارة الطبيب أو الطوارئ عند الحاجة."
            ),
        }

        lines = [
            f"العمر: {patient_info.get('age', '')}",
            f"النوع: {patient_info.get('gender', '')}",
            f"نسبة الخطر المتوقعة من النموذج: {risk_percent:.2f}%",
            f"مستوى الخطر: {risk_level}",
            f"هل الحالة عند أو فوق العتبة؟: {at_risk}",
            f"العتبة المستخدمة للتصنيف: {threshold:.2f}%",
            "",
            "الأعراض التي تم اختيار (نعم) لها:",
        ]

        if positive_symptoms:
            for s in positive_symptoms:
                lines.append(f"- {s}")
        else:
            lines.append("- لا توجد أعراض رئيسية مسجلة")

        lines.append(
            "\nاكتب من 3 إلى 5 جمل تشرح معنى هذه النسبة، "
            "وما العوامل التي قد تكون رفعت الخطر، "
            "واذكر أن هذا تقييم مبدئي بالذكاء الاصطناعي وليس تشخيصًا طبيًا نهائيًا."
        )
        user_msg = {"role": "user", "content": "\n".join(lines)}

    else:
        system_msg = {
            "role": "system",
            "content": (
                "You are a virtual clinical assistant. Explain the stroke risk result "
                "in simple patient-friendly English using age, gender, symptoms, predicted risk percentage, "
                "and risk level. Do NOT give a definite diagnosis or treatment plan, only general guidance. "
                "Be calm, clear, and non-alarming. "
                "End with a clear disclaimer that this is not a medical diagnosis and that "
                "the patient should see a doctor or emergency department if concerned."
            ),
        }

        lines = [
            f"Age: {patient_info.get('age', '')}",
            f"Gender: {patient_info.get('gender', '')}",
            f"Predicted stroke risk: {risk_percent:.2f}%",
            f"Risk level: {risk_level}",
            f"At or above threshold?: {at_risk}",
            f"Threshold used for classification: {threshold:.2f}%",
            "",
            "Positive symptoms (answered Yes):",
        ]

        if positive_symptoms:
            for s in positive_symptoms:
                lines.append(f"- {s}")
        else:
            lines.append("- No major symptoms reported")

        lines.append(
            "\nWrite a 3–5 sentence explanation of what this predicted risk may mean, "
            "which factors may have increased the risk, "
            "and end with a reminder that this is not a medical diagnosis."
        )
        user_msg = {"role": "user", "content": "\n".join(lines)}

    payload = {
        "model": GROQ_MODEL,
        "messages": [system_msg, user_msg],
        "temperature": 0.2,
        "max_tokens": 500,
    }
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(
            f"{GROQ_BASE}/chat/completions",
            json=payload,
            headers=headers,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        choice = data["choices"][0]
        msg = choice.get("message", {})
        text = (msg.get("content") or "").strip()

        return text or (
            "لم يتم استلام نص من نموذج الذكاء الاصطناعي."
            if lang == "ar"
            else "No text was returned from the AI model."
        )
    except Exception as e:
        print("AI analysis error:", e)
        return (
            f"حدث خطأ أثناء الاتصال بنموذج الذكاء الاصطناعي: {e}"
            if lang == "ar"
            else f"An error occurred while contacting the AI model: {e}"
        )


@app.route("/")
def index():
    return render_template(
        "index.html",
        translations=TRANSLATIONS,
        symptoms=SYMPTOMS_AR,
    )


@app.route("/api/predict", methods=["POST"])
def predict():
    """
    Regression prediction endpoint.
    The model predicts Stroke Risk (%) directly.
    Then we derive:
    - prediction: 0 or 1
    - at_risk: bool
    - risk_level: low / medium / high
    """
    try:
        data = request.get_json(force=True)

        patient_info = {
            "name": data.get("name", ""),
            "age": int(data.get("age", 0)),
            "gender": data.get("gender", ""),
        }

        symptoms = data.get("symptoms", {}) or {}
        threshold = float(data.get("threshold", 0.5))

        result = model_handler.predict(
            age=patient_info["age"],
            symptoms=symptoms,
            threshold=threshold,
        )

        return jsonify(
            {
                "success": True,
                "prediction": result["prediction"],       # 0 / 1
                "at_risk": result["at_risk"],             # True / False
                "probability": result["probability"],     # risk % for compatibility
                "risk_percent": result["risk_percent"],   # explicit name
                "risk_level": result["risk_level"],
                "threshold": result["threshold"],         # normalized threshold in %
            }
        )

    except Exception as e:
        print("predict endpoint error:", e)
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/ai-analysis", methods=["POST"])
def ai_analysis():
    """
    AI explanation endpoint.
    Takes patient data + regression prediction output and returns friendly text.
    """
    try:
        data = request.get_json(force=True)

        patient = {
            "name": data.get("name", ""),
            "age": data.get("age", ""),
            "gender": data.get("gender", ""),
        }

        symptoms = data.get("symptoms", {}) or {}

        pred = {
            "risk_level": data.get("risk_level", ""),
            "probability": data.get("probability", 0),
            "threshold": data.get("threshold", 50),
            "prediction": data.get("prediction", 0),
            "at_risk": data.get("at_risk", False),
        }

        lang = data.get("language", "ar")

        analysis = generate_ai_analysis(patient, symptoms, pred, language=lang)
        return jsonify({"success": True, "analysis": analysis})

    except Exception as e:
        print("ai-analysis endpoint error:", e)
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/export-pdf", methods=["POST"])
def export_pdf():
    """
    Generate PDF report.
    We regenerate the AI analysis on the server to ensure consistency.
    """
    try:
        data = request.get_json(force=True)

        patient = {
            "name": data.get("name", ""),
            "age": data.get("age", ""),
            "gender": data.get("gender", ""),
        }

        symptoms = data.get("symptoms", {}) or {}

        pred = {
            "risk_level": data.get("risk_level", ""),
            "probability": data.get("probability", 0),
            "threshold": data.get("threshold", 50),
            "prediction": data.get("prediction", 0),
            "at_risk": data.get("at_risk", False),
        }

        lang = data.get("language", "ar")

        pred["ai_analysis"] = generate_ai_analysis(patient, symptoms, pred, language=lang)

        pdf_path, suggested_name = pdf_gen.generate_report(
            patient_info=patient,
            symptoms=symptoms,
            prediction_result=pred,
            language=lang,
        )

        return send_file(
            pdf_path,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=suggested_name,
        )

    except Exception as e:
        print("export-pdf endpoint error:", e)
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/translations/<lang>")
def get_translations(lang):
    return jsonify(TRANSLATIONS.get(lang, TRANSLATIONS["ar"]))


@app.errorhandler(404)
def not_found(e):
    return "404 - Not Found", 404


@app.errorhandler(500)
def server_error(e):
    return "500 - Server Error", 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)