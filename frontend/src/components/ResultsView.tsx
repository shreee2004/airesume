import AtsScorePanel from "./AtsScorePanel";
import CoverLetterPreview from "./CoverLetterPreview";
import DownloadButtons from "./DownloadButtons";
import KeywordsPanel from "./KeywordsPanel";
import ResumePreview from "./ResumePreview";
import SuggestionsPanel from "./SuggestionsPanel";
import type { GenerateResponse } from "../types";

interface Props {
  result: GenerateResponse;
  onReset: () => void;
}

export default function ResultsView({ result, onReset }: Props) {
  return (
    <>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
        <strong style={{ fontSize: 15 }}>Results for {result.tailored_resume.candidate_name}</strong>
        <button className="ghost" onClick={onReset}>← Start over</button>
      </div>

      <AtsScorePanel ats={result.ats} />
      <KeywordsPanel ats={result.ats} />
      <ResumePreview resume={result.tailored_resume} />
      <CoverLetterPreview coverLetter={result.cover_letter} />
      <SuggestionsPanel s={result.suggestions} />
      <DownloadButtons resume={result.tailored_resume} coverLetter={result.cover_letter} />
    </>
  );
}
