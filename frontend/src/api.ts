import type {
  GenerateInput,
  GenerateResponse,
  TailoredResume,
} from "./types";

// In dev (npm run dev), Vite proxies /api/* to the local backend, so leaving
// API_BASE empty makes `/api/generate` work via the proxy.
// In production (Vercel build), set VITE_API_BASE_URL to your Render backend
// URL, e.g. https://airesume-backend.onrender.com.
const API_BASE = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");

function apiUrl(path: string): string {
  return `${API_BASE}${path}`;
}

async function readErrorMessage(res: Response): Promise<string> {
  try {
    const data = await res.json();
    if (typeof data?.detail === "string") return data.detail;
    if (data?.detail) return JSON.stringify(data.detail);
    return res.statusText || `HTTP ${res.status}`;
  } catch {
    return res.statusText || `HTTP ${res.status}`;
  }
}

export async function generate(input: GenerateInput): Promise<GenerateResponse> {
  const form = new FormData();
  form.append("resume_pdf", input.resumeFile);
  form.append("job_description", input.jobDescription);
  form.append("experience_level", input.experienceLevel);
  form.append("industry", input.industry);
  form.append("tone", input.tone);

  const res = await fetch(apiUrl("/api/generate"), { method: "POST", body: form });
  if (!res.ok) throw new Error(await readErrorMessage(res));
  return (await res.json()) as GenerateResponse;
}

function triggerDownload(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export async function downloadResumePdf(
  resume: TailoredResume,
): Promise<void> {
  const res = await fetch(apiUrl("/api/download/resume"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tailored_resume: resume }),
  });
  if (!res.ok) throw new Error(await readErrorMessage(res));
  const blob = await res.blob();
  triggerDownload(blob, `${slug(resume.candidate_name)}_resume.pdf`);
}

export async function downloadCoverPdf(
  coverLetter: string,
  candidateName: string,
  contact: Record<string, string>,
): Promise<void> {
  const res = await fetch(apiUrl("/api/download/cover"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      cover_letter: coverLetter,
      candidate_name: candidateName,
      contact,
    }),
  });
  if (!res.ok) throw new Error(await readErrorMessage(res));
  const blob = await res.blob();
  triggerDownload(blob, `${slug(candidateName)}_cover_letter.pdf`);
}

function slug(s: string): string {
  return (s || "document").replace(/[^A-Za-z0-9._-]+/g, "_").replace(/^_+|_+$/g, "");
}
