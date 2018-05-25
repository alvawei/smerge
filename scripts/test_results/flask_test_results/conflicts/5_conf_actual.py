# -*- coding: utf-8 -*-
from __future__ import print_function




extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
]




master_doc = 'index'

project = 'Flask'




















html_favicon = '_static/flask-favicon.ico'

html_static_path = ['_static']



html_sidebars = {
    'index': [
        'searchbox.html',
    ],
    '**': [
        'localtoc.html',
        'relations.html',
        'searchbox.html',
    ]
}



latex_documents = [
]
latex_use_modindex = False
latex_elements = {
    'fontpkg': r'\usepackage{mathpazo}',
    'papersize': 'a4paper',
    'pointsize': '12pt',
    'preamble': r'\usepackage{flaskstyle}',
}
latex_use_parts = True
latex_additional_files = ['flaskstyle.sty', 'logo.pdf']
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'werkzeug': ('http://werkzeug.pocoo.org/docs/', None),
    'click': ('http://click.pocoo.org/', None),
    'jinja': ('http://jinja.pocoo.org/docs/', None),
    'sqlalchemy': ('https://docs.sqlalchemy.org/en/latest/', None),
    'wtforms': ('https://wtforms.readthedocs.io/en/latest/', None),
    'blinker': ('https://pythonhosted.org/blinker/', None),
}
def unwrap_decorators():
    import sphinx.util.inspect as inspect
    import functools
    old_getargspec = inspect.getargspec
    def getargspec(x):
        return old_getargspec(getattr(x, '_original_function', x))
    inspect.getargspec = getargspec
    old_update_wrapper = functools.update_wrapper
    def update_wrapper(wrapper, wrapped, *a, **kw):
        rv = old_update_wrapper(wrapper, wrapped, *a, **kw)
        rv._original_function = wrapped
        return rv
    functools.update_wrapper = update_wrapper
unwrap_decorators()
del unwrap_decorators

