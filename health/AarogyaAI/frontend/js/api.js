/**
 * api.js — thin fetch wrapper shared by every page.
 * Change API_BASE if the backend runs somewhere other than localhost:5000.
 */
const API_BASE = "http://localhost:5000/api";

function getToken() {
  return localStorage.getItem("aarogyaai_token");
}

function setSession(token, userId, name) {
  localStorage.setItem("aarogyaai_token", token);
  localStorage.setItem("aarogyaai_user_id", userId);
  localStorage.setItem("aarogyaai_name", name);
}

function clearSession() {
  localStorage.removeItem("aarogyaai_token");
  localStorage.removeItem("aarogyaai_user_id");
  localStorage.removeItem("aarogyaai_name");
}

function requireAuth() {
  if (!getToken()) {
    window.location.href = "index.html";
  }
}

async function apiRequest(path, { method = "GET", body = null, auth = true } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth) {
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  let data = null;
  try {
    data = await res.json();
  } catch (e) {
    data = null;
  }

  if (!res.ok) {
    const message = (data && data.error) || `Request failed (${res.status})`;
    if (res.status === 401) {
      clearSession();
      window.location.href = "index.html";
    }
    throw new Error(message);
  }
  return data;
}
