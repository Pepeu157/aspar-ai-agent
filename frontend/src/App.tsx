import { useEffect, useState } from 'react';
import { listRequests, type RequestRecord } from './api';
import './styles.css';

export default function App() {
  const [requests, setRequests] = useState<RequestRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listRequests()
      .then(setRequests)
      .catch(() => setError('API local indisponível. Inicie o backend para consultar registros.'))
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="shell">
      <header className="header">
        <div>
          <p className="eyebrow">ASPAR / MME · desenvolvimento local</p>
          <h1>Solicitações de audiência</h1>
        </div>
        <span className="badge">Sem conexão institucional</span>
      </header>
      <section className="panel" aria-live="polite">
        <h2>Registros</h2>
        {loading && <p>Consultando API local…</p>}
        {error && <p role="alert">{error}</p>}
        {!loading && !error && requests.length === 0 && (
          <p>Nenhuma solicitação registrada. Não há dados demonstrativos.</p>
        )}
        {requests.map((item) => (
          <article className="record" key={item.request_id}>
            <p><strong>Classificação:</strong> {item.classification}</p>
            <p><strong>Status:</strong> {item.status}</p>
            <p><strong>Assunto:</strong> {item.analysis.extracted_fields.subject ?? 'Não informado'}</p>
            <p><strong>Data sugerida:</strong> {item.analysis.extracted_fields.suggested_date ?? 'Não informada'}</p>
          </article>
        ))}
      </section>
      <footer>Revisão humana obrigatória · envio de e-mail não implementado</footer>
    </main>
  );
}
