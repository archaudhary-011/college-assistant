import { API } from "../constants";

const authHeaders = (token) => ({
  "Content-Type": "application/json",
  "Authorization": `Bearer ${token}`,
});

// ── Auth ──────────────────────────────────────────────────────────────────────
export const loginApi = (username, password) =>
  fetch(`${API}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });

export const registerApi = (username, password) =>
  fetch(`${API}/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });

// ── Conversations ─────────────────────────────────────────────────────────────
export const getConversationsApi = (token) =>
  fetch(`${API}/conversations`, { headers: authHeaders(token) });

export const createConversationApi = (token) =>
  fetch(`${API}/conversations`, { method: "POST", headers: authHeaders(token) });

export const deleteConversationApi = (token, id) =>
  fetch(`${API}/conversations/${id}`, { method: "DELETE", headers: authHeaders(token) });

export const getMessagesApi = (token, id) =>
  fetch(`${API}/conversations/${id}/messages`, { headers: authHeaders(token) });

// ── Chat ──────────────────────────────────────────────────────────────────────
export const sendMessageApi = (token, conversationId, message) =>
  fetch(`${API}/chat`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ conversation_id: conversationId || null, message }),
  });
