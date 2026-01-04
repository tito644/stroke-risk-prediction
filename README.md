# 🧠 Stroke Risk Prediction System (NERVA)

An end-to-end data science and machine learning project developed as part of the **Digital Egypt Pioneers Initiative (DEPI)**.  
The system predicts stroke risk using clinical symptoms and demographic data, with a strong focus on interpretability, medical relevance, and real-world deployment.

---

## 📌 Project Overview

Stroke is one of the leading causes of death and long-term disability worldwide.  
This project aims to support **early risk detection** by building a reliable, data-driven machine learning system that classifies individuals as **At Risk / Not At Risk** based on medical indicators.

---

## 🎯 Objectives

- Perform in-depth exploratory data analysis (EDA) to understand stroke risk patterns
- Build and compare multiple machine learning models
- Prioritize **high recall** to minimize missed high-risk cases
- Deliver an interpretable and deployment-ready solution
- Support data-driven medical decision-making

---

## 🧠 Dataset

- **Source:** Kaggle – Stroke Risk Prediction Dataset  
- **Features:**
  - Binary symptoms (Chest Pain, Dizziness, Shortness of Breath, etc.)
  - Numeric features (Age, Stroke Risk %)
- **Target:** `At Risk` (Binary Classification)

---

## 🔍 Exploratory Data Analysis (EDA)

- Distribution analysis for binary and numeric features
- Symptom-level prevalence comparison
- Correlation analysis between Age, Symptoms, and Stroke Risk
- Identification and handling of missing values and outliers
- Medical consistency validation of patterns

---

## 🤖 Machine Learning Models

The following models were trained and evaluated:

- Logistic Regression ✅ (Best Model)
- Random Forest
- Decision Tree
- XGBoost

### 📊 Evaluation Metrics
- Accuracy
- Precision
- **Recall (Critical for medical use cases)**
- F1-score
- ROC-AUC

> **Best Result:**  
> Logistic Regression achieved **ROC-AUC ≈ 0.99** with excellent recall and interpretability.

---

## 🧬 Feature Engineering & Interpretation

- Feature importance analysis
- Correlation validation between Age and Stroke Risk
- Symptom contribution assessment
- Model explainability aligned with medical logic

---

## ⚙️ MLOps & Deployment Concepts

- Experiment tracking
- Model monitoring
- Threshold tuning for medical safety
- PDF report generation
- Bilingual UI (Arabic / English) with RTL support

---

## 🖥️ User Interface

- Bilingual (Arabic / English)
- Medical-friendly design
- Stroke risk probability output
- AI-generated medical explanation
- Exportable PDF reports

---

## 📁 Repository Structure

