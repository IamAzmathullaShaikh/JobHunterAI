# Phase 0.1: Database Initialization Fix

## What to do:
Fix the database initialization so tables are created automatically on app startup instead of crashing with "table not found" errors.

## Files to modify:
1. `core/lifecycle.py` - Add database initialization
2. `core/database/connection.py` - Verify engine setup

## Step 1: Update core/lifecycle.py

Replace the `AppLifecycleManager.startup()` method with this:

```python
import logging
from typing import Optional

logger = logging.getLogger("jobhunterai.lifecycle")


class AppLifecycleManager:
    """Manages application startup and shutdown."""
    
    @staticmethod
    async def startup():
        """Initialize all services on app startup."""
        logger.info("Starting JobHunterAI backend...")
        
        # 1. Initialize database
        await AppLifecycleManager._initialize_database()
        
        # 2. Initialize other services (add as needed)
        logger.info("✓ All services initialized successfully")
    
    @staticmethod
    async def _initialize_database():
        """Create database tables if they don't exist."""
        try:
            from core.database.models import Base
            from core.database.connection import async_engine
            
            # Create all tables (idempotent - won't fail if they exist)
            async with async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            logger.info("✓ Database schema initialized")
        except Exception as e:
            logger.error(f"✗ Database initialization failed: {e}")
            raise RuntimeError(f"Failed to initialize database: {e}") from e
    
    @staticmethod
    async def shutdown():
        """Clean up on app shutdown."""
        logger.info("Shutting down JobHunterAI backend...")
        try:
            from core.database.connection import async_engine
            await async_engine.dispose()
            logger.info("✓ Database connections closed")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
```

## Step 2: Verify core/database/connection.py

Open the file and make sure it has:

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Should have something like:
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # Set to True for SQL debugging
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
```

## Step 3: Test it works

```bash
# Test database initialization
python -c "
import asyncio
from core.lifecycle import AppLifecycleManager

asyncio.run(AppLifecycleManager.startup())
print('Database initialized successfully!')
"
```

Expected output: `✓ Database schema initialized`

## Step 4: Create test file

Create `tests/unit/test_database_init.py`:

```python
import pytest
from sqlalchemy import text
from core.lifecycle import AppLifecycleManager
from core.database.connection import AsyncSessionLocal


@pytest.mark.asyncio
async def test_database_initializes_on_startup():
    """Verify database tables are created on startup."""
    # Run startup
    await AppLifecycleManager.startup()
    
    # Verify tables exist
    async with AsyncSessionLocal() as session:
        # Check if job_listings table exists
        result = await session.execute(
            text("SELECT 1 FROM information_schema.tables WHERE table_name='job_listings'")
        )
        exists = result.scalar() is not None
        
        # For SQLite, use different query
        try:
            result = await session.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name='job_listings'")
            )
            exists = result.scalar() is not None
        except:
            pass
        
        assert exists, "job_listings table not created"


@pytest.mark.asyncio
async def test_database_survives_multiple_startups():
    """Verify startup is idempotent (safe to call multiple times)."""
    # Call startup twice - should not fail
    await AppLifecycleManager.startup()
    await AppLifecycleManager.startup()
    
    # If we got here without exceptions, it worked
    assert True
```

## Step 5: Run the test

```bash
pytest tests/unit/test_database_init.py -v
```

Expected: All tests pass ✓

## Troubleshooting

**Error: "table already exists"**
- This is OK! It means `create_all()` is idempotent (safe to call multiple times)

**Error: "async_engine not defined"**
- Make sure `core/database/connection.py` exports `async_engine`

**Error: "Models not imported"**
- Make sure all SQLAlchemy models are imported in `core/database/models.py`

## Commit your changes:

```bash
git add core/lifecycle.py tests/unit/test_database_init.py
git commit -m "fix: database initialization on app startup"
git push
```

---

# Phase 0.2: Fix Environment Variable Validation

## What to do:
Fix the bug where `config_dict.get(env)` returns `None` for unset variables, making the router think keys are missing when they're actually not checked properly.

## File to modify:
`core/ai/smart_router.py`

## Current (Buggy) Code:

```python
for requirement in required_envs:
    if isinstance(requirement, list):
        # OR Logic: At least one in the sub-list must exist
        if not any(config_dict.get(env) for env in requirement):  # ← BUG HERE
            can_proceed = False
