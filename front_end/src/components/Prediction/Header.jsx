import "./Header.css";

function Header({ prediction }) {
  return (
    <header className="prediction-header">
      <h1 className="prediction-model">{prediction.model}</h1>
      <p className="confidence">{prediction.verdict}</p>
    </header>
  );
}

export default Header;
