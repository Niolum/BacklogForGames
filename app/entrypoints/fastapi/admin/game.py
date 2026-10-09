from typing import override

from sqladmin import ModelView
from starlette.requests import Request
from wtforms import BooleanField, DateField, Form, IntegerField, SelectMultipleField, StringField, TextAreaField
from wtforms.validators import InputRequired, Optional

from adapters.databases.sqlalchemy.models import GameORM
from domain.services import GameChangeData, GameCreateData
from domain.use_cases import create_game, get_genres, update_game


def _genre_names(game: GameORM, _attribute: str) -> list[str]:
    """Names of the genres attached to the game."""
    return [genre.name for genre in game.genres]


class GameAdmin(ModelView, model=GameORM):
    """Game screen of the admin panel."""

    name = 'Game'
    name_plural = 'Games'
    column_list = [GameORM.id, GameORM.title, GameORM.release_date, GameORM.is_published]
    column_formatters_detail = {GameORM.genres: _genre_names}
    form_columns = [
        GameORM.title,
        GameORM.release_date,
        GameORM.description,
        GameORM.metacritic,
        GameORM.developer,
        GameORM.publisher,
        GameORM.genres,
        GameORM.is_published,
    ]

    def _identity_for_object(self, obj):
        # For objects of our model, we use our own identity.
        if isinstance(obj, self.model):
            return self.identity

        # For related objects, we look for a suitable ModelView.
        admin = getattr(self, '_admin_ref', None)
        if admin:
            for view in admin.views:
                if isinstance(view, ModelView) and isinstance(obj, view.model):
                    return view.identity

        # If nothing is found, we revert to standard behavior.
        return super()._identity_for_object(obj)

    @override
    async def scaffold_form(self, rules: list[str] | None = None) -> type[Form]:
        """Build the game form and fill genre choices from the catalog."""
        genres = await get_genres()
        choices = [(genre.id, genre.name) for genre in genres]

        class GameAdminForm(Form):
            title = StringField('Title', validators=[InputRequired()])
            release_date = DateField('Release date', validators=[Optional()])
            description = TextAreaField('Description', validators=[Optional()])
            metacritic = IntegerField('Metacritic', validators=[Optional()])
            developer = StringField('Developer', validators=[Optional()])
            publisher = StringField('Publisher', validators=[Optional()])
            genres = SelectMultipleField('Genres', choices=choices, coerce=int)
            is_published = BooleanField('Published', default=True)

        return GameAdminForm

    @override
    async def insert_model(self, request: Request, data: dict) -> GameORM:
        """Create a game through the domain service."""
        game = await create_game(GameCreateData.model_validate(data))
        return GameORM.from_model(game)

    @override
    async def update_model(self, request: Request, pk: str, data: dict) -> GameORM:
        """Change a game through the domain service."""
        game = await update_game(int(pk), GameChangeData.model_validate(data))
        return GameORM.from_model(game)


GameAdmin.identity = 'game'
