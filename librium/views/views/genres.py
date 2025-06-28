from librium.services import GenreService
from librium.views.views.utils import GenreType, get_raw


def get_genres(args) -> dict[str, GenreType | int]:
    # Get genres using the service
    genres, pagination = get_raw(GenreService, args, {})

    options = {"genres": genres, "pagination": pagination}

    return options
