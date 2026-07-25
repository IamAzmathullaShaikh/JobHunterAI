from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class InterviewQuestionDTO:
    id: str
    category: str
    difficulty: str
    text: str
    target_skill: Optional[str]


@dataclass(frozen=True)
class STARAnalysisDTO:
    score: float
    feedback: str
    missing_components: List[str]
    suggestions: List[str]


@dataclass(frozen=True)
class InterviewSessionDTO:
    id: str
    application_id: str
    status: str
    question_count: int
    answer_count: int
    started_at: str


@dataclass(frozen=True)
class StudyTopicDTO:
    topic: str
    priority: str
    time_estimate: int


@dataclass(frozen=True)
class StudyPlanDTO:
    id: str
    topic_count: int
    topics: List[StudyTopicDTO]
    created_at: str


@dataclass(frozen=True)
class ReadinessScoreDTO:
    overall: float
    is_ready: bool
    priorities: List[str]
    breakdown: Dict[str, float]


@dataclass(frozen=True)
class InterviewPreparationDTO:
    focus_themes: List[str]
    estimated_prep_hours: int
    recommended_focus: str


@dataclass(frozen=True)
class InterviewFeedbackDTO:
    average_star_score: float
    critical_gaps: List[str]
    overall_sentiment: str


@dataclass(frozen=True)
class InterviewSummaryDTO:
    session_id: str
    status: str
    summary_text: str
    completion_rate: float


@dataclass(frozen=True)
class InterviewPreparationPackageDTO:
    questions: List[InterviewQuestionDTO]
    readiness: ReadinessScoreDTO
    study_plan: StudyPlanDTO


@dataclass(frozen=True)
class PreparationPathDTO:
    strategy: InterviewPreparationDTO
    study_plan: StudyPlanDTO


@dataclass(frozen=True)
class CompanyInsightsDTO:
    company_name: str
    overview: str
    culture_themes: List[str]
    tech_stack: List[str]
    likely_interview_questions: List[str]
