# No shebang line. This file is meant to be imported.
#
# Confidential and Proprietary Source Code
#
# This Digital Domain 3.0, Inc. ("DD3.0")  source code, including without
# limitation any human-readable  computer programming code and associated
# documentation (together "Source Code"),  contains valuable confidential,
# proprietary  and trade secret information of DD3.0  and is protected by
# the laws of the United States and other countries. DD3.0 may, from time
# to time, authorize specific employees to use the Source Code internally
# at DD3.0's premises  solely for  developing,  updating,  and/or trouble-
# shooting  the Source Code.  Any other use of the Source Code, including
# without  limitation  any disclosure,  copying or reproduction,  without
# the prior written authorization of DD3.0 is strictly prohibited.
#
# Copyright (c) [2024] Digital Domain 3.0, Inc. All rights reserved.
#
# ruff: E401
"""The drop allows the user to select which preset they want to use in the node graph.
"""
from functools import lru_cache
import dataclasses as _dataclasses
import re

from PySide2 import QtWidgets, QtCore, QtGui

# Example of a regex pattern to match the url.
# https://d2.shotgrid.autodesk.com/detail/Version/3760156
# https://d2.shotgrid.autodesk.com/page/154860#Version_3780273
PATTERNS = (r"[vV]ersion[_/](\d+)",)

FLOW_VERSION_FIELDS = (
    "sg_format_path",
    "sg_format_type",
    "sg_version.Version.sg_source_path",
    "sg_version.Version.id",
)
IGNORE_TYPES = (
    "wav",
    "cc",
)


def time_it(func):
    """Decorator to time the execution of a function.

    Args:
        func (function): Function to be timed.

    Returns:
        function: The timed function.

    """

    def wrapper(*args, **kwargs):
        import time
        import cProfile
        import pstats

        profile = cProfile.Profile()
        start = time.time()
        profile.enable()
        result = func(*args, **kwargs)
        profile.disable()
        print(f"{func.__name__} took {time.time() - start} seconds to execute.")

        # Print the profile
        stats = pstats.Stats(profile).sort_stats("cumulative")
        stats.print_stats(50)

        return result

    return wrapper


@_dataclasses.dataclass(frozen=True)
class FlowFormat:
    """Dataclass to hold the flow format information.

    Attributes:
        path (str): The path to the format.
        type_ (str): The type of the format.
        id_ (int): The id of the format.
        version_id (int): The id of the version.
        version_source (str): The source path of the version.
    """

    path: str
    type_: str
    id_: int
    version_id: int
    version_source: str

    @classmethod
    def from_flow_data(cls, data: dict) -> "FlowFormat":
        """Create a FlowFormat object from the flow data.

        Args:
            data (dict): The flow data.

        Returns:
            FlowFormat: The FlowFormat object.
        """
        return cls(
            path=data.get("sg_format_path"),
            type_=data.get("sg_format_type"),
            id_=data.get("id"),
            version_id=data.get("sg_version.Version.id"),
            version_source=data.get("sg_version.Version.sg_source_path"),
        )


@_dataclasses.dataclass
class FormatContainer:
    """Dataclass to hold the format container information."""

    items: "list[FlowFormat]" = _dataclasses.field(default_factory=list)

    @classmethod
    def ingest(cls, data: list[dict]):
        """Ingest the data into the format container.

        Args:
            data (list[dict]): The data to ingest.
        """
        format_container = cls()
        for item in data:
            flow_format = FlowFormat.from_flow_data(item)
            if "thumbnail" in flow_format.path.lower() or flow_format.type_ in IGNORE_TYPES:
                continue
            format_container.items.append(flow_format)
        return format_container

    def validate_version(self, version_id: int):
        """Validate the version id.

        Args:
            version_id (int): The version id.

        Returns:
            list[FlowFormat]: The formats attached to the version.
        """
        return all([item for item in self.items if item.version_id == version_id])

    def has_items(self) -> bool:
        """Check if the container has items.

        Returns:
            bool: True if the container has items, False otherwise.
        """
        return bool(self.items)

    def get_source(self):
        """Get the source path of the container.

        Returns:
            str: The source path.
        """
        return self.items[0].version_source


def create_nodes(paths):
    """Create the nodes from the paths.

    Args:
        paths (list[str]): The paths to create the nodes from.
    """
    import nuke
    for path in paths:
        read = nuke.createNode("Read")
        read["file"].fromUserText(path)
    return True


class DropMenu(QtWidgets.QMenu):
    """The drop menu for the flow node."""

    def __init__(self, container: "FormatContainer"):
        super().__init__()
        self.container = container
        self._ready_to_close = False

        source_action = self.addAction(f"src - {self.container.get_source()}")
        source_action.setData(self.container.get_source())
        source_action.setCheckable(True)
        self.addSeparator()

        for item in self.container.items:
            action = self.addAction(f"{item.type_} - {item.path}")
            action.setData(item.path)
            action.setCheckable(True)

        self.addAction("Proceed!", self.flip_ready_to_close)

    def flip_ready_to_close(self):
        """Flip the ready to close flag.

        Returns:
            bool: The ready to close flag.
        """
        self._ready_to_close = not self._ready_to_close
        self.close()
        return self._ready_to_close
    
    def get_checked_paths(self):
        """Get the checked paths.

        Returns:
            list[str]: The checked paths.
        """
        return [action.data() for action in self.actions() if action.isChecked()]

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:  # noqa: N802  # pylint: disable=invalid-name
        """Wrap the close event to handle the closing of the menu.

        Args:
            event (QtGui.QCloseEvent): The close event.
        """
        if not self._ready_to_close:
            event.ignore()
            return None
        event.accept()

        create_nodes(self.get_checked_paths())

        return super().closeEvent(event)


