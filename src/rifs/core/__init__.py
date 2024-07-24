"""The core module for the rif package.
"""

from rifs.core import constants as core_constants
from rifs.core.abstraction import AbstractRif, ProcessorRif
from rifs.core.soumission import insert_job
from rifs.core.validation import is_abstract_rif, is_soumission

__all__ = [
    "AbstractRif",
    "core_constants",
    "insert_job",
    "is_abstract_rif",
    "is_soumission",
    "ProcessorRif",
]
