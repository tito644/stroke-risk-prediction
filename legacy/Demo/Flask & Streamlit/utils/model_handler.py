# utils/model_handler.py

import joblib
import numpy as np
import pandas as pd
from pathlib import Path


class ModelHandler:
    """
    Handles regression model loading and predictions for Stroke Risk (%).

    Expected saved joblib format:
    {
        "model": trained_regression_model,
        "features": list_of_feature_names
    }

    The regression model predicts Stroke Risk as a percentage (0 -> 100).
    Then:
        - prediction / at_risk = 1 if predicted risk >= threshold
        - prediction / at_risk = 0 otherwise
    """

    FEATURE_MAP = {
        # Arabic labels from UI -> training feature names
        "ألم في الصدر": "Chest Pain",
        "ضيق في التنفس": "Shortness of Breath",
        "اضطراب نبضات القلب": "Irregular Heartbeat",
        "التعب و ضعط مرتفع": "Fatigue & Weakness",
        "دوخة": "Dizziness",
        "تورم (وذمة)": "Swelling (Edema)",
        "ألم في الرقبة / الكتف / الظهر": "Pain in Neck/Jaw/Shoulder/Back",
        "ألم في الرقبة / العد / الكتف / الظهر": "Pain in Neck/Jaw/Shoulder/Back",
        "التعرق الزائد": "Excessive Sweating",
        "السعال المستمر": "Persistent Cough",
        "الغثيان/القيء": "Nausea/Vomiting",
        "ضعط دم مرتفع": "High Blood Pressure",
        "أرتجاع في الصدر": "Chest Discomfort (Activity)",
        "أرتجاع في الصدر (النساط)": "Chest Discomfort (Activity)",
        "الأيدي الباردة / القدمين": "Cold Hands/Feet",
        "الشخير/توقف التنفس أثناء النوم": "Snoring/Sleep Apnea",
        "القلق / الشعور بالهلاك": "Anxiety/Feeling of Doom",
        "الغلق / الشعور بالهلاك": "Anxiety/Feeling of Doom",

        # English labels -> training feature names
        "Chest Pain": "Chest Pain",
        "Shortness of Breath": "Shortness of Breath",
        "Irregular Heartbeat": "Irregular Heartbeat",
        "Fatigue & Weakness": "Fatigue & Weakness",
        "Fatigue & High BP": "Fatigue & Weakness",
        "Dizziness": "Dizziness",
        "Swelling (Edema)": "Swelling (Edema)",
        "Pain in Neck/Jaw/Shoulder/Back": "Pain in Neck/Jaw/Shoulder/Back",
        "Excessive Sweating": "Excessive Sweating",
        "Persistent Cough": "Persistent Cough",
        "Nausea/Vomiting": "Nausea/Vomiting",
        "High Blood Pressure": "High Blood Pressure",
        "Chest Discomfort (Activity)": "Chest Discomfort (Activity)",
        "Cold Hands/Feet": "Cold Hands/Feet",
        "Snoring/Sleep Apnea": "Snoring/Sleep Apnea",
        "Anxiety/Feeling of Doom": "Anxiety/Feeling of Doom",
    }

    POSITIVE_VALUES = {"yes", "1", "true", "on", "نعم"}
    NEGATIVE_VALUES = {"no", "0", "false", "off", "لا"}

    def __init__(self, model_path):
        self.model_path = Path(model_path)
        self.model = None
        self.features = []
        self._load_model()

    def _load_model(self):
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")

        data = joblib.load(self.model_path)

        # Supported formats:
        # 1) dict: {"model": estimator, "features": [...]}
        # 2) raw estimator only
        if isinstance(data, dict) and "model" in data:
            self.model = data["model"]
            self.features = data.get("features", [])
        else:
            self.model = data
            self.features = list(getattr(self.model, "feature_names_in_", []))

        if self.model is None:
            raise ValueError("Loaded model is None.")

        if not self.features:
            raise ValueError(
                "Feature list is missing in the saved joblib file. "
                "Please save the model as: {'model': model, 'features': list(X_train.columns)}"
            )

        print("✓ Regression model loaded successfully")
        print(f"✓ Features count: {len(self.features)}")
        print(f"✓ First features: {self.features[:5]}")

    def _normalize_threshold(self, threshold):
        """
        Supports:
        - 0.5  -> interpreted as 50%
        - 50   -> interpreted as 50%
        """
        threshold = float(threshold)

        if 0 <= threshold <= 1:
            return threshold * 100.0

        return threshold

    def _normalize_prediction_to_percent(self, prediction):
        """
        Assumes regression output is Stroke Risk (%) in range 0..100.
        Clamps output for safety.
        """
        pred = float(prediction)
        pred = max(0.0, min(pred, 100.0))
        return pred

    def _to_binary_value(self, value):
        """
        Convert UI symptom value to 0/1.
        """
        if isinstance(value, (int, float, np.integer, np.floating)):
            return 1 if float(value) >= 1 else 0

        text = str(value).strip().lower()
        if text in self.POSITIVE_VALUES:
            return 1
        if text in self.NEGATIVE_VALUES:
            return 0

        return 0

    def _build_input_dataframe(self, age, symptoms):
        if self.model is None:
            raise RuntimeError("Model not loaded properly.")

        # Always build exact same feature order as training
        row = pd.DataFrame(np.zeros((1, len(self.features))), columns=self.features, dtype=float)

        if "Age" in row.columns:
            row.loc[0, "Age"] = float(age)

        for label, value in (symptoms or {}).items():
            feature_name = self.FEATURE_MAP.get(label, label)
            if feature_name in row.columns:
                row.loc[0, feature_name] = self._to_binary_value(value)

        non_zero = [col for col in row.columns if float(row.loc[0, col]) != 0.0]
        print(f"Non-zero features: {non_zero}")

        return row

    def _get_risk_level(self, risk_percent):
        """
        Risk levels based on percentage.
        """
        if risk_percent < 30:
            return "low"
        elif risk_percent < 70:
            return "medium"
        return "high"

    def predict(self, age, symptoms, threshold=0.5):
        """
        Predict stroke risk percentage using regression model.

        Returns:
        {
            "prediction": 0 or 1,
            "at_risk": bool,
            "probability": risk_percent,
            "risk_percent": risk_percent,
            "risk_level": "low" | "medium" | "high",
            "threshold": threshold_percent
        }
        """
        threshold_percent = self._normalize_threshold(threshold)
        X = self._build_input_dataframe(age, symptoms)

        raw_pred = self.model.predict(X)[0]
        risk_percent = self._normalize_prediction_to_percent(raw_pred)

        prediction = 1 if risk_percent >= threshold_percent else 0
        at_risk = bool(prediction)
        risk_level = self._get_risk_level(risk_percent)

        return {
            "prediction": prediction,
            "at_risk": at_risk,
            "probability": risk_percent,   # keep same API name for compatibility
            "risk_percent": risk_percent,
            "risk_level": risk_level,
            "threshold": threshold_percent
        }

    def predict_dataframe(self, df):
        """
        Predict on a full DataFrame already aligned with training features.
        Returns predicted risk percentages.
        """
        missing = [f for f in self.features if f not in df.columns]
        if missing:
            raise ValueError(f"Missing required features: {missing}")

        X = df[self.features].copy()
        preds = self.model.predict(X)
        preds = np.clip(preds, 0, 100)
        return preds

    def get_feature_importance(self):
        """
        For regression models:
        - Linear models: returns coefficients
        - Tree models: returns feature_importances_
        """
        if hasattr(self.model, "coef_"):
            coef = np.ravel(self.model.coef_)
            importance = pd.DataFrame({
                "feature": self.features,
                "importance": coef,
                "abs_importance": np.abs(coef)
            }).sort_values("abs_importance", ascending=False)
            return importance.to_dict(orient="records")

        if hasattr(self.model, "feature_importances_"):
            vals = np.ravel(self.model.feature_importances_)
            importance = pd.DataFrame({
                "feature": self.features,
                "importance": vals,
                "abs_importance": np.abs(vals)
            }).sort_values("abs_importance", ascending=False)
            return importance.to_dict(orient="records")

        return None