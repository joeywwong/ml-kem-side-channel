# Deferred hardware checklist — D4/D5 NOT RUN

The Nano is not available. No board has been opened or flashed by these scripts.
`capture_nano.py` is an explicit D4 guard, not an implemented capture pipeline.

When the Nano arrives:

1. Inspect actual PCB revision and MCU markings; compare official hardware docs.
   Identify library/firmware version and USB connectivity without updating firmware.
   Keep serial identifiers in local-only metadata.
2. Run a stock NewAE Nano sanity capture and preserve raw data/configuration.
   Verify trigger, clipping, alignment, repeatability and disconnect handling.
3. Build only the scalar target for the verified F030: nominal 16 KB flash,
   4 KB RAM. Verify map and stack budget. Implement a bounded serial protocol and
   confirm permission **before flashing**. Do not attempt full ML-KEM on it.
4. Use the actual supported Nano API: rising edge, <=50,000 samples, <=20 MS/s,
   no streaming/offset/pretrigger assumption. At 20 MS/s the buffer is 2.5 ms.
5. Define trigger windows, clock/sample rates and leakage model from actual
   optimized ARM assembly. Capture pilots, then compare identical conditions.
   Keep physical raw traces under `local-results/nano-physical/`.

For F407 software testing: read physical marking and flash-size register, record
board revision and device ID, verify accessible RAM regions and linker allocation.
The previously reported 0x413 ID does not resolve VET6/VGT6 flash size. Use the
Discovery board's startup, clock, UART and ST-LINK configuration. Require explicit
connected-board execution request before running KATs/DWT timing.

**BLOCKED: safe external measurement interface not yet verified.** Nano normally
measures its integrated target. Before an F407 capture, obtain both exact revision
schematics; identify shunt location/analog gain/input limits, supply paths, common
ground, 3.3 V trigger and UART, and asynchronous clock effects. Determine required
headers, shunt/analog front-end and probes from those schematics; do not buy or
recommend exact parts on an unverified topology. This is a feasibility checklist,
not a wiring diagram. Do not connect MEASURE to a supply rail, join independently
powered 3.3 V outputs, apply 5 V logic, or modify/break either board. No glitching.

References: [Nano hardware](https://chipwhisperer.readthedocs.io/en/latest/Capture/ChipWhisperer-Nano.html),
[scope API](https://chipwhisperer.readthedocs.io/en/latest/scope-api.html),
[STM32F407 documentation](https://www.st.com/en/microcontrollers-microprocessors/stm32f407-417.html).
