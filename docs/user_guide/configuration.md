# Configuration

The configuration allows the user to set various options that affect the look and behavior of the application.
It can be accessed by opening the [Settings](../ui_components/menu_bar.md#settings-menu) menu and selecting the **Preferences** option.

The available options are:

## Plot

These options modify the look and interaction behavior of plots on the [Editing](../ui_components/pages.md#editing) page.

- **Background**: The background color of the plot.
- **Foreground**: The foreground (text, axis, etc.) color of the plot.
- **LineColor**: The color of the line representing the signal data.
- **PointColor**: The color of the points representing the detected peaks.
- **SectionColor**: The color of the sections in the overview plot.
- **LineClickWidth**: The area around the signal line in pixels where a click is considered to be on the line.
- **ClickRadius**: The radius in data points around a click in which to search for a maximum or minimum value.

## Editing

These options control how the data is processed and how results are calculated.

- **FilterStacking**: If enabled, filters can be applied to an already filtered signal. If disabled, the signal data needs to be reset before applying a new filter.
- **RateMethod**: How to calculate the signal rate from the detected peaks. Options are:
  - **RollingWindow**: Calculate the rate by counting the number of peaks in a window with a size of one minute, with a new window every 10 seconds.
  - **Instantaneous**: Calculate the rate per minute as `60 / period`, where the `period` is the time between the peaks.

## Data

These options control how data is read and displayed.

- **FloatPrecision**: The number of decimal places to show for floating-point numbers.
- **TextSeparatorChar**: The character used to separate fields when reading from text files.