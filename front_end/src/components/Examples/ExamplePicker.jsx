import "../States/States.css";
import examples from "../../data/examples.json";
import { displayName } from "../../utils/format";

// Sits under the upload button. Small hairline thumbnails, the chosen one is underlined.
function ExamplePicker({ onPick, activeId }) {
  return (
    <div className="samples">
      <p>No photo to hand? Try a sample.</p>
      <div className="sample-row">
        {examples.map((ex) => (
          <button
            key={ex.id}
            type="button"
            className="sample"
            aria-pressed={activeId === ex.id}
            aria-label={`Sample: ${displayName(ex.id)}`}
            title={displayName(ex.id)}
            onClick={() => onPick(ex)}
          >
            <img src={ex.image} alt="" loading="lazy" />
          </button>
        ))}
      </div>
      <span className="credit">
        Open-licence photos. <a href="/examples/credits.html" target="_blank" rel="noopener noreferrer">Credits</a>
      </span>
    </div>
  );
}

export default ExamplePicker;
