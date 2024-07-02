"""The backend render framework objects that are used to submit jobs."""

import dataclasses as _dataclasses
import os as _os
import typing as _typing

# Package imports
from rifs.core import AbstractRif as _AbstractRif

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
    depend_on: _typing.List["DummyJob"] = _dataclasses.field(default_factory=list)
    name: str = "dummy"
    notes: str = ""

    def submit(self):
        """Submit the job."""
        import subprocess as _subprocess  # pylint: disable=import-outside-toplevel

        try:
            process = _subprocess.Popen(self.command, env=_os.environ, stdout=_subprocess.PIPE, stderr=_subprocess.PIPE)
        except _subprocess.CalledProcessError as e:
            print(e)

        # Print the output and stderr
        output, error = process.communicate()
        if process.returncode == 0:
            print(output.decode("utf-8"))
        else:
            print(error.decode("utf-8"))


def insert_job(operation: "_AbstractRif", script: str, **kwargs) -> "DummyJob":
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
        DummyJob: The job object.
    """
    rif_duck_job = DummyJob()
    rif_duck_job.command = ["python", script]
    rif_duck_job.env["outputImage"] = kwargs.get("outputImage", "")

    for key, value in kwargs.items():
        setattr(rif_duck_job, key, value)

    # Set the values from the operation
    for rif_field in _dataclasses.fields(_AbstractRif):
        if hasattr(operation, rif_field.name) and not rif_field.metadata.get("exempt"):
            setattr(rif_duck_job, rif_field.name, getattr(operation, rif_field.name))

    return rif_duck_job
