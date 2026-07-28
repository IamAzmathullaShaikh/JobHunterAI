from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from core.database.models import (InterviewQuestion, InterviewSession,
                                  JobListing, Resume)
from core.dependencies import get_job_service, get_interview_service
from core.schemas.api_payloads import (AnswerSubmissionRequest,
                                       InterviewSessionCreateRequest)
from core.services.job_service import JobService
from core.services.interview_service import InterviewService

router = APIRouter(prefix="/api/interview", tags=["interview"])


@router.get("/sessions")
async def list_sessions(job_service: JobService = Depends(get_job_service)):
    db = job_service.session
    stmt = select(InterviewSession).order_by(InterviewSession.updated_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/sessions", status_code=status.HTTP_201_CREATED)
async def create_session(
    request: InterviewSessionCreateRequest,
    job_service: JobService = Depends(get_job_service),
    service: InterviewService = Depends(get_interview_service),
):
    db = job_service.session
    resume = await db.get(Resume, request.resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    jd = request.job_description
    if not jd and request.job_id:
        job = await db.get(JobListing, request.job_id)
        if job:
            jd = job.description_raw or job.title

    if not jd:
        raise HTTPException(status_code=400, detail="Job description context is required")

    # 1. Create Session
    new_session = InterviewSession(
        name=request.name,
        resume_id=request.resume_id,
        job_id=request.job_id,
        difficulty=request.difficulty,
        status="In-Progress",
    )
    db.add(new_session)
    await db.flush()

    # 2. Generate Questions via AI
    questions_data = await service.generate_questions(
        resume_content=resume.content,
        job_description=jd,
        difficulty=request.difficulty,
    )

    for q in questions_data:
        db_q = InterviewQuestion(
            session_id=new_session.id,
            question_text=q["question_text"],
            category=q["category"],
        )
        db.add(db_q)

    await db.commit()
    await db.refresh(new_session)
    return new_session


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: int, job_service: JobService = Depends(get_job_service)
):
    db = job_service.session
    # Load with questions
    from sqlalchemy.orm import selectinload
    stmt = select(InterviewSession).where(InterviewSession.id == session_id).options(selectinload(InterviewSession.questions))
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.post("/questions/{question_id}/answer")
async def submit_answer(
    question_id: int,
    request: AnswerSubmissionRequest,
    job_service: JobService = Depends(get_job_service),
    service: InterviewService = Depends(get_interview_service),
):
    db = job_service.session
    question = await db.get(InterviewQuestion, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Evaluate via AI
    evaluation = await service.evaluate_answer(
        question=question.question_text,
        answer=request.user_answer
    )

    question.user_answer = request.user_answer
    question.score = evaluation.get("score", 0)
    question.feedback = evaluation
    question.improved_answer = evaluation.get("improved_answer")

    await db.commit()
    await db.refresh(question)
    return question


@router.post("/sessions/{session_id}/finalize")
async def finalize_session(
    session_id: int, job_service: JobService = Depends(get_job_service)
):
    """Calculates final metrics for an interview session."""
    db = job_service.session
    from sqlalchemy.orm import selectinload
    stmt = select(InterviewSession).where(InterviewSession.id == session_id).options(selectinload(InterviewSession.questions))
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    answered = [q for q in session.questions if q.score is not None]
    if not answered:
        session.overall_score = 0
    else:
        session.overall_score = sum(q.score for q in answered) / len(answered)

    session.status = "Completed"
    await db.commit()
    return session


@router.post("/sessions/{session_id}/export")
async def export_session(
    session_id: int,
    request: dict,  # format
    job_service: JobService = Depends(get_job_service),
):
    db = job_service.session
    from sqlalchemy.orm import selectinload
    stmt = select(InterviewSession).where(InterviewSession.id == session_id).options(selectinload(InterviewSession.questions))
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    format = request.get("format", "pdf")

    # We can use TemplateEngine for this too, or a simple Markdown/PDF generator
    # For now, we'll implement a simple markdown export
    md = f"# Interview Prep: {session.name}\n"
    md += f"Difficulty: {session.difficulty} | Overall Score: {session.overall_score or 0}/10\n\n"

    for q in session.questions:
        md += f"## {q.category}: {q.question_text}\n"
        md += f"**Your Answer:** {q.user_answer}\n\n"
        md += f"**Score:** {q.score}/10\n"
        md += f"**Feedback:** {q.feedback.get('suggestions', 'N/A') if q.feedback else 'N/A'}\n\n"
        md += "---\n\n"

    if format == "markdown":
        return {"success": True, "data": md}

    if format == "pdf":
        output_path = f"interview_export_{session.id}.pdf"
        # Serialize session for template engine
        session_data = {
            "name": session.name,
            "difficulty": session.difficulty,
            "overall_score": round(session.overall_score or 0, 1),
            "questions": [
                {
                    "category": q.category,
                    "question_text": q.question_text,
                    "user_answer": q.user_answer,
                    "score": q.score,
                    "feedback": q.feedback,
                    "improved_answer": q.improved_answer
                } for q in session.questions
            ]
        }
        try:
            await template_engine.export_pdf_interview_session(session_data, "interview_session_standard", output_path)
            return {"success": True, "download_url": f"/api/resumes/download/{output_path}"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return {"success": False, "error": "Format not supported"}


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: int, job_service: JobService = Depends(get_job_service)
):
    db = job_service.session
    session = await db.get(InterviewSession, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    await db.delete(session)
    await db.commit()
    return {"success": True}
