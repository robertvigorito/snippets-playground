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
"""The transimission module supports utilities code for converying data between the RIFs objects
and the submission jobs.
"""
import logging
import os as _os
from dataclasses import fields as _fields

# import dd.runtime.api

# dd.runtime.api.load("python_black")
# import black as _black


# Package imports
import rifs.core
from rifs.core import constants as _constants


_logger = logging.getLogger("dd." + __name__)
_logger.addHandler(logging.NullHandler())


def generate_script(operation: "rifs.core.AbstractRif") -> str:
    """Generate a script from the operation object. If the operation object is a processor
    we skip the generation of the script. Its not necessary since we are using the straight 
    command.

    Args:
        operation (rifs.core.AbstractRif): The operation object.

    Returns:
        str: The path to the generated
    """
    if isinstance(operation, rifs.core.ProcessorRif):
        return ""
    # Get the module name
    operation_module_name = operation.namespace or operation.__module__
    # Get the class name
    operation_class_name = type(operation).__name__
    # Get the kwargs
    operation_kwargs = {}
    for field in _fields(operation):


        print(field.metadata, field.init, field.name)
        # Moving to python 3.9 we can use the kw_only attribute
        ignore_field_condition = [field.metadata.get(key, False) for key in ["kw_only", "exempt"]]
        if field.init and not any(ignore_field_condition):
            operation_kwargs[field.name] = getattr(operation, field.name)
    # Build the script from the template and save it in the temp directory
    operation_duck_script = _constants.RIF_SCRIPT_TEMPLATE.format(
        module=operation_module_name, class_name=operation_class_name, kwargs=operation_kwargs
    )
    # Format the script with black - Make it pretty
    # operation_duck_script = _black.format_str(operation_duck_script, mode=_black.FileMode())
    # Write the script to the temporary directory
    temp_script_path = _os.path.join(operation.temporary_directory, f"rif_{operation_class_name.lower()}.py")
    with open(temp_script_path, "w", encoding="utf-8") as open_script_file:
        open_script_file.write(operation_duck_script)

    return temp_script_path
