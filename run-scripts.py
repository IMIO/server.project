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
    verbose('Pst budget correction on %s' % obj.absolute_url_path())
    catalog = obj.portal_catalog
    from imio.project.core.events import onModifyProject
    for brain in catalog(portal_type='projectspace'):
        ps = brain.getObject()
        verbose(ps.absolute_url())
        ret = ps.restrictedTraverse('clean_budget/display')()
        verbose("Before: {}".format(ret.split('<br />\n')[0]))
        ps.restrictedTraverse('clean_budget/delete')(empty_budget=False)
        path = brain.getPath()
        pt = ('pstaction', 'operationalobjective', 'strategicobjective')
        for brain in catalog(portal_type=pt, path=path, sort_on='path'):
            onModifyProject(brain.getObject(), None)
        ret = ps.restrictedTraverse('clean_budget/display')()
        verbose("After : {}".format(ret.split('<br />\n')[0]))
    transaction.commit()


info = ["You can pass following parameters (with the first one always script number):", "1: various"]

scripts = {'1': script1}

if len(sys.argv) < 4 or sys.argv[3] not in scripts:
    error("Bad script parameter")
    verbose('\n>> =>'.join(info))
    sys.exit(0)

with api.env.adopt_user(username='admin'):
    scripts[sys.argv[3]]()


def script1_1():
    verbose('Pst archive migrations on %s' % obj.absolute_url_path())
    from imio.project.pst.interfaces import IImioPSTProject
    from zope.interface import alsoProvides
    # consider modified schema for projectspace
    obj.portal_setup.runImportStepFromProfile('imio.project.core:default', 'typeinfo', run_dependencies=False)
    verbose('Typeinfo updated')
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
    verbose('Pstproject: marker added, years added, localroles added')
    # add archive action
    obj.portal_setup.runImportStepFromProfile('imio.project.pst:default', 'actions', run_dependencies=False)
    verbose('Actions updated')
    # update dexterity type local roles
    from plone.dexterity.interfaces import IDexterityFTI
    from zope.component import getUtility
    fti = getUtility(IDexterityFTI, name='projectspace')
    lr = getattr(fti, 'localroles')
    lrsc = lr['static_config']
    if 'internally_published' in lrsc and 'pst_editors' in lrsc['internally_published']:
        del(lrsc['internally_published']['pst_editors'])
        lr._p_changed = True
    verbose('Dexterity local roles removed')


def script1_2():
    verbose('Pst migration on %s' % obj.absolute_url_path())
    catalog = obj.portal_catalog
    for brain in catalog(portal_type='projectspace'):
        ps = brain.getObject()
        ps.manage_addLocalRoles("pst_editors", ('Reader', 'Editor', 'Reviewer', 'Contributor', ))
        ps.reindexObject()
        ps.reindexObjectSecurity()


def script1_3():
    verbose('Pst dashboards migration on %s' % obj.absolute_url_path())
    catalog = obj.portal_catalog
    from collective.eeafaceted.collectionwidget.utils import _updateDefaultCollectionFor
    from imio.project.pst import add_path
    for brain in catalog(portal_type='projectspace'):
        ps = brain.getObject()
        if 'operationalobjectives' not in ps:
            continue
        folder = ps['operationalobjectives']
        xmlpath = add_path('faceted_conf/operationalobjective.xml')
        folder.unrestrictedTraverse('@@faceted_exportimport').import_xml(import_file=open(xmlpath))
        _updateDefaultCollectionFor(folder, folder['all'].UID())
    obj.portal_setup.runImportStepFromProfile('imio.project.core:default', 'viewlets', run_dependencies=False)
    transaction.commit()
