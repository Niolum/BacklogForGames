from datetime import date

from pydantic import BaseModel, ConfigDict, Field


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
    name: str


class RawgGameCard(RawgModel):
    """One game from GET /api/games/{id}."""

    id: int
    description: str | None = None
    developers: list[RawgCompany] = Field(default_factory=list)
    publishers: list[RawgCompany] = Field(default_factory=list)


class RawgGenreCard(RawgModel):
    """One genre from GET /api/genres/{id}."""

    id: int
    name: str
    description: str | None = None
