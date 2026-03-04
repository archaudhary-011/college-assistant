export default function AuthScreen({
  authMode, authError, authLoading, registerSuccess,
  username, password,
  setUsername, setPassword, setAuthError,
  handleLogin, handleRegister, switchMode,
}) {
  return (
    <div className="auth-screen">
      <div className="auth-bg-orb orb1" />
      <div className="auth-bg-orb orb2" />

      {/* ── Left Panel ── */}
      <div className="auth-left">
        <div className="auth-brand">
          <div className="auth-brand-icon">✦</div>
          <span className="auth-brand-name">College Assistant</span>
        </div>
        <div className="auth-left-content">
          <h1 className="auth-hero-title">
            Think deeper.<br />Work faster.<br />Chat smarter.
          </h1>
          <p className="auth-hero-sub">
            A powerful AI assistant for deep work, creative exploration, and real productivity.
          </p>
          <div className="auth-features">
            <div className="auth-feature"><span>⚡</span> Instant AI responses</div>
            <div className="auth-feature"><span>💬</span> Saved chat history</div>
            <div className="auth-feature"><span>🔒</span> Secure & private</div>
          </div>
        </div>
        <div className="auth-left-footer">© 2025 College Assistant</div>
      </div>

      {/* ── Right Panel ── */}
      <div className="auth-right">
        <div className="auth-card">
          <div className="auth-tab-row">
            <button
              className={`auth-tab ${authMode === "login" ? "active" : ""}`}
              onClick={() => switchMode("login")}
            >Sign In</button>
            <button
              className={`auth-tab ${authMode === "register" ? "active" : ""}`}
              onClick={() => switchMode("register")}
            >Register</button>
          </div>

          <div className="auth-form">
            <h2 className="auth-form-title">
              {authMode === "login" ? "Welcome back" : "Create your account"}
            </h2>
            <p className="auth-form-sub">
              {authMode === "login" ? "Enter your credentials to continue." : "Get started for free, no card needed."}
            </p>

            {registerSuccess && (
              <div className="auth-success">✓ Account created! Redirecting to login…</div>
            )}
            {authError && (
              <div className="auth-error">⚠ {authError}</div>
            )}

            <div className="field-group">
              <label>Username</label>
              <input
                type="text"
                placeholder="e.g. john_doe"
                value={username}
                onChange={e => { setUsername(e.target.value); setAuthError(""); }}
                onKeyDown={e => e.key === "Enter" && (authMode === "login" ? handleLogin() : handleRegister())}
                autoFocus
              />
            </div>
            <div className="field-group">
              <label>Password</label>
              <input
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={e => { setPassword(e.target.value); setAuthError(""); }}
                onKeyDown={e => e.key === "Enter" && (authMode === "login" ? handleLogin() : handleRegister())}
              />
            </div>

            <button
              className="auth-submit-btn"
              onClick={authMode === "login" ? handleLogin : handleRegister}
              disabled={authLoading}
            >
              {authLoading
                ? <span className="btn-spinner" />
                : authMode === "login" ? "Sign In →" : "Create Account →"
              }
            </button>

            <p className="auth-switch-text">
              {authMode === "login"
                ? <>Don't have an account?{" "}<span onClick={() => switchMode("register")}>Register free</span></>
                : <>Already have an account?{" "}<span onClick={() => switchMode("login")}>Sign in</span></>
              }
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
