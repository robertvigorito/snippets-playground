"""The abstraction module for the RIF package."""

import abc as _abc
import dataclasses as _dataclasses
import datetime as _datetime
import os as _os
import typing as _typing
import uuid as _uuid
import tempfile as _tempfile

__all__ = ["AbstractRif", "ProcessorRif", "unique_temporary_directory"]


def unique_temporary_directory() -> str:
    """Create a unique temporary directory.

    Returns:
        str: The full path to the unique temporary directory.
    """
    # root = _os.path.expandvars("/$DD_SHOWS_ROOT/$DD_SHOW/$DD_SEQ/$DD_SHOT/user/work.$USER/farm/rifs")
    root = _os.path.expandvars("/vfx/wgid/tmp/farm/rifs/$USER")
    now = _datetime.datetime.now().strftime("%Y%m%d-%H%M")
    full_path = _os.path.join(root, now, _uuid.uuid4().hex[:8])  # Create the directory
    _os.makedirs(full_path, exist_ok=True)

    return full_path


@_dataclasses.dataclass
class AbstractRif(_abc.ABC):
    """The main duck class for testing positional arguments

    Notes:
        The exempt flag is used to exclude the field from transferring to the job object.

    Attributes:
        name (str): The name of the operation.
        notes (str): The notes for the operation.
        depend_on (List[str]): The list of operations to depend on.
        soumission_kwargs (Dict[str, Any]): The keyword arguments for the operation which passed to the submission operation.
        temporary_directory (str): The temporary directory for the operation.
        namespace (str): The namespace for the operation.
    """

    name: str = _dataclasses.field(default_factory=str, metadata={"kw_only": True})
    notes: str = _dataclasses.field(default_factory=str, metadata={"kw_only": True})
    depend_on: _typing.List["AbstractRif"] = _dataclasses.field(
        default_factory=list, repr=False, metadata={"kw_only": True}, hash=False
    )
    soumission_kwargs: _typing.Dict[str, _typing.Any] = _dataclasses.field(
        default_factory=dict, repr=False, metadata={"exempt": True}
    )
    temporary_directory: str = _dataclasses.field(
        default=unique_temporary_directory(), repr=False, metadata={"exempt": True}
    )
    # The namespace allows us to explicitly define the namespace for the operation if constructing
    # from __main__.
    namespace: str = _dataclasses.field(default="", repr=False, metadata={"exempt": True, "kw_only": True})

    command_override: _typing.ClassVar[list] = ["python"]

    def __post_init__(self) -> None:
        """Post init method for the AbstractRif class."""
        self.temporary_directory = unique_temporary_directory()

    @_abc.abstractmethod
    def __call__(self, *args, **kwargs) -> _typing.Any:
        pass


@_dataclasses.dataclass
class ProcessorRif(AbstractRif):
    """The processor RIF object is a low level object that doesn't require the python executable framework.

    All it requires is a command that is translated to the sumbmission job object in the transmission stage.

    Notes:
        Why is this different vs constructing the job object directly?

    Attributes:
        command (str): The command to execute.
    """

    command: str = _dataclasses.field(default="", metadata={"kw_only": True})

    def __call__(self, *args, **kwargs) -> _typing.Any:
        """The call method for the processor RIF object."""
        raise NotImplementedError("The processor RIF object is not callable.")
