import "./Home.css";
import { useRef, useState } from "react";
import UploadBox from "../components/Upload/UploadBox.jsx";
import PredictionPanel from "../components/Prediction/PredictionPanel.jsx";
import Intro from "../components/Intro/Intro.jsx";
import LoadingPanel from "../components/States/LoadingPanel.jsx";
import ErrorPanel from "../components/States/ErrorPanel.jsx";
import NoWatchPanel from "../components/States/NoWatchPanel.jsx";
import { NO_WATCH } from "../utils/format";

function Home({ serverState }) {
  const [prediction, setPrediction] = useState(() => {
    try {
      const saved = sessionStorage.getItem("rolex_prediction");
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState(null);
  const controlsRef = useRef(null);

  // persist=false for samples: their image is not saved, so a saved result would come back without a photo
  const handlePrediction = (newPred, persist = true) => {
    setPrediction(newPred);
    setError(null);
    try {
      if (newPred && persist) {
        sessionStorage.setItem("rolex_prediction", JSON.stringify(newPred));
      } else if (!newPred) {
        sessionStorage.removeItem("rolex_prediction");
      } else {
        sessionStorage.removeItem("rolex_prediction");
      }
    } catch {}
  };

  let content;
  if (isScanning) {
    content = <LoadingPanel serverState={serverState} />;
  } else if (error) {
    content = <ErrorPanel kind={error.kind} onRetry={() => controlsRef.current?.find()} onChoose={() => controlsRef.current?.choose()} />;
  } else if (prediction?.predicted_class === NO_WATCH) {
    content = <NoWatchPanel onChoose={() => controlsRef.current?.choose()} />;
  } else if (prediction) {
    content = <PredictionPanel prediction={prediction} />;
  } else {
    content = <Intro />;
  }

  return (
    <main className="home">
      <aside className="upload-panel">
        <UploadBox
          onPrediction={handlePrediction}
          onError={setError}
          onScanChange={setIsScanning}
          serverState={serverState}
          controlsRef={controlsRef}
        />
      </aside>

      <section className="prediction-panel" aria-live="polite">
        {content}
      </section>
    </main>
  );
}

export default Home;
