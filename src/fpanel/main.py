from typing import Any
from fpanel.panel import Panel as _Panel
from fpanel.facade import Node as _Node
from PySide2 import QtWidgets as _QtWidgets


class Interface:
    """The interface class connects the widgets to the backend core functionality.


    Attributes:
        nodes (list): A list of nodes from the Nuke script.
        nuke_submission (Panel): The submission panel for Nuke.
    """
    def __init__(self) -> None:
        self.nodes = _Node.many()
        self.nuke_submission = _Panel()
        self.nuke_submission.node_tree_view.populate(self.nodes)

        # Connect the signals and slots
        self.connections()

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
        self.nuke_submission.buttons_layout.submit.clicked.connect(self.submit)
        return True

    def submit(self) -> None:
        """Submit the settings from the submission window."""

        from pprint import pprint as pp
        pp(self.nuke_submission.settings())

        print("Submitting...")


if __name__ == "__main__":

    from PySide2 import QtWidgets as _QtWidgets

    app = _QtWidgets.QApplication([])
    window = Interface()
    window()

    app.exec_()
