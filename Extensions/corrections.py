# -*- coding: utf-8 -*-
from imio.project.core.utils import getProjectSpace
from plone import api
from Products.CPUtils.Extensions.utils import check_zope_admin


def correct_registry(self, dochange=''):
    """
        Correct registry record
    """
    from zope.component import getUtility
    from plone.registry.interfaces import IRegistry
    from collective.contact.plonegroup.config import FUNCTIONS_REGISTRY
    out = []
    pr = self.portal_registry
    records = pr._records
    errors = []
    for name in records.keys():
        try:
            records[name]
        except KeyError:
            out.append("Record '%s' is corrupted" % name)
            errors.append(name)

    if dochange not in ('', '0', 'False', 'false'):
        if FUNCTIONS_REGISTRY in errors:
            del records._fields[FUNCTIONS_REGISTRY]
            del records._values[FUNCTIONS_REGISTRY]
            self.portal_setup.runAllImportStepsFromProfile(u'profile-collective.contact.plonegroup:default')
            registry = getUtility(IRegistry)
            registry[FUNCTIONS_REGISTRY] = [{'fct_title': u"Gestionnaire d'action",
                                             'fct_id': u'actioneditor'}]
            try:
                records[FUNCTIONS_REGISTRY]
            except Exception:
                out.append("Record '%s' not corrected" % FUNCTIONS_REGISTRY)
            else:
                out.append("Record '%s' corrected" % FUNCTIONS_REGISTRY)

    return '\n'.join(out)


def update_reference_number(self, ptypes='strategicobjective|operationalobjective|pstaction', doit=''):
    """
        Correct reference numbers
    """
    if not check_zope_admin():
        return "You must be a zope manager to run this script"
    out = []
    # search regarding context
    types = ptypes.split('|')
    ps = getProjectSpace(self)
    out.append("Working on projectspace {}".format(ps))
    out.append('Searching on context {} for types {}'.format(self, types))
    brains = api.content.find(context=self, portal_type=types, sort_on='path')
    nref = ps.last_reference_number
    for brain in brains:
        nref += 1
        obj = brain.getObject()
        out.append("Changing ref from '{}' to {} on '{}'".format(obj.reference_number, nref, brain.getPath()))
        if doit == '1':
            obj.reference_number = nref
            obj.reindexObject()

    if doit == '1':
        ps.last_reference_number = nref
    return '\n'.join(out)


def various(self):
    """
        corrections diverses avec ipdb
    """
    # Changer le default d'un tb, ici ne rien mettre au niveau le plus haut
    context = self
    from imio.dashboard.utils import getCollectionLinkCriterion
    criterion = getCollectionLinkCriterion(context)
    criterion.default = u''
    from eea.facetednavigation.criteria.interfaces import ICriteria
    ICriteria(context).criteria._p_changed = True

    # Réparer la vue de la page pst
    context.setLayout('view')
    from imio.project.pst.setuphandlers import configure_faceted_folder
    configure_faceted_folder(context, xml='default_dashboard_widgets.xml', default_UID=None)
