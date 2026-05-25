PYTHON      ?= python3.12
VENV_DIR    ?= .venv
VENV_PY     := $(VENV_DIR)/bin/python
VENV_PIP    := $(VENV_DIR)/bin/pip

# CSVS es la lista de archivos a graficar (uno o dos). Ejemplo:
#   make plot CSVS="/tmp/m57.csv /tmp/m8.csv"
CSVS ?=
OUT  ?= monitoring-report.png

.PHONY: venv venv-clean plot help

help:
	@echo "Targets:"
	@echo "  venv         Crea $(VENV_DIR) e instala pandas + matplotlib"
	@echo "  venv-clean   Elimina $(VENV_DIR)"
	@echo "  plot         Genera PNG. Pasa los CSVs vía CSVS=\"a.csv [b.csv]\""
	@echo ""
	@echo "Ejemplo:"
	@echo "  make plot CSVS=\"/tmp/mysql57.csv /tmp/mysql8.csv\" OUT=compare.png"

venv: $(VENV_DIR)/.installed

$(VENV_DIR)/.installed: requirements.txt
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install -r requirements.txt
	touch $@

venv-clean:
	rm -rf $(VENV_DIR)

plot: venv
	@if [ -z "$(CSVS)" ]; then \
		echo "Error: pasa CSVS=\"a.csv [b.csv]\""; exit 64; \
	fi
	$(VENV_PY) plot.py $(CSVS) -o $(OUT)
