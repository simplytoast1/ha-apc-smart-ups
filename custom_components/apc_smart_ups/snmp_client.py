"""Thin async SNMPv2c wrapper around pysnmp's high-level API.

Design:
  * The ``SnmpEngine`` is created once per client and reused across all
    requests. pysnmp builds substantial internal state when an engine
    starts up; recreating it every poll would be wasteful. The engine is
    shut down via :meth:`ApcSnmpClient.shutdown` when the integration
    unloads.
  * A single GET request can carry many OIDs, so each poll cycle uses
    one round trip regardless of how many sensors the integration
    exposes.
  * Value coercion uses ``isinstance`` against the real pysnmp classes
    (not class-name string matching) so the integration is robust
    against pysnmp internal renames or subclassing.
"""
from __future__ import annotations

import logging
from typing import Any

from pysnmp.hlapi.v3arch.asyncio import (
    CommunityData,
    ContextData,
    ObjectIdentity,
    ObjectType,
    SnmpEngine,
    UdpTransportTarget,
    get_cmd,
)
from pysnmp.proto.rfc1902 import OctetString
from pysnmp.proto.rfc1905 import EndOfMibView, NoSuchInstance, NoSuchObject

_LOGGER = logging.getLogger(__name__)


class SnmpAuthError(Exception):
    """Raised when SNMP authentication fails (wrong community)."""


class SnmpTransportError(Exception):
    """Raised on network errors / timeouts / non-auth SNMP errors."""


class ApcSnmpClient:
    """Async SNMPv2c client targeting an APC NMC.

    Holds a long-lived ``SnmpEngine``; call :meth:`shutdown` from your
    integration's unload path so the dispatcher's sockets are released.
    """

    def __init__(
        self,
        host: str,
        port: int = 161,
        *,
        community: str,
        timeout: float = 3.0,
        retries: int = 1,
    ) -> None:
        self.host = host
        self.port = port
        self.community = community
        self.timeout = timeout
        self.retries = retries
        self._engine: SnmpEngine = SnmpEngine()

    async def get(self, oids: list[str]) -> dict[str, Any]:
        """Single GET-request for many OIDs. Returns a dict keyed by OID string."""
        transport = await UdpTransportTarget.create(
            (self.host, self.port),
            timeout=self.timeout,
            retries=self.retries,
        )
        obj_types = [ObjectType(ObjectIdentity(o)) for o in oids]

        error_indication, error_status, _error_index, var_binds = await get_cmd(
            self._engine,
            # mpModel=1 -> SNMPv2c. The NMC's "SNMPv1" config page accepts
            # both v1 and v2c clients via the same community.
            CommunityData(self.community, mpModel=1),
            transport,
            ContextData(),
            *obj_types,
        )

        if error_indication:
            msg = str(error_indication)
            if any(
                k in msg.lower()
                for k in ("authentication failure", "wrong digest")
            ):
                raise SnmpAuthError(msg)
            raise SnmpTransportError(msg)

        if error_status:
            raise SnmpTransportError(
                f"SNMP error: {error_status.prettyPrint()}"
            )

        out: dict[str, Any] = {}
        for var in var_binds:
            out[str(var[0])] = coerce_value(var[1])
        return out

    def shutdown(self) -> None:
        """Release the pysnmp dispatcher's sockets. Safe to call multiple times."""
        try:
            self._engine.transportDispatcher.closeDispatcher()
        except Exception:  # noqa: BLE001
            # Engine may already be closed, or never opened a transport.
            pass


def coerce_value(snmp_value: Any) -> Any:
    """Convert a pysnmp value to a Python primitive.

    Uses ``isinstance`` against pysnmp's real classes so the function is
    not coupled to internal class names.
    """
    # NoSuchObject/NoSuchInstance mean the agent does not implement this
    # OID (firmware-dependent); EndOfMibView ends a walk. Surface them as
    # None so the entity layer can show "Unavailable".
    if isinstance(snmp_value, (NoSuchObject, NoSuchInstance, EndOfMibView)):
        return None
    if isinstance(snmp_value, OctetString):
        try:
            return bytes(snmp_value).decode("utf-8", errors="replace").rstrip("\x00")
        except Exception:  # noqa: BLE001
            return str(snmp_value)
    # All Integer-like (Integer, Counter32/64, Gauge32, TimeTicks, etc).
    try:
        return int(snmp_value)
    except (TypeError, ValueError):
        return str(snmp_value)
