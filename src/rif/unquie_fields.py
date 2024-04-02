"""This module is the test framework for the rif (render interface framework)."""

import abc as _abc
import black as _black
import dataclasses as _dataclasses
import typing as _typing
import shutil as _shutil
import os as _os
import uuid as _uuid





@_dataclasses.dataclass
class MainDuck(_abc.ABC):
    """The main duck class for testing positional arguments"""

    name: str
    note: str
    depend_on: _typing.List[str] = _dataclasses.field(default_factory=list, kw_only=True, repr=False)
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


@_dataclasses.dataclass
class LayeredDuck(MainDuck):
    """The main duck class for testing positional arguments"""

    required_one: str
    required_two: int
    required_three: float

    class_variable: _dataclasses.InitVar[str] = "class_variable"

    def __call__(self) -> None:
        print(self)


duck_template = """
from {module} import {class_name}

kwargs = {kwargs}

{class_name}(**kwargs)()
{class_name}.teardown()
"""


@_dataclasses.dataclass(eq=False, order=False, frozen=True, repr=False, unsafe_hash=True)
class ReconstructDuck:
    """Turn a duck object into a execuatable python file for farm submission."""

    operations: _typing.List["MainDuck"]

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
            operation_duck_script = duck_template.format(
                module=operation_module_name, class_name=operation_class_name, kwargs=operation_kwargs
            )
            # Format the script with black - Make it pretty
            operation_duck_script = _black.format_str(operation_duck_script, mode=_black.FileMode())

            # Write the script to the temporary directory
            temp_script_path = _os.path.join(operation.temporary_directory, f"rif_{operation_class_name.lower()}.py")
            with open(temp_script_path, "w", encoding="utf-8") as open_script_file:
                open_script_file.write(operation_duck_script)

            # Convert the object to job
        
        return constructed_ducks


if __name__ == "__main__":
    duck = LayeredDuck(required_one="one", required_two=2, required_three=3.0, name="duck", note="quack")

    # Build the reconstruct duck object
    reconstruct_duck = ReconstructDuck([duck])
    reconstruct_duck()
