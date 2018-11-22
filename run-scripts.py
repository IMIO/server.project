# -*- coding: utf-8 -*-

import sys
from imio.pyutils.system import verbose, error
import transaction
from plone import api

# Parameters check
if len(sys.argv) < 3 or sys.argv[2] != 'run-scripts.py':
    error("Inconsistent or unexpected args len: %s" % sys.argv)
    sys.exit(0)


def script1():
    verbose(' on %s' % obj.absolute_url_path())
    transaction.commit()


info = ["You can pass following parameters (with the first one always script number):", "1: various"]

scripts = {'1': script1}

if len(sys.argv) < 4 or sys.argv[3] not in scripts:
    error("Bad script parameter")
    verbose('\n>> =>'.join(info))
    sys.exit(0)

with api.env.adopt_user(username='admin'):
    scripts[sys.argv[3]]()
