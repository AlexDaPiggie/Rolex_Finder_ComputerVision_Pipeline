import "./MatchNotice.css";

function MatchNotice({ note }) {
  return (
    <section className="match-notice">

      <h2>
        Closest known matches
      </h2>

      <p>{note}</p>

    </section>
  );
}

export default MatchNotice;
