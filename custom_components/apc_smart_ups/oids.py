"""OID definitions used by the APC Smart-UPS integration.

Drawn from the APC PowerNet-MIB (enterprise OID 1.3.6.1.4.1.318) and
RFC 1628 (the standard UPS MIB at 1.3.6.1.2.1.33). The integration
prefers PowerNet over RFC 1628 because PowerNet gives finer-grained
data (e.g. real *and* apparent load, exact firmware string) and matches
what `apcaccess`/NUT users expect to see.

Each OID's value is reported in the comment alongside its scale (where
applicable). The coordinator dispatches a single SNMP GET-request with
the union of all OIDs below per poll cycle (the NMC handles a multi-OID
GET-request in one round trip).
"""
from __future__ import annotations

# Identification (read once, cached on the entity device_info)
OID_MODEL = "1.3.6.1.4.1.318.1.1.1.1.1.1.0"            # upsBasicIdentModel - OctetString
OID_NAME = "1.3.6.1.4.1.318.1.1.1.1.1.2.0"             # upsBasicIdentName - OctetString
OID_FIRMWARE = "1.3.6.1.4.1.318.1.1.1.1.2.1.0"         # upsAdvIdentFirmwareRevision - OctetString
OID_MFG_DATE = "1.3.6.1.4.1.318.1.1.1.1.2.2.0"         # upsAdvIdentDateOfManufacture - OctetString "mm/dd/yyyy"
OID_SERIAL = "1.3.6.1.4.1.318.1.1.1.1.2.3.0"           # upsAdvIdentSerialNumber - OctetString
OID_SKU = "1.3.6.1.4.1.318.1.1.1.1.2.5.0"              # upsAdvIdentSkuNumber - OctetString (some firmwares)

# Battery
OID_BATTERY_STATUS = "1.3.6.1.4.1.318.1.1.1.2.1.1.0"   # upsBasicBatteryStatus - INTEGER {unknown(1), batteryNormal(2), batteryLow(3), batteryInFaultCondition(4)}
OID_BATTERY_LAST_REPLACE = "1.3.6.1.4.1.318.1.1.1.2.1.3.0"  # upsBasicBatteryLastReplaceDate - OctetString "mm/dd/yyyy"
OID_BATTERY_CHARGE = "1.3.6.1.4.1.318.1.1.1.2.2.1.0"   # upsAdvBatteryCapacity - Gauge (%)
OID_BATTERY_TEMP = "1.3.6.1.4.1.318.1.1.1.2.2.2.0"     # upsAdvBatteryTemperature - Gauge (°C)
OID_BATTERY_RUNTIME = "1.3.6.1.4.1.318.1.1.1.2.2.3.0"  # upsAdvBatteryRunTimeRemaining - TimeTicks (1/100s)
OID_BATTERY_REPLACE_INDICATOR = "1.3.6.1.4.1.318.1.1.1.2.2.4.0"  # upsAdvBatteryReplaceIndicator - INTEGER {noBatteryNeedsReplacing(1), batteryNeedsReplacing(2)}
OID_BATTERY_VOLTAGE = "1.3.6.1.4.1.318.1.1.1.2.2.8.0"  # upsAdvBatteryActualVoltage - INTEGER (V)
OID_BATTERY_CURRENT = "1.3.6.1.4.1.318.1.1.1.2.2.9.0"  # upsAdvBatteryCurrent - INTEGER (A)

# Input
OID_INPUT_VOLTAGE = "1.3.6.1.4.1.318.1.1.1.3.2.1.0"    # upsAdvInputLineVoltage - Gauge (V)
OID_INPUT_VOLTAGE_MAX = "1.3.6.1.4.1.318.1.1.1.3.2.2.0"  # upsAdvInputMaxLineVoltage - Gauge (V)
OID_INPUT_VOLTAGE_MIN = "1.3.6.1.4.1.318.1.1.1.3.2.3.0"  # upsAdvInputMinLineVoltage - Gauge (V)
OID_INPUT_FREQUENCY = "1.3.6.1.4.1.318.1.1.1.3.2.4.0"  # upsAdvInputFrequency - Gauge (Hz)
OID_INPUT_FAIL_CAUSE = "1.3.6.1.4.1.318.1.1.1.3.2.5.0" # upsAdvInputLineFailCause - INTEGER enum

