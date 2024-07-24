"""By passing the rif objects to the transmit module, the objects are converted into executable python 
files for farm submission.
"""

import dataclasses as _dataclasses
import logging as _logging
import typing as _typing

# Internal imports
from rifs.core.soumission import _Job
from rifs.core.transmission import generate_script as _generate_script
from rifs.core import AbstractRif as _AbstractRif, insert_job as _insert_job
from rifs.core.resolver import Resolver as _Resolver



__all__ = ["Constructor"]


_logger = _logging.getLogger("dd." + __name__)
_logger.addHandler(_logging.NullHandler())


@_dataclasses.dataclass(eq=True, order=True, frozen=True)
class Constructor:
    """Turn a rif object into a executable python file for farm submission."""

    operations: _typing.List["_AbstractRif"]

    def submit(self, ignore: bool = False) -> _typing.List[_typing.Tuple[str, str]]:
        """Submit all the grouping jobs to the farm.

        Args:
            ignore (bool, optional): The resolve looks to see if the jobs are enlist in the grouping.
                                     This is a flag to ignore the depend_on. Defaults to False.
        Returns:
            _typing.List[_typing.Tuple[str, str]]: The list of the job name and the job id.
        """
        results: _typing.List[_typing.Tuple[str, str]] = []

        for grouping in self.build().resolve(ignore=ignore):
            results.append(grouping.job.submit())

        return results

    def build(self) -> "_Resolver":
        """Turn the rif objects into a executable python file for farm submission.

        Returns:
            Resolver: The resolver object.
        """
        rifs_resolver = _Resolver()

        for operation in self.operations:

            operation_class_name = operation.__class__.__name__
            if isinstance(operation, _Job):
                _logger.info("Injecting job %s into the resolver.", operation_class_name)
                rifs_resolver.inject(operation=operation, job=operation)
                continue
            if not issubclass(type(operation), _AbstractRif):
                _logger.info("Skipping %s. Not a valid rif object.", operation)
                continue
            # Generate the script if its an abstract rif
            temp_script_path = _generate_script(operation)
            _logger.info(
                "Generated script %s for %s. Will skip if its a processor rif",
                temp_script_path or None,
                operation_class_name,
            )
            # Convert the object to job
            rif_job_soumission = _insert_job(operation, temp_script_path, **operation.soumission_kwargs)
            # Inject the job into the resolver
            _logger.info("Injecting job %s into the resolver.", rif_job_soumission.job_name)
            rifs_resolver.inject(operation, rif_job_soumission)

        return rifs_resolver


def only_one(operation: _typing.Union[_AbstractRif, _Job]) -> _typing.Tuple[str, str]:
    """Submit only one job to the farm.

    Args:
        operation (Union[AbstractRif, Job]): The operation to submit.

    Returns:
        Tuple[str, str]: The job name and the job id.
    """
    # Validate the operation
    if not isinstance(operation, (_AbstractRif, _Job)):
        raise TypeError(f"Only AbstractRif or Job objects are allowed. Got {type(operation)}.")
    return Constructor([operation]).submit()[0]
