// Mirrors backend/app/schemas.py — keep in sync.

export type ExperienceLevel = "fresher" | "experienced";
export type Tone = "professional" | "confident" | "formal";

export interface AtsAnalysis {
  score: number;
  keyword_match_percent: number;
  matched_keywords: string[];
  missing_keywords: string[];
  strength_areas: string[];
  weak_areas: string[];
  explanation: string;
}

export interface ResumeExperience {
  role: string;
  company: string;
  location?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  bullets: string[];
}

export interface ResumeProject {
  name: string;
  description: string;
  tech: string[];
  bullets: string[];
}

export interface ResumeEducation {
  degree: string;
  institution: string;
  location?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  details?: string | null;
}

export interface TailoredResume {
  candidate_name: string;
  contact: Record<string, string>;
  professional_summary: string;
  technical_skills: string[];
  experience: ResumeExperience[];
  projects: ResumeProject[];
  education: ResumeEducation[];
  certifications: string[];
  achievements: string[];
  tools_technologies: string[];
}

export interface SkillSuggestions {
  missing_skills: string[];
  certifications: string[];
  project_ideas: string[];
  interview_topics: string[];
  resume_tips: string[];
  portfolio_tips: string[];
  linkedin_tips: string[];
}

export interface AutomationMeta {
  candidate_name: string;
  target_role: string;
  experience_level: string;
  primary_skills: string[];
  secondary_skills: string[];
  preferred_locations: string[];
  job_keywords: string[];
  ats_score: number;
  auto_apply_ready: boolean;
}

export interface GenerateResponse {
  ats: AtsAnalysis;
  tailored_resume: TailoredResume;
  cover_letter: string;
  suggestions: SkillSuggestions;
  automation: AutomationMeta;
}

export interface GenerateInput {
  resumeFile: File;
  jobDescription: string;
  experienceLevel: ExperienceLevel;
  industry: string;
  tone: Tone;
}
