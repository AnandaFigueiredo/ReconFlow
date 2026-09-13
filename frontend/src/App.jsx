import { useEffect, useState } from "react";
import "./App.css";

const API_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000";

const exampleSourceA = `[
  {
    "operation_id": "OP201",
    "client_id": "CL201",
    "amount": 10000,
    "status": "PROCESSADA"
  },
  {
    "operation_id": "OP202",
    "client_id": "CL202",
    "amount": 5000,
    "status": "PROCESSADA"
  }
]`;

const exampleSourceB = `[
  {
    "operation_id": "OP201",
    "client_id": "CL201",
    "amount": 10000,
    "status": "PROCESSADA"
  },
  {
    "operation_id": "OP202",
    "client_id": "CL202",
    "amount": 4900,
    "status": "PROCESSADA"
  }
]`;

function App() {
  const [batches, setBatches] = useState([]);
  const [selectedBatch, setSelectedBatch] = useState(null);
  const [exceptions, setExceptions] = useState([]);

  const [showForm, setShowForm] = useState(false);
  const [batchCode, setBatchCode] = useState("");
  const [sourceA, setSourceA] = useState(exampleSourceA);
  const [sourceB, setSourceB] = useState(exampleSourceB);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function loadBatches() {
    const response = await fetch(`${API_URL}/reconciliations`);
    const data = await response.json();
    setBatches(data);
  }

  async function loadBatch(batchId) {
    const response = await fetch(
      `${API_URL}/reconciliations/${batchId}`
    );

    const data = await response.json();
    setSelectedBatch(data);

    const exceptionsResponse = await fetch(
      `${API_URL}/reconciliations/${batchId}/exceptions`
    );

    const exceptionsData = await exceptionsResponse.json();
    setExceptions(exceptionsData.exceptions);
  }

  async function createReconciliation(event) {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      const parsedSourceA = JSON.parse(sourceA);
      const parsedSourceB = JSON.parse(sourceB);

      const response = await fetch(`${API_URL}/reconciliations`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          batch_code: batchCode,
          source_a: parsedSourceA,
          source_b: parsedSourceB,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Erro ao processar conciliação."
        );
      }

      await loadBatches();
      await loadBatch(data.batch_id);

      setBatchCode("");
      setShowForm(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadBatches();
  }, []);

  return (
    <div className="app">
      <header>
        <div>
          <h1>ReconFlow</h1>
          <p>Automated Reconciliation & Exception Management</p>
        </div>
      </header>

      <main>
        <div className="page-top">
          <h2>Histórico de conciliações</h2>

          <button
            className="primary-button"
            onClick={() => setShowForm(!showForm)}
          >
            + Nova conciliação
          </button>
        </div>

        {showForm && (
          <section className="new-reconciliation">
            <h2>Nova conciliação</h2>

            <form onSubmit={createReconciliation}>
              <label>
                Código do lote
                <input
                  type="text"
                  value={batchCode}
                  onChange={(event) =>
                    setBatchCode(event.target.value)
                  }
                  placeholder="Ex: BATCH-004"
                  required
                />
              </label>

              <div className="sources-grid">
                <label>
                  Fonte A
                  <textarea
                    value={sourceA}
                    onChange={(event) =>
                      setSourceA(event.target.value)
                    }
                  />
                </label>

                <label>
                  Fonte B
                  <textarea
                    value={sourceB}
                    onChange={(event) =>
                      setSourceB(event.target.value)
                    }
                  />
                </label>
              </div>

              {error && (
                <div className="error-message">
                  {error}
                </div>
              )}

              <div className="form-actions">
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() => setShowForm(false)}
                >
                  Cancelar
                </button>

                <button
                  type="submit"
                  className="primary-button"
                  disabled={loading}
                >
                  {loading
                    ? "Processando..."
                    : "Executar conciliação"}
                </button>
              </div>
            </form>
          </section>
        )}

        <section>
          <div className="batch-list">
            {batches.map((batch) => (
              <button
                key={batch.batch_id}
                className="batch-item"
                onClick={() => loadBatch(batch.batch_id)}
              >
                <strong>{batch.batch_code}</strong>
                <span>{batch.status}</span>
              </button>
            ))}
          </div>
        </section>

        {selectedBatch && (
          <>
            <section>
              <h2>{selectedBatch.batch_code}</h2>

              <div className="cards">
                <div className="card">
                  <span>Fonte A</span>
                  <strong>{selectedBatch.total_a}</strong>
                </div>

                <div className="card">
                  <span>Fonte B</span>
                  <strong>{selectedBatch.total_b}</strong>
                </div>

                <div className="card">
                  <span>Conciliadas</span>
                  <strong>
                    {selectedBatch.total_matched}
                  </strong>
                </div>

                <div className="card">
                  <span>Divergentes</span>
                  <strong>
                    {selectedBatch.total_divergent}
                  </strong>
                </div>

                <div className="card">
                  <span>Ausentes</span>
                  <strong>
                    {selectedBatch.total_missing}
                  </strong>
                </div>
              </div>
            </section>

            <section>
              <h2>Exceções</h2>

              {exceptions.length === 0 ? (
                <p>Nenhuma exceção encontrada.</p>
              ) : (
                <table>
                  <thead>
                    <tr>
                      <th>Operação</th>
                      <th>Resultado</th>
                      <th>Detalhes</th>
                    </tr>
                  </thead>

                  <tbody>
                    {exceptions.map((item) => (
                      <tr key={item.operation_id}>
                        <td>{item.operation_id}</td>
                        <td>{item.result}</td>
                        <td>{item.details}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </section>
          </>
        )}
      </main>
    </div>
  );
}

export default App;