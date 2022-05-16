BIN=venv/bin/
SHELL=/bin/bash

venv: venv/bin/activate
venv/bin/activate: requirements.txt
	test -d venv || virtualenv -p /usr/bin/python3.8 venv
	venv/bin/python -m pip install --upgrade pip
	venv/bin/pip install -Ur requirements.txt
	touch venv/bin/activate

clean:
	rm -rf venv