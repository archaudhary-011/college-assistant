export default function Toast({ toast }) {
  if (!toast) return null;
  return (
    <div className={`toast toast-${toast.type}`}>
      <span className="toast-icon">{toast.type === "success" ? "✓" : "⚠"}</span>
      {toast.message}
    </div>
  );
}
