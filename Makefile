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