# Output
OID_OUTPUT_STATUS = "1.3.6.1.4.1.318.1.1.1.4.1.1.0"    # upsBasicOutputStatus - INTEGER {unknown(1), onLine(2), onBattery(3), onSmartBoost(4), timedSleeping(5), softwareBypass(6), off(7), rebooting(8), switchedBypass(9), hardwareFailureBypass(10), sleepingUntilPowerReturn(11), onSmartTrim(12)}
OID_OUTPUT_VOLTAGE = "1.3.6.1.4.1.318.1.1.1.4.2.1.0"   # upsAdvOutputVoltage - Gauge (V)
OID_OUTPUT_FREQUENCY = "1.3.6.1.4.1.318.1.1.1.4.2.2.0" # upsAdvOutputFrequency - Gauge (Hz)
OID_OUTPUT_LOAD_PCT = "1.3.6.1.4.1.318.1.1.1.4.2.3.0"  # upsAdvOutputLoad - Gauge (%)
OID_OUTPUT_CURRENT = "1.3.6.1.4.1.318.1.1.1.4.2.4.0"   # upsAdvOutputCurrent - Gauge (A)

# Self-test
OID_TEST_RESULT = "1.3.6.1.4.1.318.1.1.1.7.2.3.0"      # upsAdvTestDiagnosticsResults - INTEGER {ok(1), failed(2), invalidTest(3), testInProgress(4)}
OID_TEST_LAST_DATE = "1.3.6.1.4.1.318.1.1.1.7.2.4.0"   # upsAdvTestLastDiagnosticsDate - OctetString "mm/dd/yyyy"

# Communication status (we infer "online" from this: 1=ok means we can reach the NMC)
OID_COMM_STATUS = "1.3.6.1.4.1.318.1.1.1.8.1.0"        # upsCommStatus - INTEGER {ok(1), noComm(2)}


# Lookup tables for enum-typed values
BATTERY_STATUS = {
    1: "unknown",
    2: "normal",
    3: "low",
    4: "fault",
}

BATTERY_REPLACE = {
    1: False,  # noBatteryNeedsReplacing
    2: True,   # batteryNeedsReplacing
}

OUTPUT_STATUS = {
    1: "unknown",
    2: "online",
    3: "onbattery",
    4: "boost",
    5: "sleeping",
    6: "bypass_software",
    7: "off",
    8: "rebooting",
    9: "bypass_switched",
    10: "bypass_hardware_fault",
    11: "sleeping_until_power",
    12: "trim",
}

TEST_RESULT = {
    1: "ok",
    2: "failed",
    3: "invalid",
    4: "in_progress",
}

COMM_STATUS = {
    1: "ok",
    2: "no_comm",
}


# OID groups for the SNMP coordinator
ALL_OIDS = {
    # name           OID                              cast
    "model":         (OID_MODEL,                     "str"),
    "ups_name":      (OID_NAME,                      "str"),
    "firmware":      (OID_FIRMWARE,                  "str"),
    "mfg_date":      (OID_MFG_DATE,                  "str"),
    "serial":        (OID_SERIAL,                    "str"),
    "battery_status":     (OID_BATTERY_STATUS,       "int"),
    "battery_last_replace":(OID_BATTERY_LAST_REPLACE,"str"),
    "battery_charge":     (OID_BATTERY_CHARGE,       "int"),
    "battery_temp":       (OID_BATTERY_TEMP,         "int"),
    "battery_runtime":    (OID_BATTERY_RUNTIME,      "timeticks"),
    "battery_replace":    (OID_BATTERY_REPLACE_INDICATOR, "int"),
    "battery_voltage":    (OID_BATTERY_VOLTAGE,      "int"),
    "battery_current":    (OID_BATTERY_CURRENT,      "int"),
    "input_voltage":      (OID_INPUT_VOLTAGE,        "int"),
    "input_voltage_max":  (OID_INPUT_VOLTAGE_MAX,    "int"),
    "input_voltage_min":  (OID_INPUT_VOLTAGE_MIN,    "int"),
    "input_frequency":    (OID_INPUT_FREQUENCY,      "int"),
    "input_fail_cause":   (OID_INPUT_FAIL_CAUSE,     "int"),
    "output_status":      (OID_OUTPUT_STATUS,        "int"),
    "output_voltage":     (OID_OUTPUT_VOLTAGE,       "int"),
    "output_frequency":   (OID_OUTPUT_FREQUENCY,     "int"),
    "output_load":        (OID_OUTPUT_LOAD_PCT,      "int"),
    "output_current":     (OID_OUTPUT_CURRENT,       "int"),
    "test_result":        (OID_TEST_RESULT,          "int"),
    "test_last_date":     (OID_TEST_LAST_DATE,       "str"),
    "comm_status":        (OID_COMM_STATUS,          "int"),
}
