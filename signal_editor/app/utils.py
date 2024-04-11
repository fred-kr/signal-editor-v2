import datetime
import math


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

    return f"{day_str}{hours:02d}h {minutes:02d}m {seconds:02d}s {microseconds:06d}\u03bcs"


def round_to_n(x: float, n: int) -> float:
    return round(x, -int(math.floor(math.log10(x))) + (n - 1))


def check_string_for_non_ascii(string: str) -> tuple[bool, list[tuple[str, int]]]:
    """
    Checks a file name for possible non-ASCII characters.

    Parameters
    ----------
    string : str
        The string to check.

    Returns
    -------
    tuple[bool, list[tuple[str, int]]
        A tuple containing a boolean indicating whether non-ASCII characters were found and a list of tuples containing the detected non-ASCII characters and their positions in the input string.
    """
    non_ascii_chars = [(char, idx) for idx, char in enumerate(string) if ord(char) > 127]
    return bool(non_ascii_chars), non_ascii_chars

    # @QtCore.Slot(list, bool)
    # def show_non_ascii_warning(
    #     self, non_ascii_chars: list[tuple[int, tuple[str, list[tuple[str, int]]]]], is_edf: bool
    # ) -> None:
    #     chars = {
    #         c[1][0]: [nc[1][1][0][0] for nc in non_ascii_chars if nc[1][0] == c[1][0]]
    #         for c in non_ascii_chars
    #     }

    #     msg = (
    #         "Non-ASCII characters found while reading from input file.\n"
    #         "This may cause issues when reading the file or exporting results.\n"
    #         f"If possible, rename the {'Channel' if is_edf else 'Column'} (see below), and try again.\n------\n"
    #         f"<b>{'Channel' if is_edf else 'Column'}</b>: {non_ascii_chars[0][1][0]}, <b>Non-ASCII characters</b>: {chars[non_ascii_chars[0][1][0]]}\n------\n"
    #         f"Rename the {'Channels' if is_edf else 'Columns'} now?"
    #     )
    #     btn = QtWidgets.QMessageBox.warning(
    #         self.main_window,
    #         "Non-ASCII characters found",
    #         msg,
    #         QtWidgets.QMessageBox.StandardButton.Yes
    #         | QtWidgets.QMessageBox.StandardButton.No
    #         | QtWidgets.QMessageBox.StandardButton.Cancel,
    #     )
    #     if btn == QtWidgets.QMessageBox.StandardButton.Yes:
    #         self.sig_open_rename_dialog.emit([c[1][0] for c in non_ascii_chars], is_edf)
