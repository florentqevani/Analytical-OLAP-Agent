import React, { useEffect, useMemo, useState } from "react";
import { analyzePrompt, getAgents, getHistory } from "./services/api";

const DEFAULT_USER_ID = "demo_user";
const DEFAULT_PROMPT =
  "Example: drill down revenue from Year to Quarter to Month, then roll up daily variance to quarter.";

function splitCsvLine(line) {
  const parts = [];
  let current = "";
  let inQuotes = false;

  for (let i = 0; i < line.length; i += 1) {
    const char = line[i];
    if (char === '"') {
      inQuotes = !inQuotes;
      continue;
    }
    if (char === "," && !inQuotes) {
      parts.push(current.trim());
      current = "";
      continue;
    }
    current += char;
  }
  parts.push(current.trim());
  return parts;
}

function buildConversation(runResult) {
  if (!runResult) {
    return "Upload a CSV, then ask your selected agent for a business report.";
  }

  const report = runResult.report || {};
  const findings = Array.isArray(report.keyFindings) ? report.keyFindings : [];
  const recommendations = Array.isArray(report.recommendations)
    ? report.recommendations
    : [];
  const risks = Array.isArray(report.risks) ? report.risks : [];

  const lines = [];
  lines.push(report.title || "Business Report");
  lines.push("");
  lines.push(
    report.executiveSummary || runResult.message || "No summary available.",
  );
  lines.push("");
  lines.push("Key Findings:");
  if (findings.length === 0) {
    lines.push("- No key findings returned.");
  } else {
    findings.slice(0, 6).forEach((item) => lines.push(`- ${item}`));
  }

  lines.push("");
  lines.push("Risks:");
  if (risks.length === 0) {
    lines.push("- No risks reported.");
  } else {
    risks.slice(0, 6).forEach((item) => lines.push(`- ${item}`));
  }

  lines.push("");
  lines.push("Recommendations:");
  if (recommendations.length === 0) {
    lines.push("- No recommendations returned.");
  } else {
    recommendations.slice(0, 6).forEach((item) => lines.push(`- ${item}`));
  }

  return lines.join("\n");
}

function buildChartModel(runResult) {
  const report = (runResult && runResult.report) || {};
  const chartHint = report.chartHint || {};
  const chartData = report.chartData || {};
  const rawSeries = Array.isArray(chartData.series) ? chartData.series : [];

  const series = rawSeries
    .map((item, index) => {
      const rawValue =
        item && typeof item === "object"
          ? (item.value ?? item.y ?? item.amount ?? item.metric)
          : null;
      const value = Number(rawValue);
      if (!Number.isFinite(value)) {
        return null;
      }

      const label =
        (item &&
          typeof item === "object" &&
          (item.label || item.name || item.x)) ||
        `Point ${index + 1}`;

      return {
        label: String(label),
        value,
      };
    })
    .filter(Boolean);

  return {
    title: String(chartData.title || "Agent Chart"),
    unit: String(chartData.unit || ""),
    dimension: String(chartHint.dimension || "dimension"),
    metric: String(chartHint.metric || "metric"),
    series,
  };
}

