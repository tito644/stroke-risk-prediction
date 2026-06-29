// Translation strings for the Stroke Risk Screening app.
// Mirrors the TR dict structure used in streamlit_app.py, so both UIs
// communicate the same content and disclaimers in both languages.

const TRANSLATIONS = {
  ar: {
    brand: "فحص خطر السكتة الدماغية",
    title: "تقييم أولي لخطر السكتة الدماغية",
    subtitle: "أداة فحص أولي مبنية على بيانات سريرية حقيقية من 5,110 حالة",
    disclaimer_title: "تنبيه مهم",
    disclaimer_body:
      "هذه الأداة ليست تشخيصًا طبيًا. هي أداة فحص أولي تعليمية تعتمد على نموذج تعلّم آلي مدرّب على بيانات " +
      "سريرية حقيقية، لكنها لا تعرف تاريخك الطبي الكامل ولا يمكنها استبدال تقييم طبيب مختص. إذا شعرت بأعراض " +
      "مفاجئة (تنميل، صعوبة في الكلام، ضعف مفاجئ في جانب من الجسم)، اتصل بالطوارئ فورًا.",
    form_header: "البيانات الصحية",
    age: "العمر (بالسنوات)",
    gender: "النوع",
    gender_male: "ذكر",
    gender_female: "أنثى",
    hypertension: "هل تم تشخيصك بارتفاع ضغط الدم؟",
    heart_disease: "هل لديك تاريخ مرضي بأمراض القلب؟",
    ever_married: "هل تزوجت سابقًا؟",
    ever_married_help: "هذا السؤال يُستخدم لأن الحالة الاجتماعية ترتبط إحصائيًا بالعمر في بيانات النموذج، وليس لأنها سبب مباشر لخطر السكتة",
    residence_type: "نوع منطقة السكن",
    residence_urban: "حضري (مدينة)",
    residence_rural: "ريفي",
    work_type: "نوع العمل",
    work_private: "قطاع خاص",
    work_self_employed: "عمل خاص / حر",
    work_govt: "قطاع حكومي",
    work_children: "طفل (لم يبدأ العمل بعد)",
    work_never: "لم يعمل من قبل",
    smoking_status: "حالة التدخين",
    smoking_never: "لم يدخن من قبل",
    smoking_former: "مدخن سابق",
    smoking_current: "مدخن حاليًا",
    smoking_unknown: "غير معروف / أفضل عدم الإجابة",
    glucose: "متوسط مستوى الجلوكوز في الدم (mg/dL)",
    glucose_help: "إذا لم تكن متأكدًا، القيمة الطبيعية التقريبية أثناء الصيام هي 70–100 mg/dL",
    bmi: "مؤشر كتلة الجسم (BMI)",
    bmi_unknown: "لا أعرف مؤشر كتلة جسمي",
    bmi_help: "BMI = الوزن (كجم) ÷ (الطول بالمتر)²",
    submit: "🔍 احسب نسبة الخطر",
    result_header: "نتيجة التقييم",
    risk_low: "منخفض نسبيًا",
    risk_high: "مرتفع نسبيًا — يُنصح بمراجعة الطبيب",
    model_note:
      "تم استخدام نموذج Logistic Regression المدرّب على بيانات سريرية حقيقية (5,110 حالة)، بدقة تمييز " +
      "(ROC-AUC) تبلغ 0.84. عتبة التصنيف ({threshold}%) محسوبة إحصائيًا (Youden's J) لتحقيق أفضل توازن بين " +
      "نسبة اكتشاف الحالات الحقيقية (حساسية 80%) ودقة استبعاد الحالات السليمة (نوعية 77%).",
    footer_note: "مشروع تحليل بيانات لخطر السكتة الدماغية — يستخدم نموذج تعلّم آلي تدرّب على بيانات Kaggle الحقيقية.",
    error_prefix: "حدث خطأ: ",
    error_network: "تعذّر الاتصال بالخادم. تأكد من تشغيل التطبيق وحاول مرة أخرى.",
  },
  en: {
    brand: "Stroke Risk Screening",
    title: "Preliminary Stroke Risk Assessment",
    subtitle: "A preliminary screening tool built on real clinical data from 5,110 cases",
    disclaimer_title: "Important Disclaimer",
    disclaimer_body:
      "This tool is not a medical diagnosis. It's an educational screening aid based on a machine learning " +
      "model trained on real clinical data, but it does not know your full medical history and cannot " +
      "replace a qualified doctor's assessment. If you experience sudden symptoms (numbness, difficulty " +
      "speaking, sudden weakness on one side of the body), call emergency services immediately.",
    form_header: "Health Information",
    age: "Age (years)",
    gender: "Gender",
    gender_male: "Male",
    gender_female: "Female",
    hypertension: "Have you been diagnosed with high blood pressure (hypertension)?",
    heart_disease: "Do you have a history of heart disease?",
    ever_married: "Have you ever been married?",
    ever_married_help: "This question is included because marital status statistically correlates with age in the training data, not because it directly causes stroke risk",
    residence_type: "Residence type",
    residence_urban: "Urban",
    residence_rural: "Rural",
    work_type: "Work type",
    work_private: "Private sector",
    work_self_employed: "Self-employed",
    work_govt: "Government sector",
    work_children: "Child (not yet working)",
    work_never: "Never worked",
    smoking_status: "Smoking status",
    smoking_never: "Never smoked",
    smoking_former: "Formerly smoked",
    smoking_current: "Currently smokes",
    smoking_unknown: "Unknown / prefer not to say",
    glucose: "Average blood glucose level (mg/dL)",
    glucose_help: "If unsure, a typical fasting value is roughly 70–100 mg/dL",
    bmi: "Body Mass Index (BMI)",
    bmi_unknown: "I don't know my BMI",
    bmi_help: "BMI = weight (kg) ÷ (height in meters)²",
    submit: "🔍 Calculate Risk",
    result_header: "Assessment Result",
    risk_low: "Relatively low",
    risk_high: "Relatively high — consider consulting a doctor",
    model_note:
      "This result uses a Logistic Regression model trained on real clinical data (5,110 cases), with " +
      "ROC-AUC = 0.84. The classification threshold ({threshold}%) is statistically derived (Youden's J) to " +
      "balance catching real cases (80% sensitivity) against not over-flagging healthy people (77% specificity).",
    footer_note: "A stroke risk data science project — powered by a model trained on real Kaggle clinical data.",
    error_prefix: "Error: ",
    error_network: "Could not reach the server. Make sure the app is running and try again.",
  },
};
