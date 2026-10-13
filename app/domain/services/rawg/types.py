from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RawgModel(BaseModel):
    """RAWG payload. Fields outside this model are ignored."""

    model_config = ConfigDict(extra='ignore')


class RawgListedGenre(RawgModel):
    """Genre id attached to a game in the RAWG list."""

    id: int


class RawgListedGame(RawgModel):
    """One game from GET /api/games."""

    id: int
    name: str
    released: date | None = None
    background_image: str | None = None
    metacritic: int | None = None
    genres: list[RawgListedGenre] = Field(default_factory=list)


class RawgGamesPage(RawgModel):
    """One page from GET /api/games."""

    count: int
    next: str | None = None
    previous: str | None = None
    results: list[RawgListedGame]


class RawgCompany(RawgModel):
    """Developer or publisher on a RAWG game card."""

    id: int
    name: str | None = None

    @field_validator('name')
    @classmethod
    def empty_name_is_none(cls, name: str | None) -> str | None:
        """An empty name is no name."""
        if name == '':
            return None
        return name


class RawgGameCard(RawgModel):
    """One game from GET /api/games/{id}."""

    id: int
    description: str | None = None
    developers: list[RawgCompany] = Field(default_factory=list)
    publishers: list[RawgCompany] = Field(default_factory=list)

    @field_validator('description')
    @classmethod
    def empty_description_is_none(cls, description: str | None) -> str | None:
        """An empty description is no description."""
        if description == '':
            return None
        return description

    @property
    def developer(self) -> str | None:
        """Name of the first developer."""
        if not self.developers:
            return None
        return self.developers[0].name

    @property
    def publisher(self) -> str | None:
        """Name of the first publisher."""
        if not self.publishers:
            return None
        return self.publishers[0].name


class RawgGenreCard(RawgModel):
    """One genre from GET /api/genres/{id}."""

    id: int
    name: str
    description: str | None = None

    @field_validator('description')
    @classmethod
    def empty_description_is_none(cls, description: str | None) -> str | None:
        """An empty description is no description."""
        if description == '':
            return None
        return description
