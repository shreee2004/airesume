import type { SkillSuggestions } from "../types";

interface Section {
  title: string;
  items: string[];
}

export default function SuggestionsPanel({ s }: { s: SkillSuggestions }) {
  const sections: Section[] = [
    { title: "Missing skills to build", items: s.missing_skills },
    { title: "Recommended certifications", items: s.certifications },
    { title: "Project ideas", items: s.project_ideas },
    { title: "Interview prep topics", items: s.interview_topics },
    { title: "Resume improvement tips", items: s.resume_tips },
    { title: "Portfolio tips", items: s.portfolio_tips },
    { title: "LinkedIn optimization tips", items: s.linkedin_tips },
  ];

  return (
    <div className="card">
      <h3 style={{ margin: "0 0 10px" }}>Skill-gap suggestions</h3>
      {sections.map((sec) =>
        sec.items.length === 0 ? null : (
          <details className="accordion" key={sec.title}>
            <summary>{sec.title} <span style={{ color: "#5b6175", fontWeight: 400 }}>({sec.items.length})</span></summary>
            <div className="body">
              <ul>{sec.items.map((it, i) => <li key={i}>{it}</li>)}</ul>
            </div>
          </details>
        ),
      )}
    </div>
  );
}
