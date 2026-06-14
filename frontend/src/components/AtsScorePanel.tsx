import type { AtsAnalysis } from "../types";

export default function AtsScorePanel({ ats }: { ats: AtsAnalysis }) {
  return (
    <div className="card">
      <div className="score-row">
        <div
          className="score-ring"
          style={{ ["--pct" as never]: ats.score } as React.CSSProperties}
          aria-label={`ATS score ${ats.score} out of 100`}
        >
          <div className="score-text">
            {ats.score}
            <small>/ 100</small>
          </div>
        </div>
        <div className="score-side">
          <div className="match-pct">Keyword match: <strong>{ats.keyword_match_percent}%</strong></div>
          <p style={{ margin: "4px 0 10px" }}>{ats.explanation}</p>
          {ats.strength_areas.length > 0 && (
            <>
              <div className="section-title">Strengths</div>
              <div className="chip-row">
                {ats.strength_areas.map((s) => (
                  <span key={s} className="chip green">{s}</span>
                ))}
              </div>
            </>
          )}
          {ats.weak_areas.length > 0 && (
            <>
              <div className="section-title">Weak areas</div>
              <div className="chip-row">
                {ats.weak_areas.map((s) => (
                  <span key={s} className="chip red">{s}</span>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
