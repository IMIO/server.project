#!/usr/bin/make
#
all: run

.PHONY: bootstrap
bootstrap:
	virtualenv-2.7 .
	bin/easy_install setuptools==11.1
	bin/easy_install setuptools==30.2.0
	./bin/python bootstrap.py

.PHONY: buildout
buildout:
	if ! test -f bin/buildout;then make bootstrap;fi
	if ! test -f var/filestorage/Data.fs;then make standard-config; else bin/buildout -v;fi

.PHONY: standard-config
standard-config:
	if ! test -f bin/buildout;then make bootstrap;fi
	bin/buildout -vt 5 -c standard-config.cfg

.PHONY: run
run:
	if ! test -f bin/instance1;then make buildout;fi
	bin/instance1 fg

.PHONY: coverage
coverage:
	bin/coveragepst
	bin/report

.PHONY: robot-server
robot-server:
	bin/robot-server -v imio.project.pst.testing.PST_ROBOT_TESTING

.PHONY: doc
doc:
	# can be run by example with: make doc opt='-t "Test1 *"'
	bin/robot $(opt) src/imio.project.pst/src/imio/project/pst/tests/robot/doc.robot

.PHONY: cleanall
cleanall:
	rm -fr develop-eggs downloads eggs parts .installed.cfg lib include bin

.PHONY: templates_update
templates_update:
	if test -f bin/instance-debug;then bin/instance-debug run templates.py; else bin/instance1 run templates.py;fi
