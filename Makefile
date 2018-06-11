VENV=./ve
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip
PROJECT=swagger_aor_generator

$(VENV):
	virtualenv $(VENV) --python=python3.6

virtualenv: $(VENV)
	$(PIP) install -r requirements.txt

clean-virtualenv:
	rm -rf $(VENV)

test:
	$(VENV)/bin/nosetests --verbose

demo-aor:
	mkdir demo
	$(PYTHON) swagger_aor_generator/generator.py tests/resources/petstore-aor.json aor --output-dir=demo --module-name="A Pet Admin" --rest-server-url="localhost:3000/api/v1"

permissions-demo-aor:
	mkdir demo
	$(PYTHON) swagger_aor_generator/generator.py tests/resources/petstore-aor.json aor --output-dir=demo --module-name="A Pet Admin" --rest-server-url="localhost:3000/api/v1" --permissions

demo-ra:
	mkdir demo
	$(PYTHON) swagger_aor_generator/generator.py tests/resources/petstore-aor.json ra --output-dir=demo --module-name="A Pet Admin" --rest-server-url="localhost:3000/api/v1"

clean-demo:
	rm -rf demo