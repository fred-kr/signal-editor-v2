import enum

from PySide6 import QtGui


class IconBase:
    def path(self) -> str:
        raise NotImplementedError

    def icon(self) -> QtGui.QIcon:
        return QtGui.QIcon(self.path())


class AppIcons(IconBase, enum.Enum):
    SignalEditor = ":/icons/app_icon.svg"
    Add = ":/icons/fluent-icons/Add.svg"
    AddCircle = ":/icons/fluent-icons/AddCircle.svg"
    AddSquare = ":/icons/fluent-icons/AddSquare.svg"
    ArrowAutofitHeight = ":/icons/fluent-icons/ArrowAutofitHeight.svg"
    ArrowAutofitHeightDotted = ":/icons/fluent-icons/ArrowAutofitHeightDotted.svg"
    ArrowExportLtr = ":/icons/fluent-icons/ArrowExportLtr.svg"
    ArrowExportUp = ":/icons/fluent-icons/ArrowExportUp.svg"
    ArrowImport = ":/icons/fluent-icons/ArrowImport.svg"
    ArrowLeft = ":/icons/fluent-icons/ArrowLeft.svg"
    ArrowNext = ":/icons/fluent-icons/ArrowNext.svg"
    ArrowPrevious = ":/icons/fluent-icons/ArrowPrevious.svg"
    ArrowReset = ":/icons/fluent-icons/ArrowReset.svg"
    ArrowRight = ":/icons/fluent-icons/ArrowRight.svg"
    ArrowSync = ":/icons/fluent-icons/ArrowSync.svg"
    AutoFitHeight = ":/icons/fluent-icons/AutoFitHeight.svg"
    BookInformation = ":/icons/fluent-icons/BookInformation.svg"
    BookQuestionMark = ":/icons/fluent-icons/BookQuestionMark.svg"
    BookSearch = ":/icons/fluent-icons/BookSearch.svg"
    Broom = ":/icons/fluent-icons/Broom.svg"
    Bug = ":/icons/fluent-icons/Bug.svg"
    CaretLeft = ":/icons/fluent-icons/CaretLeft.svg"
    CaretRight = ":/icons/fluent-icons/CaretRight.svg"
    CheckboxChecked = ":/icons/fluent-icons/CheckboxChecked.svg"
    CheckboxIndeterminate = ":/icons/fluent-icons/CheckboxIndeterminate.svg"
    CheckboxUnchecked = ":/icons/fluent-icons/CheckboxUnchecked.svg"
    CheckboxWarning = ":/icons/fluent-icons/CheckboxWarning.svg"
    Checkmark = ":/icons/fluent-icons/Checkmark.svg"
    CheckmarkCircle = ":/icons/fluent-icons/CheckmarkCircle.svg"
    CheckmarkSquare = ":/icons/fluent-icons/CheckmarkSquare.svg"
    ChevronCircleDown = ":/icons/fluent-icons/ChevronCircleDown.svg"
    ChevronCircleRight = ":/icons/fluent-icons/ChevronCircleRight.svg"
    ChevronDown = ":/icons/fluent-icons/ChevronDown.svg"
    ChevronLeft = ":/icons/fluent-icons/ChevronLeft.svg"
    ChevronRight = ":/icons/fluent-icons/ChevronRight.svg"
    ChevronUp = ":/icons/fluent-icons/ChevronUp.svg"
    Circle = ":/icons/fluent-icons/Circle.svg"
    CircleEdit = ":/icons/fluent-icons/CircleEdit.svg"
    CircleHalfFill = ":/icons/fluent-icons/CircleHalfFill.svg"
    CircleLine = ":/icons/fluent-icons/CircleLine.svg"
    Code = ":/icons/fluent-icons/Code.svg"
    Color = ":/icons/fluent-icons/Color.svg"
    ConvertToTable = ":/icons/fluent-icons/ConvertToTable.svg"
    Copy = ":/icons/fluent-icons/Copy.svg"
    DataArea = ":/icons/fluent-icons/DataArea.svg"
    DataHistogram = ":/icons/fluent-icons/DataHistogram.svg"
    DataScatter = ":/icons/fluent-icons/DataScatter.svg"
    Delete = ":/icons/fluent-icons/Delete.svg"
    DeleteDismiss = ":/icons/fluent-icons/DeleteDismiss.svg"
    DesktopPulse = ":/icons/fluent-icons/DesktopPulse.svg"
    Dismiss = ":/icons/fluent-icons/Dismiss.svg"
    DismissCircle = ":/icons/fluent-icons/DismissCircle.svg"
    DismissSquare = ":/icons/fluent-icons/DismissSquare.svg"
    DocumentArrowLeft = ":/icons/fluent-icons/DocumentArrowLeft.svg"
    DocumentArrowRight = ":/icons/fluent-icons/DocumentArrowRight.svg"
    DocumentBulletListClock = ":/icons/fluent-icons/DocumentBulletListClock.svg"
    DocumentDismiss = ":/icons/fluent-icons/DocumentDismiss.svg"
    DocumentEndnote = ":/icons/fluent-icons/DocumentEndnote.svg"
    DocumentToolbox = ":/icons/fluent-icons/DocumentToolbox.svg"
    Edit = ":/icons/fluent-icons/Edit.svg"
    EditOff = ":/icons/fluent-icons/EditOff.svg"
    EditSettings = ":/icons/fluent-icons/EditSettings.svg"
    Eraser = ":/icons/fluent-icons/Eraser.svg"
    ErrorCircle = ":/icons/fluent-icons/ErrorCircle.svg"
    EyeHide = ":/icons/fluent-icons/EyeHide.svg"
    EyeShow = ":/icons/fluent-icons/EyeShow.svg"
    FolderOpen = ":/icons/fluent-icons/FolderOpen.svg"
    History = ":/icons/fluent-icons/History.svg"
    Important = ":/icons/fluent-icons/Important.svg"
    Info = ":/icons/fluent-icons/Info.svg"
    Lasso = ":/icons/fluent-icons/Lasso.svg"
    LightbulbCircle = ":/icons/fluent-icons/LightbulbCircle.svg"
    List = ":/icons/fluent-icons/List.svg"
    LockClosed = ":/icons/fluent-icons/LockClosed.svg"
    LockOpen = ":/icons/fluent-icons/LockOpen.svg"
    MoreHorizontal = ":/icons/fluent-icons/MoreHorizontal.svg"
    MoreVertical = ":/icons/fluent-icons/MoreVertical.svg"
    Navigation = ":/icons/fluent-icons/Navigation.svg"
    New = ":/icons/fluent-icons/New.svg"
    Options = ":/icons/fluent-icons/Options.svg"
    PageFit = ":/icons/fluent-icons/PageFit.svg"
    Play = ":/icons/fluent-icons/Play.svg"
    PlayCircle = ":/icons/fluent-icons/PlayCircle.svg"
    Prohibited = ":/icons/fluent-icons/Prohibited.svg"
    Pulse = ":/icons/fluent-icons/Pulse.svg"
    Question = ":/icons/fluent-icons/Question.svg"
    QuestionCircle = ":/icons/fluent-icons/QuestionCircle.svg"
    RectangleLandscape = ":/icons/fluent-icons/RectangleLandscape.svg"
    Save = ":/icons/fluent-icons/Save.svg"
    SaveArrowRight = ":/icons/fluent-icons/SaveArrowRight.svg"
    SaveEdit = ":/icons/fluent-icons/SaveEdit.svg"
    ScanObject = ":/icons/fluent-icons/ScanObject.svg"
    Search = ":/icons/fluent-icons/Search.svg"
    SearchSquare = ":/icons/fluent-icons/SearchSquare.svg"
    SearchVisual = ":/icons/fluent-icons/SearchVisual.svg"
    SelectObject = ":/icons/fluent-icons/SelectObject.svg"
    Send = ":/icons/fluent-icons/Send.svg"
    Settings = ":/icons/fluent-icons/Settings.svg"
    Status = ":/icons/fluent-icons/Status.svg"
    Subtract = ":/icons/fluent-icons/Subtract.svg"
    SubtractCircle = ":/icons/fluent-icons/SubtractCircle.svg"
    SubtractSquare = ":/icons/fluent-icons/SubtractSquare.svg"
    TabDesktopArrowClockwise = ":/icons/fluent-icons/TabDesktopArrowClockwise.svg"
    Table = ":/icons/fluent-icons/Table.svg"
    Temperature = ":/icons/fluent-icons/Temperature.svg"
    Toolbox = ":/icons/fluent-icons/Toolbox.svg"
    Warning = ":/icons/fluent-icons/Warning.svg"
    WindowDevTools = ":/icons/fluent-icons/WindowDevTools.svg"
    Wrench = ":/icons/fluent-icons/Wrench.svg"
    ZoomIn = ":/icons/fluent-icons/ZoomIn.svg"
    ZoomOut = ":/icons/fluent-icons/ZoomOut.svg"

    def path(self) -> str:
        return self.value

    @staticmethod
    def app_icon() -> QtGui.QIcon:
        return QtGui.QIcon(":/icons/app_icon.svg")
