# streamlit_app.py

import os
from datetime import datetime
import base64

import streamlit as st
import streamlit.components.v1 as components

from utils.model_handler import ModelHandler
from utils.pdf_generator import PDFGenerator
from utils.language import TRANSLATIONS

# ========= إعداد أساسي =========
st.set_page_config(
    page_title="Stroke Risk Assistant",
    page_icon="🧠",
    layout="wide",
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "stroke_model.joblib")


SYMPTOMS_AR = [
    "ألم في الصدر", "ضيق في التنفس", "اضطراب نبضات القلب", "التعب و ضعط مرتفع", "دوخة",
    "تورم (وذمة)", "ألم في الرقبة / العد / الكتف / الظهر", "التعرق الزائد", "السعال المستمر",
    "الغثيان/القيء", "ضعط دم مرتفع", "أرتجاع في الصدر (النساط)", "الأيدي الباردة / القدمين",
    "الشخير/توقف التنفس أثناء النوم", "الغلق / الشعور بالهلاك",
]

SYMPTOMS_MAP_EN = {
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
    "الغلق / الشعور بالهلاك": "Anxiety/Feeling of Doom"
}


THEMES = {
    "slate": {
        "primary": "#0ea5e9",
        "primary_hover": "#0284c7",
        "bg": "#020617",
        "card": "#0f172a",
        "fg": "#e5e7eb",
        "muted": "#64748b",
        "border": "#334155",
        "success": "#10b981",
        "danger": "#ef4444",
        "name_ar": "أزرق سماوي",
        "name_en": "Sky Blue"
    },
    "teal": {
        "primary": "#14b8a6",
        "primary_hover": "#0d9488",
        "bg": "#020617",
        "card": "#0f172a",
        "fg": "#e5e7eb",
        "muted": "#94a3b8",
        "border": "#334155",
        "success": "#10b981",
        "danger": "#ef4444",
        "name_ar": "تيل",
        "name_en": "Teal"
    },
    "rose": {
        "primary": "#e11d48",
        "primary_hover": "#be123c",
        "bg": "#020617",
        "card": "#111827",
        "fg": "#e5e7eb",
        "muted": "#9f1239",
        "border": "#4b5563",
        "success": "#10b981",
        "danger": "#ef4444",
        "name_ar": "وردي",
        "name_en": "Rose"
    },
    "indigo": {
        "primary": "#6366f1",
        "primary_hover": "#4f46e5",
        "bg": "#020617",
        "card": "#0f172a",
        "fg": "#e5e7eb",
        "muted": "#a5b4fc",
        "border": "#4f46e5",
        "success": "#10b981",
        "danger": "#ef4444",
        "name_ar": "نيلي",
        "name_en": "Indigo"
    },
    "emerald": {
        "primary": "#10b981",
        "primary_hover": "#059669",
        "bg": "#022c22",
        "card": "#064e3b",
        "fg": "#ecfdf5",
        "muted": "#6ee7b7",
        "border": "#065f46",
        "success": "#34d399",
        "danger": "#ef4444",
        "name_ar": "زمردي",
        "name_en": "Emerald"
    },
    "amber": {
        "primary": "#f59e0b",
        "primary_hover": "#d97706",
        "bg": "#451a03",
        "card": "#78350f",
        "fg": "#fffbeb",
        "muted": "#fcd34d",
        "border": "#92400e",
        "success": "#10b981",
        "danger": "#ef4444",
        "name_ar": "كهرماني",
        "name_en": "Amber"
    },
}

# ========= Cache =========
@st.cache_resource
def get_model_handler():
    return ModelHandler(MODEL_PATH)

@st.cache_resource
def get_pdf_generator():
    return PDFGenerator(out_dir=os.path.join(BASE_DIR, "reports"))

model_handler = get_model_handler()
pdf_gen = get_pdf_generator()


