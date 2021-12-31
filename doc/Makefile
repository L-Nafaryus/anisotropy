# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SPHINXAPIDOC  ?= sphinx-apidoc
SOURCEDIR     = source
BUILDDIR      = build
PROJECTDIR 	  = ..

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	[ -d "$(BUILDDIR)/html" ] && cp -vf "$(BUILDDIR)/html" anisotropy/

update:
	@$(SPHINXAPIDOC) -f -o "$(SOURCEDIR)" "$(PROJECTDIR)"
	rm -vf "$(SOURCEDIR)/modules.rst" "$(SOURCEDIR)/tests.rst" "$(SOURCEDIR)/setup.rst"
	sed -i 's/:maxdepth: 4/:maxdepth: 1/' "$(SOURCEDIR)/anisotropy.rst"
	cp -vf "$(PROJECTDIR)/README.rst" "$(SOURCEDIR)/"
	cp -vf "$(PROJECTDIR)/INSTALL.rst" "$(SOURCEDIR)/"
	peewee-erd -o="$(SOURCEDIR)/static/er-diagram.png" --main-color="#333333" --bg-color="#eeeeee" --font-size="12" "$(PROJECTDIR)/anisotropy/core/models.py"
	pydeps "$(PROJECTDIR)/anisotropy" --max-bacon 2 --cluster -o "$(SOURCEDIR)/static/structure.png" -T png --noshow
