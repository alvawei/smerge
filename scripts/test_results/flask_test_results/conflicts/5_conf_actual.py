# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import print_function
import inspect
import inspect
import re
import re
from pallets_sphinx_themes import DocVersion, ProjectLink, get_version
from pallets_sphinx_themes import ProjectLink, get_version
# Project --------------------------------------------------------------
copyright = '2010 Pallets Team'
author = 'Pallets Team'
release, version = get_version('Flask')
# General --------------------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinxcontrib.log_cabinet',
]
# HTML -----------------------------------------------------------------
html_theme = 'flask'
<<<<<<< REMOTE
html_context = {
    'project_links': [
        ProjectLink('Donate to Pallets', 'https://psfmember.org/civicrm/contribute/transact?reset=1&id=20'),
        ProjectLink('Flask Website', 'https://palletsprojects.com/p/flask/'),
        ProjectLink('PyPI releases', 'https://pypi.org/project/Flask/'),
        ProjectLink('Source Code', 'https://github.com/pallets/flask/'),
        ProjectLink(
            'Issue Tracker', 'https://github.com/pallets/flask/issues/'),
    ],
    'canonical_url': 'http://flask.pocoo.org/docs/{}/'.format(version),
    'carbon_ads_args': 'zoneid=1673&serve=C6AILKT&placement=pocooorg',
}
=======
html_context = {
    'project_links': [
        ProjectLink('Donate to Pallets', 'https://psfmember.org/civicrm/contribute/transact?reset=1&id=20'),
        ProjectLink('Flask Website', 'https://palletsprojects.com/p/flask/'),
        ProjectLink('PyPI releases', 'https://pypi.org/project/Flask/'),
        ProjectLink('Source Code', 'https://github.com/pallets/flask/'),
        ProjectLink(
            'Issue Tracker', 'https://github.com/pallets/flask/issues/'),
    ],
    'versions': [
        DocVersion('dev', 'Development', 'unstable'),
        DocVersion('1.0', 'Flask 1.0', 'stable'),
        DocVersion('0.12', 'Flask 0.12'),
    ],
    'canonical_url': 'http://flask.pocoo.org/docs/{}/'.format(version),
    'carbon_ads_args': 'zoneid=1673&serve=C6AILKT&placement=pocooorg',
}
>>>>>>> LOCAL
html_logo = '_static/flask.png'
html_additional_pages = {
    '404': '404.html',
}
html_show_sourcelink = False

# LaTeX ----------------------------------------------------------------

latex_documents = [
    (master_doc, 'Flask.tex', 'Flask Documentation', 'Pallets Team', 'manual'),
]
latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '12pt',
    'fontpkg': r'\usepackage{mathpazo}',
    'preamble': r'\usepackage{flaskstyle}',
}
# linkcheck ------------------------------------------------------------
linkcheck_anchors = False
# Local Extensions -----------------------------------------------------
_internal_mark_re = re.compile(r'^\s*:internal:\s*$(?m)', re.M)
def skip_internal(app, what, name, obj, skip, options):
def cut_module_meta(app, what, name, obj, options, lines):
def github_link(
    name, rawtext, text, lineno, inliner, options=None, content=None
):
def setup(app):
master_doc = 'index'

