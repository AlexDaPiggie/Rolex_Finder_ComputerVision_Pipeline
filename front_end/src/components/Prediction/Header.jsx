import "./Header.css";

function Header({ prediction }) {
  return (
    <header className="prediction-header">

      <div>

        <p className="prediction-label">
          PREDICTED ROLEX MODEL
        </p>

        <h1 className="prediction-model">
          {prediction.model}
        </h1>

      </div>

      <div className="confidence">

        <span>
          Confidence
        </span>

        <h2>
          {prediction.confidence}%
        </h2>

      </div>

    </header>
  );
}

export default Header;