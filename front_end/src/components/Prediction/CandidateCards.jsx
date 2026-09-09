import "./CandidateCards.css";
import CandidateCard from "./CandidateCard";

function CandidateCards({ matches }) {
  return (
    <section className="candidate-section">

      <h2 className="candidate-title">
        Variant Candidates
      </h2>

      <div className="candidate-grid">
        {matches.map((card) => (
          <CandidateCard
            key={card.rank}
            {...card}
          />
        ))}
      </div>

    </section>
  );
}

export default CandidateCards;