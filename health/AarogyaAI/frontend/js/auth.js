const loginForm = document.getElementById("loginForm");
const signupForm = document.getElementById("signupForm");
const errorBanner = document.getElementById("errorBanner");

document.getElementById("showSignup").addEventListener("click", (e) => {
  e.preventDefault();
  loginForm.style.display = "none";
  document.querySelector(".switch-link").style.display = "none";
  signupForm.style.display = "block";
  document.getElementById("backToLoginWrap").style.display = "block";
});

document.getElementById("showLogin").addEventListener("click", (e) => {
  e.preventDefault();
  signupForm.style.display = "none";
  document.getElementById("backToLoginWrap").style.display = "none";
  loginForm.style.display = "block";
  document.querySelector(".switch-link").style.display = "block";
});

function showError(message) {
  errorBanner.textContent = message;
  errorBanner.style.display = "block";
}

loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  errorBanner.style.display = "none";
  try {
    const data = await apiRequest("/auth/login", {
      method: "POST",
      auth: false,
      body: {
        email: document.getElementById("loginEmail").value,
        password: document.getElementById("loginPassword").value,
      },
    });
    setSession(data.token, data.user_id, data.name);
    window.location.href = "dashboard.html";
  } catch (err) {
    showError(err.message);
  }
});

signupForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  errorBanner.style.display = "none";
  try {
    const data = await apiRequest("/auth/signup", {
      method: "POST",
      auth: false,
      body: {
        name: document.getElementById("signupName").value,
        email: document.getElementById("signupEmail").value,
        password: document.getElementById("signupPassword").value,
        wellness_goal: document.getElementById("signupGoal").value,
      },
    });
    setSession(data.token, data.user_id, data.name);
    window.location.href = "dashboard.html";
  } catch (err) {
    showError(err.message);
  }
});
