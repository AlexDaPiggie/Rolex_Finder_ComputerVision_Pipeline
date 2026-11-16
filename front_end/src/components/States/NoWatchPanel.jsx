import "./States.css";

function NoWatchPanel({ onChoose }) {
  return (
    <div className="status" role="status">
      <p className="status-line">No watch found in this photo.</p>
      <p className="status-detail">
        Show the dial straight on, in daylight, filling most of the frame. Rolex Finder only knows Rolex watches.
      </p>
      <div className="status-actions">
        <button type="button" className="text-action" onClick={onChoose}>
          Choose another photo
        </button>
      </div>
    </div>
  );
}

export default NoWatchPanel;