def load_image_as_base64(image_path):
    """تحميل صورة وتحويلها إلى base64"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None


if "lang" not in st.session_state:
    st.session_state.lang = "ar"
if "theme" not in st.session_state:
    st.session_state.theme = "slate"
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "symptoms_state" not in st.session_state:
    st.session_state.symptoms_state = {s: False for s in SYMPTOMS_AR}


lang = st.session_state.lang
theme = THEMES[st.session_state.theme]
TR = TRANSLATIONS.get(lang, TRANSLATIONS["ar"])

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    
    * {{
        font-family: 'Cairo', sans-serif;
    }}
    
    :root {{
        --primary: {theme['primary']};
        --primary-hover: {theme['primary_hover']};
        --bg: {theme['bg']};
        --card: {theme['card']};
        --fg: {theme['fg']};
        --muted: {theme['muted']};
        --border: {theme['border']};
        --success: {theme['success']};
        --danger: {theme['danger']};
    }}
    
    .stApp {{
        background-color: var(--bg);
        color: var(--fg);
    }}
    
    .block-container {{
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 100%;
        {'direction: rtl;' if lang == 'ar' else 'direction: ltr;'}
    }}
    
    /* Header */
    .app-header {{
        background: linear-gradient(135deg, var(--card) 0%, #1e293b 100%);
        padding: 1.2rem 1.5rem;
        border-radius: 16px;
        border: 1px solid var(--border);
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 0.8rem;
    }}
    
    .app-title {{
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary);
        margin: 0;
        text-align: {'right' if lang == 'ar' else 'left'};
    }}
    
    .app-subtitle {{
        font-size: 0.95rem;
        color: var(--muted);
        margin-top: 0.3rem;
        text-align: {'right' if lang == 'ar' else 'left'};
    }}
    
    /* Cards */
    .custom-card {{
        background: var(--card);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid var(--border);
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        height: 100%;
    }}
    
    .card-title {{
        font-size: 1.4rem;
        font-weight: 600;
        color: var(--primary);
        margin-bottom: 1rem;
        text-align: {'right' if lang == 'ar' else 'left'};
    }}
    
    /* Form Inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {{
        background-color: #0c1424 !important;
        color: var(--fg) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        padding: 0.6rem 1rem !important;
        font-size: 0.95rem !important;
    }}
    
    .stTextInput > label,
    .stNumberInput > label,
    .stSelectbox > label {{
        color: var(--fg) !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        margin-bottom: 0.5rem !important;
    }}
    
    /* Symptoms Section */
    .symptoms-section {{
        margin-top: 1.5rem;
        padding-top: 1rem;
        border-top: 1px solid var(--border);
    }}
    
    .symptoms-title {{
        font-size: 1.2rem;
        font-weight: 600;
        color: var(--primary);
        margin-bottom: 1rem;
        text-align: {'right' if lang == 'ar' else 'left'};
    }}
    
    /* Symptom Toggle Container */
    .symptom-container {{
        background: #0c1424;
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.8rem;
        transition: all 0.3s ease;
    }}
    
    .symptom-container:hover {{
        border-color: var(--primary);
        background: #131b2e;
    }}
    
    .symptom-label {{
        font-size: 0.95rem;
        color: var(--fg);
        font-weight: 500;
        margin-bottom: 0.5rem;
        display: block;
    }}
    
    
    
    /* Hide default radio input completely */
    .stRadio input[type="radio"] {{
        position: absolute !important;
        opacity: 0 !important;
        width: 0 !important;
        height: 0 !important;
        pointer-events: none !important;
    }}
    
    /* Hide radio circle indicator */
    .stRadio label > div:first-child,
    .stRadio label > div[data-testid] {{
        display: none !important;
    }}
    
    /* Radio container styling */
    .stRadio > div {{
        display: flex !important;
        gap: 0.5rem !important;
        justify-content: {'flex-start' if lang == 'en' else 'flex-end'} !important;
        flex-direction: row !important;
        background: transparent !important;
        padding: 0 !important;
        border: none !important;
    }}
    
    /* Remove all borders and backgrounds from radio group */
    div[data-testid="stRadio"],
    div[data-testid="stRadio"] > div,
    .stRadio,
    .stRadio > div[role="radiogroup"] {{
        background: transparent !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
    }}
    
    /* Toggle Button Label Styling */
    .stRadio label {{
        background: transparent !important;
        border: 1px solid var(--border) !important;
        border-radius: 20px !important;
        padding: 0.4rem 1.2rem !important;
        color: var(--muted) !important;
        cursor: pointer !important;
        font-size: 0.9rem !important;
        transition: all 0.25s ease !important;
        margin: 0 !important;
        min-width: 60px !important;
        text-align: center !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    
    /* Hover State */
    .stRadio label:hover {{
        border-color: var(--primary) !important;
        background: rgba(14, 165, 233, 0.1) !important;
        transform: translateY(-1px) !important;
    }}
    
    /* Selected/Active State */
    .stRadio label:has(input:checked),
    .stRadio input:checked + label,
    .stRadio label[data-checked="true"] {{
        background: var(--primary) !important;
        color: white !important;
        border-color: var(--primary) !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 8px rgba(14, 165, 233, 0.3) !important;
    }}
    
    /* Remove focus outline */
    .stRadio label:focus,
    .stRadio label:focus-within,
    .stRadio label:active {{
        outline: none !important;
        box-shadow: none !important;
    }}
    
    /* Override any Streamlit default styling */
    .stRadio > div > label > div {{
        background: transparent !important;
        border: none !important;
    }}
    
    /* ===== END TOGGLE BUTTONS STYLING ===== */
    
    /* Buttons */
    .stButton > button {{
        background: var(--primary);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }}
    
    .stButton > button:hover {{
        background: var(--primary-hover);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.4);
    }}
    
    .stButton > button:disabled {{
        background: var(--muted);
        cursor: not-allowed;
        transform: none;
    }}
    
    /* Download Button */
    .stDownloadButton > button {{
        background: var(--success);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
    }}
    
    .stDownloadButton > button:hover {{
        background: #059669;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
    }}
    
    /* Assistant Card */
    .assistant-card {{
        background: linear-gradient(135deg, #312e81 0%, #1e1b4b 100%);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid #4c1d95;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
    }}
    
    .assistant-title {{
        font-size: 1.3rem;
        font-weight: 600;
        color: #818cf8;
        margin-bottom: 1rem;
        text-align: center;
    }}
    
    /* Result Box */
    .result-box {{
        background: linear-gradient(135deg, #065f46 0%, #064e3b 100%);
        border: 1px solid #059669;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1rem;
    }}
    
    .result-title {{
        font-size: 1.2rem;
        color: #6ee7b7;
        font-weight: 600;
        margin-bottom: 0.8rem;
    }}
    
    .result-item {{
        color: #d1fae5;
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }}
    
    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    </style>
    """,
    unsafe_allow_html=True,
)

