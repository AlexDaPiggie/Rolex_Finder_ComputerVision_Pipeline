import "./HowItWorks.css";

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
        <div className="intro-columns">
          <div className="intro-text">
            <p>
              A detector finds the watch in your photo and crops the dial. A vision model (CLIP) turns the
              crop into a set of numbers. A small trained layer picks the family, such as Submariner or
              Datejust.
            </p>
            <p>
              The same numbers are then compared with the catalog of 95 variants, so the answer comes with
              reference numbers you can search. A first scan can take up to 45 seconds while the server
              wakes up. After that it takes about a second.
            </p>
          </div>
          <img
            className="intro-shot"
            src="/how-it-works.jpg"
            alt="Result page for a sample photo: family name, a Strong match label, and the closest variants with reference numbers"
            loading="lazy"
          />
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
          Perpetual and President, and it sometimes mixes up Submariner and Sea-Dweller. Variants were only
          measured well on shop photos. Treat every answer as the closest estimate, then check it with
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
