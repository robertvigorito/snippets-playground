"""The internal constants for the rif module."""


__all__ = ["RIF_SCRIPT_TEMPLATE"]


RIF_SCRIPT_TEMPLATE = """
from {module} import {class_name}

kwargs = {kwargs}

{class_name}(**kwargs)()
"""
