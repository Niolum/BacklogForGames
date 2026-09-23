from enum import StrEnum, auto


class Environment(StrEnum):
    """Среда выполнения"""

    production = auto()
    development = auto()
    testing = auto()

    @property
    def is_testing(self) -> bool:
        """Testing?"""
        return self is self.testing

    @property
    def is_development(self) -> bool:
        """Development?"""
        return self is self.development

    @property
    def is_production(self) -> bool:
        """Production?"""
        return self is self.production
