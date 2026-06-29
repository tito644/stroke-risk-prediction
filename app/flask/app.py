# -*- coding: utf-8 -*-
"""
Stroke Risk Prediction — Flask Edition (Real-World Clinical Data)
====================================================================
This Flask app mirrors the logic of streamlit_app.py exactly: same model
(Logistic Regression trained on real clinical data), same feature mapping,
and the same statistically-derived classification threshold (Youden's J).

Model provenance & limitations:
This app uses a model trained on REAL clinical data (Kaggle: Healthcare
Dataset Stroke Data), not the synthetic dataset used elsewhere in this
project's exploratory notebooks. See the project's Phase 3 comparison
notebook for why that distinction matters.

This tool is a screening aid, not a medical diagnosis.
"""

import os
import joblib
import pandas as pd
from flask import Flask, render_template, request, jsonify

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "stroke_classification_model_real_data.joblib")

# Classification threshold derived from Youden's J statistic (sensitivity + specificity - 1),
# computed on the held-out test set in Phase2c_Classification_Modeling.ipynb. This is the
# standard statistical method for choosing a clinical screening cutoff, and balances catching
# real stroke cases (sensitivity) against not over-flagging healthy people (specificity).
# At this threshold: Sensitivity (Recall) = 80.0%, Specificity = 77.1%.
RISK_THRESHOLD = 0.5314

app = Flask(__name__)

# -----------------------------------------------------------------------
# Load model once at startup
# -----------------------------------------------------------------------
try:
    _package = joblib.load(MODEL_PATH)
    MODEL = _package["model"]
    FEATURE_NAMES = _package["features"]
    TRAIN_BMI_MEDIAN = _package["train_bmi_median"]
    MODEL_LOAD_ERROR = None
    print(f"Model loaded successfully. {len(FEATURE_NAMES)} features expected.")
except Exception as e:
    MODEL, FEATURE_NAMES, TRAIN_BMI_MEDIAN = None, [], 28.1
    MODEL_LOAD_ERROR = str(e)
    print(f"WARNING: failed to load model from {MODEL_PATH}: {e}")

VALID_WORK_TYPES = ["Private", "Self-employed", "Govt_job", "children", "Never_worked"]
VALID_SMOKING_STATUSES = ["never smoked", "formerly smoked", "smokes", "Unknown"]


def build_feature_row(inputs):
    """
    Build a single-row DataFrame matching the exact column order and
    one-hot encoding scheme the model was trained on. Mirrors the logic
    in streamlit_app.py exactly, so both UIs produce identical predictions
    for identical inputs.
    """
    row = {name: 0 for name in FEATURE_NAMES}

    row["age"] = inputs["age"]
    row["gender"] = 1 if inputs["gender"] == "female" else 0
    row["hypertension"] = 1 if inputs["hypertension"] else 0
    row["heart_disease"] = 1 if inputs["heart_disease"] else 0
    row["ever_married"] = 1 if inputs["ever_married"] else 0
    row["Residence_type"] = 1 if inputs["residence"] == "urban" else 0
    row["avg_glucose_level"] = inputs["glucose"]

    if inputs["bmi_known"]:
        row["bmi"] = inputs["bmi"]
        row["bmi_missing"] = 0
    else:
        row["bmi"] = TRAIN_BMI_MEDIAN
        row["bmi_missing"] = 1

    work_col = f"work_type_{inputs['work_type']}"
    if work_col in row:
        row[work_col] = 1

    smoke_col = f"smoking_status_{inputs['smoking_status']}"
    if smoke_col in row:
        row[smoke_col] = 1

    return pd.DataFrame([row], columns=FEATURE_NAMES)


def validate_inputs(data):
    """
    Validate and normalize the incoming JSON payload. Returns
    (cleaned_inputs, error_message). error_message is None if valid.
    """
    try:
        age = float(data.get("age"))
    except (TypeError, ValueError):
        return None, "age must be a number"
    if not (0 <= age <= 120):
        return None, "age must be between 0 and 120"

    gender = data.get("gender")
    if gender not in ("male", "female"):
        return None, "gender must be 'male' or 'female'"

    residence = data.get("residence")
    if residence not in ("urban", "rural"):
        return None, "residence must be 'urban' or 'rural'"

    work_type = data.get("work_type")
    if work_type not in VALID_WORK_TYPES:
        return None, f"work_type must be one of {VALID_WORK_TYPES}"

    smoking_status = data.get("smoking_status")
    if smoking_status not in VALID_SMOKING_STATUSES:
        return None, f"smoking_status must be one of {VALID_SMOKING_STATUSES}"

    try:
        glucose = float(data.get("glucose"))
    except (TypeError, ValueError):
        return None, "glucose must be a number"
    if not (40 <= glucose <= 400):
        return None, "glucose must be between 40 and 400 mg/dL"

    bmi_known = bool(data.get("bmi_known", True))
    bmi = 0.0
    if bmi_known:
        try:
            bmi = float(data.get("bmi"))
        except (TypeError, ValueError):
            return None, "bmi must be a number when bmi_known is true"
        if not (10 <= bmi <= 80):
            return None, "bmi must be between 10 and 80"

    cleaned = {
        "age": age,
        "gender": gender,
        "hypertension": bool(data.get("hypertension", False)),
        "heart_disease": bool(data.get("heart_disease", False)),
        "ever_married": bool(data.get("ever_married", False)),
        "residence": residence,
        "glucose": glucose,
        "bmi_known": bmi_known,
        "bmi": bmi,
        "work_type": work_type,
        "smoking_status": smoking_status,
    }
    return cleaned, None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/predict", methods=["POST"])
def predict():
    if MODEL is None:
        return jsonify({
            "success": False,
            "error": f"Model is not loaded on the server: {MODEL_LOAD_ERROR}",
        }), 500

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"success": False, "error": "Request body must be valid JSON"}), 400

    cleaned_inputs, error = validate_inputs(data)
    if error:
        return jsonify({"success": False, "error": error}), 400

    try:
        X_row = build_feature_row(cleaned_inputs)
        proba = float(MODEL.predict_proba(X_row)[0, 1])
    except Exception as e:
        return jsonify({"success": False, "error": f"Prediction failed: {e}"}), 500

    is_high_risk = proba >= RISK_THRESHOLD

    return jsonify({
        "success": True,
        "risk_probability": proba,
        "risk_percent": round(proba * 100, 1),
        "threshold": RISK_THRESHOLD,
        "threshold_percent": round(RISK_THRESHOLD * 100, 1),
        "is_high_risk": is_high_risk,
    })


@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok" if MODEL is not None else "model_not_loaded",
        "model_loaded": MODEL is not None,
        "n_features": len(FEATURE_NAMES),
    })


@app.errorhandler(404)
def not_found(e):
    return jsonify({"success": False, "error": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"success": False, "error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
