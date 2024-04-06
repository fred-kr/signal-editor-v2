import datetime
import math

def human_readable_timedelta(
    time_delta: datetime.timedelta | None = None, seconds: int | None = None, microseconds: int | None = None
) -> str:
    if time_delta is None:
        if seconds is None or microseconds is None:
            raise ValueError(
                "Either 'time_delta' or 'seconds' and 'microseconds' must be provided."
            )
        time_delta = datetime.timedelta(seconds=seconds, microseconds=microseconds)

    days = time_delta.days
    hours, remainder = divmod(time_delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    microseconds = time_delta.microseconds
    day_str = f"{days}d " if days > 0 else ""

    return f"{day_str}{hours:02d}h {minutes:02d}m {seconds:02d}s {microseconds:06d}\u03bcs"



def round_to_n(x: float, n: int) -> float:
    return round(x, -int(math.floor(math.log10(x))) + (n - 1))