def load(mime_type, data):
    """Load the data into the nuke script.

    Args:
        mime_type (str): The mime type of the data.
        data (str): The data to load.
    """

    items = [
        FlowFormat(
            path="/dd/dailies/uncompressed/BIMINI/FY/5240/SHARED/104_FY_5240_cp_ddo_v0046/exr.client/104_FY_5240_cp_ddo_v0046.%04d.exr",
            type_="exr",
            id_=26253786,
            version_id=3780272,
            version_source="/dd/shows/BIMINI/FY/5240/SHARED/IMG/comp/fy5240_comp_v016.sv4ks100/fy5240_comp_v016.%04d.exr",
        ),
        FlowFormat(
            path="/dd/dailies/compressed/BIMINI/FY/5240/SHARED/104_FY_5240_cp_ddo_v0046/exr.proxy/104_FY_5240_cp_ddo_v0046.%04d.exr",
            type_="exr",
            id_=26253788,
            version_id=3780272,
            version_source="/dd/shows/BIMINI/FY/5240/SHARED/IMG/comp/fy5240_comp_v016.sv4ks100/fy5240_comp_v016.%04d.exr",
        ),
        FlowFormat(
            path="/dd/dailies/compressed/BIMINI/FY/5240/SHARED/104_FY_5240_cp_ddo_v0046/jpg/104_FY_5240_cp_ddo_v0046.%04d.jpg",
            type_="jpg",
            id_=26253789,
            version_id=3780272,
            version_source="/dd/shows/BIMINI/FY/5240/SHARED/IMG/comp/fy5240_comp_v016.sv4ks100/fy5240_comp_v016.%04d.exr",
        ),
        FlowFormat(
            path="/dd/dailies/compressed/BIMINI/FY/5240/SHARED/104_FY_5240_cp_ddo_v0046/mp4.client/104_FY_5240_cp_ddo_v0046.mov",
            type_="mp4",
            id_=26253790,
            version_id=3780272,
            version_source="/dd/shows/BIMINI/FY/5240/SHARED/IMG/comp/fy5240_comp_v016.sv4ks100/fy5240_comp_v016.%04d.exr",
        ),
        FlowFormat(
            path="/dd/dailies/editorial/BIMINI/2024_10_24/104_FY_5240_cp_ddo_v0046.mov",
            type_="qt",
            id_=26253791,
            version_id=3780272,
            version_source="/dd/shows/BIMINI/FY/5240/SHARED/IMG/comp/fy5240_comp_v016.sv4ks100/fy5240_comp_v016.%04d.exr",
        ),
    ]

    items_two = [
        FlowFormat(
            path="/dd/dailies/uncompressed/BIMINI/FY/1100/SHARED/104_FY_1100_cp_ddo_v0035/exr.client/104_FY_1100_cp_ddo_v0035.%04d.exr",
            type_="exr",
            id_=26253797,
            version_id=3780273,
            version_source="/dd/shows/BIMINI/FY/1100/SHARED/IMG/comp/fy1100_comp_v020.sv4ks100/fy1100_comp_v020.%04d.exr",
        ),
        FlowFormat(
            path="/dd/dailies/compressed/BIMINI/FY/1100/SHARED/104_FY_1100_cp_ddo_v0035/exr.proxy/104_FY_1100_cp_ddo_v0035.%04d.exr",
            type_="exr",
            id_=26253801,
            version_id=3780273,
            version_source="/dd/shows/BIMINI/FY/1100/SHARED/IMG/comp/fy1100_comp_v020.sv4ks100/fy1100_comp_v020.%04d.exr",
        ),
        FlowFormat(
            path="/dd/dailies/compressed/BIMINI/FY/1100/SHARED/104_FY_1100_cp_ddo_v0035/jpg/104_FY_1100_cp_ddo_v0035.%04d.jpg",
            type_="jpg",
            id_=26253802,
            version_id=3780273,
            version_source="/dd/shows/BIMINI/FY/1100/SHARED/IMG/comp/fy1100_comp_v020.sv4ks100/fy1100_comp_v020.%04d.exr",
        ),
        FlowFormat(
            path="/dd/dailies/compressed/BIMINI/FY/1100/SHARED/104_FY_1100_cp_ddo_v0035/mp4.client/104_FY_1100_cp_ddo_v0035.mov",
            type_="mp4",
            id_=26253805,
            version_id=3780273,
            version_source="/dd/shows/BIMINI/FY/1100/SHARED/IMG/comp/fy1100_comp_v020.sv4ks100/fy1100_comp_v020.%04d.exr",
        ),
        FlowFormat(
            path="/dd/dailies/editorial/BIMINI/2024_10_24/104_FY_1100_cp_ddo_v0035.mov",
            type_="qt",
            id_=26253807,
            version_id=3780273,
            version_source="/dd/shows/BIMINI/FY/1100/SHARED/IMG/comp/fy1100_comp_v020.sv4ks100/fy1100_comp_v020.%04d.exr",
        ),
    ]
    for build_item in [items, items_two]:
        format_container = FormatContainer(items=build_item)

        from pprint import pprint as pp

        pp(format_container.items)

        # Create the menu item for the flow node.
        menu = DropMenu(container=format_container)
        menu.exec_(QtGui.QCursor.pos())


if __name__ == "__main__":

    tests = [
        "https://d2.shotgrid.autodesk.com/detail/Version/3780272",
        "https://d2.shotgrid.autodesk.com/page/154860#Version_3780273",
    ]
    for test in tests:
        load("text/plain", test)
