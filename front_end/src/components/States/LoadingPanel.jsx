import { useEffect, useState } from "react";
import "./States.css";

// The API reports no progress, so there is no percentage. One sentence now, a second one if it runs long.
const SLOW_AFTER_SECONDS = 8;

function LoadingPanel({ serverState }) {
  const [slow, setSlow] = useState(false);

  useEffect(() => {
    const id = setTimeout(() => setSlow(true), SLOW_AFTER_SECONDS * 1000);
    return () => clearTimeout(id);
  }, []);

  const showWake = slow && serverState !== "ready";

  return (
    <div role="status" aria-live="polite" style={{ width: "100%", maxWidth: 640 }}>
      <div className="wait-line" aria-hidden="true" />
      <p className="status-line">Reading the dial and case.</p>
      {showWake && (
        <p className="status-detail">
          The server was resting, so the first look takes up to 45 seconds. Later ones are quick.
        </p>
      )}
    </div>
  );
}

export default LoadingPanel;
