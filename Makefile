.PHONY: pip_install
pip_install:
	pipenv install --dev
	pip install --upgrade build


.PHONY: test
test:
	pytest -v --cov --cov-report=term --cov-report=html


.PHONY: build
build: clean stubs docs
	python -m build
	twine check dist/*


.PHONY: stubs
stubs:
	bin/mkstubs.py


.PHONY: clean
clean:
	rm -rf ./dist/*
	rm -rf ./htmlcov


.PHONY: docs
docs:
	rm -rf ./docs/*
	pdoc --html --output-dir ./docs ./src/synapsis
	mv ./docs/synapsis/* ./docs/
	rmdir ./docs/synapsis


.PHONY: install_local
install_local:
	pip install -e .


.PHONY: publish
publish: build
	python -m twine upload dist/*


.PHONY: uninstall
uninstall:
	pip uninstall -y synapsis
