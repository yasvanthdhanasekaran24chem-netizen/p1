import { useEffect, useState } from "react";
import "./App.css";

function StatusPill({ ok, text }) {
  return <span className={`pill ${ok ? "ok" : "bad"}`}>{text}</span>;
}

function App() {
  const [live, setLive] = useState(null);
  const [summary, setSummary] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const [liveRes, summaryRes, jobsRes] = await Promise.all([
        fetch("/api/health/live"),
        fetch("/api/summary"),
        fetch("/api/jobs?limit=10"),
      ]);

      if (!liveRes.ok) throw new Error(`health/live failed: ${liveRes.status}`);
      if (!summaryRes.ok) throw new Error(`summary failed: ${summaryRes.status}`);
      if (!jobsRes.ok) throw new Error(`jobs failed: ${jobsRes.status}`);

      const liveData = await liveRes.json();
      const summaryData = await summaryRes.json();
      const jobsData = await jobsRes.json();

      setLive(liveData);
      setSummary(summaryData);
      setJobs(Array.isArray(jobsData) ? jobsData : []);
    } catch (e) {
      setError(String(e.message || e));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    const id = setInterval(load, 5000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="page">
      <header className="header">
        <h1>P1 Control Panel</h1>
        <button onClick={load} disabled={loading}>
          {loading ? "Refreshing..." : "Refresh"}
        </button>
      </header>

      {error && <div className="error">{error}</div>}

      <section className="grid">
        <div className="card">
          <h3>Backend Live</h3>
          <StatusPill ok={!!live?.status && live.status === "ok"} text={live?.status || "unknown"} />
          <p>Timestamp: {live?.ts ? new Date(live.ts * 1000).toLocaleString() : "-"}</p>
        </div>

        <div className="card">
          <h3>Summary</h3>
          <pre>{summary ? JSON.stringify(summary, null, 2) : "Loading..."}</pre>
        </div>
      </section>

      <section className="card">
        <h3>Recent Jobs</h3>
        {jobs.length === 0 ? (
          <p>No jobs found.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Job ID</th>
                <th>Backend</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {jobs.map((j) => (
                <tr key={j.job_id || j.id || Math.random()}>
                  <td>{j.job_id || j.id || "-"}</td>
                  <td>{j.backend || "-"}</td>
                  <td>{j.status || "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}

export default App;
