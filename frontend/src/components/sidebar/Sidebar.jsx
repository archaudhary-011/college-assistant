export default function Sidebar({
  conversations, activeConvId,
  onSelectConversation, onNewConversation,
  onDeleteConversation, onLogout,
}) {
  return (
    <div className="sidebar">

      {/* ── Top ── */}
      <div className="sidebar-top">
        <div className="brand">
          <span className="brand-icon">✦</span>
          <span className="brand-name">College Assistant</span>
        </div>
        <button className="new-chat-btn" onClick={onNewConversation}>
          <span className="plus-icon">＋</span>
          <span>New conversation</span>
        </button>
      </div>

      {/* ── Conversation List ── */}
      <div className="chat-list-section">
        <div className="chat-list-label">Conversations</div>
        <div className="chat-list">
          {conversations.length === 0 && (
            <div className="no-convs">No conversations yet.</div>
          )}
          {conversations.map(conv => (
            <div
              key={conv.id}
              className={`chat-item ${conv.id === activeConvId ? "active" : ""}`}
              onClick={() => onSelectConversation(conv.id)}
            >
              <span className="chat-item-dot" />
              <span className="chat-item-title">{conv.title}</span>
              <button
                className="delete-conv-btn"
                onClick={e => { e.stopPropagation(); onDeleteConversation(conv.id); }}
                title="Delete conversation"
              >🗑</button>
            </div>
          ))}
        </div>
      </div>

      {/* ── Footer ── */}
      <div className="sidebar-footer">
        <button onClick={onLogout} className="logout-btn">
          <span>⏏</span> Sign out
        </button>
      </div>

    </div>
  );
}
