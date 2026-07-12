import { useState } from "react";
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
  BarChart, Bar, Legend,
} from "recharts";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

function App() {
  const [ticker, setTicker] = useState("");
  const [company, setCompany] = useState(null);
  const [prices, setPrices] = useState([]);
  const [financials, setFinancials] = useState([]);
  const [scores, setScores] = useState(null);
  const [period, setPeriod] = useState("1y");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [report, setReport] = useState("");
  const [reportLoading, setReportLoading] = useState(false);
  const [macro, setMacro] = useState([]);
  const [macroLoading, setMacroLoading] = useState(false);

  const fetchAll = async (tk, per) => {
    setLoading(true);
    setError("");
    setReport("");
    setMacro([]);
    try {
      const [cRes, pRes, fRes, sRes] = await Promise.all([
        fetch(`${API_BASE}/company/${tk}`),
        fetch(`${API_BASE}/prices/${tk}?period=${per}`),
        fetch(`${API_BASE}/financials/${tk}`),
        fetch(`${API_BASE}/scores/${tk}`),
      ]);
      if (!cRes.ok || !pRes.ok) throw new Error("Request failed");
      const cData = await cRes.json();
      const pData = await pRes.json();
      const fData = await fRes.json();
      const sData = await sRes.json();
      if (!cData.name) throw new Error("Not found");
      setCompany(cData);
      setPrices(pData.prices || []);
      setFinancials(fData.financials || []);
      setScores(sData || null);
    } catch (err) {
      setError("Could not find that ticker. Try AAPL, TSLA, NVDA, MSFT.");
      setCompany(null);
      setPrices([]);
      setFinancials([]);
      setScores(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    if (!ticker.trim()) return;
    fetchAll(ticker.trim().toUpperCase(), period);
  };

  const handlePeriodChange = (newPeriod) => {
    setPeriod(newPeriod);
    if (company) fetchAll(company.ticker, newPeriod);
  };

  const handleGenerateReport = async () => {
    if (!company) return;
    setReportLoading(true);
    setReport("");
    try {
      const res = await fetch(`${API_BASE}/report/${company.ticker}`);
      if (!res.ok) throw new Error("Report failed");
      const data = await res.json();
      setReport(data.report || "");
    } catch (err) {
      setReport("Failed to generate report. Please try again.");
    } finally {
      setReportLoading(false);
    }
  };

  const handleMacro = async () => {
    if (!company) return;
    setMacroLoading(true);
    setMacro([]);
    try {
      const res = await fetch(`${API_BASE}/macro/${company.ticker}`);
      if (!res.ok) throw new Error("Macro failed");
      const data = await res.json();
      setMacro(data.macro_factors || []);
    } catch (err) {
      setMacro([]);
    } finally {
      setMacroLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") handleSearch();
  };

  const formatMarketCap = (n) => {
    if (!n) return "N/A";
    if (n >= 1e12) return `$${(n / 1e12).toFixed(2)}T`;
    if (n >= 1e9) return `$${(n / 1e9).toFixed(2)}B`;
    return `$${n.toLocaleString()}`;
  };

  const periods = ["1mo", "6mo", "1y", "5y"];

  const impactColor = (impact) => {
    if (impact === "Positive") return "#34d399";
    if (impact === "Negative") return "#f87171";
    return "#fbbf24"; // Mixed
  };

  return (
    <div style={styles.page}>
      <div style={styles.container}>
        <h1 style={styles.title}>Kinstars</h1>
        <p style={styles.subtitle}>AI Financial Research Assistant</p>

        <div style={styles.searchRow}>
          <input
            style={styles.input}
            placeholder="Enter ticker (e.g. AAPL)"
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <button style={styles.button} onClick={handleSearch}>Analyze</button>
        </div>

        {loading && <p style={styles.info}>Loading...</p>}
        {error && <p style={styles.error}>{error}</p>}

        {company && (
          <div style={styles.card}>
            <h2 style={styles.cardName}>
              {company.name} <span style={styles.cardTicker}>{company.ticker}</span>
            </h2>
            <div style={styles.grid}>
              <Metric label="Sector" value={company.sector || "N/A"} />
              <Metric label="Industry" value={company.industry || "N/A"} />
              <Metric label="Market Cap" value={formatMarketCap(company.market_cap)} />
              <Metric label="Current Price" value={company.current_price ? `$${company.current_price}` : "N/A"} />
              <Metric label="P/E (Trailing)" value={company.pe_trailing ? company.pe_trailing.toFixed(2) : "N/A"} />
              <Metric label="P/E (Forward)" value={company.pe_forward ? company.pe_forward.toFixed(2) : "N/A"} />
            </div>
            {company.summary && <p style={styles.summary}>{company.summary}</p>}
          </div>
        )}

        {prices.length > 0 && (
          <div style={styles.card}>
            <div style={styles.chartHeader}>
              <h3 style={styles.chartTitle}>Price History</h3>
              <div style={styles.periodRow}>
                {periods.map((p) => (
                  <button key={p}
                    style={{ ...styles.periodBtn, ...(period === p ? styles.periodBtnActive : {}) }}
                    onClick={() => handlePeriodChange(p)}>
                    {p}
                  </button>
                ))}
              </div>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={prices}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="date" stroke="#94a3b8" tick={{ fontSize: 11 }} minTickGap={40} />
                <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} domain={["auto", "auto"]} />
                <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: "8px", color: "#e2e8f0" }} />
                <Line type="monotone" dataKey="close" stroke="#60a5fa" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {financials.length > 0 && (
          <div style={styles.card}>
            <h3 style={styles.chartTitle}>Financial Performance (USD Billions)</h3>
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={financials} margin={{ top: 20, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="year" stroke="#94a3b8" tick={{ fontSize: 12 }} />
                <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} />
                <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: "8px", color: "#e2e8f0" }} />
                <Legend wrapperStyle={{ fontSize: "12px" }} />
                <Bar dataKey="revenue" name="Revenue" fill="#60a5fa" />
                <Bar dataKey="gross_profit" name="Gross Profit" fill="#34d399" />
                <Bar dataKey="operating_income" name="Operating Income" fill="#fbbf24" />
                <Bar dataKey="net_income" name="Net Income" fill="#a78bfa" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {scores && (
          <div style={styles.card}>
            <h3 style={styles.chartTitle}>Risk & Quality Scores</h3>
            <div style={styles.scoreGrid}>
              <ScoreCard label="Growth" value={scores.growth_score}
                detail={scores.revenue_growth_pct != null ? `Rev +${scores.revenue_growth_pct}%` : ""} good="High" />
              <ScoreCard label="Profitability" value={scores.profitability_score}
                detail={scores.net_margin_pct != null ? `Margin ${scores.net_margin_pct}%` : ""} good="High" />
              <ScoreCard label="Valuation Risk" value={scores.valuation_risk}
                detail={scores.pe != null ? `P/E ${scores.pe}` : ""} good="Low" />
              <ScoreCard label="Overall Risk" value={scores.overall_risk} detail="" good="Low" />
            </div>
          </div>
        )}

        {company && (
          <div style={styles.card}>
            <div style={styles.chartHeader}>
              <h3 style={styles.chartTitle}>Macroeconomic Impact</h3>
              <button style={styles.reportBtn} onClick={handleMacro} disabled={macroLoading}>
                {macroLoading ? "Analyzing..." : "Analyze Macro"}
              </button>
            </div>
            {macroLoading && (
              <p style={styles.info}>AI is analyzing macro factors for {company.ticker}...</p>
            )}
            {macro.length > 0 && !macroLoading && (
              <div>
                {macro.map((f, i) => (
                  <div key={i} style={styles.macroItem}>
                    <div style={styles.macroHeader}>
                      <span style={styles.macroFactor}>{f.factor}</span>
                      <span style={{ ...styles.macroBadge, background: impactColor(f.impact) }}>
                        {f.impact}
                      </span>
                    </div>
                    <p style={styles.macroExp}>{f.explanation}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {company && (
          <div style={styles.card}>
            <div style={styles.chartHeader}>
              <h3 style={styles.chartTitle}>AI Investment Research Report</h3>
              <button style={styles.reportBtn} onClick={handleGenerateReport} disabled={reportLoading}>
                {reportLoading ? "Generating..." : "Generate Report"}
              </button>
            </div>
            {reportLoading && (
              <p style={styles.info}>
                AI is analyzing {company.ticker} and writing the report... this may take a few seconds.
              </p>
            )}
            {report && !reportLoading && (
              <div style={styles.reportText}>
                {report.split("\n").map((line, i) => (
                  <p key={i} style={styles.reportLine}>{line}</p>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div style={styles.metric}>
      <div style={styles.metricLabel}>{label}</div>
      <div style={styles.metricValue}>{value}</div>
    </div>
  );
}

function ScoreCard({ label, value, detail, good }) {
  let color = "#94a3b8";
  if (value === good) color = "#34d399";
  else if (value === "Medium") color = "#fbbf24";
  else if (value !== "N/A") color = "#f87171";
  return (
    <div style={{ ...styles.scoreCard, borderColor: color }}>
      <div style={styles.scoreLabel}>{label}</div>
      <div style={{ ...styles.scoreValue, color }}>{value}</div>
      {detail && <div style={styles.scoreDetail}>{detail}</div>}
    </div>
  );
}

const styles = {
  page: { minHeight: "100vh", background: "#0f172a", color: "#e2e8f0", fontFamily: "system-ui, sans-serif", padding: "40px 20px" },
  container: { maxWidth: "800px", margin: "0 auto" },
  title: { fontSize: "42px", margin: 0, color: "#60a5fa" },
  subtitle: { fontSize: "16px", color: "#94a3b8", marginTop: "4px" },
  searchRow: { display: "flex", gap: "10px", marginTop: "30px" },
  input: { flex: 1, padding: "12px 16px", fontSize: "16px", borderRadius: "8px", border: "1px solid #334155", background: "#1e293b", color: "#e2e8f0" },
  button: { padding: "12px 24px", fontSize: "16px", borderRadius: "8px", border: "none", background: "#3b82f6", color: "white", cursor: "pointer", fontWeight: "600" },
  info: { color: "#94a3b8", marginTop: "20px" },
  error: { color: "#f87171", marginTop: "20px" },
  card: { marginTop: "30px", padding: "24px", borderRadius: "12px", background: "#1e293b", border: "1px solid #334155" },
  cardName: { margin: 0, fontSize: "24px" },
  cardTicker: { fontSize: "14px", color: "#60a5fa", background: "#1e3a5f", padding: "2px 8px", borderRadius: "6px", marginLeft: "8px" },
  grid: { display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "16px", marginTop: "20px" },
  metric: { background: "#0f172a", padding: "12px", borderRadius: "8px" },
  metricLabel: { fontSize: "12px", color: "#94a3b8" },
  metricValue: { fontSize: "18px", fontWeight: "600", marginTop: "4px" },
  summary: { marginTop: "20px", fontSize: "14px", lineHeight: "1.6", color: "#cbd5e1" },
  chartHeader: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" },
  chartTitle: { margin: 0, fontSize: "18px", marginBottom: "16px" },
  periodRow: { display: "flex", gap: "6px" },
  periodBtn: { padding: "4px 12px", fontSize: "13px", borderRadius: "6px", border: "1px solid #334155", background: "#0f172a", color: "#94a3b8", cursor: "pointer" },
  periodBtnActive: { background: "#3b82f6", color: "white", border: "1px solid #3b82f6" },
  reportBtn: { padding: "8px 18px", fontSize: "14px", borderRadius: "8px", border: "none", background: "#3b82f6", color: "white", cursor: "pointer", fontWeight: "600" },
  reportText: { marginTop: "10px" },
  reportLine: { fontSize: "14px", lineHeight: "1.6", color: "#cbd5e1", margin: "6px 0" },
  scoreGrid: { display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "12px" },
  scoreCard: { background: "#0f172a", padding: "16px", borderRadius: "8px", border: "2px solid #334155", textAlign: "center" },
  scoreLabel: { fontSize: "12px", color: "#94a3b8" },
  scoreValue: { fontSize: "20px", fontWeight: "700", marginTop: "6px" },
  scoreDetail: { fontSize: "11px", color: "#64748b", marginTop: "4px" },
  macroItem: { background: "#0f172a", padding: "14px", borderRadius: "8px", marginBottom: "10px" },
  macroHeader: { display: "flex", justifyContent: "space-between", alignItems: "center" },
  macroFactor: { fontSize: "15px", fontWeight: "600" },
  macroBadge: { fontSize: "11px", fontWeight: "700", color: "#0f172a", padding: "2px 10px", borderRadius: "12px" },
  macroExp: { fontSize: "13px", lineHeight: "1.5", color: "#cbd5e1", marginTop: "8px", marginBottom: 0 },
};

export default App;