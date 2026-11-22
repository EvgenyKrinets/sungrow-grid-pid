"""Local-time night discount evaluation for Sungrow Energy Manager.

Only Sunday–Thursday *starting nights* qualify. A Thursday 23:00
window therefore runs through Friday 07:00; Friday and Saturday
evening starts are excluded. This is independent of sunrise/DST.
"""
from datetime import timedelta, time

DISCOUNT_START_DAYS = frozenset((6, 0, 1, 2, 3))  # Sunday through Thursday


def is_discount_time(local_now, start: time = time(23, 0),
                     end: time = time(7, 0)) -> bool:
    """Check whether the configured discount window is active locally."""
    clock = local_now.time().replace(tzinfo=None)
    if start == end:
        return False
    if start < end:
        return local_now.weekday() in DISCOUNT_START_DAYS and start <= clock < end
    if clock >= start:
        starting_day = local_now.date()
    elif clock < end:
        starting_day = local_now.date() - timedelta(days=1)
    else:
        return False
    return starting_day.weekday() in DISCOUNT_START_DAYS
