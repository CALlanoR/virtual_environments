venv: venv/bin/activate
venv/bin/activate: requirements.txt
	test -d venv || virtualenv -p /usr/bin/python3.12 venv
	venv/bin/pip3 install -Ur requirements.txt
	touch venv/bin/activate

style:
	ruff check databricks_null_fields_v2.py

clean:
	rm -rf venv
