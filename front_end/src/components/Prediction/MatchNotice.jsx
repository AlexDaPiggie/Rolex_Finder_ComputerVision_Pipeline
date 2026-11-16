import "./MatchNotice.css";

function MatchNotice({ note, status }) {
  const title = status === "matched_known_variant" ? "Likely variants" : "Closest known variants";
  return (
    <section className="match-notice">

      <h2>
        {title}
      </h2>

      <p>{note}</p>

    </section>
  );
}

export default MatchNotice;
