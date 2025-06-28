from librium.services import YearService
from librium.views.views.utils import YearType, get_raw


def get_years(args) -> dict[str, YearType | int]:
    years, pagination = get_raw(YearService, args, {})

    options = {"years": years, "pagination": pagination}

    return options