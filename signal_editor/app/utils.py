import datetime
import typing as t

from PySide6 import QtCore, QtWidgets

MICRO: t.Final = "\u03bc"


class NonAsciiCharAndPosition(t.NamedTuple):
    char: str
    position: int


class NonAsciiResult(t.NamedTuple):
    has_non_ascii: bool
    non_ascii_chars: list[NonAsciiCharAndPosition]


def check_string_for_non_ascii(string: str) -> NonAsciiResult:
    """
    Checks a file name for possible non-ASCII characters.

    Parameters
    ----------
    string : str
        The string to check.

    Returns
    -------
    NonAsciiResult
        An instance of ``NonAsciiResult`` containing a boolean indicating whether non-ASCII
        characters were found and a list of ``NonAsciiCharAndPosition`` named tuples containing the
        detected non-ASCII characters and their positions in the input string.
    """

    non_ascii_chars = [
        NonAsciiCharAndPosition(char, idx) for idx, char in enumerate(string) if ord(char) > 127
    ]

    return NonAsciiResult(has_non_ascii=bool(non_ascii_chars), non_ascii_chars=non_ascii_chars)


def human_readable_timedelta(
    time_delta: datetime.timedelta | None = None,
    seconds: int | None = None,
    microseconds: int | None = None,
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

    return f"{day_str}{hours:02d}h {minutes:02d}m {seconds:02d}s {microseconds:06d}{MICRO}s"


def get_app_dir() -> QtCore.QDir:
    app_instance = QtWidgets.QApplication.instance()
    import sys

    if hasattr(sys, "frozen") and app_instance is not None:
        return QtCore.QDir(app_instance.applicationDirPath())
    return QtCore.QDir.current()


def safe_disconnect(
    sender: QtCore.QObject,
    signal: QtCore.SignalInstance,
    slot: QtCore.Slot | t.Callable[..., t.Any],
) -> None:
    meta_signal = QtCore.QMetaMethod.fromSignal(signal)
    if sender.isSignalConnected(meta_signal):
        signal.disconnect(slot)


def safe_multi_disconnect(
    sender: QtCore.QObject,
    signal_slot_pairs: list[tuple[QtCore.SignalInstance, QtCore.Slot | t.Callable[..., t.Any]]],
) -> None:
    for signal, slot in signal_slot_pairs:
        safe_disconnect(sender, signal, slot)


def format_long_sequence(seq: t.Sequence[int | float]) -> str:
    if len(seq) > 10:
        return f"[{', '.join(map(str, seq[:5]))}, ..., {', '.join(map(str, seq[-5:]))}]"
    else:
        return str(seq)
