import "./VariantList.css";
import variantPhotos from "../../data/variantPhotos.json";

const searchUrl = (model, ref) =>
  `https://www.google.com/search?tbm=isch&q=${encodeURIComponent(`${model} ${ref}`)}`;

function Photo({ id, alt }) {
  const photo = variantPhotos[id];
  if (!photo) return null;
  return (
    <figure className="variant-photo">
      <img src={`/variants/${photo.file}`} alt={alt} loading="lazy" />
      <figcaption>
        <a href={photo.page} target="_blank" rel="noopener noreferrer">
          {photo.web ? `Photo: ${photo.author}` : `${photo.author}, ${photo.licence}`}
        </a>
      </figcaption>
    </figure>
  );
}

// Ranked list: best match large, the rest as hairline rows. No scores, only order.
function VariantList({ matches, note }) {
  return (
    <section className="variants" aria-label="Closest catalog variants">
      <h2 className="section-title">Closest variants</h2>
      <p className="plain-note">{note}</p>

      <ol className="variant-rows">
        {matches.map((m, i) => (
          <li key={m.id} className={i === 0 ? "variant best" : "variant"}>
            <Photo id={m.id} alt={m.model} />
            <div className="variant-text">
              <h3>{m.model}</h3>
              {i === 0 && <p className="variant-tag">Best match</p>}
              {m.references.length > 0 && (
                <p className="variant-refs">
                  <span>Reference </span>
                  {m.references.map((ref, k) => (
                    <a
                      key={`${ref}-${k}`}
                      href={searchUrl(m.model, ref)}
                      target="_blank"
                      rel="noopener noreferrer"
                      title={`Search Google Images for ${m.model} ${ref}`}
                    >
                      {ref}
                    </a>
                  ))}
                </p>
              )}
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}

export default VariantList;
