# BLOCKED — toolchain and actual MCU memory unverified

Neither Windows nor the inspected WSL Ubuntu has `arm-none-eabi-gcc` on PATH.
No firmware was built. No guessed 1 MB linker script is provided: the physical
marking, flash-size register and Discovery board revision must be verified first.
Then integrate the pinned full ML-KEM baseline with Discovery-specific startup,
clock, UART and a verified linker map. Record map/stack/RAM, execute KATs only on
explicit request, and gather DWT repeat/min/median/dispersion with clock metadata.
`python tasks.py stm32-build` fails clearly until that integration is completed.
