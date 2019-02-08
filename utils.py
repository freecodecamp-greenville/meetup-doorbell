from datetime import datetime

import pytz


def get_datetime(timezone):
    """Returns datetime object as given timezone."""
    tz = pytz.timezone(timezone)
    return pytz.utc.localize(datetime.utcnow()).astimezone(tz)


def doorbell_is_active(now: datetime, suppress_dates="", force_active=False):
    if force_active:
        return True
    if suppress_dates:
        suppress_dates = [
            datetime.strptime(date, "%Y-%m-%d").date()
            for date in suppress_dates.split(",")
        ]
        if now.date() in suppress_dates:
            return False
    return (
        now.weekday() == 3
        and now.hour >= 18
        and now.hour < 21
        and (1 <= now.day <= 7 or 15 <= now.day <= 21)
    )
