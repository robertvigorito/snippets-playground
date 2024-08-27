"""The module contain generic nuke validation that preset the user with information
valid information that can assist with optimizing the render process.
"""
import abc as _abc
import dataclasses as _dataclasses
import os as _os
import typing as _typing
from enum import Enum as _Enum


class Status(_Enum):
    """The status of the nuke script."""

    OK = "ok"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"


@_dataclasses.dataclass(eq=True, order=True)
class Standard(_abc.ABC):
    """The standard validation object.

    Attributes:
        status: The status of the validation.
        fixable: The flag to indicate if the validation is fixable.
        history: The history of the validation.
        prompt: The prompt message.
    """

    fixable: bool = _dataclasses.field(default=False)
    history: list[str] = _dataclasses.field(default_factory=list)
    prompt: str = _dataclasses.field(default="")
    status: Status = _dataclasses.field(default=Status.UNKNOWN)

    def log(self, message: str):
        """Log the message."""
        self.history.append(message)
        return self

    def fix(self):
        """Fix the validation."""

    @_abc.abstractmethod
    def validate(self):
        """Check the validation."""


class FrameRangeValidation(Standard):
    """Check if the frame range is correct and matches the frame range in shotgrid."""

    fixable = True

    def validate(self):
        """Check the validation."""
        self.log("Checking the frame range.")
        return self

    def fix(self):
        """Fix the validation."""
        self.log("Fixing the frame range.")
        return self


@_dataclasses.dataclass
class FileExistsValidation(Standard):
    """Check if the file existing on disk and the user has the correct permissions."""

    # path: _typing.Union[str] = _dataclasses.field(default_factory=Path)
    # fixable = False
    path: _typing.Union[str] = ""

    def validate(self):
        """This method will validate the file exists and the user has the correct permissions."""
        path_exists = self.path.exists()
        if path_exists:
            self.prompt += "The render file exists."
            self.status = Status.WARNING

        # Check if the user has permission to write to the file
        if not _os.access(self.path, _os.W_OK):
            self.prompt += "The user does not have permission to write to the file."
            self.status = Status.ERROR
            self.prompt += "The recommended action is to version up the file."

        return self


class LargeBoundaryBoxValidation(Standard):
    """Check if the boundary box in the script tree is too large."""

    fixable = True

    def validate(self):
        """Take the node format and the node boundary box and check review the threshold.

        If the threshold is above the limit, set the status to warning.
        """


class NodeErrorInTreeValidation(Standard):
    """Review the node tree that is connected to the write node and inform the user if there is a
    node with an error.
    """

    fixable = False

    def validate(self):
        """Check the node tree for any errors."""
        self.prompt = "Checking the node tree for errors."
        return self


def extract_required(item, validator):
    """Strip the required items from the item and return the required items."""
    required_kwargs = {}

    for field in set(vars(validator)) - set(vars(Standard)):
        required_kwargs[field] = getattr(item, field, None) or item.get(field, None)

    return required_kwargs


def process(**kwargs: dict[str, _typing.Any]):
    """Process the kwargs and return a list of standard validation objects.

    Args:
        kwargs: The keyword arguments.

    Returns:
        list[Standard]: The list of standard validation objects.
    """
    validators = [
        # FrameRangeValidation,
        FileExistsValidation,
        # LargeBoundaryBoxValidation,
        # NodeErrorInTreeValidation,
    ]
    for validator in validators:
        validator_kwargs = extract_required(kwargs, type(validator))
        print(validator_kwargs)
        validator_instance = validator(**validator_kwargs)
        yield validator_instance


# def process_nodes(nodes: list["_facade.Node"]):
#     """Process the nodes and return a list of standard validation objects.

#     Args:
#         nodes: The list of facade nodes.

#     Returns:
#         list[Standard]: The list of standard validation objects.
#     """
#     validators = [
#         FrameRangeValidation,
#         FileExistsValidation,
#         LargeBoundaryBoxValidation,
#         NodeErrorInTreeValidation,
#     ]
#     for node in nodes:
#         for validator in validators:
#             validator_kwargs = strip_required(node, validator)
#             validator_instance = validator(**validator_kwargs)
#             validator_instance.validate()
#             print(validator_instance.prompt)
#             print(validator_instance.status)


# Find the kwargs that are required for the validation