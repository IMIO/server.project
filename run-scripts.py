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
    verbose('Pst marker on %s' % obj.absolute_url_path())
    from imio.project.pst.interfaces import IImioPSTProject
    from zope.interface import alsoProvides
    # consider modified schema for projectspace
    obj.portal_setup.runImportStepFromProfile('imio.project.core:default', 'typeinfo', run_dependencies=False)
    # set marker interface
    catalog = obj.portal_catalog
    for brain in catalog(portal_type='projectspace'):
        ps = brain.getObject()
        alsoProvides(ps, IImioPSTProject)
        if not ps.budget_years:
            ps.budget_years = [2013, 2014, 2015, 2016, 2017, 2018]
        ps.manage_addLocalRoles("pst_editors", ('Reader', 'Editor', 'Reviewer', 'Contributor', ))
        ps.reindexObject()
        ps.reindexObjectSecurity()
    # add archive action
    obj.portal_setup.runImportStepFromProfile('imio.project.pst:default', 'actions', run_dependencies=False)
    # update dexterity type local roles
    from plone.dexterity.interfaces import IDexterityFTI
    from zope.component import getUtility
    fti = getUtility(IDexterityFTI, name='projectspace')
    lr = getattr(fti, 'localroles')
    lrsc = lr['static_config']
    if 'internally_published' in lrsc and 'pst_editors' in lrsc['internally_published']:
        del(lrsc['internally_published']['pst_editors'])
        lr._p_changed = True

    transaction.commit()

info = ["You can pass following parameters (with the first one always script number):", "1: various"]

scripts = {'1': script1}

if len(sys.argv) < 4 or sys.argv[3] not in scripts:
    error("Bad script parameter")
    verbose('\n>> =>'.join(info))
    sys.exit(0)

with api.env.adopt_user(username='admin'):
    scripts[sys.argv[3]]()
