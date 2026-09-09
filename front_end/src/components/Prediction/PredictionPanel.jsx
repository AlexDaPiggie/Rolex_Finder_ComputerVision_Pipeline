import "./PredictionPanel.css";

import Header from "./Header";
import MatchNotice from "./MatchNotice";
import CandidateCards from "./CandidateCards";
import ProbabilityTable from "./ProbabilityTable";
import Summary from "./Summary";

function PredictionPanel({ prediction }) {
  const matches = (prediction.variant_candidates ?? []).map((candidate, index) => ({
    rank: index + 1,
    model: candidate.display_name,
    score: candidate.score * 100,
    references: candidate.reference_examples ?? [],
  }));

  const probabilities = Object.entries(prediction.probabilities ?? {}).map(
    ([name, value]) => ({
      name: name.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase()),
      value: `${(value * 100).toFixed(4)}%`,
    }),
  );

  return (
    <div className="prediction-wrapper">

      <Header prediction={{
        model: prediction.model_name ?? prediction.predicted_class,
        confidence: (prediction.confidence * 100).toFixed(2),
      }} />

      {matches.length > 0 && <MatchNotice note={prediction.variant_note} />}

      {matches.length > 0 && <CandidateCards matches={matches} />}

      {probabilities.length > 0 && <ProbabilityTable probabilities={probabilities} />}

      {matches.length > 0 && (
        <Summary
          modelName={prediction.model_name ?? prediction.predicted_class}
          matches={matches}
        />
      )}

    </div>
  );
}

export default PredictionPanel;
