import "./PredictionPanel.css";
import "../States/States.css";

import Header from "./Header";
import MatchNotice from "./MatchNotice";
import CandidateCards from "./CandidateCards";
import ProbabilityTable from "./ProbabilityTable";
import Summary from "./Summary";
import { displayName, formatPct, confidenceLevel, VERDICT } from "../../utils/format";

function PredictionPanel({ prediction }) {
  const matches = (prediction.variant_candidates ?? []).map((candidate, index) => ({
    rank: index + 1,
    model: candidate.display_name,
    score: candidate.score * 100,
    references: candidate.reference_examples ?? [],
  }));

  const probabilities = Object.entries(prediction.probabilities ?? {})
    .sort((a, b) => b[1] - a[1])
    .map(([name, value]) => ({
      name: displayName(name),
      value: formatPct(value),
      raw: value,
    }));

  const modelName = displayName(prediction.predicted_class);
  const level = confidenceLevel(prediction.confidence);

  return (
    <div className="prediction-wrapper">

      <Header prediction={{
        model: modelName,
        verdict: VERDICT[level],
      }} />

      {level === "low" && (
        <p className="plain-note" role="status">
          No clear winner. These are the closest references. A sharper, front-facing photo with the whole
          watch in frame usually helps.
        </p>
      )}

      {matches.length > 0 && (
        <MatchNotice note={prediction.variant_note} status={prediction.variant_status} />
      )}

      {matches.length > 0 && <CandidateCards matches={matches} />}

      {probabilities.length > 0 && <ProbabilityTable probabilities={probabilities} />}

      {matches.length > 0 && (
        <Summary modelName={modelName} matches={matches} />
      )}

      <p className="disclaimer">
        Unofficial tool, not affiliated with Rolex. It estimates the model from a photo and does not
        authenticate watches. Confirm with an authorised dealer before buying.
      </p>

    </div>
  );
}

export default PredictionPanel;
