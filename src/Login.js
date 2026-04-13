import { useState } from "react";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const login = async () => {
    const res = await fetch("http://127.0.0.1:8000/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });

    const data = await res.json();
    alert(data.msg);
  };

  return (
    <div>
      <h2>Login</h2>
      <input onChange={e => setUsername(e.target.value)} placeholder="User" />
      <input type="password" onChange={e => setPassword(e.target.value)} />
      <button onClick={login}>Login</button>
    </div>
  );
}

const loadTheme = async () => {
  const res = await fetch("http://127.0.0.1:8000/auth/get-theme?username=admin");
  const data = await res.json();
  setTheme(data.theme);
};

export default function Login({ onLogin }) {

  const login = async () => {
    // API call here
    onLogin();   // ✅ switch to dashboard	
	loadTheme();
  };
  
	<div style={{ display: "flex", justifyContent: "space-between" }}>
	  <h2>SmartMerge SaaS</h2>

	  <select onChange={e => setTheme(e.target.value)}>
		<option>dark</option>
		<option>light</option>
	  </select>
	</div>
}

export default function Login({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const login = async () => {
    const res = await fetch("http://127.0.0.1:8000/auth/login", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ username, password })
    });

    const data = await res.json();

    if (data.access_token) {
      localStorage.setItem("token", data.access_token); // 🔐 SAVE TOKEN
      localStorage.setItem("user", username);
      onLogin();
    } else {
      alert("Login failed");
    }
  };

  return (
    <div>
      <input onChange={e => setUsername(e.target.value)} />
      <input type="password" onChange={e => setPassword(e.target.value)} />
      <button onClick={login}>Login</button>
    </div>
  );
}