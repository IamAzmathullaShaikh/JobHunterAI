import pytest

from domain.discovery.entities import (ATSScore, Job, Location, MatchBreakdown,
                                       MatchResult)
from domain.profile.candidate import Candidate
from domain.services.interview.feedback_analysis import FeedbackAnalysisService
from domain.services.interview.preparation_service import \
    InterviewPreparationService
from domain.services.interview.readiness_service import \
    InterviewReadinessService
from domain.services.interview.star_coaching import STARCoachingService
from domain.shared.value_objects import (CandidateId, ContactInfo,
                                         EmailAddress, JobId, QuestionId,
                                         SessionId, STARAnalysis)
from domain.tracking.interview_entities import Answer, InterviewSession


def test_star_analysis_heuristic():
    # 1. Complete Answer
    text = "When I was at Google, I was tasked with scaling the search engine. I built a new index. The result was a 20% speed increase."
    analysis = STARCoachingService.analyze_answer(text)
    assert analysis.has_situation
    assert analysis.has_task
    assert analysis.has_action
    assert analysis.has_result
    assert analysis.completeness_score == 1.0

    # 2. Incomplete Answer
    text = "I built a new index."
    analysis = STARCoachingService.analyze_answer(text)
    assert not analysis.has_situation
    assert not analysis.has_result
    assert analysis.completeness_score < 1.0


def test_readiness_calculation():
    match = MatchResult(
        job_id=JobId(),
        candidate_id=CandidateId(),
        overall_score=0.8,
        breakdown=MatchBreakdown(0.8, 0.8, 1.0, 0.7, 1.0, 1.0),
        matched_skills=[],
        missing_skills=[],
        fit_summary="Good",
    )
    ats = ATSScore(
        resume_id="r1", overall_score=0.9, section_scores={}, recommendations=[]
    )

    readiness = InterviewReadinessService.calculate_readiness(
        match_result=match, ats_score=ats, mock_sessions_count=3, average_mock_score=0.9
    )

    assert readiness.overall_score > 0.8
    assert readiness.is_ready == True


def test_feedback_analysis():
    session = InterviewSession(id=SessionId(), application_id=JobId(), questions=[])
    session.answers.append(
        Answer(
            question_id=QuestionId(),
            text="...",
            star_analysis=STARAnalysis(True, True, True, True, 1.0, "Good", []),
        )
    )

    analysis = FeedbackAnalysisService.analyze_session(session)
    assert analysis["average_star_score"] == 1.0
    assert analysis["overall_sentiment"] == "Positive"


def test_preparation_strategy():
    candidate = Candidate(
        id=CandidateId(),
        _full_name="Alex",
        _contact_info=ContactInfo(EmailAddress("a@b.com")),
    )
    job = Job(
        id=JobId(),
        company_id="Google",
        title="Senior Engineer",
        description="...",
        url="",
        location=Location("NY", "USA"),
    )

    strategy = InterviewPreparationService.create_strategy(candidate, job)
    assert "Leadership & Scale" in strategy["focus_themes"]
    assert strategy["estimated_prep_hours"] > 0
