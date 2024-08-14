# Loading Data

To load data into the application, use the `Open File` button in the [File menu](../ui_components/) or on the `Import` page, then select the file you want to load.

The selected file is searched for available columns or channels of data by either reading the available metadata (EDF files) or scanning the first few rows of the file. If any are found, their names are made available for selection in the `Signal Data` and `Additional Data` fields.

The sampling rate of the data is also retrieved from the file's metadata (EDF files). For other file formats, an attempt is made to detect the sampling rate automatically. If the attempt fails, the user is prompted to enter the sampling rate manually.

## Supported File Formats

### EDF (European Data Format)

EDF files are read using the [mne](https://mne.tools/stable/index.html) library. The full metadata can be viewed in the `Additional Metadata` tab of the `File Metadata` dialog (open by clicking on the `File Metadata` button in the Toolbar or the `File` menu).

- CSV / TSV / TXT
- XLSX
- Arrow IPC / Feather (v2)
- HDF5 result files (created by the application)
