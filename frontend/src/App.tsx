
import { useEffect, useRef, useState } from 'react';
import { extractOrder, getMenu } from './services/api';
import type { AssistantResponse } from './types/order';

import AssistantResult from './components/AssistantResult';
type MenuItem = {
  id: string;
  naziv: string;
};

export default function App() {
  const [text, setText] = useState('');
  const [results, setResults] = useState<AssistantResponse[]>([]);
  const [menuNames, setMenuNames] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  const submitting = useRef(false);

  useEffect(() => {
    async function loadMenu() {
      try {
        const menu = (await getMenu()) as MenuItem[];

        const names = Object.fromEntries(
          menu.map(item => [item.id, item.naziv])
        );

        setMenuNames(names);
      } catch (error) {
        console.error('Greška pri učitavanju jelovnika:', error);
      }
    }

    loadMenu();
  }, []);

  async function submit(event: React.SyntheticEvent<HTMLFormElement>) {
    event.preventDefault();

    if (submitting.current || !text.trim()) return;

    submitting.current = true;
    setLoading(true);
    setError('');
    setMessage('');

    try {
      const result = await extractOrder(text);

      setResults(current => [result, ...current]);
      setText('');

      setMessage(
        result.order && result.answer
          ? 'Narudžba i prijedlog uspješno generirani.'
          : result.order
            ? 'Narudžba je uspješno generirana.'
            : 'Prijedlog iz jelovnika je spreman.'
      );
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : 'Obrada unosa nije uspjela.'
      );
    } finally {
      setLoading(false);
      submitting.current = false;
    }
  }

  return (
    <main className="app">
      <header className="app-header">
        <h1>Asistent za narudžbe</h1>
        <p>
          Unesite narudžbu ili postavite pitanje o jelovniku.
        </p>
      </header>

      <form onSubmit={submit} aria-busy={loading}>
        <label htmlFor="transcript">
          Unos korisnika
        </label>

        <textarea
          id="transcript"
          placeholder="Npr. Dvije margarite i jednu colu ili Imate li nešto bez mesa?"
          value={text}
          onChange={event => {
            setText(event.target.value);
            setError('');
            setMessage('');
          }}
          maxLength={15000}
          disabled={loading}
          required
        />

        <button
          className="generate"
          type="submit"
          disabled={loading || !text.trim()}
        >
          {loading ? 'Obrađujem…' : 'Obradi unos'}
        </button>

        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}

        <p className="feedback" role="status">
          {loading ? 'Analiziram korisnikov unos…' : message}
        </p>
      </form>

      
      
        {results.length > 0 && (
          <section className="orders">
            <h2>Rezultati</h2>

            {results.map((result, index) => (
              <AssistantResult
                key={index}
                result={result}
                menuNames={menuNames}
              />
            ))}
          </section>
        )}     
    </main>
  );
}
