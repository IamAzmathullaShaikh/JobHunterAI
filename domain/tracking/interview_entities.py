from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Tuple

from domain.shared.enums import InterviewStatus
from domain.shared.value_objects import (ApplicationId, CandidateId,
                                         QuestionId, ReadinessScore, SessionId,
                                         STARAnalysis, StudyPlanId)


@dataclass(frozen=True)
class InterviewQuestion:
    """A single interview question with deterministic metadata."""

    id: QuestionId
    category: str  # technical, behavioural, hr, situational
    difficulty: str  # beginner, intermediate, advanced
    text: str
    sample_answer: Optional[str] = None
    target_skill: Optional[str] = None


@dataclass
class Answer:
    """A user response to a mock interview question."""

    question_id: QuestionId
    text: str
    star_analysis: Optional[STARAnalysis] = None
    recorded_at: datetime = field(default_factory=datetime.now)
    feedback: Optional[str] = None


@dataclass
class InterviewSession:
    """Aggregate root for a mock interview simulation."""

    id: SessionId
    application_id: ApplicationId
    questions: List[InterviewQuestion]
    answers: List[Answer] = field(default_factory=list)
    status: str = "started"  # started, completed, cancelled
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    def record_answer(
        self,
        question_id: QuestionId,
        text: str,
        analysis: Optional[STARAnalysis] = None,
    ):
        if self.status == "completed":
            raise ValueError("Cannot record answer for a completed session.")

        answer = Answer(question_id=question_id, text=text, star_analysis=analysis)
        self.answers.append(answer)

        if len(self.answers) == len(self.questions):
            self.complete()

    def complete(self):
        self.status = "completed"
        self.completed_at = datetime.now()


@dataclass(frozen=True)
class StudyTopic:
    topic: str
    priority: str  # high, medium, low
    estimated_time_minutes: int
    learning_objectives: List[str]


@dataclass
class StudyPlan:
    """Structured learning path for interview preparation."""

    id: StudyPlanId
    candidate_id: CandidateId
    job_id: Optional[str]
    topics: List[StudyTopic]
    created_at: datetime = field(default_factory=datetime.now)
