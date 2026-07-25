from application.dto.common.location_dto import LocationDTO
from domain.shared.value_objects import Location


class LocationMapper:
    @staticmethod
    def to_domain(dto: LocationDTO) -> Location:
        return Location(
            city=dto.city, country=dto.country, state=dto.state, is_remote=dto.is_remote
        )

    @staticmethod
    def to_dto(domain: Location) -> LocationDTO:
        return LocationDTO(
            city=domain.city,
            country=domain.country,
            state=domain.state,
            is_remote=domain.is_remote,
        )
