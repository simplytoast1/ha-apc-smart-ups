"""Unit tests for ``snmp_client.coerce_value`` covering the pysnmp value types
the integration actually sees."""
from __future__ import annotations

from pysnmp.proto.rfc1902 import (
    Counter32,
    Counter64,
    Gauge32,
    Integer,
    OctetString,
    TimeTicks,
)
from pysnmp.proto.rfc1905 import EndOfMibView, NoSuchInstance, NoSuchObject

from apc_smart_ups.snmp_client import coerce_value


def test_octet_string_returns_str():
    assert coerce_value(OctetString("Smart-UPS 1500")) == "Smart-UPS 1500"


def test_octet_string_strips_trailing_nulls():
    assert coerce_value(OctetString(b"foo\x00\x00")) == "foo"


def test_integer_returns_int():
    assert coerce_value(Integer(42)) == 42


def test_gauge_returns_int():
    assert coerce_value(Gauge32(120)) == 120


def test_counter32_returns_int():
    assert coerce_value(Counter32(7)) == 7


def test_counter64_returns_int():
    assert coerce_value(Counter64(2**40)) == 2**40


def test_timeticks_returns_int_in_hundredths():
    # caller is expected to divide by 100 to get seconds
    assert coerce_value(TimeTicks(12345)) == 12345


def test_no_such_object_returns_none():
    assert coerce_value(NoSuchObject("")) is None


def test_no_such_instance_returns_none():
    assert coerce_value(NoSuchInstance("")) is None


def test_end_of_mib_view_returns_none():
    assert coerce_value(EndOfMibView("")) is None
