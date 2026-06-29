// Stroke Risk Screening — frontend logic
// Handles: language toggle, segmented button groups, form validation/submission,
// calling /api/predict, and rendering the result gauge.

(function () {
  "use strict";

  let currentLang = "ar";

  const htmlRoot = document.getElementById("html-root");
  const langToggleBtn = document.getElementById("lang-toggle");
  const form = document.getElementById("risk-form");
  const resultCard = document.getElementById("result-card");
  const errorBox = document.getElementById("error-box");

  // ---------------------------------------------------------------------
  // i18n: apply translations to every element with a data-tr attribute
  // ---------------------------------------------------------------------
  function applyTranslations(lang) {
    const dict = TRANSLATIONS[lang];
    document.querySelectorAll("[data-tr]").forEach((el) => {
      const key = el.getAttribute("data-tr");
      if (!dict[key]) return;
      // Tooltip-only elements (info-dot) get their text via data-tip attribute target
      if (el.hasAttribute("data-tip")) {
        el.setAttribute("title", dict[key]);
      } else {
        el.textContent = dict[key];
      }
    });

    htmlRoot.lang = lang;
    htmlRoot.dir = lang === "ar" ? "rtl" : "ltr";
    langToggleBtn.textContent = lang === "ar" ? "English" : "العربية";
  }

  langToggleBtn.addEventListener("click", () => {
    currentLang = currentLang === "ar" ? "en" : "ar";
    applyTranslations(currentLang);
  });

  // ---------------------------------------------------------------------
  // Segmented button groups (gender, residence) act like radio buttons
  // ---------------------------------------------------------------------
  document.querySelectorAll(".segmented").forEach((group) => {
    group.addEventListener("click", (e) => {
      const btn = e.target.closest(".seg-btn");
      if (!btn) return;
      group.querySelectorAll(".seg-btn").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
    });
  });

  function getSegmentedValue(name) {
    const group = document.querySelector(`.segmented[data-name="${name}"]`);
    const active = group.querySelector(".seg-btn.active");
    return active ? active.getAttribute("data-value") : null;
  }

  // ---------------------------------------------------------------------
  // BMI unknown checkbox disables the BMI number input
  // ---------------------------------------------------------------------
  const bmiInput = document.getElementById("bmi");
  const bmiUnknownCheckbox = document.getElementById("bmi_unknown");
  bmiUnknownCheckbox.addEventListener("change", () => {
    bmiInput.disabled = bmiUnknownCheckbox.checked;
  });

  // ---------------------------------------------------------------------
  // Form submission
  // ---------------------------------------------------------------------
  function showError(message) {
    errorBox.textContent = message;
    errorBox.classList.remove("hidden");
    resultCard.classList.add("hidden");
  }

  function hideError() {
    errorBox.classList.add("hidden");
  }

  function renderResult(data) {
    hideError();
    resultCard.classList.remove("hidden");

    const riskPercentEl = document.getElementById("risk-percent");
    const gaugeFill = document.getElementById("gauge-fill");
    const riskBanner = document.getElementById("risk-banner");
    const modelNote = document.getElementById("model-note");

    riskPercentEl.textContent = data.risk_percent.toFixed(1) + "%";

    // Gauge: circle circumference = 2*pi*52 ≈ 326.7
    const circumference = 2 * Math.PI * 52;
    const fillLength = (data.risk_probability * circumference);
    gaugeFill.style.strokeDasharray = `${fillLength} ${circumference}`;

    const dict = TRANSLATIONS[currentLang];
    if (data.is_high_risk) {
      riskBanner.textContent = dict.risk_high;
      riskBanner.className = "risk-banner risk-high";
      gaugeFill.classList.remove("gauge-low");
      gaugeFill.classList.add("gauge-high");
    } else {
      riskBanner.textContent = dict.risk_low;
      riskBanner.className = "risk-banner risk-low";
      gaugeFill.classList.remove("gauge-high");
      gaugeFill.classList.add("gauge-low");
    }

    modelNote.textContent = dict.model_note.replace("{threshold}", data.threshold_percent.toFixed(1));

    resultCard.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideError();

    const bmiKnown = !bmiUnknownCheckbox.checked;

    const payload = {
      age: parseFloat(document.getElementById("age").value),
      gender: getSegmentedValue("gender"),
      residence: getSegmentedValue("residence"),
      work_type: document.getElementById("work_type").value,
      smoking_status: document.getElementById("smoking_status").value,
      glucose: parseFloat(document.getElementById("glucose").value),
      bmi_known: bmiKnown,
      bmi: bmiKnown ? parseFloat(bmiInput.value) : null,
      hypertension: document.getElementById("hypertension").checked,
      heart_disease: document.getElementById("heart_disease").checked,
      ever_married: document.getElementById("ever_married").checked,
    };

    const submitBtn = form.querySelector(".submit-btn");
    submitBtn.disabled = true;
    submitBtn.textContent = currentLang === "ar" ? "جارٍ الحساب..." : "Calculating...";

    try {
      const response = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();

      if (!response.ok || !data.success) {
        showError(TRANSLATIONS[currentLang].error_prefix + (data.error || response.statusText));
      } else {
        renderResult(data);
      }
    } catch (err) {
      showError(TRANSLATIONS[currentLang].error_network);
    } finally {
      submitBtn.disabled = false;
      applyTranslations(currentLang); // restore the submit button label
    }
  });

  // ---------------------------------------------------------------------
  // Initial render
  // ---------------------------------------------------------------------
  applyTranslations(currentLang);
})();