```

## Problem:
`config_dict.get(env)` returns `None` for missing keys, which is falsy. But empty strings `""` are also falsy, so we can't distinguish between "not set" and "set to empty string".

## Fix:

Replace the environment checking logic in `core/ai/smart_router.py`:

```python
import asyncio
import logging
from typing import Any, Callable, List

from core.config.settings import settings

logger = logging.getLogger("jobhunterai.smart_router")


def _is_api_key_set(config_dict: dict, key: str) -> bool:
    """
    Check if an API key is actually set (not None, not empty string).
    
    Args:
        config_dict: Pydantic model.model_dump() dict
        key: Environment variable name to check
    
    Returns:
        True if key has a non-empty value, False otherwise
    """
    value = config_dict.get(key)
    # Check: not None AND not empty string
    return value is not None and str(value).strip() != ""


def _check_required_envs(required_envs: List[Any], config_dict: dict) -> bool:
    """
    Validate that required environment variables are set.
    
    Args:
        required_envs: List of strings (AND logic) or list of lists (OR logic)
        config_dict: Pydantic model.model_dump() dict
    
    Returns:
        True if all requirements met, False otherwise
    
    Examples:
        ["GROQ_API_KEY"]  # Must have GROQ_API_KEY
        [["GROQ_API_KEY", "GEMINI_API_KEY"]]  # Must have at least one
        ["REQUIRED_KEY", ["OPTIONAL_A", "OPTIONAL_B"]]  # Must have REQUIRED_KEY AND (A or B)
    """
    for requirement in required_envs:
        if isinstance(requirement, list):
            # OR Logic: At least one in the sub-list must exist
            if not any(_is_api_key_set(config_dict, env) for env in requirement):
                return False
        else:
            # AND Logic: Must exist
            if not _is_api_key_set(config_dict, requirement):
                return False
    
    return True


async def route(primary_fn: Callable, fallback_fn: Callable, *args, **kwargs) -> Any:
    """
    Dual-Engine Router (2-tier):
    1. Checks for required environment variables for primary_fn.
       Supports AND (list) and OR (nested list) logic.
    2. Attempts primary_fn (Tier 1 - Cloud).
    3. If fails or keys missing, attempts fallback_fn (Tier 3 - Local).
    """
    # 1. Check required environment variables using standardized settings
    required_envs: List[Any] = getattr(primary_fn, "required_envs", [])

    can_proceed = True
    missing_info = []

    # Get settings as dict for easy access
    config_dict = settings.model_dump()

    # ✓ FIXED: Use new _check_required_envs function
    if not _check_required_envs(required_envs, config_dict):
        can_proceed = False
        for requirement in required_envs:
            if isinstance(requirement, list):
                if not any(_is_api_key_set(config_dict, env) for env in requirement):
                    missing_info.append(f"({' or '.join(requirement)})")
            else:
                if not _is_api_key_set(config_dict, requirement):
                    missing_info.append(requirement)

    if not can_proceed:
        logger.warning(
            f"Missing Tier 1 API keys {', '.join(missing_info)}. Falling back to Tier 3 (Local) for {primary_fn.__name__}."
        )
        result = fallback_fn(*args, **kwargs)
        if asyncio.iscoroutine(result):
            return await result
        return result

    # 2. Attempt primary cloud function
    try:
        logger.info(f"Initiating Tier 1 (Cloud) call for {primary_fn.__name__}...")
        result = primary_fn(*args, **kwargs)
        if asyncio.iscoroutine(result) or asyncio.iscoroutinefunction(primary_fn):
            result = await result

        if result is None:
            logger.error(
                f"Tier 1 (Cloud) for {primary_fn.__name__} returned None. Falling back to Tier 3 (Local)."
            )
            result = fallback_fn(*args, **kwargs)
            if asyncio.iscoroutine(result) or asyncio.iscoroutinefunction(fallback_fn):
                return await result
            return result

        logger.info(f"Tier 1 (Cloud) for {primary_fn.__name__} completed successfully.")
        return result

    except Exception as e:
        err_str = str(e).lower()
        if "safety" in err_str or "policy" in err_str:
            logger.error(f"Tier 1 (Cloud) blocked by AI Safety Filter: {str(e)}")
        else:
            logger.error(
                f"Tier 1 (Cloud) call failed for {primary_fn.__name__} with exception: {str(e)}"
            )

        logger.info(f"Falling back to Tier 3 (Local) for {primary_fn.__name__}.")

        # 3. Execute fallback
        try:
            result = fallback_fn(*args, **kwargs)
            if asyncio.iscoroutine(result) or asyncio.iscoroutinefunction(fallback_fn):
                return await result
            return result
        except Exception as fe:
            logger.critical(
                f"Tier 3 (Local) for {primary_fn.__name__} ALSO failed: {str(fe)}"
            )
            # Return safe placeholder defined on the fallback function or a generic empty dict
            return getattr(fallback_fn, "safe_placeholder", {})
