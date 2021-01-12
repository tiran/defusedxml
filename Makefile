PYTHON=python3
SETUPFLAGS=
COMPILEFLAGS=
INSTALLFLAGS=

.PHONY: inplace all rebuild test_inplace test fulltests clean distclean
.PHONY: sdist install black

all: inplace black README.html README.md

README.md: README.txt CHANGES.txt
	pandoc --from=rst --to=gfm README.txt > $@
	pandoc --from=rst --to=gfm CHANGES.txt >> $@
	sed -i ':a;N;$$!ba;s/\n\[!/[!/g' $@

README.html: README.txt CHANGES.txt void.css
	@echo | cat README.txt - CHANGES.txt | \
	    rst2html --verbose --exit-status=1 --stylesheet=void.css \
            > README.html

inplace:
	$(PYTHON) setup.py $(SETUPFLAGS) build_ext -i $(COMPILEFLAGS)

rebuild: clean all

test_inplace: inplace
	$(PYTHON) -m tests

test: test_inplace

black:
	black $(CURDIR) || true

clean:
	@find . \( -name '*.o' -or -name '*.so' -or -name '*.sl' -or \
	           -name '*.py[cod]' -or -name README.html \) \
	    -and -type f -delete
	@rm -f .coverage .coverage.* coverage.xml

distclean: clean
	@rm -rf build
	@rm -rf dist
	@find . \( -name '~*' -or -name '*.orig' -or -name '*.bak' -or \
	          -name 'core*' \) -and -type f  -delete

whitespace:
	@find \( -name '*.rst' -or -name '*.py' -or -name '*.xml' \) | \
	    xargs sed -i 's/[ \t]*$$//'


packages: README.html README.md
	$(PYTHON) setup.py packages

install:
	$(PYTHON) setup.py $(SETUPFLAGS) build $(COMPILEFLAGS)
	$(PYTHON) setup.py install $(INSTALLFLAGS)
