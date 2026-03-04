export default function ConfirmModal({
  icon, iconClass, title, message, confirmText,
  onConfirm, onCancel,
}) {
  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal-box" onClick={e => e.stopPropagation()}>
        <div className={`modal-icon ${iconClass}`}>{icon}</div>
        <h3 className="modal-title">{title}</h3>
        <p className="modal-sub">{message}</p>
        <div className="modal-actions">
          <button className="modal-cancel"  onClick={onCancel}>Cancel</button>
          <button className="modal-confirm" onClick={onConfirm}>{confirmText}</button>
        </div>
      </div>
    </div>
  );
}
