import "./UploadBox.css";
import { useCallback, useEffect, useRef, useState } from "react";
import WatchIcon from "../UI/WatchIcon";
import "../States/States.css";
import ExamplePicker from "../Examples/ExamplePicker";

const PREDICT_URL = "https://alexdapiggie--rolex-watch-recognizer-rolexwatchapi-web.modal.run/predict";

function dataURLtoFile(dataurl, filename) {
  try {
    const arr = dataurl.split(",");
    const mime = arr[0].match(/:(.*?);/)[1];
    const bstr = atob(arr[1]);
    let n = bstr.length;
    const u8arr = new Uint8Array(n);
    while (n--) {
      u8arr[n] = bstr.charCodeAt(n);
    }
    return new File([u8arr], filename, { type: mime });
  } catch {
    return null;
  }
}

const MAX_BYTES = 15 * 1024 * 1024;
const TIMEOUT_MS = 90000;

function UploadBox({ onPrediction, onError, onScanChange, serverState, controlsRef }) {
  const [image, setImage] = useState(() => {
    try {
      return sessionStorage.getItem("rolex_image") || null;
    } catch {
      return null;
    }
  });
  const [fileName, setFileName] = useState(() => {
    try {
      return sessionStorage.getItem("rolex_filename") || "";
    } catch {
      return "";
    }
  });
  const [file, setFile] = useState(() => {
    try {
      const savedImage = sessionStorage.getItem("rolex_image");
      const savedName = sessionStorage.getItem("rolex_filename") || "Pasted image";
      if (savedImage) return dataURLtoFile(savedImage, savedName);
      return null;
    } catch {
      return null;
    }
  });
  const [isScanning, setIsScanning] = useState(false);
  const [localError, setLocalError] = useState("");
  const [dragging, setDragging] = useState(false);
  const [activeExample, setActiveExample] = useState(null);

  const inputRef = useRef(null);
  const scanIdRef = useRef(0);

  const selectImage = useCallback((selectedFile) => {
    if (!selectedFile.type.startsWith("image/")) {
      setLocalError("That file is not an image. Choose a JPG, PNG or WebP photo.");
      return;
    }
    if (selectedFile.size > MAX_BYTES) {
      setLocalError("That image is over 15 MB. Choose a smaller photo.");
      return;
    }
    setLocalError("");
    onError?.(null);
    setActiveExample(null);
    const reader = new FileReader();
    reader.onload = () => {
      const dataUrl = reader.result;
      setImage(dataUrl);
      try {
        sessionStorage.setItem("rolex_image", dataUrl);
        sessionStorage.setItem("rolex_filename", selectedFile.name || "Pasted image");
        sessionStorage.removeItem("rolex_prediction");
      } catch {}
    };
    reader.readAsDataURL(selectedFile);

    setFile(selectedFile);
    setFileName(selectedFile.name || "Pasted image");
    scanIdRef.current += 1;
    setIsScanning(false);
    onScanChange?.(false);
    onPrediction(null);
  }, [onPrediction, onError, onScanChange]);

  useEffect(() => {
    function handlePaste(event) {
      const pastedImage = Array.from(event.clipboardData?.items ?? [])
        .find((item) => item.type.startsWith("image/"))
        ?.getAsFile();

      if (!pastedImage) return;

      event.preventDefault();
      selectImage(pastedImage);
    }

    document.addEventListener("paste", handlePaste);
    return () => document.removeEventListener("paste", handlePaste);
  }, [selectImage]);

  function pickExample(ex) {
    scanIdRef.current += 1;
    setIsScanning(false);
    onScanChange?.(false);
    setLocalError("");
    onError?.(null);
    setActiveExample(ex.id);
    setImage(ex.image);
    setFileName(`Sample: ${ex.id.replaceAll("_", " ")}`);
    setFile(null);
    onPrediction(ex.result, false);
    // Load the real file so FIND also works live on the sample
    fetch(ex.image)
      .then((r) => r.blob())
      .then((blob) => setFile(new File([blob], `${ex.id}.jpg`, { type: blob.type })))
      .catch(() => {});
    try {
      sessionStorage.removeItem("rolex_image");
      sessionStorage.removeItem("rolex_filename");
    } catch {
      /* storage unavailable */
    }
  }

  function handleDrop(event) {
    event.preventDefault();
    setDragging(false);
    const dropped = event.dataTransfer?.files?.[0];
    if (dropped) selectImage(dropped);
  }

  function handleImage(event) {
    const selectedFile = event.target.files[0];
    if (selectedFile) selectImage(selectedFile);
  }

  function removeImage() {
    setImage(null);
    setFile(null);
    setFileName("");
    scanIdRef.current += 1;
    setIsScanning(false);
    onScanChange?.(false);
    setLocalError("");
    onError?.(null);
    setActiveExample(null);
    onPrediction(null);

    try {
      sessionStorage.removeItem("rolex_image");
      sessionStorage.removeItem("rolex_filename");
      sessionStorage.removeItem("rolex_prediction");
    } catch {}

    // Allows selecting the same image again
    if (inputRef.current) inputRef.current.value = "";
  }

  async function findWatch() {
    if (!file || isScanning) return;

    const scanId = ++scanIdRef.current;
    setIsScanning(true);
    onScanChange?.(true);
    setLocalError("");
    onError?.(null);
    onPrediction(null);

    const formData = new FormData();
    formData.append("file", file);

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);

    try {
      const response = await fetch(PREDICT_URL, {
        method: "POST",
        body: formData,
        signal: controller.signal,
      });

      if (!response.ok) {
        const error = new Error("http");
        error.kind = response.status >= 500 ? "server" : "file";
        throw error;
      }

      const result = await response.json();
      if (scanId !== scanIdRef.current) return;
      if (!result?.predicted_class || !result?.probabilities) {
        {
        const error = new Error("empty");
        error.kind = "server";
        throw error;
      }
      }

      onPrediction(result);
    } catch (err) {
      if (scanId === scanIdRef.current) {
        onPrediction(null);
        onError?.({
          kind: err.name === "AbortError" ? "timeout" : err instanceof TypeError ? "network" : err.kind ?? "server",
        });
      }
    } finally {
      clearTimeout(timer);
      if (scanId === scanIdRef.current) {
        setIsScanning(false);
        onScanChange?.(false);
      }
    }
  }

  useEffect(() => {
    if (!controlsRef) return;
    controlsRef.current = { find: findWatch, choose: () => inputRef.current?.click() };
  });

  return (
    <div className="upload-box">
      <h1 className="logo">
    <span>ROLEX</span>
    Finder
</h1>

      <div
        className={`drop-zone${dragging ? " dragging" : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
      >
        {image ? (
          <img
            src={image}
            alt="Preview"
            className="preview-image"
          />
        ) : (
          <>
            <WatchIcon />

            <p>Ctrl + V to paste, or drop a photo</p>

            <span>or</span>

            <button
              type="button"
              className="browse-btn"
              onClick={() => inputRef.current.click()}
            >
              Browse File
            </button>
          </>
        )}
      </div>

      {/* Only show after an image is selected */}
      {image && (
        <>
          <p className="filename">{fileName}</p>

          <div className="image-actions">
            <button
              type="button"
              className="replace-btn"
              onClick={() => inputRef.current.click()}
            >
              Replace
            </button>

            <button
              type="button"
              className="remove-btn"
              onClick={removeImage}
            >
              Remove
            </button>
          </div>
        </>
      )}

      <input
        type="file"
        accept="image/*"
        ref={inputRef}
        style={{ display: "none" }}
        onChange={handleImage}
      />

      <button
        className="find-btn"
        disabled={!image || isScanning}
        onClick={findWatch}
      >
        {isScanning ? "IDENTIFYING" : "FIND"}
      </button>
      {localError && (
        <p className="upload-error" role="alert">
          {localError}
        </p>
      )}
      {serverState !== "ready" && !isScanning && (
        <p className="server-note">The server is waking up. The first scan can take up to 45 seconds.</p>
      )}

      <ExamplePicker onPick={pickExample} activeId={activeExample} />
    </div>
  );
}

export default UploadBox;
