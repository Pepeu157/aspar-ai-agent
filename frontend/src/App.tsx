import { useEffect, useState } from 'react';
import { listRequests, type RequestRecord } from './api';
import './styles.css';

type AuditHistoryItem = {
  event_type?: string;
  actor_type?: string;
  created_at?: string;
};

type RequestWithHistory = RequestRecord & {
  history?: AuditHistoryItem[];
};

const classificationLabels: Record<RequestRecord['classification'], string> = {
  audience_request: 'Solicitação de audiência',
  ambiguous: 'Requer esclarecimento',
  out_of_scope: 'Fora do escopo',
};

const statusLabels: Record<string, string> = {
  received: 'Recebida',
  in_analysis: 'Em análise',
  awaiting_review: 'Aguardando revisão',
  in_review: 'Em revisão',
  approved: 'Aprovada',
  responded: 'Respondida',
  discarded: 'Descartada',
  needs_more_info: 'Necessita de mais informações',
  out_of_scope: 'Fora do escopo',
};

const fieldLabels = [
  ['sender_name', 'Remetente'],
  ['sender_email', 'E-mail do remetente'],
  ['institution', 'Instituição'],
  ['subject', 'Assunto'],
  ['request_summary', 'Resumo da solicitação'],
  ['suggested_date', 'Data sugerida'],
  ['suggested_time', 'Horário sugerido'],
  ['participants', 'Participantes'],
  ['context', 'Contexto'],
  ['technical_terms', 'Termos técnicos'],
  ['suggested_response', 'Resposta sugerida'],
] as const;

type FieldKey = (typeof fieldLabels)[number][0];

function displayValue(value: string | null | undefined): string {
  return value?.trim() || 'Não informado';
}

function displayList(value: string[] | null | undefined): string {
  return value?.length ? value.join(', ') : 'Não informado';
}

function formatTimestamp(value: string | undefined): string {
  if (!value) return 'Data não informada';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date);
}

