PYTHON      ?= python3.12
VENV_DIR    ?= .venv
VENV_PY     := $(VENV_DIR)/bin/python
VENV_PIP    := $(VENV_DIR)/bin/pip

.PHONY: venv venv-clean run-5.7 run-8 help

help:
	@echo "Targets:"
	@echo "  venv         Crea el virtualenv en $(VENV_DIR) e instala requirements"
	@echo "  venv-clean   Elimina $(VENV_DIR)"
	@echo "  run-5.7      Ejecuta el generador contra mysql5.7 (puerto 3306)"
	@echo "  run-8        Ejecuta el generador contra mysql8 (puerto 3308)"
	@echo ""
	@echo "Defaults del generador: 1 op/seg durante 40s, luego termina."
	@echo "Para correr indefinidamente (legacy): añade '-- -d 0' al comando python."

venv: $(VENV_DIR)/.installed

$(VENV_DIR)/.installed: requirements.txt
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install -r requirements.txt
	touch $@

venv-clean:
	rm -rf $(VENV_DIR)

run-5.7: venv
	$(VENV_PY) random_changes.py --target mysql5.7

run-8: venv
	$(VENV_PY) random_changes.py --target mysql8
