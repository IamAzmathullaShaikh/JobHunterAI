import pytest

from domain.services.career_assistant.post_processing_service import \
    ContentPostProcessingService
from domain.services.career_assistant.validation_service import \
    ContentValidationService


def test_placeholder_detection():
    validator = ContentValidationService()
    content = (
        "Dear [Hiring Manager], my name is {{Name}}. Please contact me at <Email>."
    )

    placeholders = validator.detect_placeholders(content)
    assert "[Hiring Manager]" in placeholders
    assert "{{Name}}" in placeholders
    assert "<Email>" in placeholders
    assert len(placeholders) == 3


def test_quality_score_calculation():
    validator = ContentValidationService()

    # 1. Clean content
    score_clean = validator.calculate_quality_score(
        "This is a long enough and very professional response without any issues.",
        [],
        [],
    )
    assert score_clean > 0.8

    # 2. Content with placeholders
    score_dirty = validator.calculate_quality_score(
        "Hi [Name], [Context]", ["[Name]", "[Context]"], []
    )
    assert score_dirty < 0.6


def test_formatting_cleanup():
    processor = ContentPostProcessingService()
    raw = "   \n\n   Summary:\n\n\nExpert in Python.   \n\n"
    clean = processor.cleanup_formatting(raw)
    assert clean == "Summary:\n\nExpert in Python."


def test_mandatory_keywords():
    validator = ContentValidationService()
    content = "I have experience in Python and Docker."

    missing = validator.check_mandatory_keywords(content, ["Python", "Kubernetes"])
    assert "Kubernetes" in missing
    assert "Python" not in missing
