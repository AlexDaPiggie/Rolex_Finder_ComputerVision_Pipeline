import "./HowItWorks.css";
import { useEffect, useRef, useState } from "react";

// Silent explainer (Manim, see animation/). Plays only while visible, never autoplays for reduced motion.
function ExplainerVideo() {
  const ref = useRef(null);
  const [playing, setPlaying] = useState(false);
  const userPaused = useRef(false);

  useEffect(() => {
    const video = ref.current;
    if (!video) return undefined;
    let reduce = false;
    try {
      reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    } catch {}
    if (reduce || typeof IntersectionObserver === "undefined") return undefined;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !userPaused.current) video.play().catch(() => {});
        else video.pause();
      },
      { threshold: 0.4 }
    );
    observer.observe(video);
    return () => observer.disconnect();
  }, []);

  const toggle = () => {
    const video = ref.current;
    if (!video) return;
    if (video.paused) {
      userPaused.current = false;
      video.play().catch(() => {});
    } else {
      userPaused.current = true;
      video.pause();
    }
  };

  return (
    <figure className="explainer">
      <video
        ref={ref}
        className="explainer-video"
        src="/how-it-works.mp4"
        poster="/how-it-works-poster.jpg"
        muted
        loop
        playsInline
        preload="none"
        onPlay={() => setPlaying(true)}
        onPause={() => setPlaying(false)}
        aria-label="Animation: the watch is found in the photo, the dial is cropped, turned into 512 numbers, the family is picked, and the closest variants are listed"
      />
      <figcaption>
        <button type="button" className="explainer-toggle" onClick={toggle}>
          {playing ? "Pause" : "Play"}
        </button>
        <span>Silent, about 30 seconds. Sample photo: ajay_suresh, CC BY 2.0.</span>
      </figcaption>
    </figure>
  );
}

function HowItWorks() {
  return (
    <div className="info-view">
    <div className="intro">
      <h2 className="intro-title">How it works</h2>
      <p className="intro-lead">
        What happens to your photo, and how well the answer can be trusted.
      </p>

      <section className="intro-section">
        <h3>From photo to answer</h3>
        <ExplainerVideo />
        <div className="intro-text">
          <p>
            A detector finds the watch in your photo and crops the dial. A vision model (CLIP) turns the
            crop into 512 numbers. A small trained layer picks the family, such as Submariner or Datejust.
          </p>
          <p>
            The same numbers are then compared with the catalog of 95 variants, so the answer comes with
            reference numbers you can search. A first scan can take up to 45 seconds while the server
            wakes up. After that it takes about a second.
          </p>
        </div>
      </section>

      <section className="intro-section">
        <h3>How well it works</h3>
        <table className="intro-table">
          <tbody>
            <tr>
              <td>Studio photos from shops (test set)</td>
              <td>96% right family</td>
            </tr>
            <tr>
              <td>Real photos from Wikimedia Commons and Flickr (273)</td>
              <td>71% right family</td>
            </tr>
          </tbody>
        </table>
        <p className="intro-note">
          Real photos are harder: wrists, shop windows, angles and glare. The model is weakest on Oyster
          Perpetual and President, and it sometimes mixes up Submariner and Sea-Dweller. On 31 real photos with a
          reference number in the title, the right variant was the top pick 15 times and in the top three
          27 times. Treat every answer as the closest estimate, then check it with
          Google Images or a dealer.
        </p>
      </section>

      <p className="intro-note">
        Best results: one clear, front-facing photo with the dial, bezel and bracelet in view.{" "}
        <a href="https://github.com/AlexDaPiggie/Rolex_Finder_ComputerVision_Pipeline" target="_blank" rel="noopener noreferrer">
          About this project
        </a>
      </p>
    </div>
    </div>
  );
}

export default HowItWorks;
