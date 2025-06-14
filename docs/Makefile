# Minimal Makefile for Sphinx documentation
# Adapted from `sphinx-quickstart` output (GNU make).

# You can set these variables from the command line.
SPHINXOPTS ?=
SPHINXBUILD ?= sphinx-build
SOURCEDIR := .
BUILDDIR := _build

.PHONY: help clean html dirhtml doctest linkcheck

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

clean:
	rm -rf "$(BUILDDIR)"

html:
	$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

dirhtml:
	$(SPHINXBUILD) -M dirhtml "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

doctest:
	$(SPHINXBUILD) -M doctest "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

linkcheck:
	$(SPHINXBUILD) -M linkcheck "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) 