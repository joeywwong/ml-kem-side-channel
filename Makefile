PYTHON ?= python
.PHONY: help doctor test sanitize simulate attack-sim report host-mlkem bench stm32-build nano-capture all
help doctor test sanitize simulate attack-sim report host-mlkem bench stm32-build nano-capture all:
	$(PYTHON) tasks.py $@
