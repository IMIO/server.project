
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
"""
{'_value': [{'fct_title': u"Gestionnaire d'action", 'fct_id': u'actioneditor'}], '__name__': 'collective.contact.plonegroup.browser.settings.IContactPlonegroupConfig.functions', '_field': <plone.registry.field.List object at 0x7fc88c20a320>, '__parent__': <Registry at portal_registry>, '__provides__': <zope.interface.Provides object at 0x7fc88c208350>}
"""


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