function App() {
  const [userId] = useState(DEFAULT_USER_ID);
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState("");
  const [history, setHistory] = useState([]);
  const [prompt, setPrompt] = useState(DEFAULT_PROMPT);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [conversation, setConversation] = useState(
    "Upload a CSV, then ask your selected agent for a business report.",
  );
  const [activeRunResult, setActiveRunResult] = useState(null);
  const [fileName, setFileName] = useState("");
  const [rowCount, setRowCount] = useState(0);
  const [columnCount, setColumnCount] = useState(0);
  const [sampleRows, setSampleRows] = useState([]);
  const [fileInputKey, setFileInputKey] = useState(0);

  const selectedAgentLabel = useMemo(() => {
    const found = agents.find((item) => item.agent_id === selectedAgent);
    return found ? found.label : "No Agent";
  }, [agents, selectedAgent]);

  const canRun = useMemo(
    () => Boolean(selectedAgent && prompt.trim()),
    [selectedAgent, prompt],
  );

  const chartModel = useMemo(
    () => buildChartModel(activeRunResult),
    [activeRunResult],
  );
  const chartSeries = chartModel.series;
  const chartMax = chartSeries.reduce(
    (max, item) => Math.max(max, item.value),
    0,
  );

  async function loadAgents() {
    setError("");
    const payload = await getAgents();
    const nextAgents = payload.agents || [];
    setAgents(nextAgents);
    if (!selectedAgent && nextAgents.length > 0) {
      setSelectedAgent(nextAgents[0].agent_id);
    }
  }

  async function loadHistory() {
    const payload = await getHistory(userId, 25);
    setHistory(payload.items || []);
  }

  useEffect(() => {
    loadAgents().catch((err) =>
      setError(err.message || "Failed to load agents"),
    );
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    loadHistory().catch((err) =>
      setError(err.message || "Failed to load history"),
    );
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId]);

  async function onFileChange(event) {
    const file = event.target.files && event.target.files[0];
    if (!file) {
      return;
    }

    try {
      const text = await file.text();
      const lines = text
        .split(/\r?\n/)
        .map((line) => line.trim())
        .filter((line) => line.length > 0);

      const header = lines.length > 0 ? splitCsvLine(lines[0]) : [];
      const dataLines = lines.slice(1);
      setFileName(file.name);
      setColumnCount(header.length);
      setRowCount(dataLines.length);
      setSampleRows(dataLines.slice(0, 3));
      setError("");
      setConversation(
        `CSV loaded: ${file.name}\nRows: ${dataLines.length}\nColumns: ${header.length}\n\nNow submit a prompt to generate a report.`,
      );
    } catch (err) {
      setError(err.message || "Failed to parse CSV file");
    }
  }

  function buildPrompt() {
    const lines = [prompt.trim()];
    if (fileName) {
      lines.push("");
      lines.push("CSV context:");
      lines.push(`- file: ${fileName}`);
      lines.push(`- rows: ${rowCount}`);
      lines.push(`- columns: ${columnCount}`);
      if (sampleRows.length > 0) {
        lines.push(`- sample rows: ${sampleRows.join(" | ")}`);
      }
    }
    return lines.join("\n");
  }

  async function onAnalyze(event) {
    event.preventDefault();
    if (!canRun || busy) {
      return;
    }

    setBusy(true);
    setError("");
    try {
      const payload = await analyzePrompt({
        user_id: userId,
        agent_id: selectedAgent,
        prompt: buildPrompt(),
      });

      setActiveRunResult(payload.result || null);
      setConversation(buildConversation(payload.result || null));
      await loadHistory();
    } catch (err) {
      setError(err.message || "Analyze failed");
    } finally {
      setBusy(false);
    }
  }

  function clearWorkspace() {
    setPrompt(DEFAULT_PROMPT);
    setConversation(
      "Upload a CSV, then ask your selected agent for a business report.",
    );
    setActiveRunResult(null);
    setFileName("");
    setRowCount(0);
    setColumnCount(0);
    setSampleRows([]);
    setFileInputKey((value) => value + 1);
    setError("");
  }

  function openHistoryItem(item) {
    const runResult = item && item.response ? item.response : null;
    setActiveRunResult(runResult);
    setConversation(buildConversation(runResult));
  }

  return (
    <main className="workspace">
      <header className="workspace-header">
        <div>
          <p className="eyebrow">ANALYTICAL WORKSPACE</p>
          <h1>OLAP Analyst Agent</h1>
        </div>
        <div className="badge-row">
          <span className={`pill ${busy ? "pill-running" : "pill-idle"}`}>
            {busy ? "Running" : "Idle"}
          </span>
        </div>
      </header>

      <section className="workspace-grid">
        <aside className="panel controls">
          <h2>Controls</h2>
          <label className="field-label">
            CSV file
            <input
              key={fileInputKey}
              type="file"
              accept=".csv,text/csv"
              onChange={onFileChange}
            />
          </label>
          <p className="meta">
            {fileName ? `Loaded: ${fileName}` : "No file loaded."}
          </p>

          <label className="field-label">
            Agent
            <select
              value={selectedAgent}
              onChange={(event) => setSelectedAgent(event.target.value)}
            >
              {agents.map((agent) => (
                <option key={agent.agent_id} value={agent.agent_id}>
                  {agent.label}
                </option>
              ))}
            </select>
          </label>
          {agents.length === 0 && !error ? (
            <p className="meta">Loading agents...</p>
          ) : null}

          <p className="meta">Rows: {rowCount}</p>
          <p className="meta">
            Agent: {selectedAgentLabel} ({selectedAgent ? "Active" : "Inactive"}
            )
          </p>
          <button
            type="button"
            className="secondary-btn"
            onClick={clearWorkspace}
          >
            Clear Workspace
          </button>
          {error ? <p className="error">{error}</p> : null}
        </aside>

        <section className="panel conversation">
          <div className="panel-head">
            <h2>Agent Conversation</h2>
            <span className="pill pill-provider">Provider: OpenAI</span>
          </div>

          <pre className="console">{conversation}</pre>

          <form onSubmit={onAnalyze}>
            <label className="field-label">
              Prompt
              <textarea
                rows={4}
                value={prompt}
                onChange={(event) => setPrompt(event.target.value)}
              />
            </label>
            <button
              type="submit"
              className="primary-btn"
              disabled={!canRun || busy}
            >
              {busy ? "Thinking..." : "Send to Agent"}
            </button>
          </form>
        </section>
      </section>

      <section className="panel charts-panel">
        <div className="panel-head">
          <h2>Charts</h2>
          <span className="pill metric-pill">
            {chartModel.dimension} / {chartModel.metric}
          </span>
        </div>
        {chartSeries.length === 0 ? (
          <p className="meta">
            Run an agent to generate chart data from the analysis response.
          </p>
        ) : (
          <div className="chart-wrap">
            <h3>
              {chartModel.title}
              {chartModel.unit ? ` (${chartModel.unit})` : ""}
            </h3>
            <div className="chart-bars">
              {chartSeries.map((item) => (
                <div className="bar-row" key={item.label}>
                  <span className="bar-label">{item.label}</span>
                  <div className="bar-track">
                    <div
                      className="bar-fill"
                      style={{
                        width: `${chartMax > 0 ? Math.max(6, (item.value / chartMax) * 100) : 0}%`,
                      }}
                    />
                  </div>
                  <span className="bar-value">{item.value.toFixed(2)}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </section>

      <section className="panel history">
        <div className="panel-head">
          <h2>Saved Reports</h2>
          <button
            type="button"
            className="secondary-btn"
            onClick={() =>
              loadHistory().catch((err) =>
                setError(err.message || "Refresh failed"),
              )
            }
          >
            Refresh
          </button>
        </div>
        {history.length === 0 ? (
          <p className="meta">No saved reports yet.</p>
        ) : (
          <ul className="history-list">
            {history.map((item) => (
              <li key={item.history_id} className="history-item">
                <div>
                  <p className="history-title">
                    {(item.response &&
                      item.response.report &&
                      item.response.report.title) ||
                      item.agent_id}
                  </p>
                  <p className="history-sub">
                    {item.agent_id} | {item.created_at}
                  </p>
                </div>
                <button
                  type="button"
                  className="secondary-btn"
                  onClick={() => openHistoryItem(item)}
                >
                  Open
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}

export default App;
