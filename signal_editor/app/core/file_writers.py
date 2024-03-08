from pathlib import Path
import typing as t
import tables as tb

from .. import type_defs as _t


def unpack_dict_to_attrs(
    data: (
        _t.ResultIdentifierDict
        | _t.SignalFilterParameters
        | _t.StandardizeParameters
        | _t.PeakDetectionParameters
        | _t.SummaryDict
        | dict[str, str | object]
        | None
    ),
    file: tb.File,
    node: tb.Node | str,
) -> None:
    """
    Unpacks a dictionary of attributes and sets them as node attributes in a PyTables file.

    Parameters
    ----------
    data : _t.ResultIdentifierDict | _t.SignalFilterParameters | _t.StandardizeParameters | _t.PeakDetectionParameters | _t.SummaryDict | None
        A dictionary containing the attributes to be set as node attributes. Can be one of the following types:
        - _t.ResultIdentifierDict: A dictionary containing result identifier attributes.
        - _t.SignalFilterParameters: A dictionary containing signal filter parameters.
        - _t.StandardizeParameters: A dictionary containing standardize parameters.
        - _t.PeakDetectionParameters: A dictionary containing peak detection parameters.
        - _t.SummaryDict: A dictionary containing summary attributes.
        - None: If data is None, the function returns without performing any action.

    file : tb.File
        The PyTables file object.

    node : tb.Node | str
        The node in the PyTables file where the attributes will be set. Can be either a PyTables Node object or a string representing the path to the node.
    """
    if data is None:
        return
    if isinstance(data, str):
        file.set_node_attr(node, "attribute_name", data)
        return
    for key, value in data.items():
        if value is None:
            value = "unknown"
        file.set_node_attr(node, key, value)




def create_group_or_table(parent: tb.Group | tb.File, name: str, description: str | None = None, title: str = "title", expectedrows: int = 10000) -> None:
    if description is not None:
        parent.create_table(
            parent,
            name=name,
            description=description,
            title=title,
            expectedrows=expectedrows,
        )
    else:
        parent.create_group(parent, name=name, title=title)


def set_attribute(parent: tb.File, attrname: str, attrvalue: int | float | str | bool | None) -> None:
    parent.set_node_attr(parent, attrname=attrname, attrvalue=attrvalue)


def result_dict_to_hdf5(file_path: str | Path, data: _t.CompleteResultDict) -> None:
    file_path = Path(file_path).resolve().as_posix()

    with tb.open_file(file_path, "w", title=f"Results_{Path(file_path).stem}") as h5f:
        unpack_dict_to_attrs(data["identifier"], h5f, h5f.root)

        h5f.create_table(
            h5f.root,
            name="global_dataframe",
            description=data["global_dataframe"],
            title="Global DataFrame",
            expectedrows=data["global_dataframe"].shape[0],
        )

        h5f.create_group(h5f.root, "focused_section_results", title="Focused Section Results")
        for section_id, focused_result in data["focused_section_results"].items():
            create_group_or_table(
                "/focused_section_results",
                name=f"focused_result_{section_id}",
                description=focused_result,
                title=f"Focused Result ({section_id})",
                expectedrows=focused_result.shape[0],
            )

        h5f.create_group(h5f.root, "complete_section_results", title="Complete Section Results")
        for section_id, section_result in data["complete_section_results"].items():
            create_group_or_table(
                "/complete_section_results",
                name=f"complete_result_{section_id}",
                title=f"Complete Result ({section_id})",
            )

            create_group_or_table(
                f"/complete_section_results/complete_result_{section_id}",
                name="section_dataframe",
                description=section_result["data"],
                title=f"DataFrame ({section_id})",
                expectedrows=section_result["data"].shape[0],
            )

            create_group_or_table(
                f"/complete_section_results/complete_result_{section_id}",
                name="peaks",
                title="Peaks",
            )
            h5f.create_array(
                f"/complete_section_results/complete_result_{section_id}/peaks",
                name="peak_indices_section",
                obj=section_result["peaks_section"],
                title="Peak indices (section)",
            )
            h5f.create_array(
                f"/complete_section_results/complete_result_{section_id}/peaks",
                name="peak_indices_global",
                obj=section_result["peaks_global"],
                title="Peak indices (global)",
            )
            h5f.create_array(
                f"/complete_section_results/complete_result_{section_id}/peaks",
                name="manually_added_peak_indices",
                obj=section_result["peak_edits"]["added"],
                title="Manually added (section)",
            )
            h5f.create_array(
                f"/complete_section_results/complete_result_{section_id}/peaks",
                name="manually_removed_peak_indices",
                obj=section_result["peak_edits"]["removed"],
                title="Manually removed (section)",
            )

            create_group_or_table(
                f"/complete_section_results/complete_result_{section_id}",
                name="rate",
                title="Calculated rate",
            )
            h5f.create_array(
                f"/complete_section_results/complete_result_{section_id}/rate",
                name="not_interpolated",
                obj=section_result["rate"],
                title="Rate (no interpolation)",
            )
            h5f.create_array(
                f"/complete_section_results/complete_result_{section_id}/rate",
                name="interpolated",
                obj=section_result["rate_interpolated"],
                title="Rate (interpolated to length of section)",
            )

            create_group_or_table(
                f"/complete_section_results/complete_result_{section_id}",
                name="processing_parameters",
                title=f"Processing parameters ({section_id})",
            )
            set_attribute(
                f"/complete_section_results/complete_result_{section_id}/processing_parameters",
                attrname="sampling_rate",
                attrvalue=section_result["processing_parameters"]["sampling_rate"],
            )
            set_attribute(
                f"/complete_section_results/complete_result_{section_id}/processing_parameters",
                attrname="pipeline",
                attrvalue=section_result["processing_parameters"]["pipeline"],
            )

            create_group_or_table(
                f"/complete_section_results/complete_result_{section_id}/processing_parameters",
                name="filter_parameters",
                title="Filter parameters",
            )
            unpack_dict_to_attrs(
                section_result["processing_parameters"]["filter_parameters"],
                h5f,
                f"/complete_section_results/complete_result_{section_id}/processing_parameters/filter_parameters",
            )

            create_group_or_table(
                f"/complete_section_results/complete_result_{section_id}/processing_parameters",
                name="standardize_parameters",
                title="Standardize parameters",
            )
            unpack_dict_to_attrs(
                section_result["processing_parameters"]["standardize_parameters"],
                h5f,
                f"/complete_section_results/complete_result_{section_id}/processing_parameters/standardize_parameters",
            )

            create_group_or_table(
                f"/complete_section_results/complete_result_{section_id}/processing_parameters",
                name="peak_detection_parameters",
                title="Peak detection parameters",
            )
            _peak_params = section_result["processing_parameters"]["peak_detection_parameters"]
            if _peak_params is not None:
                _method = _peak_params["method"]
                _method_params = _peak_params["method_parameters"]
                flattened_peak_detection_parameters = {"method": _method, **_method_params}
                unpack_dict_to_attrs(
                    flattened_peak_detection_parameters,
                    h5f,
                    f"/complete_section_results/complete_result_{section_id}/processing_parameters/peak_detection_parameters",
                )
