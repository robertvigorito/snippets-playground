"""The core module for the rif package.
"""

from rifs.core import constants as core_constants
from rifs.core.abstraction import AbstractRif
from rifs.core.soumission import insert_job, DummyJob
from rifs.core.validation import is_abstract_rif, is_soumission


__all__ = ["AbstractRif", "core_constants", "insert_job", "DummyJob", "is_abstract_rif", "is_soumission"]
