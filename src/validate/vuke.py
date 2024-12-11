"""The module contain generic nuke validation that preset the user with information
valid information that can assist with optimizing the render process.
"""

import abc as _abc
import dataclasses as _dataclasses
import os as _os
from pathlib import Path
import typing as _typing
from enum import Enum as _Enum


class Status(_Enum):
    """The status of the nuke script."""

    OK = "ok"
    WARNING = "warning"
    ERROR = "error"
    UNKNOWN = "unknown"


@_dataclasses.dataclass(eq=True, order=True)
class _Standard(_abc.ABC):
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

    name = "Standard Validation"

    def __post_init__(self):
        self.validate()

    def log(self, message: str, prompt:bool = False):
        """Log the message."""
        if prompt:
            self.prompt += message
        self.history.append(message)
        return self

    def fix(self):
        """Fix the validation."""

    @_abc.abstractmethod
    def validate(self):
        """Check the validation."""


class FrameRangeValidation(_Standard):
    """Check if the frame range is correct and matches the frame range in shotgrid."""
    name = "Frame Range Validation"  
    fixable = True

    def validate(self):
        """Check the validation."""
        self.log("Checking the frame range.")
        return self

    def fix(self):
        """Fix the validation."""
        self.log("Fixing the frame range.")
        return self


@_dataclasses.dataclass(eq=True, order=True)
class FileExistsValidation(_Standard):
    """Check if the file existing on disk and the user has the correct permissions."""

    # path: _typing.Union[str] = _dataclasses.field(default_factory=Path)
    # fixable = False
    path: _typing.Union[str, Path] = _dataclasses.field(default="")

    name = "File Exists Validation"

    def __post_init__(self):
        self.path = Path(self.path)
        super().__post_init__()

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


class LargeBoundaryBoxValidation(_Standard):
    """Check if the boundary box in the script tree is too large."""

    fixable = True
    name = "Large Boundary Box Validation"
    def validate(self):
        """Take the node format and the node boundary box and check review the threshold.

        If the threshold is above the limit, set the status to warning.
        """
        self.prompt = "Boundary box is too large. The recommended action is to crop the boundary box."
        self.status = Status.WARNING
        return self


# @_dataclasses.dataclass(eq=True, order=True)
class NodeErrorInTreeValidation(_Standard):
    """Review the node tree that is connected to the write node and inform the user if there is a
    node with an error.
    """

    fixable = False
    name = "Error Nodes Validation"

    def validate(self):
        """Check the node tree for any errors."""
        for fake_node in ["Read", "Write", "Viewer"]:
            self.log(f"{fake_node} node has an error.\n", prompt=True)
        self.status = Status.ERROR
        self.prompt += "Click the node to view the error in tree.\n" 
        return self
    

class TestVal(_Standard):
    """Review the node tree that is connected to the write node and inform the user if there is a
    node with an error.
    """

    fixable = False
    name = "Test for demo Validation"

    def validate(self):
        """Check the node tree for any errors."""
        self.prompt +=  "I found an error"

        self.status = Status.ERROR


        return self


def extract_required(item, validator):
    """Strip the required items from the item and return the required items."""
    required_kwargs = {}

    for field in set(vars(validator)) - set(vars(_Standard)):
        # If ignore private fields and dunder methods
        if field.startswith("_"):
            continue
        required_kwargs[field] = getattr(item, field, None) or item.get(field, None)

    return required_kwargs


def process(**kwargs: dict[str, _typing.Any]) -> _typing.Generator[_Standard, None, None]:
    """Process the kwargs and return a list of _standard validation objects.

    Args:
        kwargs: The keyword arguments.

    Returns:
        list[_Standard]: The list of _standard validation objects.
    """
    validators = [
        FrameRangeValidation,
        FileExistsValidation,
        LargeBoundaryBoxValidation,
        NodeErrorInTreeValidation,
        TestVal
    ]
    for validator in validators:
        validator_kwargs = extract_required(kwargs, type(validator))
        clean_kwargs = {k: v for k, v in validator_kwargs.items() if v in vars(validator)}
        validator_instance = validator(**clean_kwargs)
        yield validator_instance
