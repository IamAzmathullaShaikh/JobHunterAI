from datetime import datetime

from application.dto.output.health_output import (ComponentHealthDTO,
                                                  PlatformStatusDTO)
from application.results.result import Result
from application.services.platform_validation_service import \
    PlatformValidationService
from application.use_cases.base import ApplicationUseCase
from core.config.settings import settings


class GetPlatformHealthUseCase(ApplicationUseCase[None, PlatformStatusDTO]):
    def __init__(self, validation_service: PlatformValidationService):
        self._validation = validation_service

    async def _run(self, _=None) -> Result[PlatformStatusDTO]:
        # 1. Component checks
        validation_data = await self._validation.run_full_validation()

        components = []
        for name, status in validation_data.get("components", {}).items():
            components.append(ComponentHealthDTO(name=name, status=status))

        # 2. Config checks
        config_errors = self._validation.validate_configuration()

        output = PlatformStatusDTO(
            overall_status=validation_data["status"],
            version="3.0.0",
            environment=settings.NODE_ENV,
            timestamp=datetime.now().isoformat(),
            components=components,
            configuration_valid=len(config_errors) == 0,
            config_errors=config_errors,
        )

        return Result.ok(output)
