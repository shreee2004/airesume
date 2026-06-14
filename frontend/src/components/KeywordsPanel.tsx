import type { AtsAnalysis } from "../types";

export default function KeywordsPanel({ ats }: { ats: AtsAnalysis }) {
  return (
    <div className="card">
      <h3 style={{ margin: "0 0 8px" }}>Keyword analysis</h3>
      <div className="section-title">Matched ({ats.matched_keywords.length})</div>
      <div className="chip-row">
        {ats.matched_keywords.length === 0 && <span className="chip gray">None yet</span>}
        {ats.matched_keywords.map((k) => (
          <span key={k} className="chip green">{k}</span>
        ))}
      </div>
      <div className="section-title">Missing ({ats.missing_keywords.length})</div>
      <div className="chip-row">
        {ats.missing_keywords.length === 0 && <span className="chip gray">All covered</span>}
        {ats.missing_keywords.map((k) => (
          <span key={k} className="chip red">{k}</span>
        ))}
      </div>
    </div>
  );
}
