import { useState } from "react";
import "./ProbabilityTable.css";

const TOP_N = 5;

function ProbabilityTable({ probabilities }) {
  const [showAll, setShowAll] = useState(false);
  const rows = showAll ? probabilities : probabilities.slice(0, TOP_N);

  return (
    <section className="probability-table">

      <h2>
        Other possible families
      </h2>

      <div className="table-wrapper">

        <table>

          <thead>

            <tr>
              <th>Model</th>
              <th>Probability</th>
            </tr>

          </thead>

          <tbody>

            {rows.map((item, index) => (

              <tr key={item.name} className={index === 0 ? "top-probability" : undefined}>

                <td>{item.name}</td>

                <td>{item.value}</td>

              </tr>

            ))}

          </tbody>

        </table>

      </div>

      {probabilities.length > TOP_N && (
        <button type="button" className="show-all" onClick={() => setShowAll((v) => !v)}>
          {showAll ? "Show top 5 only" : `Show all ${probabilities.length}`}
        </button>
      )}

    </section>
  );
}

export default ProbabilityTable;
