"""Module for validating objects from the rifs.core module."""

from rifs.core.abstraction import AbstractRif as _AbstractRif
from rifs.core.soumission import DummyJob as _DummyJob

__all__ = ["is_abstract_rif", "is_soumission"]


def is_abstract_rif(obj):
    """Check if the object is an instance of the AbstractRif class."""
    return issubclass(type(obj), _AbstractRif)


def is_soumission(obj):
    """Check if the object is an instance of the Soumission class."""
    return isinstance(obj, _DummyJob)
