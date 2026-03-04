import { useRef, useEffect } from "react";
import MarkdownRenderer from "../ui/MarkdownRenderer";
import ChatInput from "./ChatInput";

export default function ChatWindow({
  messages, loading, convLoading,
  input, setInput, onSend,
  activeConv, activeConvId,
}) {
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  return (
    <div className="main-chat">

      {/* ── Topbar ── */}
      <div className="chat-topbar">
        <div className="topbar-left">
          <div className="topbar-status" />
          <span className="topbar-title">{activeConv?.title || "College Assistant"}</span>
        </div>
        <div className="topbar-model">llama-3.3 · groq</div>
      </div>

      {/* ── Messages ── */}
      <div className="chat-container">

        {convLoading && (
          <div className="empty-state">
            <div className="empty-icon">✦</div>
            <p>Loading messages…</p>
          </div>
        )}

        {!convLoading && messages.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">✦</div>
            <h3>What's on your mind?</h3>
            <p>Start a conversation below to get going.</p>
          </div>
        )}

        {!convLoading && messages.map((msg, index) => (
          <div
            key={msg.id ?? index}
            className={`msg-row ${msg.role === "user" ? "user-row" : "bot-row"}`}
          >
            {msg.role === "assistant" && <div className="avatar bot-avatar">AI</div>}
            <div className={msg.role === "user" ? "user-msg" : "bot-msg"}>
              {msg.role === "assistant"
                ? <MarkdownRenderer text={msg.content} />
                : msg.content
              }
              <div className="msg-time">
                {new Date(msg.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
              </div>
            </div>
            {msg.role === "user" && <div className="avatar user-avatar">U</div>}
          </div>
        ))}

        {loading && (
          <div className="msg-row bot-row">
            <div className="avatar bot-avatar">AI</div>
            <div className="bot-msg typing-msg">
              <span className="dot" /><span className="dot" /><span className="dot" />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* ── Input ── */}
      <ChatInput
        input={input}
        setInput={setInput}
        onSend={onSend}
        loading={loading}
        activeConvId={activeConvId}
      />

    </div>
  );
}
