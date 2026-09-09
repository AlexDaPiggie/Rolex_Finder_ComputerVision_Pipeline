import "./Summary.css";

function referenceText(references) {
  return references.length > 0 ? references.join(", ") : "No reference IDs available";
}

function Summary({ modelName, matches }) {
  const closestMatch = matches[0];
  const nextMatch = matches[1];

  return (
    <section className="summary">

      <h2>Prediction Summary</h2>

      <p>
        The predicted watch is <strong>{modelName}</strong>. The closest known
        variant is <strong>{closestMatch.model}</strong>, with reference IDs{" "}
        <strong>{referenceText(closestMatch.references)}</strong>.
        {nextMatch && (
          <>
            {" "}The next closest match is <strong>{nextMatch.model}</strong>,
            with reference IDs <strong>{referenceText(nextMatch.references)}</strong>.
          </>
        )}
      </p>

    </section>
  );
}

export default Summary;
