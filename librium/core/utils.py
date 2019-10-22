from typing import Optional, Tuple, Union


def parse_read_arg(status: Union[int, bool, str, None]) -> Tuple[str, Optional[bool]]:
    positives = [1, True, "true", "t", "y", "yes"]
    negatives = [0, False, "false", "f", "n", "no"]

    order = ["all", "unread", "read"]
    urls = {"all": None, "unread": 0, "read": 1}

    try:
        status = status.lower()
    except AttributeError:
        pass

    try:
        status = int(status)
    except TypeError:
        pass
    except ValueError:
        pass

    showing = "all"

    if status in positives:
        showing = "read"
    if status in negatives:
        showing = "unread"

    idx = order.index(showing) + 1

    try:
        next_status = order[idx]
    except IndexError:
        next_status = order[0]

    return next_status, urls[next_status]
