# APC Smart-UPS (NMC) for Home Assistant

[![HACS](https://github.com/simplytoast1/ha-apc-smart-ups/actions/workflows/hacs.yaml/badge.svg)](https://github.com/simplytoast1/ha-apc-smart-ups/actions/workflows/hacs.yaml)
[![Hassfest](https://github.com/simplytoast1/ha-apc-smart-ups/actions/workflows/hassfest.yaml/badge.svg)](https://github.com/simplytoast1/ha-apc-smart-ups/actions/workflows/hassfest.yaml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Local Home Assistant integration for APC Smart-UPS hardware via the **Network Management Card** (NMC2 / NMC3 — AP9640, AP9641, AP9643). Talks SNMPv2c directly to the card. No cloud, no MFA, no cookie paste.

Made with care by [Pingie.com](https://pingie.com)

## Why this exists

The official Home Assistant ecosystem already covers APC UPSes via `apcupsd` (USB) and `nut` (SNMP/NUT-server). Both work great. This integration exists for users who want a config-flow-driven, opinionated, polished entity set tied directly to the NMC's SNMP interface — no NUT server to maintain, no USB cable needed, just the network card and an IP.

If you prefer NUT or apcupsd, use them. They're excellent. This is a third option.

## Features

- **Local SNMPv2c polling** — no cloud roundtrip, no internet dependency, sub-second latency
- **One-step config flow** — paste an IP and community, done
- **Config-flow re-auth** — credential changes flow through HA's Repair UI
- **Auto device-info** — model, name, serial, firmware all read from the NMC and shown in the device registry
- **One round-trip per poll cycle** — all OIDs requested in a single SNMP GET. Default 10 seconds, adjustable from 5 to 300 seconds via the integration's **Configure** dialog

## Compatibility

- **NMC3**: AP9640, AP9641, AP9643 — verified against the [Network Management Card 3 User Guide](https://download.schneider-electric.com/files?p_enDocType=User+guide&p_File_Name=990-91148P-EN.pdf&p_Doc_Ref=SPD_CCON-AYCEFJ_EN)
- **NMC2**: AP9630, AP9631, AP9635 — should work, same PowerNet-MIB
- Tested against a **Smart-UPS 1500 (SMTL1500RM3UC)** with an NMC3
- Home Assistant **2024.11.0** or newer

## Entities exposed

### Sensors (18)
- Battery (7): charge %, runtime remaining, voltage, current, temperature, status, last-replaced date.
- Input (4): voltage, voltage peak, voltage min, frequency.
- Output (5): voltage, current, frequency, load %, operating mode.
- Self-test (2): result, last-test date.

### Binary sensors (6)
On battery, Battery low, Battery needs replacement, Fault, NMC reachable, Self-test problem.

Entities that the NMC's firmware does not report (commonly `battery_current` on smaller Smart-UPS models) gracefully read as **Unavailable** rather than falsely as zero/off.

## Installation

### HACS (recommended)

1. Make sure [HACS](https://hacs.xyz/) is installed.
2. **HACS → Integrations → ⋮ → Custom repositories**
3. Repository URL: `https://github.com/simplytoast1/ha-apc-smart-ups`
4. Category: **Integration**
5. Click **Add**, then install **APC Smart-UPS (NMC)**.
6. **Restart Home Assistant**.

### Manual

Copy `custom_components/apc_smart_ups/` into your Home Assistant `config/custom_components/` directory and restart.

## Configuring the NMC

> **Important:** on a factory-fresh NMC3, **all SNMP access is disabled by default**. You must enable it before this integration can talk to the card. The same is true on most NMC2 cards running modern firmware. The steps below cover that.

1. Install the card in your UPS's SmartSlot, connect ethernet, power on the UPS.
2. Find its IP from your router's DHCP lease list, or `arp -a | grep 28:29:86` (Schneider OUI).
3. Open `https://<nmc-ip>/` in a browser. Log in with `apc` / `apc`.
4. You'll be forced to change the Super User password. Do that.
5. Enable SNMP:
   - **Configuration → Network → SNMPv1 → Access**: tick **Enable SNMPv1 access**, then Apply.
   - **Configuration → Network → SNMPv1 → Access Control**: click the first row's community name to edit it. Set:
     - **Community Name** to something like `HomeAssistant` (case-sensitive, this is what you'll paste into HA below)
     - **Access Type** to `Read` (the integration only does GETs)
     - **NMS IP/Host Name** to `0.0.0.0` to start with (any source). Tighten to your HA host's IP once you've confirmed it works.
   - Apply.

## Configuring Home Assistant

1. **Settings → Devices & Services → Add Integration → APC Smart-UPS (NMC)**
2. Enter:
   - **Host or IP**: the NMC's IP (e.g. `192.168.1.50`)
   - **Port**: `161` (the default)
   - **Community string**: whatever you set on the NMC (case-sensitive)
3. Submit. The integration probes the NMC for model, name, and serial, then registers a device.
4. **(Optional)** Click **Configure** on the integration card to change the poll interval. Default 10s; range 5–300s. Changes apply on the next poll cycle without removing the integration.

## Troubleshooting

**"Could not reach the NMC" / connection times out.** Most common cause: SNMPv1 access is enabled on the NMC but the Access Control *row* for your community is still disabled. Each community row in **Configuration → Network → SNMPv1 → Access Control** needs its access type set to **Read** *in addition to* the top-level **Enable SNMPv1 access** toggle. Verify from another machine first:

```bash
snmpwalk -v2c -c <your-community> <nmc-ip> 1.3.6.1.2.1.1.1.0
```

If snmpwalk works from your laptop but HA times out, check the firewall between HA and the NMC for UDP/161. Also remember community strings are case-sensitive, and **NMS IP/Host Name** must be `0.0.0.0` (any) or your HA host's exact IP.

**Some sensors show "Unavailable".** Older Smart-UPS firmware doesn't implement every PowerNet-MIB OID. `battery_current` in particular is commonly missing on smaller Smart-UPS models. This is expected behavior, not a bug. The integration treats missing OIDs gracefully.

**Debug logging:**
```yaml
logger:
  default: warning
  logs:
    custom_components.apc_smart_ups: debug
```

## License

[MIT](LICENSE) — fork freely.
