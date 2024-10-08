"""The main module for the submission panel."""

from functools import partial as _partial
from typing import Any

from PySide2 import QtWidgets as _QtWidgets

from fpanel.facade import Node as _Node
from fpanel.pentry import Panel as _Panel


import nuke as _nuke

class Interface:
    """The interface class connects the widgets to the backend core functionality.


    Attributes:
        nodes (list): A list of nodes from the Nuke script.
        nuke_submission (Panel): The submission panel for Nuke.
    """
    is_local = property(lambda self: self.nuke_submission.settings()["farm_selection"] == "local")

    def __init__(self, selected=False) -> None:
        self.nodes = _Node.many(selected=selected)
        self.nuke_submission = _Panel()
        self.nuke_submission.node_tree_view.populate(self.nodes)

        # Connect the signals and slots for the submission window
        self.nuke_submission.buttons_layout.submit.clicked.connect(_partial(self.submit))
        self.nuke_submission.buttons_layout.cancel.clicked.connect(self.nuke_submission.close)

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        """Show the submission window.

        Returns:
            Panel: The submission window.
        """
        self.nuke_submission.show()

        return self.nuke_submission

    def connections(self) -> bool:
        """Connect the signals and slots for the submission window.

        Returns:
            bool: True if the connections were successful, False otherwise.
        """
        print("Connecting signals and slots...")
        return True

    def submit(self) -> bool:
        """Submit the settings from the submission window.

        Returns:
            bool: True if the submission was successful, False otherwise.

        """
        submission_panel_settings = self.nuke_submission.settings()
        submission_write_settings = self.nuke_submission.node_tree_view.active_nodes

        print(self.is_local)

        return False
        from pprint import pprint as pp

        pp(submission_panel_settings)
        pp(submission_write_settings)

        # Check for local submission
        if submission_panel_settings["farm_selection"] == "local" or True:
            nodes = []
            franges = []
            for node in submission_write_settings:
                nodes.append(node.node)
                frame_range_tuple = node.first_last_frame()
                frame_range_tuple = (frame_range_tuple[0], frame_range_tuple[1], 1)
                franges.append(frame_range_tuple)
                # limits = {'maxThreads':2, 'maxCache':4096}
                # _nuke.executeBackgroundNuke(_nuke.EXE_PATH, [node.node], frameRange=frame_ranges, views=["main"], limits=limits)

            # _nuke.executeMultiple(nodes, franges)
            

        return True


if __name__ == "__main__":

    # from PySide2 import QtWidgets as _QtWidgets
    import nuke
    app = _QtWidgets.QApplication([])
    window = Interface(selected=True)
    window()

    app.exec_()
