#!/usr/bin/make
all: buildout

run: bin/instance1
	bin/instance1 fg

bin/instance1: bin/buildout
	bin/buildout

bin/buildout: bin/pip buildout.cfg
	bin/pip install -I -r https://dist.plone.org/release/5-latest/requirements.txt

bin/pip:
	python3 -m venv .

buildout.cfg:
	ln -fs dev.cfg buildout.cfg

cleanall:
	rm -fr develop-eggs downloads eggs parts .installed.cfg lib lib64 include bin .mr.developer.cfg local/
