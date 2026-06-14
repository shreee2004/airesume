import { useState } from "react";
import ResumeForm from "./components/ResumeForm";
import ResultsView from "./components/ResultsView";
import { generate } from "./api";
import type { GenerateInput, GenerateResponse } from "./types";

export default function App() {
  const [result, setResult] = useState<GenerateResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastInput, setLastInput] = useState<GenerateInput | null>(null);

  async function handleSubmit(input: GenerateInput) {
    setLoading(true);
    setError(null);
    setLastInput(input);
    try {
      const res = await generate(input);
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  function reset() {
    setResult(null);
    setError(null);
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>AI Resume &amp; Cover Letter Generator</h1>
        <p>
          Upload your resume, paste a job description, and get a tailored,
          ATS-optimized resume plus a personalized cover letter.
        </p>
      </header>

      {error && <div className="error-banner">{error}</div>}

      {!result && (
        <ResumeForm
          loading={loading}
          initial={lastInput ?? undefined}
          onSubmit={handleSubmit}
        />
      )}

      {result && (
        <ResultsView result={result} onReset={reset} />
      )}
    </div>
  );
}
