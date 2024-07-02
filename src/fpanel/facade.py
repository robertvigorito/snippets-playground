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
"""The submission nodes module.
"""
import dataclasses as _dataclasses
import os as _os
import typing as _typing

# DCC imports
import nuke as _nuke  # pylint: disable=import-error  # type: ignore

# TODO: Preference?
EXECUTABLE_NODES_CLASSES = ["Write", "DDWrite2", "WriteGeo", "WriteGeo2", "DeepWrite", "DDDeepWrite2"]


def formatted_root_frame_range() -> str:
    """Get the formatted frame range of the root node.

    Returns:
        str: The formatted frame range of the root node
    """
    return f"{int(_nuke.root().firstFrame())}-{int(_nuke.root().lastFrame())}"


def node_frame_range(node: _nuke.Node) -> str:
    """Get the frame range of the node.

    Args:
        node (nuke.Node): The node

    Returns:
        str: The frame range of the node
    """
    first_frame_knob: _nuke.Format_Knob = node.knob("first")  # type: ignore[assignment]
    last_frame_knob: _nuke.Format_Knob = node.knob("last")  # type: ignore[assignment]
    if not (first_frame_knob.notDefault() and last_frame_knob.notDefault()):
        return formatted_root_frame_range()

    return f"{int(first_frame_knob.value())}-{int(last_frame_knob.value())}"


@_dataclasses.dataclass()
class Node:  # pylint: disable=too-many-instance-attributes
    """The nuke submission node is a constructure that allows us to easily interact with the node
    inside the widget environment.

    The purpose of this is to conventionally have a stand approach to how we review and define the
    submission nodes data under one umbrella instead of having to deal with different data structures
    for each node.

    Attributes:
        name (str): The name of the node
        full_name (str): The full name of the node
        class_ (str): The class of the node
        order (int): The order of the node
        frange (str): The frame range of the node
        basename (str): The base name of the file
        type (str): The type of the node
    """

    node: _nuke.Node = _dataclasses.field(repr=False)
    name: str = _dataclasses.field(init=False, default="")
    full_name: str = _dataclasses.field(init=False, default="")
    class_: str = _dataclasses.field(init=False, default="")
    order: int = _dataclasses.field(init=False, default=1)
    range: str = _dataclasses.field(init=False, default="")
    basename: str = _dataclasses.field(init=False, default="")
    type: str = _dataclasses.field(init=False, default="")
    disable: bool = _dataclasses.field(init=False, default=False)
    channels: str = _dataclasses.field(init=False, default="")
    headers: _typing.ClassVar[_typing.Tuple[str, str, str, str]] = ("order", "range", "channels", "basename")

    def __post_init__(self) -> None:
        """Post initialization method.

        Args:
            __mapping__ (dict): The mapping of the node attributes
        """
        self.define()

    def define(self) -> bool:
        """Define the node attributes.

        Returns:
            bool: True if the node was defined successfully, False otherwise
        """
        # Use as dict but not with node
        self.name = self.node.name()
        self.full_name = self.node.fullName()
        self.class_ = self.node.Class()
        self.order = int(self.node["render_order"].value())
        self.range = node_frame_range(self.node)
        self.basename = _os.path.basename(self.node["file"].value())
        self.type = self.node["file_type"].value()
        self.disable = self.node.knob("disable").value()  # type: ignore[union-attr]
        self.channels = self.node["channels"].value()

        return True

    def set(self, name, value):
        """Set the knob value of the node.

        Args:
            name (str): The name of the knob
            value (Any): The value of the knob
        """
        name_mapping = {
            "order": "render_order",
        }
        # Handle frame range
        if name == "range":
            first_frame, last_frame = value.split("-")
            self.node["first"].setValue(int(first_frame))
            self.node["last"].setValue(int(last_frame))
            return True
        try:
            name = name_mapping.get(name, name)
            self.node[name].setValue(value)
        except (AttributeError, ValueError):
            return False
        return True

    def renderable(self) -> bool:
        """Check if the node is renderable.

        Returns:
            bool: True if the node is renderable, False otherwise
        """
        return bool(not self.node.knob("disable").value() and self.node.inputs())  # type: ignore[union-attr]

    def __iter__(self) -> _typing.Generator[str, str, None]:
        """Iterate over the node attributes from the __order__.

        Yields:
            str: The node attribute
        """
        for key in self.headers:
            yield getattr(self, key)

    @classmethod
    def many(cls, selected: bool = False, recursive: bool = True) -> _typing.List["Node"]:
        """Get all the renderable nodes from the current script.

        Returns:
            list[Node]: A list of renderable nodes
        """
        submission_nodes = []
        # Get the list of supported nodes in the script.
        nodes = _nuke.allNodes(recurseGroups=recursive)
        if selected:
            nodes = _nuke.selectedNodes()

        nodes = [node for node in nodes if node.Class() in EXECUTABLE_NODES_CLASSES]

        for node in nodes:
            if node.Class() == "Write" and node.parent().Class() == "DDWrite2":
                continue
            if node.Class() == "DDWrite2":
                node = node.node("Write1")  # type: ignore[attr-defined]
            submission_nodes.append(cls(node=node))

        submission_nodes = sorted(submission_nodes, key=lambda x: x.order)

        return submission_nodes

    def show(self) -> bool:
        """Show the node in the node graph.

        Returns:
            bool: True if the node was shown, False otherwise
        """
        self.node.showControlPanel()
        return True

    def zoom(self) -> bool:
        """Zoom to the node in the node graph.

        Returns:
            bool: True if the node was zoomed, False otherwise
        """
        xpos = self.node.xpos() + self.node.screenWidth() / 2
        ypos = self.node.ypos() + self.node.screenHeight() / 2
        _nuke.zoom(2, [xpos, ypos])
        return True
