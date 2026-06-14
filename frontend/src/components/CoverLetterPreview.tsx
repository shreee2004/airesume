interface Props {
  coverLetter: string;
}

export default function CoverLetterPreview({ coverLetter }: Props) {
  const paragraphs = coverLetter.split(/\n{2,}/).map((p) => p.trim()).filter(Boolean);
  const words = coverLetter.trim().split(/\s+/).filter(Boolean).length;
  return (
    <div className="card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
        <h3 style={{ margin: "0 0 10px" }}>Cover letter</h3>
        <span style={{ fontSize: 12, color: "#5b6175" }}>{words} words</span>
      </div>
      <div className="cover-preview">
        {paragraphs.map((p, i) => <p key={i}>{p}</p>)}
      </div>
    </div>
  );
}
