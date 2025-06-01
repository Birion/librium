from typing import Optional, Tuple, Union, Literal

# Type aliases
ReadStatus = Literal["all", "unread", "read"]
StatusInput = Union[int, bool, str, None]

# Constants
POSITIVE_VALUES = {1, True, "true", "t", "y", "yes"}
NEGATIVE_VALUES = {0, False, "false", "f", "n", "no"}
READ_STATUS_ORDER = ["all", "unread", "read"]
URL_STATUS_MAPPING = {"all": None, "unread": 0, "read": 1}


def normalize_status(status: StatusInput) -> str:
    """Convert various input types to lowercase string if possible."""
    if isinstance(status, str):
        return status.lower()
    return str(status) if status is not None else "all"


def determine_show_status(status: StatusInput) -> ReadStatus:
    """Determine which reading status to show based on input."""
    normalized = normalize_status(status)

    try:
        status_int = int(normalized)
        if status_int in POSITIVE_VALUES:
            return "read"
        if status_int in NEGATIVE_VALUES:
            return "unread"
    except ValueError:
        if normalized in POSITIVE_VALUES:
            return "read"
        if normalized in NEGATIVE_VALUES:
            return "unread"

    return "all"


def get_next_status(current: ReadStatus) -> ReadStatus:
    """Get the next status in the rotation."""
    current_idx = READ_STATUS_ORDER.index(current)
    next_idx = (current_idx + 1) % len(READ_STATUS_ORDER)
    return READ_STATUS_ORDER[next_idx]


def parse_read_arg(status: StatusInput) -> Tuple[str, Optional[bool]]:
    """
    Parse the read status argument and return the next status with its URL parameter.

    Args:
        status: Input value indicating read status (can be int, bool, str, or None)

    Returns:
        Tuple containing the next status string and its corresponding URL parameter
    """
    current_status = determine_show_status(status)
    next_status = get_next_status(current_status)
    return next_status, URL_STATUS_MAPPING[next_status]
