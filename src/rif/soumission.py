"""The backend render framework objects that are used to submit jobs."""

import os as _os
import dataclasses as _dataclasses
import typing as _typing

# Package imports
from abstraction import AbstractRif as _AbstractRif


__all__ = ["insert_job"]


@_dataclasses.dataclass
class DummyJob:
    """Dummy job object to be used for testing purposes."""

    show = _os.getenv("DD_SHOW", "DEV01")

    activity: str = "comprender"
    command: _typing.List[str] = _dataclasses.field(default_factory=list)
    cpus: int = 2
    env: dict = _dataclasses.field(default_factory=dict)
    job_class_type: str = "NukeJob"
    job_name: str = show
    ram: int = 8000


def insert_job(operation: "_AbstractRif", script: str, **kwargs) -> bool:
    """Insert a job into the database.

    Args:
        job (DummyJob): The job object to insert.

    Keyword Args:
        activity: The activity name.
        command: The command to execute.
        cpus: The number of CPUs.
        env: The environment variables.
        job_class_type: The job class type.
        job_name: The job name.
        ram: The amount of RAM.
        show: The show name.

    Returns:
        bool: True if the operation was successful. False otherwise.
    """
    rif_duck_job = DummyJob()
    rif_duck_job.command = ["dd-python", script]
    rif_duck_job.env["outputImage"] = kwargs.get("outputImage", "")

    for key, value in kwargs.items():
        setattr(rif_duck_job, key, value)

    # Set the values from the operation
    for rif_field in _dataclasses.fields(_AbstractRif):
        if hasattr(operation, rif_field.name) and not rif_field.metadata.get("exempt"):
            setattr(rif_duck_job, rif_field.name, getattr(operation, rif_field.name))

    return True
