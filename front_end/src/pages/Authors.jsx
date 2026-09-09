import "./Authors.css";

const AUTHORS_DATA = [
  {
    name: "Phong Nguyen",
    role: "Deep Learning / Backend",
    desc: "Built the Rolex classification model, web-scraping pipeline, recognition pipeline, backend API, model integration, and Modal deployment setup.",
    image: "images/phong.jpg",
    contacts: [
      { label: "Github", url: "https://github.com/AlexDaPiggie" },
      { label: "LinkedIn", url: "https://www.linkedin.com/in/hoai-phong-nguyen-9367a4384/" }
    ],
    donation_qr: "images/phong_kofi.png",
    donation_url: "https://ko-fi.com/phong_placeholder",
    donation_caption: "Support project maintenance :cursed_tears: Spent money on AI models, now I'm broke"
  },
  {
    name: "Huy Phan",
    role: "Web Developing / UI-UX Design",
    desc: "Developed the website from Figma design, Creating interactions, visual effects, UI & UX refinement, and Vercel deployment.",
    image: "images/huy.jpg",
    contacts: [
      { label: "Github", url: "https://github.com/hertzy-da-poet" },
      { label: "Portfolio Website", url: "https://hertzy-da-poet.github.io/Hugo-Portfolio/" }
    ],
    donation_qr: "images/huy_donor.png",
    donation_url: "https://ko-fi.com/huy_placeholder",
    donation_caption: "Help me fund the side quests. The main story is getting expensive :skull-cry:"
  }
];

function Authors() {
  const renderCaption = (caption) => {
    const parts = [];
    let remaining = caption;
    const emojiMap = {
      ":cursed_tears:": "images/cursed_tears.png",
      ":skull-cry:": "images/skull-cry.png"
    };

    while (remaining) {
      const match = remaining.match(/:cursed_tears:|:skull-cry:/);
      if (!match) {
        parts.push(remaining);
        break;
      }
      const index = match.index;
      if (index > 0) {
        parts.push(remaining.substring(0, index));
      }
      const emoji = match[0];
      parts.push(
        <img
          key={emoji + index}
          src={emojiMap[emoji]}
          className="inline-emoji"
          alt={emoji.replace(/:/g, "")}
        />
      );
      remaining = remaining.substring(index + emoji.length);
    }
    return parts;
  };

  return (
    <div className="authors-view">
      <section className="simple-page-card">
        <h2 className="authors-title-gradient">Authors</h2>
        <div className="authors-grid">
          {AUTHORS_DATA.map((author, index) => (
            <div className="author-card" key={index}>
              <div className="author-photo-wrapper">
                <img
                  className="author-photo"
                  src={author.image}
                  alt={author.name}
                  onError={(e) => {
                    e.target.style.display = "none";
                  }}
                />
                <div className="author-photo-fallback">
                  {author.name.split(" ")[0]}'s Photo
                  <br />
                  <span style={{ fontSize: "11px", opacity: 0.7 }}>
                    {author.image}
                  </span>
                </div>
              </div>
              <h3>{author.name}</h3>
              <p className="author-role">{author.role}</p>
              <p className="author-desc">{author.desc}</p>
              <div className="author-contacts">
                {author.contacts.map((c, i) => (
                  <a
                    key={i}
                    href={c.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="contact-link"
                  >
                    {c.label}
                  </a>
                ))}
              </div>

              <div className="author-donation">
                <p className="donation-caption">
                  {renderCaption(author.donation_caption)}
                </p>
                <a
                  href={author.donation_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="qr-link"
                >
                  <img
                    src={author.donation_qr}
                    className="donation-qr"
                    alt="Donation QR"
                  />
                </a>
              </div>
            </div>
          ))}
        </div>

        <div className="github-info-box">
          <span className="github-icon">
            <svg
              viewBox="0 0 16 16"
              width="18"
              height="18"
              fill="currentColor"
            >
              <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z" />
            </svg>
          </span>
          <p>
            Wanna know more about how we built the Deep Learning model and Websitez?
            Visit our{" "}
            <a
              href="https://github.com/AlexDaPiggie/Rolex_Models_Recognition"
              target="_blank"
              rel="noopener noreferrer"
              className="github-link"
            >
              Github Repo
            </a>
            .
          </p>
        </div>
      </section>
    </div>
  );
}

export default Authors;
