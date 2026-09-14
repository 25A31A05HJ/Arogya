requireAuth();

const chatWindow = document.getElementById("chatWindow");
const chatInput = document.getElementById("chatInput");

document.getElementById("logoutLink").addEventListener("click", (e) => {
  e.preventDefault();
  clearSession();
  window.location.href = "index.html";
});

function appendMessage(sender, text, isRedFlag = false) {
  const div = document.createElement("div");
  div.className = `msg ${sender}${isRedFlag ? " red-flag" : ""}`;
  div.textContent = text;
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function loadHistory() {
  try {
    const history = await apiRequest("/chat/history");
    history.forEach((m) =>
      appendMessage(m.sender === "user" ? "user" : "ai", m.message, !!m.is_red_flag)
    );
    if (history.length === 0) {
      appendMessage(
        "ai",
        "Hi! I'm your AarogyaAI wellness assistant. Ask me about sleep, exercise, hydration, nutrition, or stress — or tap a suggestion below."
      );
    }
  } catch (err) {
    console.error(err);
  }
}

async function sendMessage(text) {
  if (!text.trim()) return;
  appendMessage("user", text);
  chatInput.value = "";
  try {
    const res = await apiRequest("/chat", { method: "POST", body: { message: text } });
    appendMessage("ai", res.reply, res.is_red_flag);
  } catch (err) {
    appendMessage("ai", "Sorry, something went wrong: " + err.message);
  }
}

document.getElementById("sendBtn").addEventListener("click", () => sendMessage(chatInput.value));
chatInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendMessage(chatInput.value);
});
document.querySelectorAll(".suggestion-chip").forEach((chip) => {
  chip.addEventListener("click", () => sendMessage(chip.textContent));
});

loadHistory();
