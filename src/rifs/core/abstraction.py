"""The abstraction module for the RIF package."""

import abc as _abc
import dataclasses as _dataclasses
import datetime as _datetime
import os as _os
import typing as _typing
import uuid as _uuid

__all__ = ["AbstractRif", "unique_temporary_directory"]


def unique_temporary_directory() -> str:
    """Create a unique temporary directory.

    Returns:
        str: The full path to the unique temporary directory.
    """
    root = _os.path.expandvars("/$DD_ROOT/$DD_SHOW/$DD_SEQ/$DD_SHOT/farm/rif")
    root = _os.path.expandvars("/vfx/wgid/farm/rif")
    # Append unique
    now = _datetime.datetime.now().strftime("%Y%m%d-%H%M")
    full_path = _os.path.join(root, now, _uuid.uuid4().hex[:8])
    # Create the directory
    _os.makedirs(full_path, exist_ok=True)

    return full_path


@_dataclasses.dataclass(eq=True, order=True)
class AbstractRif(_abc.ABC):
    """The main duck class for testing positional arguments"""

    name: str = _dataclasses.field(default_factory=str, kw_only=True)
    note: str = _dataclasses.field(default_factory=str, kw_only=True)
    depend_on: _typing.List["AbstractRif"] = _dataclasses.field(
        default_factory=list, kw_only=True, repr=False, metadata={"exempt": True}
    )
    temporary_directory: str = _dataclasses.field(default="", kw_only=True, repr=False)
    # The namespace allows us to explicitly define the namespace for the operation if constructing
    # from __main__.
    namespace: str = _dataclasses.field(default="", kw_only=True, repr=False)

    def __post_init__(self):
        """Post init method for the AbstractRif class."""
        self.temporary_directory = unique_temporary_directory()

    @_abc.abstractmethod
    def __call__(self, *args, **kwargs) -> _typing.Any:
        """The main method to execute the the rifs object."""
        return None
