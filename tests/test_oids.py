"""Sanity tests on the OID table itself: shape, types, and enum mappings."""
from __future__ import annotations

from apc_smart_ups.oids import (
    ALL_OIDS,
    BATTERY_REPLACE,
    BATTERY_STATUS,
    COMM_STATUS,
    OUTPUT_STATUS,
    TEST_RESULT,
)


def test_all_oids_have_correct_shape():
    for name, entry in ALL_OIDS.items():
        assert isinstance(entry, tuple), f"{name} is not a tuple"
        assert len(entry) == 2, f"{name} should be (oid, cast)"
        oid, cast = entry
        assert oid.startswith("1.3.6.1."), f"{name} OID looks wrong: {oid}"
        assert cast in {"str", "int", "timeticks"}, f"{name} bad cast: {cast}"


def test_no_duplicate_oids():
    seen: dict[str, str] = {}
    for name, (oid, _) in ALL_OIDS.items():
        assert oid not in seen, f"OID {oid} reused by {name} and {seen[oid]}"
        seen[oid] = name


def test_known_enum_values_exist():
    # Sanity: the enum maps must include every state mentioned in strings.json's
    # entity translations. Just check the common ones here.
    assert BATTERY_STATUS[2] == "normal"
    assert BATTERY_STATUS[3] == "low"
    assert OUTPUT_STATUS[2] == "online"
    assert OUTPUT_STATUS[3] == "onbattery"
    assert TEST_RESULT[1] == "ok"
    assert COMM_STATUS[1] == "ok"
    assert BATTERY_REPLACE[1] is False
    assert BATTERY_REPLACE[2] is True
