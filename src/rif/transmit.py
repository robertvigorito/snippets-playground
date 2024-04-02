"""By passing the rif objects to the transmit module, the objects are converted into executable python 
files for farm submission.
"""

import os as _os
import dataclasses as _dataclasses
import typing as _typing
import black as _black


from abstraction import AbstractRif as _AbstractRif
from soumission import insert_job as _insert_job
from internal.constants import RIF_SCRIPT_TEMPLATE as _RIF_SCRIPT_TEMPLATE


@_dataclasses.dataclass(eq=False, order=False, frozen=True, repr=False, unsafe_hash=True)
class ReconstructDuck:
    """Turn a duck object into a executable python file for farm submission."""

    operations: _typing.List["_AbstractRif"]

    def emit(self) -> bool:
        """Emit the python code for the duck object."""
        return False

    def __call__(self) -> _typing.List[_typing.Any]:
        """Turn the duck object into a executable python file for farm submission.

        Returns:
            _typing.List[_typing.Any]: The list of constructed duck objects.
        """
        constructed_ducks: _typing.List[_typing.Any] = []

        for operation in self.operations:
            # Get the module name
            operation_module_name = operation.__module__
            # Get the class name
            operation_class_name = type(operation).__name__
            # Get the kwargs
            operation_kwargs = {}
            for field in _dataclasses.fields(operation):
                if field.init and not field.kw_only:
                    operation_kwargs[field.name] = getattr(operation, field.name)

            # Build the script from the template and save it in the temp directory
            operation_duck_script = _RIF_SCRIPT_TEMPLATE.format(
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
            constructed_ducks.append(rif_soumission)

        return constructed_ducks
