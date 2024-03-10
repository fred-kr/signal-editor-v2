import functools
import traceback
import typing as t

from PySide6 import QtWidgets


def exceptions_as_dialog(
    re_raise: bool = True,
    include_traceback: bool = False,
    additional_msg: str | None = None,
):
    def decorator(func: t.Callable[..., t.Any]) -> t.Callable[..., t.Any]:
        @functools.wraps(func)
        def wrapper(*args: t.Any, **kwargs: t.Any) -> t.Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if QtWidgets.QApplication.instance() is not None:
                    msg_box = QtWidgets.QMessageBox()
                    msg_box.setWindowTitle("Error")
                    msg_box.setIcon(QtWidgets.QMessageBox.Icon.Critical)
                    msg_text = (
                        additional_msg
                        if additional_msg is not None
                        else f"An error occurred in function call to: {func.__name__}"
                    )
                    msg_box.setText(msg_text)
                    msg_box.setInformativeText(f"{type(e).__name__}: {e}")
                    if include_traceback:
                        msg_box.setDetailedText(f"Traceback:\n{traceback.format_exc()}")
                    msg_box.exec()
                if re_raise:
                    raise e

        return functools.partial(
            wrapper,
            re_raise=re_raise,
            include_traceback=include_traceback,
            additional_msg=additional_msg,
        )

    return decorator
