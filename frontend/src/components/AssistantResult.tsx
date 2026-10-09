
import type { AssistantResponse } from '../types/order';

type Props = {
  result: AssistantResponse;
  menuNames: Record<string, string>;
};

export default function AssistantResult({
  result,
  menuNames,
}: Props) {
  const order = result.order;
  const answer = result.answer;

  const hasOrder =
    order !== null &&
    (order.items.length > 0 || order.unavailable.length > 0);

  return (
    <article className="assistant-result">
      <header className="assistant-result-header">
        <h3>Odgovor</h3>
      </header>

      {/* NARUDŽBA */}
      <section className="answer-section">
        <div className="answer-section-header">
          <span className="section-indicator order-indicator" />
          <h4>Narudžba</h4>
        </div>

        {hasOrder && order ? (
          <>
            {order.items.length > 0 && (
              <ul className="answer-items">
                {order.items.map((item, index) => (
                  <li key={index}>
                    <span>
                      {menuNames[item.id] ?? item.id}
                    </span>

                    <strong>{item.quantity} ×</strong>
                  </li>
                ))}
              </ul>
            )}

            {order.unavailable.length > 0 && (
              <div className="answer-unavailable">
                <h5>Nedostupni proizvodi</h5>

                <ul className="answer-items">
                  {order.unavailable.map((item, index) => (
                    <li key={index}>
                      <span>{item.text}</span>
                      <strong>{item.quantity} ×</strong>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </>
        ) : (
          <p className="answer-empty">
            Nema naručenih proizvoda.
          </p>
        )}
      </section>

      {/* PRIJEDLOG */}
      <section className="answer-section">
        <div className="answer-section-header">
          <span className="section-indicator suggestion-indicator" />
          <h4>Prijedlog</h4>
        </div>

        {answer ? (
          <>
            <p className="answer-message">
              {answer.message}
            </p>

            {answer.suggested_ids.length > 0 && (
              <div className="answer-suggestions">
                <h5>Preporučeni proizvodi</h5>

                <ul className="answer-items">
                  {answer.suggested_ids.map(id => (
                    <li key={id}>
                      <span>{menuNames[id] ?? id}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </>
        ) : (
          <p className="answer-empty">
            Korisnik nije postavio pitanje o jelovniku.
          </p>
        )}
      </section>
    </article>
  );
}
