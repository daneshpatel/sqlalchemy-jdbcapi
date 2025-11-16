"""
DB-API 2.0 type objects and constructors.
"""

from __future__ import annotations

import datetime
import time
from typing import Any


# Type Objects for DB-API 2.0 compliance
class DBAPITypeObject:
    """Base class for DB-API type objects."""

    def __init__(self, *values: Any) -> None:
        self.values = frozenset(values)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, DBAPITypeObject):
            return self.values == other.values
        return other in self.values

    def __hash__(self) -> int:
        return hash(self.values)


# Type objects
STRING = DBAPITypeObject(str)
BINARY = DBAPITypeObject(bytes, bytearray)
NUMBER = DBAPITypeObject(int, float)
DATETIME = DBAPITypeObject(datetime.datetime, datetime.date, datetime.time)
ROWID = DBAPITypeObject(int)


# Date/Time constructors
def Date(year: int, month: int, day: int) -> datetime.date:
    """Construct a date object."""
    return datetime.date(year, month, day)


def Time(hour: int, minute: int, second: int) -> datetime.time:
    """Construct a time object."""
    return datetime.time(hour, minute, second)


def Timestamp(
    year: int, month: int, day: int, hour: int, minute: int, second: int
) -> datetime.datetime:
    """Construct a timestamp object."""
    return datetime.datetime(year, month, day, hour, minute, second)


def DateFromTicks(ticks: float) -> datetime.date:
    """Construct a date object from ticks since epoch."""
    return datetime.date.fromtimestamp(ticks)


def TimeFromTicks(ticks: float) -> datetime.time:
    """Construct a time object from ticks since epoch."""
    return datetime.datetime.fromtimestamp(ticks).time()


def TimestampFromTicks(ticks: float) -> datetime.datetime:
    """Construct a timestamp object from ticks since epoch."""
    return datetime.datetime.fromtimestamp(ticks)


def Binary(value: bytes | bytearray | str) -> bytes:
    """Construct a binary object."""
    if isinstance(value, str):
        return value.encode("utf-8")
    return bytes(value)
