import "./Home.css";
import { useState } from "react";
import UploadBox from "../components/Upload/UploadBox.jsx";
import PredictionPanel from "../components/Prediction/PredictionPanel.jsx";
import TutorialPanel from "../components/Tutorial/TutorialPanel.jsx";

function Home() {
  const [prediction, setPrediction] = useState(() => {
    try {
      const saved = sessionStorage.getItem("rolex_prediction");
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const handlePrediction = (newPred) => {
    setPrediction(newPred);
    try {
      if (newPred) {
        sessionStorage.setItem("rolex_prediction", JSON.stringify(newPred));
      } else {
        sessionStorage.removeItem("rolex_prediction");
      }
    } catch {}
  };

  return (
    <main className="home">
      <aside className="upload-panel">
        <UploadBox onPrediction={handlePrediction} />
      </aside>

      <section className="prediction-panel">
        {prediction ? (
          <PredictionPanel prediction={prediction} />
        ) : (
          <TutorialPanel />
        )}
      </section>
    </main>
  );
}

export default Home;
