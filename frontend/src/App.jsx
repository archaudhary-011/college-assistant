import { useState, useEffect } from "react";
import "./App.css";

import { useAuth } from "./hooks/useAuth";
import {
  getConversationsApi, createConversationApi,
  deleteConversationApi, getMessagesApi, sendMessageApi
} from "./api/api";

import AuthScreen from "./components/auth/AuthScreen";
import Sidebar from "./components/sidebar/Sidebar";
import ChatWindow from "./components/chat/ChatWindow";
import ConfirmModal from "./components/modals/ConfirmModal";
import Toast from "./components/ui/Toast";

export default function App() {

  // ── Toast ─────────────────────────────────────────────────────────────────────
  const [toast, setToast] = useState(null);
  const showToast = (message, type = "success") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  // ── Auth ──────────────────────────────────────────────────────────────────────
  const auth = useAuth(showToast);

  // ── Chat State ────────────────────────────────────────────────────────────────
  const [conversations, setConversations] = useState([]);
  const [activeConvId, setActiveConvId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [convLoading, setConvLoading] = useState(false);

  // ── Modals ────────────────────────────────────────────────────────────────────
  const [showLogoutModal, setShowLogoutModal] = useState(false);
  const [deleteTargetId, setDeleteTargetId] = useState(null);

  // ── Session expired helper ────────────────────────────────────────────────────
  const handleExpired = (res) => {
    if (res.status === 401 || res.status === 403) {
      showToast("Session expired. Please login again.", "error");
      auth.handleLogout();
      return true;
    }
    return false;
  };

  // ── Load conversations on login ───────────────────────────────────────────────
  useEffect(() => {
    if (auth.token) fetchConversations();
  }, [auth.token]);

  const fetchConversations = async () => {
    try {
      const res = await getConversationsApi(auth.token);
      if (handleExpired(res)) return;
      const data = await res.json();
      setConversations(data);
      if (data.length > 0) selectConversation(data[0].id);
    } catch (err) { console.error(err); }
  };

  const selectConversation = async (id) => {
    setActiveConvId(id);
    setConvLoading(true);
    try {
      const res = await getMessagesApi(auth.token, id);
      if (handleExpired(res)) return;
      const data = await res.json();
      setMessages(data);
    } catch (err) { console.error(err); }
    setConvLoading(false);
  };

  // ── New Conversation ──────────────────────────────────────────────────────────
  const createNewConversation = async () => {
    try {
      const res = await createConversationApi(auth.token);
      if (handleExpired(res)) return;
      const newConvo = await res.json();
      setConversations(prev => [newConvo, ...prev]);
      setActiveConvId(newConvo.id);
      setMessages([]);
    } catch (err) { console.error(err); }
  };

  // ── Delete Conversation ───────────────────────────────────────────────────────
  const confirmDeleteConversation = async () => {
    if (!deleteTargetId) return;
    const id = deleteTargetId;
    setDeleteTargetId(null);
    try {
      const res = await deleteConversationApi(auth.token, id);
      if (handleExpired(res)) return;
      const remaining = conversations.filter(c => c.id !== id);
      setConversations(remaining);
      if (activeConvId === id) {
        if (remaining.length > 0) selectConversation(remaining[0].id);
        else { setActiveConvId(null); setMessages([]); }
      }
      showToast("Conversation deleted.");
    } catch (err) {
      console.error(err);
      showToast("Failed to delete conversation.", "error");
    }
  };

  // ── Send Message ──────────────────────────────────────────────────────────────
  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const userText = input.trim();
    setInput("");
    setLoading(true);

    setMessages(prev => [...prev, {
      id: Date.now(), role: "user",
      content: userText, timestamp: new Date().toISOString(),
    }]);

    try {
      const res = await sendMessageApi(auth.token, activeConvId, userText);
      if (handleExpired(res)) return;
      const data = await res.json();

      if (!activeConvId || data.conversation_id !== activeConvId) {
        setActiveConvId(data.conversation_id);
        setConversations(prev => {
          const exists = prev.find(c => c.id === data.conversation_id);
          if (exists) return prev.map(c =>
            c.id === data.conversation_id ? { ...c, title: data.conversation_title } : c
          );
          return [{ id: data.conversation_id, title: data.conversation_title, created_at: new Date().toISOString() }, ...prev];
        });
      } else {
        setConversations(prev =>
          prev.map(c => c.id === data.conversation_id ? { ...c, title: data.conversation_title } : c)
        );
      }

      setMessages(prev => [...prev, {
        id: Date.now() + 1, role: "assistant",
        content: data.answer, timestamp: new Date().toISOString(),
      }]);

    } catch (err) { console.error(err); }
    setLoading(false);
  };

  // ── Logout ────────────────────────────────────────────────────────────────────
  const confirmLogout = () => {
    setShowLogoutModal(false);
    showToast("Signed out successfully.");
    setTimeout(() => {
      auth.handleLogout();
      setConversations([]);
      setActiveConvId(null);
      setMessages([]);
    }, 800);
  };

  // ═══════════════════════════════════════════════════════════════════════════════
  // RENDER
  // ═══════════════════════════════════════════════════════════════════════════════

  if (!auth.token) return <AuthScreen {...auth} />;

  const activeConv = conversations.find(c => c.id === activeConvId);

  return (
    <>
      <Toast toast={toast} />

      {showLogoutModal && (
        <ConfirmModal
          icon="⏏" iconClass="modal-icon-warn"
          title="Sign out?"
          message="You'll need to log back in to continue your conversations."
          confirmText="Yes, sign out"
          onConfirm={confirmLogout}
          onCancel={() => setShowLogoutModal(false)}
        />
      )}

      {deleteTargetId && (
        <ConfirmModal
          icon="🗑" iconClass="modal-icon-delete"
          title="Delete conversation?"
          message="This will permanently delete this conversation and all its messages. This cannot be undone."
          confirmText="Yes, delete"
          onConfirm={confirmDeleteConversation}
          onCancel={() => setDeleteTargetId(null)}
        />
      )}

      <div className="app">
        <Sidebar
          conversations={conversations}
          activeConvId={activeConvId}
          onSelectConversation={selectConversation}
          onNewConversation={createNewConversation}
          onDeleteConversation={(id) => setDeleteTargetId(id)}
          onLogout={() => setShowLogoutModal(true)}
        />
        <ChatWindow
          messages={messages}
          loading={loading}
          convLoading={convLoading}
          input={input}
          setInput={setInput}
          onSend={sendMessage}
          activeConv={activeConv}
          activeConvId={activeConvId}
        />
      </div>
    </>
  );
}
