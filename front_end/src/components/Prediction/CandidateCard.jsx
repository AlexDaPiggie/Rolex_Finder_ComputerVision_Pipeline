import "./CandidateCard.css";

function CandidateCard({
  rank,
  model,
  score,
  references
}) {
  const buildImageSearchUrl = (ref) => {
    const query = encodeURIComponent(`${model} ${ref}`);
    return `https://www.google.com/search?tbm=isch&q=${query}`;
  };

  return (
    <div className="candidate-card">

      <div className="candidate-number">
        {rank}
      </div>

      <h3>
        {model}
      </h3>

      <div className="score-section">

    <p>
        Match Score: <strong>{score.toFixed(2)}%</strong>
    </p>

</div>

      <div className="references">

        {references.map((ref, index) => (
          <a
            key={`${ref}-${index}`}
            href={buildImageSearchUrl(ref)}
            target="_blank"
            rel="noopener noreferrer"
            title={`Search Google Images for ${model} ${ref}`}
          >
            {ref}
          </a>
        ))}

      </div>

    </div>
  );
}

export default CandidateCard;
