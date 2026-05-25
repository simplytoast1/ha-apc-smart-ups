"""Unit tests for the None-aware binary-sensor lambdas.

We avoid importing ``binary_sensor.py`` itself because that pulls in
homeassistant. Instead we copy the trivial helpers under test directly
here. If the helpers in ``binary_sensor.py`` change, mirror them here
too - or refactor into a separate helper module.
"""
from __future__ import annotations


def _eq(key, target):
    def fn(d):
        v = d.get(key)
        return None if v is None else v == target
    return fn


def _fault(d):
    bs = d.get("battery_status")
    os_ = d.get("output_status")
    if bs is None and os_ is None:
        return None
    return bs == 4 or os_ == 10


# --- _eq behavior ---

def test_eq_returns_true_on_match():
    assert _eq("output_status", 3)({"output_status": 3}) is True


def test_eq_returns_false_on_mismatch():
    assert _eq("output_status", 3)({"output_status": 2}) is False


def test_eq_returns_none_when_key_missing():
    # Critical: must be None (Unavailable), NOT False, when the OID isn't
    # supported by the firmware. Avoids "Off" lies.
    assert _eq("output_status", 3)({}) is None


def test_eq_returns_none_when_value_none():
    assert _eq("output_status", 3)({"output_status": None}) is None


# --- _fault behavior ---

def test_fault_returns_none_when_both_missing():
    assert _fault({}) is None


def test_fault_returns_true_on_battery_fault():
    assert _fault({"battery_status": 4}) is True


def test_fault_returns_true_on_hardware_bypass():
    assert _fault({"output_status": 10}) is True


def test_fault_returns_false_when_healthy():
    assert _fault({"battery_status": 2, "output_status": 2}) is False


def test_fault_returns_false_when_only_one_known_and_healthy():
    # If only output_status reports and it's online, treat as "no fault".
    assert _fault({"output_status": 2}) is False
