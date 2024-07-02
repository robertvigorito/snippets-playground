"""By passing the rif objects to the transmit module, the objects are converted into executable python 
files for farm submission.
"""
import dataclasses as _dataclasses
import os as _os
import typing as _typing

import black as _black

# Package imports
from rifs.core import AbstractRif as _AbstractRif
from rifs.core import constants as _constants
from rifs.core import insert_job as _insert_job
from rifs.core.resolver import Resolver as _Resolver

__all__ = ["Constructor"]


@_dataclasses.dataclass(eq=True, order=True, frozen=True)
class Constructor:
    """Turn a duck object into a executable python file for farm submission."""

    operations: _typing.List["_AbstractRif"]

    def submit(self, **kwargs) -> _typing.List[_typing.Any]:
        """Emit the python code for the duck object.

        Keyword Args:
            ignore bool: Ignore the dependency resolution.
        
        Returns:
            _typing.List[_typing.Any]: The list of results from the job submission.
        """
        results = []
        pool: _typing.List[str] = []

        for grouping in self.build().resolve(**kwargs):
            print(grouping.name(), grouping.job.command)
            # result = grouping.job.submit()
            result = "Job submitted"
            # Add to the pool for dependency resolution
            pool.append(grouping.job.name)

            from pprint import pprint as pp

            pp(pool)
            # print(grouping.job.depend_on)
            for depend_on in grouping.job.depend_on:
                if depend_on.name in pool:
                    print(f"{grouping.name()} - Dependency resolved")

            results.append(result)

        return results

    def build(self) -> "_Resolver":
        """Turn the duck object into a executable python file for farm submission.

        Returns:
            _Resolver: The list of constructed duck objects.
        """
        rifs_resolver = _Resolver()

        for operation in self.operations:
            # Get the module name
            operation_module_name = operation.namespace or operation.__module__
            # Get the class name
            operation_class_name = type(operation).__name__
            # Get the kwargs
            operation_kwargs = {}
            for field in _dataclasses.fields(operation):
                if field.init and not field.kw_only:
                    operation_kwargs[field.name] = getattr(operation, field.name)

            # Build the script from the template and save it in the temp directory
            operation_duck_script = _constants.RIF_SCRIPT_TEMPLATE.format(
                module=operation_module_name, class_name=operation_class_name, kwargs=operation_kwargs
            )
            # Format the script with black - Make it pretty
            operation_duck_script = _black.format_str(operation_duck_script, mode=_black.FileMode())

            # Write the script to the temporary directory
            temp_script_path = _os.path.join(operation.temporary_directory, f"rif_{operation_class_name.lower()}.py")
            with open(temp_script_path, "w", encoding="utf-8") as open_script_file:
                open_script_file.write(operation_duck_script)

            # Convert the object to job
            rif_soumission = _insert_job(operation, temp_script_path)
            rifs_resolver.inject(operation, rif_soumission)

        return rifs_resolver
