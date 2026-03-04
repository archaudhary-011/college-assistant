import { useState } from "react";
import { loginApi, registerApi } from "../api/api";

export function useAuth(showToast) {
  const [token, setToken]               = useState(localStorage.getItem("token"));
  const [username, setUsername]         = useState("");
  const [password, setPassword]         = useState("");
  const [authMode, setAuthMode]         = useState("login");
  const [authError, setAuthError]       = useState("");
  const [authLoading, setAuthLoading]   = useState(false);
  const [registerSuccess, setRegisterSuccess] = useState(false);

  const handleLogin = async () => {
    if (!username.trim() || !password.trim()) { setAuthError("Please fill in all fields."); return; }
    setAuthLoading(true); setAuthError("");
    try {
      const res = await loginApi(username, password);
      if (!res.ok) { setAuthError("Invalid username or password."); setAuthLoading(false); return; }
      const data = await res.json();
      localStorage.setItem("token", data.access_token);
      setToken(data.access_token);
      showToast("Logged in successfully.");
    } catch { setAuthError("Connection failed. Is the server running?"); }
    setAuthLoading(false);
  };

  const handleRegister = async () => {
    if (!username.trim() || !password.trim()) { setAuthError("Please fill in all fields."); return; }
    if (password.length < 4) { setAuthError("Password must be at least 4 characters."); return; }
    setAuthLoading(true); setAuthError("");
    try {
      const res = await registerApi(username, password);
      if (res.status === 409) { setAuthError("Username already taken."); setAuthLoading(false); return; }
      if (!res.ok) { setAuthError("Registration failed. Try again."); setAuthLoading(false); return; }
      setRegisterSuccess(true);
      setUsername(""); setPassword("");
      setTimeout(() => { setRegisterSuccess(false); setAuthMode("login"); }, 1800);
    } catch { setAuthError("Connection failed. Is the server running?"); }
    setAuthLoading(false);
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setToken(null);
  };

  const switchMode = (mode) => {
    setAuthMode(mode);
    setAuthError("");
    setUsername("");
    setPassword("");
  };

  return {
    token,
    username, setUsername,
    password, setPassword,
    authMode, authError, setAuthError,
    authLoading, registerSuccess,
    handleLogin, handleRegister, handleLogout,
    switchMode,
  };
}