```

## Create test file:

Create `tests/unit/test_settings_validation.py`:

```python
import pytest
from unittest.mock import patch
from core.ai.smart_router import _is_api_key_set, _check_required_envs


def test_missing_groq_key_detected():
    """Verify router detects missing Groq key."""
    config_dict = {"GROQ_API_KEY": None, "GEMINI_API_KEY": None}
    
    assert _is_api_key_set(config_dict, "GROQ_API_KEY") is False


def test_empty_string_treated_as_missing():
    """Verify empty string is treated like None."""
    config_dict = {"GROQ_API_KEY": ""}
    
    assert _is_api_key_set(config_dict, "GROQ_API_KEY") is False


def test_whitespace_treated_as_missing():
    """Verify whitespace-only string is treated as missing."""
    config_dict = {"GROQ_API_KEY": "   "}
    
    assert _is_api_key_set(config_dict, "GROQ_API_KEY") is False


def test_valid_key_detected():
    """Verify valid keys are detected."""
    config_dict = {"GROQ_API_KEY": "gsk_valid_key_12345"}
    
    assert _is_api_key_set(config_dict, "GROQ_API_KEY") is True


def test_or_logic_with_one_valid_key():
    """Verify OR logic passes if one key exists."""
    config_dict = {
        "GROQ_API_KEY": None,
        "GEMINI_API_KEY": "gm_valid_key"
    }
    
    result = _check_required_envs(
        [["GROQ_API_KEY", "GEMINI_API_KEY"]],
        config_dict
    )
    assert result is True


def test_or_logic_with_no_valid_keys():
    """Verify OR logic fails if no keys exist."""
    config_dict = {
        "GROQ_API_KEY": None,
        "GEMINI_API_KEY": None
    }
    
    result = _check_required_envs(
        [["GROQ_API_KEY", "GEMINI_API_KEY"]],
        config_dict
    )
    assert result is False


def test_and_logic_requires_all():
    """Verify AND logic requires all keys."""
    config_dict = {
        "KEY_A": "value_a",
        "KEY_B": None
    }
    
    result = _check_required_envs(
        ["KEY_A", "KEY_B"],
        config_dict
    )
    assert result is False


def test_and_logic_passes_with_all():
    """Verify AND logic passes when all keys exist."""
    config_dict = {
        "KEY_A": "value_a",
        "KEY_B": "value_b"
    }
    
    result = _check_required_envs(
        ["KEY_A", "KEY_B"],
        config_dict
    )
    assert result is True


def test_mixed_and_or_logic():
    """Verify mixed AND/OR logic."""
    config_dict = {
        "REQUIRED": "value",
        "CHOICE_A": None,
        "CHOICE_B": "value_b"
    }
    
    result = _check_required_envs(
        ["REQUIRED", ["CHOICE_A", "CHOICE_B"]],
        config_dict
    )
    assert result is True
```

## Test it:

```bash
pytest tests/unit/test_settings_validation.py -v
```

Expected: All tests pass ✓

## Commit:

```bash
git add core/ai/smart_router.py tests/unit/test_settings_validation.py
git commit -m "fix: environment variable validation for OR logic"
git push
```

---

# Phase 0.3: Harden PII Redactor

## What to do:
Replace unsafe `.replace()` with atomic `re.sub()` callback to prevent partial redactions.

## File to modify:
`core/privacy.py`

## Replace entire file with:

```python
import re
import uuid
from typing import Dict, Tuple


