# External capture blocked — safe analog interface unverified

No firmware is built in this repository. The sibling `ml-kem-m4` repository used
ARM GCC 14.3.1 to build STM32F407 firmware and completed functional board
validation with a verified linker map. Its later basemul instrumentation build
was tested on the host and cross-compiled but not flashed. The physical VE/VG
marking is still unresolved; no external power-capture interface is verified.
`python tasks.py stm32-build` remains a guard in this repository.
