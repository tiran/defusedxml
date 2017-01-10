PYTHON=python
SETUPFLAGS=
COMPILEFLAGS=
INSTALLFLAGS=
PYTHONS=python2.6 python2.7 python3.1 python3.2 python3.3 python3.4

.PHONY: inplace all rebuild test_inplace test fulltests clean distclean
.PHONY: sdist install

all: inplace README.html

README.html: README.rst CHANGES.rst void.css
	@echo | cat README.rst - CHANGES.rst | \
	    rst2html.py --verbose --exit-status=1 --stylesheet=void.css \
            > README.html

inplace:
	$(PYTHON) setup.py $(SETUPFLAGS) build_ext -i $(COMPILEFLAGS)

rebuild: clean all

test_inplace: inplace
	$(PYTHON) -m tests

test: test_inplace

fulltest:
	$(MAKE) clean
	@set -e; \
	for python in $(PYTHONS); do \
		if [ -z $$(which $$python) ]; then \
			echo "*** $$python not found ***\n"; \
			continue; \
		fi; \
		echo "*** $$python ***"; \
		$$python $(SETUPFLAGS) setup.py -q test; \
		echo ""; \
	done
	$(MAKE) clean

clean:
	@find . \( -name '*.o' -or -name '*.so' -or -name '*.sl' -or \
	           -name '*.py[cod]' -or -name README.html \) \
	    -and -type f -delete

distclean: clean
	@rm -rf build
	@rm -rf dist
	@find . \( -name '~*' -or -name '*.orig' -or -name '*.bak' -or \
	          -name 'core*' \) -and -type f  -delete

whitespace:
	@find \( -name '*.rst' -or -name '*.py' -or -name '*.xml' \) | \
	    xargs sed -i 's/[ \t]*$$//'


sdist: README.html
	$(PYTHON) setup.py sdist --formats gztar,zip

install:
	$(PYTHON) setup.py $(SETUPFLAGS) build $(COMPILEFLAGS)
	$(PYTHON) setup.py install $(INSTALLFLAGS)
