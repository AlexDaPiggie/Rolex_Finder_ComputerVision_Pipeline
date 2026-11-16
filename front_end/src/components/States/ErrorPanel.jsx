import "./States.css";

// One sentence per cause, so the user knows what to do next.
const COPY = {
  network: {
    line: "No connection to the server.",
    detail: "Check your network. Your photo is kept.",
  },
  timeout: {
    line: "The server did not answer in time.",
    detail: "It may still be starting up. Your photo is kept, so try again in a moment.",
  },
  file: {
    line: "That file could not be read.",
    detail: "Use a JPG, PNG or WebP photo under 15 MB.",
  },
  server: {
    line: "The server could not process this photo.",
    detail: "Try again, or choose a different photo.",
  },
};

function ErrorPanel({ kind = "server", onRetry, onChoose }) {
  const copy = COPY[kind] ?? COPY.server;
  return (
    <div className="status problem" role="alert">
      <p className="status-line">{copy.line}</p>
      <p className="status-detail">{copy.detail}</p>
      <div className="status-actions">
        {kind !== "file" && onRetry && (
          <button type="button" className="text-action" onClick={onRetry}>
            Try again
          </button>
        )}
        <button type="button" className="text-action" onClick={onChoose}>
          Choose another photo
        </button>
      </div>
    </div>
  );
}

export default ErrorPanel;
