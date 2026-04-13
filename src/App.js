import { useState } from "react";
import Login from "./Login";
import Dashboard from "./Dashboard";

const themes = {
  dark: { background: "#0f172a", color: "white" },
  light: { background: "white", color: "black" },
  blue: { background: "#0a192f", color: "#64ffda" }
};

function App() {
  const [theme, setTheme] = useState("dark");
  const [loggedIn, setLoggedIn] = useState(false);

  return (
    <div style={{
      background: themes[theme].background,
      color: themes[theme].color,
      minHeight: "100vh",
      padding: "20px"
    }}>

      {/* 🔽 THEME DROPDOWN */}
	  <Dashboard data={data} theme={themes[theme]} />
      <select onChange={e => setTheme(e.target.value)} value={theme}>
        <option value="dark">Dark</option>
        <option value="light">Light</option>
        <option value="blue">Blue</option>
      </select>

      <hr />

      {/* 🔽 PAGE SWITCH */}
      {loggedIn ? (
        <Dashboard />
      ) : (
        <Login onLogin={() => setLoggedIn(true)} />
      )}

    </div>
  );
}

const saveTheme = async (themeValue) => {
  await fetch("http://127.0.0.1:8000/auth/set-theme", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      username: "admin",
      theme: themeValue
    })
  });
};

export default App;