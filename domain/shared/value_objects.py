import re
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Generic, List, Optional, TypeVar

from domain.shared.exceptions import ValidationError

T = TypeVar("T")


@dataclass(frozen=True)
class DomainId:
    """Base class for all strongly-typed domain identifiers."""

    value: uuid.UUID = field(default_factory=uuid.uuid4)

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def from_str(cls: type[T], value: str) -> T:
        try:
            return cls(value=uuid.UUID(value))
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid UUID for {cls.__name__}: {value}")


@dataclass(frozen=True)
class CandidateId(DomainId):
    pass


@dataclass(frozen=True)
class ResumeId(DomainId):
    pass


@dataclass(frozen=True)
class ResumeVersionId(DomainId):
    pass


@dataclass(frozen=True)
class CompanyId(DomainId):
    pass


@dataclass(frozen=True)
class JobId(DomainId):
    pass


@dataclass(frozen=True)
class ApplicationId(DomainId):
    pass


@dataclass(frozen=True)
class InterviewId(DomainId):
    pass


@dataclass(frozen=True)
class CertificationId(DomainId):
    pass


@dataclass(frozen=True)
class SkillId(DomainId):
    pass


@dataclass(frozen=True)
class QuestionId(DomainId):
    pass


@dataclass(frozen=True)
class SessionId(DomainId):
    pass


@dataclass(frozen=True)
class StudyPlanId(DomainId):
    pass


@dataclass(frozen=True)
class PromptId(DomainId):
    pass


@dataclass(frozen=True)
class ContentId(DomainId):
    pass


@dataclass(frozen=True)
class PromptMetadata:
    """Metadata for a versioned prompt template."""

    prompt_id: str
    version: str
    category: str
    expected_variables: List[str]
    output_type: str  # text, json, list
    is_active: bool = True


@dataclass(frozen=True)
class AIRequestPolicy:
    """Constraints and routing rules for an AI request."""

    max_tokens: int = 1000
    timeout_seconds: float = 30.0
    retry_count: int = 2
    cost_budget_usd: float = 0.05
    preferred_provider: Optional[str] = None
    fallback_priority: List[str] = field(
        default_factory=lambda: ["groq", "gemini", "openai"]
    )


@dataclass(frozen=True)
class ProviderCapabilities:
    """Flags for supported features of a specific AI provider."""

    can_chat: bool = True
    can_json: bool = False
    can_stream: bool = False
    can_embed: bool = False
    can_tool_call: bool = False
    can_vision: bool = False


@dataclass(frozen=True)
class GenerationConfig:
    """Settings for AI content generation."""

    temperature: float = 0.1
    max_tokens: int = 2048
    top_p: float = 1.0
    provider_override: Optional[str] = None
    model_override: Optional[str] = None
    json_mode: bool = True


@dataclass(frozen=True)
class EmailAddress:
    value: str

    def __post_init__(self):
        # Normalize first
        normalized = self.value.lower().strip()
        # RFC 5322 compliant regex (simplified for domain use)
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(pattern, normalized):
            raise ValidationError(f"Invalid email address format: {self.value}")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True)
class PhoneNumber:
    value: str

    def __post_init__(self):
        # Allow +, digits, and spaces/dashes (normalized later)
        if not re.match(r"^\+?[0-9\s\-]{7,20}$", self.value):
            raise ValidationError(f"Invalid phone number format: {self.value}")
        # Normalize: strip non-digits except lead plus
        normalized = re.sub(r"(?<!^)\D", "", self.value)
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True)
class ContactInfo:
    email: EmailAddress
    phone: Optional[PhoneNumber] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None


@dataclass(frozen=True)
class Location:
    city: str
    country: str
    state: Optional[str] = None
    is_remote: bool = False

    def matches(self, other: "Location") -> bool:
        if self.is_remote or other.is_remote:
            return True
        return (
            self.city.lower() == other.city.lower()
            and self.country.lower() == other.country.lower()
        )


@dataclass(frozen=True)
class Money:
    amount: float
    currency: str = "USD"

    def __post_init__(self):
        if self.amount < 0:
            raise ValidationError("Money amount cannot be negative.")
        if not self.currency or len(self.currency) != 3:
            raise ValidationError("Currency must be a 3-letter ISO code.")
        object.__setattr__(self, "currency", self.currency.upper())


@dataclass(frozen=True)
class SalaryRange:
    min_amount: Money
    max_amount: Money

    def __post_init__(self):
        if self.min_amount.currency != self.max_amount.currency:
            raise ValidationError("Salary range must be in the same currency.")
        if self.min_amount.amount > self.max_amount.amount:
            raise ValidationError("Salary minimum cannot be greater than maximum.")

    def contains(self, amount: Money) -> bool:
        if self.min_amount.currency != amount.currency:
            return False
        return self.min_amount.amount <= amount.amount <= self.max_amount.amount


@dataclass(frozen=True)
class SkillLevel:
    value: int  # 1 to 5

    def __post_init__(self):
        if not (1 <= self.value <= 5):
            raise ValidationError("Skill level must be between 1 and 5.")


@dataclass(frozen=True)
class STARAnalysis:
    """Analysis of a STAR-method interview response."""

    has_situation: bool
    has_task: bool
    has_action: bool
    has_result: bool
    completeness_score: float  # 0.0 to 1.0
    feedback: str
    suggestions: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class ReadinessScore:
    """Aggregation of various factors determining interview readiness."""

    overall_score: float  # 0.0 to 1.0
    category_scores: Dict[str, float]
    improvement_priorities: List[str]
    is_ready: bool
