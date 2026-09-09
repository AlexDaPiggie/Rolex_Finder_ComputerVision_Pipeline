import "./UploadBox.css";
import { useCallback, useEffect, useRef, useState } from "react";
import WatchIcon from "../UI/WatchIcon";

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

function UploadBox({ onPrediction }) {
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

  const inputRef = useRef(null);
  const scanIdRef = useRef(0);

  const selectImage = useCallback((selectedFile) => {
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
    onPrediction(null);
  }, [onPrediction]);

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
    onPrediction(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(PREDICT_URL, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("The image could not be scanned");

      const result = await response.json();
      if (scanId !== scanIdRef.current) return;
      if (!result?.predicted_class || !result?.probabilities) {
        throw new Error("The scan returned no prediction");
      }

      onPrediction(result);
    } catch {
      // A failed scan intentionally leaves the prediction area blank.
      if (scanId === scanIdRef.current) onPrediction(null);
    } finally {
      if (scanId === scanIdRef.current) setIsScanning(false);
    }
  }

  return (
    <div className="upload-box">
      <h1 className="logo">
    <span>ROLEX</span>
    Finder
</h1>

      <div className="drop-zone">
        {image ? (
          <img
            src={image}
            alt="Preview"
            className="preview-image"
          />
        ) : (
          <>
            <WatchIcon />

            <p>Ctrl + V to Paste image</p>

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
        {isScanning ? "SCANNING..." : "FIND"}
      </button>
      {isScanning && (
        <p className = "scan-note">
          Note: First-time running may take up to 40s
        </p>
      )}
    </div>
  );
}

export default UploadBox;
