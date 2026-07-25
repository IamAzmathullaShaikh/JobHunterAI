from application.dto.output.resume_output import ResumeScoreDTO
from application.results.result import Result
from application.use_cases.resume.score_resume import ScoreResumeUseCase


class ResumeScoringService:
    def __init__(self, score_uc: ScoreResumeUseCase):
        self._score_uc = score_uc

    async def score(self, resume_id: str) -> Result[ResumeScoreDTO]:
        return await self._score_uc.execute(resume_id)
