# -*- coding: utf-8 -*-

import logging
import sys

from zope.component.hooks import setSite
from Products.CPUtils.Extensions.utils import get_all_site_objects
from imio.updates.helpers import setup_app, setup_logger


def main(app):
    setup_logger()
    logger = logging.getLogger('templates')
    user = setup_app(app, logger=logger)
    if not user:
        logger.error("User zope admin wasn't found")
        sys.exit(1)
    sites = [site for site in get_all_site_objects(app) if site.id not in ['standard', 'p1']]
    if len(sites) != 1:
        logger.error("No site or multiple sites '%s'" % sites)
        sys.exit(1)
    for site in sites:
        setSite(site)
        ret = site.portal_setup.runImportStepFromProfile('profile-imio.project.pst:update',
                                                         'imioprojectpst-update-templates')
        # if 'messages' in ret:
        #     logger.info(ret['messages']['imioprojectpst-update-templates'])

if __name__ == '__main__':
    main(app)  # NOQA
