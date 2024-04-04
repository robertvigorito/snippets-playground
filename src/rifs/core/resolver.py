"""The resolver module for the RIFs package allows us to map the dependencies of the RIFs objects
to the corresponding jobs.
"""

import typing as _typing

from collections import namedtuple as _namedtuple
from dataclasses import dataclass as _dataclass, field as _field

# Package imports
from rifs.core import AbstractRif as _AbstractRif, DummyJob as _DummyJob


__all__ = ["Grouping"]


class Grouping(_namedtuple("Grouping", ["operation", "job"])):
    """The grouping class takes an operation and a job and groups them together."""

    operator: "_AbstractRif"
    job: "_DummyJob"

    def __hash__(self) -> int:
        """Hash the grouping object.

        Returns:
            int: The hash value of the grouping object.
        """
        return hash(str(self.operation) + str(self.job))

    def has_depend_on(self) -> bool:
        """Check if the operation has depend_on.

        Returns:
            bool: True if the operation has depend_on.
        """
        return bool(self.operation.depend_on) or bool(self.job.depend_on)

    def name(self) -> str:
        """Return the name of the grouping.

        Returns:
            str: The name of the grouping.
        """
        return f"{self.operation.name} - {self.job.name}"


@_dataclass(eq=True, order=True)
class Resolver:
    """The resolver class for the RIFs package."""

    groupings: _typing.List[Grouping] = _field(default_factory=list)

    def __iter__(self) -> _typing.Iterator["Grouping"]:
        """Iterate over the resolver.

        Yields:
            Grouping: The grouping object.
        """
        return iter(self.groupings)

    def __contains__(self, items: _typing.List["Grouping"]) -> bool:
        """Check if the items are in the resolver.

        Args:
            items (List[Grouping]): The list of grouping objects.

        Returns:
            bool: True if the items are in the resolver.
        """
        # The comparable items are in either grouping, operations or jobs
        in_operations = all(item in self.only_operations() for item in items)
        in_jobs = all(item in self.only_jobs() for item in items)
        in_grouping = all(item in self.groupings for item in items)

        return any([in_operations, in_jobs, in_grouping])

    def only_jobs(self) -> list:
        """Return only the jobs from the resolver.

        Returns:
            list: The list of jobs from the resolver.
        """
        return [grouping.job for grouping in self.groupings]

    def only_operations(self) -> list:
        """Return only the operations from the resolver.

        Returns:
            list: The list of operations from the resolver.
        """
        return [grouping.operation for grouping in self.groupings]

    def find(
        self, operation: "_AbstractRif", job: _typing.Optional["_DummyJob"] = None
    ) -> _typing.Optional["Grouping"]:
        """Find the grouping from either the operation or the job.

        Args:
            operation (AbstractRif): The operation object.
            job (DummyJob): The job object.

        Returns:
            Grouping: The grouping object.
        """
        for grouping in self.groupings:
            if grouping.operation == operation or grouping.job == job:
                return grouping

        return None

    def swap_depend_on(self, grouping: "Grouping") -> bool:
        """Swap the depend_on from the operation to the job.

        Args:
            grouping (Grouping): The grouping object.

        Returns:
            bool: True if the depend_on was swapped.
        """
        # Check if the grouping is in the resolver
        new_depend_on = []
        for depend_on in grouping.operation.depend_on:
            # Find the grouping that has the depend_on
            depend_on_grouping = self.find(operation=depend_on)
            if depend_on_grouping:
                new_depend_on.append(depend_on_grouping.job)
        grouping.job.depend_on = new_depend_on

        return True

    def resolve(self) -> "Resolver":
        """Resolve the dependencies of the RIFs objects to the corresponding jobs.

        Returns:
            Resolver: The resolved dependencies of the RIFs objects to the corresponding jobs.
        """
        # We only want to work on grouping that have depend_on
        attempts = 0  # Safety net for the while loop
        ordered_resolver = Resolver()
        cloned_groupings = self.groupings.copy()

        while cloned_groupings and attempts < 10:
            grouping = cloned_groupings.pop(0)
            if not grouping.has_depend_on():
                ordered_resolver.groupings.append(grouping)
                continue
            if grouping.operation.depend_on in ordered_resolver:
                # Need to update the job depend_on to the grouping job and not the operation job
                self.swap_depend_on(grouping)
                ordered_resolver.groupings.append(grouping)
                continue
            # Try again once the others are added in the list
            cloned_groupings.append(grouping)
            attempts += 1

        return ordered_resolver

    def inject(self, operation: "_AbstractRif", job: "_DummyJob") -> bool:
        """Add a job to the resolver.

        Args:
            operation (AbstractRif): The operation object.
            job (DummyJob): The job object.

        Returns:
            bool: True if the job was added to the resolver.
        """
        self.groupings.append(Grouping(operation=operation, job=job))
        return True
