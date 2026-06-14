from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


ExperienceLevel = Literal["fresher", "experienced"]
Tone = Literal["professional", "confident", "formal"]


class AtsAnalysis(BaseModel):
    score: int = Field(ge=0, le=100)
    keyword_match_percent: int = Field(ge=0, le=100)
    matched_keywords: list[str]
    missing_keywords: list[str]
    strength_areas: list[str]
    weak_areas: list[str]
    explanation: str


class ResumeExperience(BaseModel):
    role: str
    company: str
    location: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    bullets: list[str] = []


class ResumeProject(BaseModel):
    name: str
    description: str
    tech: list[str] = []
    bullets: list[str] = []


class ResumeEducation(BaseModel):
    degree: str
    institution: str
    location: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    details: str | None = None


class TailoredResume(BaseModel):
    candidate_name: str
    contact: dict[str, str] = {}
    professional_summary: str
    technical_skills: list[str]
    experience: list[ResumeExperience] = []
    projects: list[ResumeProject] = []
    education: list[ResumeEducation] = []
    certifications: list[str] = []
    achievements: list[str] = []
    tools_technologies: list[str] = []


class SkillSuggestions(BaseModel):
    missing_skills: list[str] = []
    certifications: list[str] = []
    project_ideas: list[str] = []
    interview_topics: list[str] = []
    resume_tips: list[str] = []
    portfolio_tips: list[str] = []
    linkedin_tips: list[str] = []


class AutomationMeta(BaseModel):
    candidate_name: str
    target_role: str
    experience_level: str
    primary_skills: list[str] = []
    secondary_skills: list[str] = []
    preferred_locations: list[str] = []
    job_keywords: list[str] = []
    ats_score: int = Field(ge=0, le=100)
    auto_apply_ready: bool = True


class GenerateResponse(BaseModel):
    ats: AtsAnalysis
    tailored_resume: TailoredResume
    cover_letter: str
    suggestions: SkillSuggestions
    automation: AutomationMeta


class DownloadResumeRequest(BaseModel):
    tailored_resume: TailoredResume


class DownloadCoverRequest(BaseModel):
    cover_letter: str
    candidate_name: str
    contact: dict[str, str] = {}
    company_name: str | None = None
    role_title: str | None = None
