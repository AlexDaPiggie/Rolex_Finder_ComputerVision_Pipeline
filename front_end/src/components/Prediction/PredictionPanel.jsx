import "./PredictionPanel.css";
import "../States/States.css";

import Header from "./Header";
import VariantList from "./VariantList";
import ProbabilityTable from "./ProbabilityTable";
import { displayName, formatPct, confidenceLevel, closeCall, VERDICT } from "../../utils/format";

function PredictionPanel({ prediction }) {
  const matches = (prediction.variant_candidates ?? []).map((candidate) => ({
    id: candidate.id,
    model: candidate.display_name,
    references: candidate.reference_examples ?? [],
  }));

  const probabilities = Object.entries(prediction.probabilities ?? {})
    .sort((a, b) => b[1] - a[1])
    .map(([key, value]) => ({ key, name: displayName(key), value: formatPct(value), raw: value }));

  const modelName = displayName(prediction.predicted_class);
  const level = confidenceLevel(prediction.confidence);
  const close = closeCall(probabilities);

  return (
    <div className="prediction-wrapper">
      <Header prediction={{ model: modelName, verdict: VERDICT[level] }} />

      {level === "low" && (
        <p className="plain-note" role="status">
          No clear winner. These are the closest references. A sharper, front-facing photo with the whole
          watch in frame usually helps.
        </p>
      )}

      {close && (
        <p className="plain-note" role="status">
          Close call: {close}
        </p>
      )}

      {matches.length > 0 && <VariantList matches={matches} note={prediction.variant_note} />}

      {probabilities.length > 0 && <ProbabilityTable probabilities={probabilities} />}

      <p className="disclaimer">
        Unofficial tool, not affiliated with Rolex. It estimates the model from a photo and does not
        authenticate watches. Confirm with an authorised dealer before buying.
      </p>
    </div>
  );
}

export default PredictionPanel;
