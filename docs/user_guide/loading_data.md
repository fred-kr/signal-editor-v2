# Loading Data

To start working with the app, use the `Open File` command in the [File Menu](../ui_components/menu_bar.md#file-menu), [Toolbar](../ui_components/tool_bar.md) or the [Import Page](../ui_components/pages.md#import), then select the file you want to load.

The selected file is searched for available columns or channels of data by either reading the available metadata (EDF files) or scanning the first few rows of the file [^1]. If any are found, their names are made available for selection in the `Signal Data` and `Additional Data` fields.

The sampling rate of the data is also retrieved from the file's metadata (EDF files). For other file formats, an attempt is made to detect the sampling rate automatically. If the attempt fails, the user is prompted to enter the sampling rate manually.

[^1]: This is done to avoid reading the entire file into memory, which can be slow for large files. Can't be done for XLSX files, as they don't support lazy reading. In this case, the entire file is read into memory to extract the column names.

## Supported File Formats

### EDF (European Data Format)

EDF files are read using the [mne](https://mne.tools/stable/index.html) library. The full metadata can be viewed in the `Additional Metadata` tab of the `File Metadata` dialog (open by clicking on the `File Metadata` button in the [tool bar](../ui_components/tool_bar.md) or the [file](../ui_components/menu_bar.md) menu).

### Tabular Data

This includes .csv, .txt, .tsv, .xlsx and .feather files.

The separator character to use when reading .txt files can be set via the `TextSeparatorChar` setting in the [Settings](../user_guide/configuration.md#data).

### HDF5

HDF5 file reading is not yet implemented.
