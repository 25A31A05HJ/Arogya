requireAuth();

document.getElementById("logoutLink").addEventListener("click", (e) => {
  e.preventDefault();
  clearSession();
  window.location.href = "index.html";
});

const CATEGORY_ICONS = {
  water: "💧", exercise: "🏃", sleep: "😴", appointment: "📅", other: "🔔",
};

async function loadReminders() {
  const reminders = await apiRequest("/reminders");
  const list = document.getElementById("reminderList");

  if (reminders.length === 0) {
    list.innerHTML = '<p class="muted">No reminders yet — add one above.</p>';
    return;
  }

  list.innerHTML = reminders
    .map(
      (r) => `
      <div class="reminder-item" data-id="${r.reminder_id}">
        <div>
          <span class="time">${r.remind_time}</span>
          ${CATEGORY_ICONS[r.category] || "🔔"} ${r.title}
          ${r.is_active ? "" : '<span class="muted">(paused)</span>'}
        </div>
        <div class="actions">
          <button class="btn small secondary toggle-btn">${r.is_active ? "Pause" : "Resume"}</button>
          <button class="btn small secondary delete-btn">Delete</button>
        </div>
      </div>`
    )
    .join("");

  list.querySelectorAll(".toggle-btn").forEach((btn, i) => {
    btn.addEventListener("click", async () => {
      const id = reminders[i].reminder_id;
      await apiRequest(`/reminders/${id}`, {
        method: "PUT",
        body: { is_active: reminders[i].is_active ? 0 : 1 },
      });
      loadReminders();
    });
  });

  list.querySelectorAll(".delete-btn").forEach((btn, i) => {
    btn.addEventListener("click", async () => {
      const id = reminders[i].reminder_id;
      await apiRequest(`/reminders/${id}`, { method: "DELETE" });
      loadReminders();
    });
  });
}

document.getElementById("reminderForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  await apiRequest("/reminders", {
    method: "POST",
    body: {
      category: document.getElementById("reminderCategory").value,
      title: document.getElementById("reminderTitle").value,
      remind_time: document.getElementById("reminderTime").value,
    },
  });
  document.getElementById("reminderTitle").value = "";
  document.getElementById("reminderTime").value = "";
  loadReminders();
});

loadReminders();
