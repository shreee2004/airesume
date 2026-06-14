import { useState } from "react";
import { downloadCoverPdf, downloadResumePdf } from "../api";
import type { TailoredResume } from "../types";

interface Props {
  resume: TailoredResume;
  coverLetter: string;
}

export default function DownloadButtons({ resume, coverLetter }: Props) {
  const [busy, setBusy] = useState<"resume" | "cover" | null>(null);
  const [err, setErr] = useState<string | null>(null);

  async function go(kind: "resume" | "cover") {
    setBusy(kind);
    setErr(null);
    try {
      if (kind === "resume") {
        await downloadResumePdf(resume);
      } else {
        await downloadCoverPdf(coverLetter, resume.candidate_name, resume.contact);
      }
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="card">
      <h3 style={{ margin: "0 0 8px" }}>Download</h3>
      <div className="download-row">
        <button className="primary" disabled={busy !== null} onClick={() => go("resume")}>
          {busy === "resume" ? "Generating PDF…" : "Download resume PDF"}
        </button>
        <button className="primary" disabled={busy !== null} onClick={() => go("cover")}>
          {busy === "cover" ? "Generating PDF…" : "Download cover letter PDF"}
        </button>
      </div>
      {err && <div className="error-banner" style={{ marginTop: 10 }}>{err}</div>}
    </div>
  );
}
