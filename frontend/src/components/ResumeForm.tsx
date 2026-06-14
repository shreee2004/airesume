import { useRef, useState, type DragEvent } from "react";
import type { ExperienceLevel, GenerateInput, Tone } from "../types";

interface Props {
  loading: boolean;
  initial?: GenerateInput;
  onSubmit: (input: GenerateInput) => void;
}

const LEVELS: { value: ExperienceLevel; label: string }[] = [
  { value: "fresher", label: "Fresher" },
  { value: "experienced", label: "Experienced" },
];

const TONES: { value: Tone; label: string }[] = [
  { value: "professional", label: "Professional" },
  { value: "confident", label: "Confident" },
  { value: "formal", label: "Formal" },
];

export default function ResumeForm({ loading, initial, onSubmit }: Props) {
  const [file, setFile] = useState<File | null>(initial?.resumeFile ?? null);
  const [jd, setJd] = useState(initial?.jobDescription ?? "");
  const [level, setLevel] = useState<ExperienceLevel>(initial?.experienceLevel ?? "experienced");
  const [industry, setIndustry] = useState(initial?.industry ?? "Technology");
  const [tone, setTone] = useState<Tone>(initial?.tone ?? "professional");
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const valid = file && jd.trim().length > 30 && industry.trim().length > 0;

  function handleFile(f: File | null | undefined) {
    if (!f) return;
    if (f.type !== "application/pdf" && !f.name.toLowerCase().endsWith(".pdf")) {
      alert("Please upload a PDF file.");
      return;
    }
    if (f.size > 5 * 1024 * 1024) {
      alert("Resume must be under 5 MB.");
      return;
    }
    setFile(f);
  }

  function onDrop(e: DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setDragging(false);
    handleFile(e.dataTransfer.files?.[0]);
  }

  function submit() {
    if (!file) return;
    onSubmit({
      resumeFile: file,
      jobDescription: jd.trim(),
      experienceLevel: level,
      industry: industry.trim(),
      tone,
    });
  }

  return (
    <div className="card">
      <div className="form-grid">
        <div className="full">
          <label className="field">
            Resume PDF <span className="hint">Digital (text-based) PDFs only — max 5 MB</span>
          </label>
          <div
            className={`file-drop ${dragging ? "dragging" : ""} ${file ? "has-file" : ""}`}
            onClick={() => inputRef.current?.click()}
            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={onDrop}
            role="button"
            tabIndex={0}
          >
            {file ? (
              <>
                <div className="filename">{file.name}</div>
                <div className="meta">{(file.size / 1024).toFixed(1)} KB — click to replace</div>
              </>
            ) : (
              <>
                <div>Click or drop your resume PDF here</div>
                <div className="meta">Your file stays on your machine until you click Generate.</div>
              </>
            )}
            <input
              ref={inputRef}
              type="file"
              accept="application/pdf,.pdf"
              hidden
              onChange={(e) => handleFile(e.target.files?.[0])}
            />
          </div>
        </div>

        <label className="field full">
          Job description
          <span className="hint">Paste the full posting — responsibilities, requirements, everything.</span>
          <textarea
            value={jd}
            onChange={(e) => setJd(e.target.value)}
            placeholder="Paste the job description here..."
            rows={10}
          />
        </label>

        <label className="field">
          Experience level
          <div className="radios">
            {LEVELS.map((l) => (
              <label key={l.value} className={level === l.value ? "active" : ""}>
                <input
                  type="radio"
                  name="level"
                  value={l.value}
                  checked={level === l.value}
                  onChange={() => setLevel(l.value)}
                />
                {l.label}
              </label>
            ))}
          </div>
        </label>

        <label className="field">
          Industry
          <input
            type="text"
            value={industry}
            onChange={(e) => setIndustry(e.target.value)}
            placeholder="e.g. Technology, Finance, Healthcare"
          />
        </label>

        <label className="field full">
          Tone
          <div className="radios">
            {TONES.map((t) => (
              <label key={t.value} className={tone === t.value ? "active" : ""}>
                <input
                  type="radio"
                  name="tone"
                  value={t.value}
                  checked={tone === t.value}
                  onChange={() => setTone(t.value)}
                />
                {t.label}
              </label>
            ))}
          </div>
        </label>
      </div>

      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: 18, gap: 12, flexWrap: "wrap" }}>
        {loading ? (
          <div className="loading">
            <div className="spinner" />
            Analyzing resume and generating tailored content — this usually takes 20–40 seconds.
          </div>
        ) : <span />}
        <button className="primary" onClick={submit} disabled={!valid || loading}>
          {loading ? "Generating…" : "Generate tailored resume"}
        </button>
      </div>
    </div>
  );
}
