import "./States.css";

const LENS_URL = "https://lens.google.com/";

// Shown when the photo looks like a watch that is not a Rolex we know. The photo is never sent anywhere by us:
// the Google Lens link only opens Lens, where the person can add the photo themselves.
function UnknownWatchPanel({ onChoose, onShowAnyway }) {
  return (
    <div className="status" role="status">
      <p className="status-line">Not a Rolex I know.</p>
      <p className="status-detail">
        This looks like a different brand, or a Rolex model outside the 14 families this tool covers. Rolex Finder
        only names Rolex watches, so it will not guess. Google Lens can search for other brands.
      </p>
      <div className="status-actions">
        <a className="text-action" href={LENS_URL} target="_blank" rel="noopener noreferrer">
          Search with Google Lens
        </a>
        <button type="button" className="text-action" onClick={onChoose}>
          Choose another photo
        </button>
        <button type="button" className="text-action" onClick={onShowAnyway}>
          Show the closest Rolex anyway
        </button>
      </div>
    </div>
  );
}

export default UnknownWatchPanel;
