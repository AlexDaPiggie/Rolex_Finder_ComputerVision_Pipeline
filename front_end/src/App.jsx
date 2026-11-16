import { useEffect, useState } from "react";
import NavBar from "./components/UI/NavBar";
import Home from "./pages/Home";
import Authors from "./pages/Authors";

const HEALTH_URL = "https://alexdapiggie--rolex-watch-recognizer-rolexwatchapi-web.modal.run/health";

// Clear stored session on page refresh/reload
try {
  const navEntry = performance.getEntriesByType("navigation")[0];
  if (navEntry && navEntry.type === "reload") {
    sessionStorage.removeItem("rolex_image");
    sessionStorage.removeItem("rolex_filename");
    sessionStorage.removeItem("rolex_prediction");
  }
} catch {}

function App() {
  const [page, setPage] = useState("home");
  // "warming" until the backend answers the health ping, then "ready"
  const [serverState, setServerState] = useState("warming");

  useEffect(() => {
    // Ping backend on page load to wake / warm the container
    fetch(HEALTH_URL, { method: "GET" })
      .then((r) => setServerState(r.ok ? "ready" : "warming"))
      .catch(() => setServerState("warming"));
  }, []);

  return (
    <>
      <NavBar currentPage={page} onPageChange={setPage} />
      {page === "home" ? <Home serverState={serverState} /> : <Authors />}
    </>
  );
}

export default App;
