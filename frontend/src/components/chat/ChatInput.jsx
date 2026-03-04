export default function ChatInput({ input, setInput, onSend, loading, activeConvId }) {
  return (
    <div className="input-area">
      <div className="input-wrapper">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && onSend()}
          placeholder={activeConvId ? "Message College Assistant…" : "Start a new conversation…"}
        />
        <button
          onClick={onSend}
          className={`send-btn ${input.trim() && !loading ? "ready" : ""}`}
          disabled={loading || !input.trim()}
        >↑</button>
      </div>
      <p className="input-hint">
        Enter to send · College Assistant can make mistakes. Double-check important info.
      </p>
    </div>
  );
}
