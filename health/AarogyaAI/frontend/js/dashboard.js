requireAuth();

const DIMENSION_LABELS = {
  sleep: "Sleep", exercise: "Exercise", hydration: "Hydration",
  nutrition: "Nutrition", stress: "Stress",
};

document.getElementById("greeting").textContent =
  `Hi ${localStorage.getItem("aarogyaai_name") || ""} — here's your wellness dashboard`;

document.getElementById("logoutLink").addEventListener("click", (e) => {
  e.preventDefault();
  clearSession();
  window.location.href = "index.html";
});

function showAlert(message) {
  const box = document.getElementById("alertBox");
  box.textContent = message;
  box.style.display = "block";
}

async function loadDashboard() {
  try {
    const data = await apiRequest("/dashboard");
    document.getElementById("scoreValue").textContent = data.wellness_score;
    document.getElementById("sleepValue").textContent = data.sleep_hours || 0;
    document.getElementById("waterValue").textContent = ((data.water_ml || 0) / 1000).toFixed(1);
    document.getElementById("exerciseValue").textContent = data.exercise_minutes || 0;
    document.getElementById("insightText").textContent = data.insight;

    const barsHtml = Object.entries(data.score_breakdown)
      .map(([dim, val]) => `
        <div class="bar-row">
          <div class="bar-label">${DIMENSION_LABELS[dim] || dim}</div>
          <div class="bar-track"><div class="bar-fill" style="width:${val}%"></div></div>
          <div class="bar-value">${val}</div>
        </div>`)
      .join("");
    document.getElementById("breakdownBars").innerHTML = barsHtml;

    document.getElementById("recList").innerHTML = data.recommendations
      .map((r) => `<li>${r}</li>`)
      .join("");
  } catch (err) {
    showAlert("Could not load dashboard: " + err.message);
  }
}

async function loadTrend() {
  try {
    const history = await apiRequest("/logs/history?days=7");
    const labels = history.map((h) => h.log_date.slice(5));
    const scores = history.map((h) => h.wellness_score || 0);

    new Chart(document.getElementById("trendChart"), {
      type: "line",
      data: {
        labels,
        datasets: [{
          label: "Wellness Score",
          data: scores,
          borderColor: "#2e7d6b",
          backgroundColor: "rgba(46,125,107,0.15)",
          fill: true,
          tension: 0.3,
        }],
      },
      options: {
        scales: { y: { min: 0, max: 100 } },
        plugins: { legend: { display: false } },
      },
    });
  } catch (err) {
    console.error(err);
  }
}

async function loadExerciseAndMeals() {
  const today = await apiRequest("/logs/today");
  document.getElementById("exerciseList").innerHTML = "";
  document.getElementById("mealList").innerHTML = "";
}

// ---------- Tabs ----------
document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".log-tab").forEach((t) => (t.style.display = "none"));
    btn.classList.add("active");
    document.getElementById(btn.dataset.tab + "Tab").style.display = "flex";
  });
});

// ---------- Sleep ----------
document.getElementById("sleepTab").addEventListener("submit", async (e) => {
  e.preventDefault();
  const sleep_hours = parseFloat(document.getElementById("sleepHours").value);
  const res = await apiRequest("/logs/today", { method: "POST", body: { sleep_hours } });
  if (res.safety_alert) showAlert(res.safety_alert);
  loadDashboard();
});

// ---------- Water ----------
document.getElementById("waterTab").addEventListener("submit", async (e) => {
  e.preventDefault();
  const water_ml_add = parseInt(document.getElementById("waterMl").value, 10);
  await apiRequest("/logs/today", { method: "POST", body: { water_ml_add } });
  document.getElementById("waterMl").value = "";
  loadDashboard();
});

// ---------- Exercise ----------
document.getElementById("exerciseTab").addEventListener("submit", async (e) => {
  e.preventDefault();
  const activity = document.getElementById("exerciseActivity").value;
  const minutes = parseInt(document.getElementById("exerciseMinutes").value, 10);
  const res = await apiRequest("/logs/exercise", { method: "POST", body: { activity, minutes } });
  document.getElementById("exerciseList").innerHTML = res.entries
    .map((en) => `<li>${en.activity} — ${en.minutes} min</li>`).join("");
  document.getElementById("exerciseMinutes").value = "";
  loadDashboard();
});

// ---------- Meal ----------
document.getElementById("mealTab").addEventListener("submit", async (e) => {
  e.preventDefault();
  const meal_type = document.getElementById("mealType").value;
  const description = document.getElementById("mealDescription").value;
  const nutrition_rating = document.getElementById("nutritionRating").value || undefined;
  const res = await apiRequest("/logs/meal", {
    method: "POST",
    body: { meal_type, description, nutrition_rating },
  });
  document.getElementById("mealList").innerHTML = res.meals
    .map((m) => `<li>${m.meal_type}: ${m.description}</li>`).join("");
  document.getElementById("mealDescription").value = "";
  loadDashboard();
});

// ---------- Stress / Symptoms ----------
document.getElementById("stressTab").addEventListener("submit", async (e) => {
  e.preventDefault();
  const stress_level = document.getElementById("stressLevel").value;
  const mood_note = document.getElementById("moodNote").value;
  const symptoms_text = document.getElementById("symptomsText").value;
  const res = await apiRequest("/logs/today", {
    method: "POST",
    body: { stress_level, mood_note, symptoms_text },
  });
  if (res.safety_alert) showAlert(res.safety_alert);
  loadDashboard();
});

loadDashboard();
loadTrend();
loadExerciseAndMeals();