# ========= Header with Logos =========
header_container = st.container()
with header_container:
    logo_col1, title_col, logo_col2 = st.columns([0.8, 6, 0.8])
    
    with logo_col1:
        left_logo_path = os.path.join(BASE_DIR, "static", "img", "leftt_logo.ico")
        if os.path.exists(left_logo_path):
            st.image(left_logo_path, width=70)
        else:
            st.markdown('<div style="font-size: 3.5rem; text-align: center;">🏥</div>', unsafe_allow_html=True)
    
    with title_col:
        st.markdown(f"""
        <div class="app-header">
            <h1 class="app-title">{TR.get('title', 'تقييم خطر السكتة الدماغية')}</h1>
            <p class="app-subtitle">{TR.get('subtitle', 'أدخل البيانات واحصل على التقييم فوراً')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with logo_col2:
        right_logo_path = os.path.join(BASE_DIR, "static", "img", "right_logo.png")
        if os.path.exists(right_logo_path):
            st.image(right_logo_path, width=90)
        else:
            st.markdown('<div style="font-size: 3.5rem; text-align: center;">🧠</div>', unsafe_allow_html=True)

# ========= Language and Theme Controls =========
st.markdown("<br>", unsafe_allow_html=True)
ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([4, 1, 1])

with ctrl_col2:
    new_lang = st.selectbox(
        "🌐 اللغة / Language",
        options=["ar", "en"],
        index=0 if st.session_state.lang == "ar" else 1,
        format_func=lambda v: "EG العربية" if v == "ar" else "🇬🇧 English",
        key="lang_selector"
    )
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()

with ctrl_col3:
    new_theme = st.selectbox(
        "🎨 السمة / Theme",
        options=list(THEMES.keys()),
        index=list(THEMES.keys()).index(st.session_state.theme),
        format_func=lambda k: THEMES[k]["name_ar"] if lang == "ar" else THEMES[k]["name_en"],
        key="theme_selector"
    )
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ========= Main Layout =========
col_form, col_assistant = st.columns([2.8, 1.2])

# ---------- Form Column ----------
with col_form:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown(f'<h3 class="card-title">{TR.get("title", "تقييم خطر السكتة الدماغية")}</h3>', unsafe_allow_html=True)
    
    # Patient Info
    row1 = st.columns(2)
    with row1[0]:
        name = st.text_input(
            TR.get("name", "الاسم" if lang == "ar" else "Name"),
            placeholder="من فضلك اكتب اسم المريض" if lang == "ar" else "Please enter patient name",
            key="patient_name"
        )
    with row1[1]:
        age = st.number_input(
            TR.get("age", "العمر" if lang == "ar" else "Age"),
            min_value=0, max_value=120, value=60, step=1,
            key="patient_age"
        )
    
    row2 = st.columns(2)
    with row2[0]:
        gender = st.selectbox(
            TR.get("gender", "النوع" if lang == "ar" else "Gender"),
            options=["male", "female"],
            format_func=lambda v: ("ذكر" if v == "male" else "أنثى") if lang == "ar" else ("Male" if v == "male" else "Female"),
            key="patient_gender"
        )
    with row2[1]:
        threshold = st.number_input(
            TR.get("threshold", "العتبة" if lang == "ar" else "Threshold"),
            min_value=0.0, max_value=1.0, value=0.5, step=0.01,
            key="risk_threshold"
        )
    
    # Symptoms Section
    st.markdown('<div class="symptoms-section">', unsafe_allow_html=True)
    st.markdown(f'<h4 class="symptoms-title">{"الأعراض" if lang == "ar" else "Symptoms"}</h4>', unsafe_allow_html=True)
    
    # Create symptom toggles in 3 columns with Yes/No radio buttons
    symptom_cols = st.columns(3)
    for i, symptom_ar in enumerate(SYMPTOMS_AR):
        col_idx = i % 3
        with symptom_cols[col_idx]:
            symptom_label = symptom_ar if lang == "ar" else SYMPTOMS_MAP_EN.get(symptom_ar, symptom_ar)
            
            st.markdown(f'<div class="symptom-container">', unsafe_allow_html=True)
            st.markdown(f'<span class="symptom-label">{symptom_label}</span>', unsafe_allow_html=True)
            
            # Radio buttons for Yes/No in respective language
            if lang == "ar":
                options = ["لا", "نعم"]
                default_index = 1 if st.session_state.symptoms_state[symptom_ar] else 0
            else:
                options = ["No", "Yes"]
                default_index = 1 if st.session_state.symptoms_state[symptom_ar] else 0
            
            choice = st.radio(
                "",
                options=options,
                index=default_index,
                key=f"symptom_{i}",
                horizontal=True,
                label_visibility="collapsed"
            )
            
            # Update state based on selection
            if lang == "ar":
                st.session_state.symptoms_state[symptom_ar] = (choice == "نعم")
            else:
                st.session_state.symptoms_state[symptom_ar] = (choice == "Yes")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Action Buttons
    st.markdown("<br>", unsafe_allow_html=True)
    btn_col1, btn_col2 = st.columns(2)
    
    with btn_col1:
        if st.button(
            "🔍 " + ("تقييم الخطر" if lang == "ar" else "Evaluate Risk"),
            use_container_width=True,
            key="evaluate_btn"
        ):
            try:
                symptoms_dict = {s: ("Yes" if st.session_state.symptoms_state[s] else "No") for s in SYMPTOMS_AR}
                result = model_handler.predict(
                    age=int(age), symptoms=symptoms_dict, threshold=float(threshold)
                )
                st.session_state.last_result = {
                    "name": name if name else ("بدون اسم" if lang == "ar" else "No name"),
                    "age": int(age),
                    "gender": gender,
                    "symptoms": symptoms_dict,
                    "risk_level": result["risk_level"],
                    "probability": result["probability"],
                    "threshold": result["threshold"],
                    "language": lang,
                }
                st.rerun()
            except Exception as e:
                st.error(f"{'خطأ' if lang == 'ar' else 'Error'}: {e}")
    
    with btn_col2:
        if st.session_state.last_result:
            lr = st.session_state.last_result
            try:
                pdf_path, suggested_name = pdf_gen.generate_report(
                    patient_info={"name": lr["name"], "age": lr["age"], "gender": lr["gender"]},
                    symptoms=lr["symptoms"],
                    prediction_result={
                        "risk_level": lr["risk_level"],
                        "probability": lr["probability"],
                        "threshold": lr["threshold"],
                    },
                    language=lr["language"],
                )
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()
                
                st.download_button(
                    label="📄 " + ("تحميل التقرير" if lang == "ar" else "Download Report"),
                    data=pdf_bytes,
                    file_name=suggested_name,
                    mime="application/pdf",
                    use_container_width=True,
                    key="download_pdf_btn"
                )
            except Exception as e:
                st.error(f"{'خطأ PDF' if lang == 'ar' else 'PDF Error'}: {e}")
        else:
            st.button(
                "📄 " + ("تحميل التقرير" if lang == "ar" else "Download Report"),
                use_container_width=True,
                disabled=True,
                key="download_pdf_disabled"
            )
    
    # Display Results
    if st.session_state.last_result:
        lr = st.session_state.last_result
        result_html = f"""
        <div class="result-box">
            <h4 class="result-title">{'📊 نتيجة التقييم' if lang == 'ar' else '📊 Assessment Result'}</h4>
            <p class="result-item"><strong>{'👤 الاسم' if lang == 'ar' else '👤 Name'}:</strong> {lr['name']}</p>
            <p class="result-item"><strong>{'⚠️ مستوى الخطر' if lang == 'ar' else '⚠️ Risk Level'}:</strong> {lr['risk_level']}</p>
            <p class="result-item"><strong>{'📈 النسبة' if lang == 'ar' else '📈 Probability'}:</strong> {lr['probability']:.2f}%</p>
            <p class="result-item"><strong>{'⚖️ العتبة' if lang == 'ar' else '⚖️ Threshold'}:</strong> {lr['threshold']}</p>
        </div>
        """
        st.markdown(result_html, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Assistant Column ----------
with col_assistant:
    st.markdown('<div class="assistant-card">', unsafe_allow_html=True)
    st.markdown(f'<h3 class="assistant-title">{"🤖 مساعد ذكي" if lang == "ar" else "🤖 Smart Assistant"}</h3>', unsafe_allow_html=True)
    
    desc_text = "نيرفا: رفيقك الذكي للكشف المبكر عن السكتة الدماغية والوقاية منها" if lang == "ar" else "Nirfa: Your smart companion for early stroke detection and prevention"
    st.markdown(f'<p style="text-align: center; color: #c7d2fe; font-size: 0.85rem; margin-bottom: 1rem;">{desc_text}</p>', unsafe_allow_html=True)
    
    # Embed JotForm Agent
    iframe_lang = "ar" if lang == "ar" else "en"
    agent_url = f"https://www.jotform.com/agent/019a5ffe42ef74048854da897e8de95af3e4?lang={iframe_lang}"
    
    components.html(
        f"""
        <iframe
            src="{agent_url}"
            style="width:100%; height:500px; border:0; border-radius:12px;"
            allow="clipboard-write; microphone; camera">
        </iframe>
        """,
        height=520,
    )
    
    # Open in new tab button
    patient_name = st.session_state.last_result["name"] if st.session_state.last_result else ("بدون اسم" if lang == "ar" else "No name")
    btn_label = f"{'🔗 فتح في صفحة جديدة' if lang == 'ar' else '🔗 Open in New Tab'} – {patient_name}"
    
    if st.button(btn_label, use_container_width=True, key="open_assistant"):
        st.markdown(f'<a href="{agent_url}" target="_blank" rel="noopener noreferrer">✅ {btn_label}</a>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)