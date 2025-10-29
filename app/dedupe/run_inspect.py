#!/usr/bin/env python3

"""
Script to run the InspectStorage procedure.
"""

from gen.commands import InspectStorage
from gen.procedures import InspectStorageContext, InspectStorageQueries, InspectStorageEmitters
from queries.file_scanners.linux import ListHardDrivesQuery, ListPartitionsQuery
from procedures.inspect_storage import InspectStorageProcedure


def main():
    # Create context with real Linux query implementations
    context = InspectStorageContext(
        emit=None,
        query=InspectStorageQueries(
            list_hard_drives=ListHardDrivesQuery().execute,
            list_partitions=ListPartitionsQuery().execute,
        )
    )

    # Create command
    command = InspectStorage()

    # Execute procedure
    procedure = InspectStorageProcedure()
    procedure(context, command)


if __name__ == "__main__":
    main()
