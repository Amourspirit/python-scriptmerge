.PHONY: test upload clean bootstrap

test:
	sh -c 'python -m pytest'

upload:
	_virtualenv/bin/python setup.py sdist bdist_wheel upload
	make clean

register:
	poetry build
	poetry install


clean:
	rm -rf dist

bootstrap:
	poetry install
	make clean
