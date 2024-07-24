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
"""The backend render framework objects that are used to submit jobs."""

import dataclasses as _dataclasses
import os as _os

# Package imports
from rifs.core.abstraction import AbstractRif as _AbstractRif


__all__ = ["insert_job"]

# Create a mock job object
@_dataclasses.dataclass
class _Job:
    """The job object."""

    show: str = "DEV01"
    activity: str = "comprender"
    job_class_type: str = "NukeJob"
    job_name: str = "DEV01"
    env: dict = _dataclasses.field(default_factory=dict)
    ram: int = 8000
    cpus: int = 2
    command: list = _dataclasses.field(default_factory=list)
    frame_range: str = ""
    auto_dump: bool = False
    honor_cores: bool = True

    def submit(self):
        """Submit the job."""
        import subprocess
        process = subprocess.Popen(self.command)
        process.wait()
        return process


def standard_job(**kwargs) -> _Job:
    """Create a standard submission job object with the default values the suffice for Nuke.

    Keyword Arguments:
        activity (str): The activity name. Defaults to "comprender".
        auto_dump (bool): The auto dump. Defaults to False.
        cpus (int): The cpus. Defaults to 2.
        env (dict): The environment variables. Defaults to {}.
        frame_range (str): The frame range. Defaults to "".
        honor_cores (bool): The honor cores. Defaults to True.
        job_class_type (str): The job class type. Defaults to "NukeJob".
        job_name (str): The job name. Defaults to "DEV01".
        ram (int): The ram. Defaults to 8000.
        show (str): The show name. Defaults to "DEV01".

    Returns:
        Job: The job object.
    """
    show = _os.getenv("DD_SHOW", "DEV01")
    sousmission_job = _Job()
    sousmission_job.show = show
    sousmission_job.activity = "comprender"
    sousmission_job.job_class_type = "NukeJob"
    sousmission_job.job_name = show
    sousmission_job.env["outputImage"] = kwargs.get("outputImage", "")
    # Default ram and cpu
    sousmission_job.ram = 8000
    sousmission_job.cpus = 2

    for key, value in kwargs.items():
        setattr(sousmission_job, key, value)

    return sousmission_job


def insert_job(operation: "_AbstractRif", script: str, **kwargs) -> "_job.Job":
    """Wrap a rifs operation into a job object.

    Args:
        operation (AbstractRif): The operation to wrap.
        script (str): The script to run.

    Keyword Args:
        outputImage (str): The output image.

    Returns:
        Job: The job object.
    """
    rif_duck_job = standard_job(**kwargs)
    rif_duck_job.command = operation.command_override + [script]  # pylint: disable=protected-access
    print(rif_duck_job.command)
    rif_duck_job.env["outputImage"] = kwargs.get("outputImage", "")

    for key, value in kwargs.items():
        setattr(rif_duck_job, key, value)

    # Set the values from the operation
    for rif_field in _dataclasses.fields(_AbstractRif):
        if hasattr(operation, rif_field.name) and not rif_field.metadata.get("exempt"):
            setattr(rif_duck_job, rif_field.name, getattr(operation, rif_field.name))

    return rif_duck_job