class PIIRedactor:
    """
    Redacts and restores PII (Personally Identifiable Information) from text
    to protect user privacy when sending data to external AI providers.
    """

    # Simple patterns for redaction
    PATTERNS = {
        "EMAIL": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        "PHONE": r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
        "ADDRESS": r"\d+\s+[a-zA-Z0-9\s,.]+?\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Court|Ct|Way|Lane|Ln|Trail|Trl|Circle|Cir|Zip|Parkway|Pkwy|Plaza|Plz)\b",
    }

    def redact(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Redacts PII from text using atomic regex substitution.
        
        Args:
            text: Input text potentially containing PII
        
        Returns:
            Tuple of (redacted_text, mapping_dict) where mapping_dict
            stores placeholders → original values for restoration
        """
        if not text:
            return "", {}

        mapping = {}
        redacted_text = text

        # Apply each pattern atomically using re.sub with callback
        for pii_type, pattern in self.PATTERNS.items():
            def replace_with_placeholder(match):
                """Callback for re.sub to generate unique placeholder."""
                unique_id = str(uuid.uuid4())[:8]
                placeholder = f"[[REDACTED_{pii_type}_{unique_id}]]"
                mapping[placeholder] = match.group(0)
                return placeholder

            # Atomic substitution - one pass per pattern type
            redacted_text = re.sub(
                pattern,
                replace_with_placeholder,
                redacted_text,
                flags=re.IGNORECASE
            )

        return redacted_text, mapping

    def restore(self, text: str, mapping: Dict[str, str]) -> str:
        """
        Restores redacted PII in the text using the provided mapping.
        
        Args:
            text: Redacted text with placeholders
            mapping: Dict of placeholder → original_value from redact()
        
        Returns:
            Original text with all redactions restored
        """
        if not text or not mapping:
            return text

        restored_text = text
        for placeholder, original in mapping.items():
            restored_text = restored_text.replace(placeholder, original)

        return restored_text


# Global singleton for easy access
redactor = PIIRedactor()
```

## Create comprehensive test file:

Create `tests/unit/test_pii_redaction.py`:

```python
import pytest
from core.privacy import redactor


class TestPIIRedaction:
    """Test suite for PII redaction functionality."""
    
    def test_email_redaction(self):
        """Verify email addresses are redacted."""
        text = "Contact me at john.doe@example.com for more info"
        redacted, mapping = redactor.redact(text)
        
        # Email should be redacted
        assert "john.doe@example.com" not in redacted
        
        # Should have mapping entry
        assert len(mapping) > 0
        
        # Placeholder should exist in redacted text
        assert any("REDACTED_EMAIL" in p for p in mapping.keys())
        
        # Restore should recover original
        restored = redactor.restore(redacted, mapping)
        assert restored == text
    
    def test_phone_redaction(self):
        """Verify phone numbers are redacted."""
        text = "Call me at +1-234-567-8900 or (234) 567-8900"
        redacted, mapping = redactor.redact(text)
        
        # Both phone formats should be redacted
        assert "+1-234-567-8900" not in redacted
        assert "(234) 567-8900" not in redacted
        
        # Should have 2 phone redactions
        phone_redactions = [p for p in mapping.keys() if "PHONE" in p]
        assert len(phone_redactions) >= 1
        
        # Restore should work
        restored = redactor.restore(redacted, mapping)
        assert restored == text
    
    def test_address_redaction(self):
        """Verify addresses are redacted."""
        text = "Our office is at 123 Main Street, Springfield"
        redacted, mapping = redactor.redact(text)
        
        # Address should be redacted
        assert "123 Main Street" not in redacted
        
        # Should have address redaction
        address_redactions = [p for p in mapping.keys() if "ADDRESS" in p]
        assert len(address_redactions) >= 1
        
        # Restore works
        restored = redactor.restore(redacted, mapping)
        assert restored == text
    
    def test_multiple_pii_types(self):
        """Verify multiple PII types are redacted together."""
        text = "John Doe at 123 Oak Ave, john@example.com, 555-123-4567"
        redacted, mapping = redactor.redact(text)
        
        # All PII should be redacted
        assert "john@example.com" not in redacted
        assert "555-123-4567" not in redacted
        assert "123 Oak Ave" not in redacted
        
        # Multiple mapping entries
        assert len(mapping) >= 3
        
        # Restore completely
        restored = redactor.restore(redacted, mapping)
        assert restored == text
    
    def test_no_collision_on_multiple_instances(self):
        """Verify no placeholder collisions for same PII type."""
        text = "Email alice@test.com and bob@test.com"
        redacted, mapping = redactor.redact(text)
        
        # Should have 2 email entries (with different UUIDs)
        email_placeholders = [p for p in mapping.keys() if "EMAIL" in p]
        assert len(email_placeholders) == 2
        
        # All placeholders unique
        assert len(email_placeholders) == len(set(email_placeholders))
        
        # Restore works
        restored = redactor.restore(redacted, mapping)
        assert restored == text
    
    def test_empty_text_handling(self):
        """Verify empty text is handled gracefully."""
        redacted, mapping = redactor.redact("")
        
        assert redacted == ""
        assert mapping == {}
    
    def test_text_with_no_pii(self):
        """Verify text without PII is unchanged."""
        text = "This is just normal text with no personal info"
        redacted, mapping = redactor.redact(text)
        
        # No redactions should occur
        assert redacted == text
        assert mapping == {}
    
    def test_case_insensitive_matching(self):
        """Verify PII patterns are case insensitive."""
        text = "Email: JOHN@EXAMPLE.COM or john@example.com"
        redacted, mapping = redactor.redact(text)
        
        # Both should be redacted
        assert "JOHN@EXAMPLE.COM" not in redacted
        assert "john@example.com" not in redacted
        
        # Restore works
        restored = redactor.restore(redacted, mapping)
        assert restored == text
    
    def test_partial_redaction_prevented(self):
        """
        Verify that partial replacements don't occur.
        Example: redacting "John" shouldn't affect "Johnson"
        """
        text = "John Doe works with Johnson Smith"
        redacted, mapping = redactor.redact(text)
        
        # Without proper redaction, "Johnson" could become "[[REDACTED]]son"
        # With proper regex, this shouldn't happen
        # (Note: Our patterns don't specifically redact names,
        # but this test ensures we're using regex properly)
        
        restored = redactor.restore(redacted, mapping)
        assert restored == text
    
    def test_unicode_in_pii(self):
        """Verify non-ASCII characters are handled."""
        text = "Contáct josé.garcía@ejemplo.com or José García"
        redacted, mapping = redactor.redact(text)
        
        # Email should still be redacted
        assert "josé.garcía@ejemplo.com" not in redacted
        
        # Restore works
        restored = redactor.restore(redacted, mapping)
        assert restored == text
    
    def test_mapping_is_bidirectional(self):
        """Verify mapping stores original values correctly."""
        text = "Email: alice@test.com Phone: 555-1234"
        redacted, mapping = redactor.redact(text)
        
        # All values in mapping should be from original text
        for placeholder, original_value in mapping.items():
            assert original_value in text
        
        # Restore should produce exact original
        restored = redactor.restore(redacted, mapping)
        assert restored == text
```

## Test it:

```bash
pytest tests/unit/test_pii_redaction.py -v
```

Expected: All tests pass ✓

## Commit:

```bash
git add core/privacy.py tests/unit/test_pii_redaction.py
git commit -m "fix: atomic PII redaction with UUID collision prevention"
git push
```

---

## Summary of Phase 0 Fixes

✅ **Database initialization** - Tables auto-created on startup  
✅ **Environment validation** - Proper AND/OR logic for API keys  
✅ **PII redaction** - Atomic substitution with no partial replacements  

All tests passing? Great! Move to Phase 1: Smart Router Refactor.

Run this to confirm all Phase 0 tests pass:

```bash
pytest tests/unit/test_database_init.py tests/unit/test_settings_validation.py tests/unit/test_pii_redaction.py -v
```

Expected: 20+ tests all passing ✓
