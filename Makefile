#!/usr/bin/make
#
# plone-path is added when "vhost_path: mount/site" is defined in puppet
plone=$(shell grep plone-path port.cfg|cut -c 14-)
hostname=$(shell hostname)
instance1_port=$(shell grep instance1-http port.cfg|cut -c 18-)
disable=0
copydata=1
instance=instance-debug
profile=imio.project.pst:default

all: run

.PHONY: bootstrap
bootstrap:
	virtualenv-2.7 .
	./bin/python bootstrap.py

.PHONY: setup
setup:
	if command -v python2 >/dev/null && command -v virtualenv; then virtualenv -p python2 . ; elif command -v virtualenv-2.7; then virtualenv-2.7 . ;fi
	./bin/pip install --upgrade pip
	./bin/pip install -r requirements.txt

.PHONY: buildout
buildout:
	if ! test -f bin/buildout;then make setup;fi
	if ! test -f var/filestorage/Data.fs;then make standard-config; else bin/buildout -v;fi
	git checkout .gitignore

.PHONY: copy
copy:
	@# copy-data is generated by puppet when data_source is found
	@echo "disable: $(disable)"
	if [ $(copydata) = 1 ] && [ -f copy-data.sh ]; then (if [ $(disable) = 1 ]; then ./copy-data.sh --disable-auth=1; else ./copy-data.sh; fi); fi
	@$ echo "copy-data finished for instance $(plone), check http://$(hostname):$(instance1_port)/manage_main" | mail -s "copy-data finished" franck.fngaha@imio.be

.PHONY: upgrade
upgrade:
	@if ! test -f bin/instance1;then make buildout;fi
	@echo "plone: $(plone)"
	./bin/$(instance) -O$(plone) run bin/run-portal-upgrades --username admin -A $(plone)
	@#./bin/upgrade-portals --username admin -A -G profile-imio.project.pst:default $(plone)

.PHONY: standard-config
standard-config:
	if ! test -f bin/buildout;then make setup;fi
	bin/buildout -vt 5 -c standard-config.cfg
	git checkout .gitignore

.PHONY: run
run:
	if ! test -f bin/instance1;then make buildout;fi
	bin/instance1 fg

.PHONY: ports
ports:
	@echo "plone: $(plone)"
	bin/$(instance) -O$(plone) run run-scripts.py 2

.PHONY: coveragepst
coveragepst:
	bin/coveragepst
	bin/report

.PHONY: coveragecore
coveragecore:
	bin/coveragecore
	bin/report

.PHONY: robot-server
robot-server:
	env ZSERVER_HOST=localhost ZSERVER_PORT=55001 bin/robot-server -v imio.project.pst.testing.PST_ROBOT_TESTING

.PHONY: doc
doc:
	# can be run by example with: make doc opt='-t "Test1 *"'
	# env ZSERVER_PORT=55001 ??  https://github.com/plone/plone.app.robotframework/issues/99
	env ZSERVER_HOST=localhost ZSERVER_PORT=55001 bin/robot $(opt) src/imio.project.pst/src/imio/project/pst/tests/robot/doc.robot

.PHONY: cleanall
cleanall:
	rm -fr develop-eggs downloads eggs parts .installed.cfg lib include bin

.PHONY: various-script
various-script:
	@echo "plone: $(plone)"
	bin/$(instance) -O$(plone) run run-scripts.py 1

.PHONY: script
script:
	# script.py is not committed
	@echo "plone: $(plone)"
	bin/instance1 -O$(plone) run script.py

.PHONY: vc
vc:
	bin/versioncheck -rbo checkversion.html

.PHONY: install_requests
install_requests:
	./bin/pip install requests
