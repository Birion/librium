from librium.services import SeriesService
from librium.views.views.utils import SeriesType, get_raw


def get_series(args) -> dict[str, list[SeriesType] | int]:
    series, pagination = get_raw(SeriesService, args, {})
    options = {"series": series, "pagination": pagination}

    return options
