"""The abstraction module for the RIF package."""
import abc as _abc
import dataclasses as _dataclasses
import os as _os
import shutil as _shutil
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
    full_path = _os.path.join(root, _uuid.uuid1().hex)
    # Create the directory
    _os.makedirs(full_path, exist_ok=True)

    return full_path


@_dataclasses.dataclass
class AbstractRif(_abc.ABC):
    """The main duck class for testing positional arguments"""

    name: str
    note: str
    depend_on: _typing.List[str] = _dataclasses.field(default_factory=list, kw_only=True, repr=False, metadata={"exempt": True})
    temporary_directory: str = _dataclasses.field(default=unique_temporary_directory(), kw_only=True, repr=False)

    @_abc.abstractmethod
    def __call__(self, *args, **kwargs) -> _typing.Any:
        pass

    def teardown(self) -> bool:
        """Perform any necessary cleanup operations.

        Returns:
            bool: True if the operation was successful. False otherwise.
        """
        # Remove the temporary directory
        _shutil.rmtree(self.temporary_directory, ignore_errors=True)
        return True
