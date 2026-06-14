import type { TailoredResume } from "../types";

export default function ResumePreview({ resume }: { resume: TailoredResume }) {
  const contactValues = Object.values(resume.contact).filter(Boolean);
  return (
    <div className="card">
      <h3 style={{ margin: "0 0 10px" }}>Tailored resume</h3>
      <div className="resume-preview">
        <h1>{resume.candidate_name}</h1>
        {contactValues.length > 0 && (
          <div className="contact">{contactValues.join(" • ")}</div>
        )}

        {resume.professional_summary && (
          <>
            <h2>Professional Summary</h2>
            <p>{resume.professional_summary}</p>
          </>
        )}

        {resume.technical_skills.length > 0 && (
          <>
            <h2>Technical Skills</h2>
            <div className="chip-row">
              {resume.technical_skills.map((s) => (
                <span key={s} className="chip">{s}</span>
              ))}
            </div>
          </>
        )}

        {resume.experience.length > 0 && (
          <>
            <h2>Experience</h2>
            {resume.experience.map((j, i) => (
              <div key={i} className="entry">
                <div className="entry-head">
                  <span className="entry-title">{j.role} — {j.company}</span>
                  <span className="entry-meta">
                    {j.start_date || j.end_date
                      ? `${j.start_date ?? ""} – ${j.end_date ?? "Present"}`
                      : ""}
                  </span>
                </div>
                {j.location && <div className="entry-meta">{j.location}</div>}
                <ul>{j.bullets.map((b, k) => <li key={k}>{b}</li>)}</ul>
              </div>
            ))}
          </>
        )}

        {resume.projects.length > 0 && (
          <>
            <h2>Projects</h2>
            {resume.projects.map((p, i) => (
              <div key={i} className="entry">
                <div className="entry-head">
                  <span className="entry-title">{p.name}</span>
                  {p.tech.length > 0 && <span className="entry-meta">{p.tech.join(", ")}</span>}
                </div>
                {p.description && <div className="entry-meta">{p.description}</div>}
                {p.bullets.length > 0 && <ul>{p.bullets.map((b, k) => <li key={k}>{b}</li>)}</ul>}
              </div>
            ))}
          </>
        )}

        {resume.education.length > 0 && (
          <>
            <h2>Education</h2>
            {resume.education.map((e, i) => (
              <div key={i} className="entry">
                <div className="entry-head">
                  <span className="entry-title">{e.degree} — {e.institution}</span>
                  {(e.start_date || e.end_date) && (
                    <span className="entry-meta">
                      {[e.start_date, e.end_date].filter(Boolean).join(" – ")}
                    </span>
                  )}
                </div>
                {e.details && <div className="entry-meta">{e.details}</div>}
              </div>
            ))}
          </>
        )}

        {resume.certifications.length > 0 && (
          <>
            <h2>Certifications</h2>
            <ul>{resume.certifications.map((c, i) => <li key={i}>{c}</li>)}</ul>
          </>
        )}

        {resume.achievements.length > 0 && (
          <>
            <h2>Achievements</h2>
            <ul>{resume.achievements.map((a, i) => <li key={i}>{a}</li>)}</ul>
          </>
        )}

        {resume.tools_technologies.length > 0 && (
          <>
            <h2>Tools &amp; Technologies</h2>
            <div className="chip-row">
              {resume.tools_technologies.map((t) => (
                <span key={t} className="chip">{t}</span>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
