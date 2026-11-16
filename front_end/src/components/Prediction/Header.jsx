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

      <p className="confidence">{prediction.verdict}</p>

    </header>
  );
}

export default Header;