export default function App() {
  const [requests, setRequests] = useState<RequestWithHistory[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;

    listRequests()
      .then((records) => {
        if (!mounted) return;
        const recordsWithHistory = records as RequestWithHistory[];
        setRequests(recordsWithHistory);
        setSelectedId(recordsWithHistory[0]?.request_id ?? null);
      })
      .catch(() => {
        if (mounted) setError('API local indisponível. Inicie o backend para consultar registros.');
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  const selectedRequest = requests.find((request) => request.request_id === selectedId) ?? null;

  return (
    <main className="shell">
      <header className="topbar">
        <div className="brand-mark" aria-hidden="true">AS</div>
        <div className="brand-copy">
          <p className="eyebrow">Ministério de Minas e Energia</p>
          <p className="brand-title">ASPAR <span>·</span> Gestão de solicitações</p>
        </div>
        <div className="review-notice"><span className="notice-dot" /> Revisão humana obrigatória</div>
      </header>

      <section className="page-heading">
        <div>
          <p className="eyebrow">Painel administrativo</p>
          <h1>Solicitações de audiência</h1>
          <p className="page-description">Consulte os registros recebidos e os dados identificados na análise.</p>
        </div>
        {!loading && !error && (
          <div className="request-count" aria-label={`${requests.length} solicitações`}>
            <strong>{requests.length}</strong>
            <span>{requests.length === 1 ? 'registro' : 'registros'}</span>
          </div>
        )}
      </section>

      {loading && (
        <section className="state-panel" aria-live="polite">
          <span className="loading-indicator" aria-hidden="true" />
          <p>Carregando solicitações…</p>
        </section>
      )}

      {error && (
        <section className="state-panel error-panel" role="alert">
          <span className="state-icon" aria-hidden="true">!</span>
          <div>
            <h2>Não foi possível carregar os registros</h2>
            <p>{error}</p>
          </div>
        </section>
      )}

      {!loading && !error && requests.length === 0 && (
        <section className="state-panel empty-panel" aria-live="polite">
          <span className="state-icon" aria-hidden="true">—</span>
          <h2>Nenhuma solicitação registrada</h2>
          <p>Quando houver registros, eles serão apresentados neste painel.</p>
        </section>
      )}

      {!loading && !error && requests.length > 0 && (
        <div className="workspace">
          <aside className="request-panel" aria-labelledby="request-list-heading">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Caixa de entrada</p>
                <h2 id="request-list-heading">Registros</h2>
              </div>
              <span className="count-chip">{requests.length}</span>
            </div>
            <ul className="request-list">
              {requests.map((request) => {
                const selected = request.request_id === selectedId;
                return (
                  <li key={request.request_id}>
                    <button
                      type="button"
                      className={`request-item${selected ? ' is-selected' : ''}`}
                      onClick={() => setSelectedId(request.request_id)}
                      aria-current={selected ? 'true' : undefined}
                    >
                      <span className={`classification-mark classification-${request.classification}`} aria-hidden="true" />
                      <span className="request-item-content">
                        <span className="request-item-title">
                          {displayValue(request.analysis?.extracted_fields?.subject)}
                        </span>
                        <span className="request-item-meta">
                          <span className={`status-badge status-${request.status}`}>
                            {statusLabels[request.status] ?? request.status ?? 'Status não informado'}
                          </span>
                        </span>
                        <span className={`classification-label classification-text-${request.classification}`}>
                          {classificationLabels[request.classification] ?? request.classification}
                        </span>
                      </span>
                      <span className="item-chevron" aria-hidden="true">›</span>
                    </button>
                  </li>
                );
              })}
            </ul>
          </aside>

          <section className="detail-panel" aria-label="Detalhes da solicitação" aria-live="polite">
            {selectedRequest ? (
              <>
                <div className="detail-header">
                  <div>
                    <p className="eyebrow">Detalhamento do registro</p>
                    <h2>{displayValue(selectedRequest.analysis?.extracted_fields?.subject)}</h2>
                    <p className="record-id">Identificador: <span>{selectedRequest.request_id}</span></p>
                  </div>
                  <div className="detail-badges">
                    <span className={`classification-badge classification-${selectedRequest.classification}`}>
                      {classificationLabels[selectedRequest.classification] ?? selectedRequest.classification}
                    </span>
                    <span className={`status-badge status-${selectedRequest.status}`}>
                      {statusLabels[selectedRequest.status] ?? selectedRequest.status ?? 'Status não informado'}
                    </span>
                  </div>
                </div>

                <section className="detail-section">
                  <div className="section-title">
                    <span className="section-number">01</span>
                    <h3>Informações da solicitação</h3>
                  </div>
                  <dl className="field-grid">
                    {fieldLabels.map(([key, label]) => {
                      const fields = selectedRequest.analysis?.extracted_fields;
                      const value = fields?.[key as FieldKey];
                      const formatted = Array.isArray(value)
                        ? displayList(value)
                        : displayValue(value as string | null | undefined);
                      return (
                        <div className={`field-card${key === 'request_summary' || key === 'context' || key === 'suggested_response' ? ' field-wide' : ''}`} key={key}>
                          <dt>{label}</dt>
                          <dd>{formatted}</dd>
                        </div>
                      );
                    })}
                  </dl>
                </section>

                <section className="detail-section">
                  <div className="section-title">
                    <span className="section-number">02</span>
                    <h3>Mensagem recebida</h3>
                  </div>
                  <p className="message-content">{displayValue(selectedRequest.message_text)}</p>
                </section>

                <section className="detail-section">
                  <div className="section-title">
                    <span className="section-number">03</span>
                    <h3>Avisos da análise</h3>
                  </div>
                  {selectedRequest.analysis?.warnings?.length ? (
                    <ul className="warning-list">
                      {selectedRequest.analysis.warnings.map((warning, index) => (
                        <li key={`${index}-${warning}`}>{warning}</li>
                      ))}
                    </ul>
                  ) : (
                    <p className="muted-copy">Nenhum aviso registrado.</p>
                  )}
                </section>

                <section className="detail-section history-section">
                  <div className="section-title">
                    <span className="section-number">04</span>
                    <h3>Histórico</h3>
                  </div>
                  {selectedRequest.history?.length ? (
                    <ol className="history-list">
                      {selectedRequest.history.map((event, index) => (
                        <li className="history-entry" key={`${event.event_type ?? 'event'}-${index}`}>
                          <span className="history-marker" aria-hidden="true" />
                          <div className="history-content">
                            <strong>{displayValue(event.event_type)}</strong>
                            <span>Responsável: {displayValue(event.actor_type)}</span>
                            <time dateTime={event.created_at}>{formatTimestamp(event.created_at)}</time>
                          </div>
                        </li>
                      ))}
                    </ol>
                  ) : (
                    <p className="muted-copy">Histórico não disponível para este registro.</p>
                  )}
                </section>

                <div className="human-review-note">
                  <span aria-hidden="true">i</span>
                  <p>Esta análise é auxiliar. A solicitação requer revisão humana antes de qualquer encaminhamento.</p>
                </div>
              </>
            ) : (
              <div className="detail-placeholder">
                <h2>Selecione uma solicitação</h2>
                <p>Escolha um registro na lista para consultar seus detalhes.</p>
              </div>
            )}
          </section>
        </div>
      )}

      <footer className="page-footer">
        <span>ASPAR · Ambiente de desenvolvimento</span>
        <span>Revisão humana obrigatória · envio de e-mail não implementado</span>
      </footer>
    </main>
  );
}
