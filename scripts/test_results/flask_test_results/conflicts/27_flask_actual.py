# -*- coding: utf-8 -*-
"""
    flask
    ~~~~~

    A microframework based on Werkzeug.  It's extensively documented
    and follows best practice patterns.

    :copyright: (c) 2010 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import with_statement
import os
import sys
import types
from datetime import datetime, timedelta

from itertools import chain
from jinja2 import Environment, PackageLoader, FileSystemLoader
from werkzeug import Request as RequestBase, Response as ResponseBase, \
     LocalStack, LocalProxy, create_environ, SharedDataMiddleware, \
     ImmutableDict, cached_property
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException
from werkzeug.contrib.securecookie import SecureCookie

# try to load the best simplejson implementation available.  If JSON
# is not installed, we add a failing class.
json_available = True
try:
    import simplejson as json
except ImportError:
    try:
        import json
    except ImportError:
        json_available = False

# utilities we import from Werkzeug and Jinja2 that are unused
# in the module but are exported as public interface.
from werkzeug import abort, redirect
from jinja2 import Markup, escape

# use pkg_resource if that works, otherwise fall back to cwd.  The
# current working directory is generally not reliable with the notable
# exception of google appengine.
try:
    import pkg_resources
    pkg_resources.resource_stream
except (ImportError, AttributeError):
    pkg_resources = None


class Request(RequestBase):
    """The request object used by default in flask.  Remembers the
    matched endpoint and view arguments.

    It is what ends up as :class:`~flask.request`.  If you want to replace
    the request object used you can subclass this and set
    :attr:`~flask.Flask.request_class` to your subclass.
    """

    endpoint = view_args = routing_exception = None

    @property
    def module(self):
        """The name of the current module"""
        if self.endpoint and '.' in self.endpoint:
            return self.endpoint.rsplit('.', 1)[0]

    @cached_property
    def json(self):
        """If the mimetype is `application/json` this will contain the
        parsed JSON data.
        """
        if __debug__:
            _assert_have_json()
        if self.mimetype == 'application/json':
            return json.loads(self.data)


class Response(ResponseBase):
    """The response object that is used by default in flask.  Works like the
    response object from Werkzeug but is set to have a HTML mimetype by
    default.  Quite often you don't have to create this object yourself because
    :meth:`~flask.Flask.make_response` will take care of that for you.

    If you want to replace the response object used you can subclass this and
    set :attr:`~flask.Flask.request_class` to your subclass.
    """
    default_mimetype = 'text/html'


class _RequestGlobals(object):
    pass


class Session(SecureCookie):
    """Expands the session for support for switching between permanent
    and non-permanent sessions.
    """
    def _get_permanent(self):
        return self.get('_permanent', False)
    def _set_permanent(self, value):
        self['_permanent'] = bool(value)
    permanent = property(_get_permanent, _set_permanent)
    del _get_permanent, _set_permanent



class _NullSession(Session):
    """Class used to generate nicer error messages if sessions are not
    available.  Will still allow read-only access to the empty session
    but fail on setting.
    """
    def _fail(self, *args, **kwargs):
        raise RuntimeError('the session is unavailable because no secret '
                           'key was set.  Set the secret_key on the '
                           'application to something unique and secret')
    __setitem__ = __delitem__ = clear = pop = popitem = \
        update = setdefault = _fail
    del _fail



class _RequestContext(object):
    """The request context contains all request relevant information.  It is
    created at the beginning of the request and pushed to the
    `_request_ctx_stack` and removed at the end of it.  It will create the
    URL adapter and request object for the WSGI environment provided.
    """
    def __init__(self, app, environ):
        self.app = app
        self.url_adapter = app.url_map.bind_to_environ(environ)
        self.request = app.request_class(environ)
        self.session = app.open_session(self.request)
        if self.session is None:
            self.session = _NullSession()
        self.g = _RequestGlobals()
        self.flashes = None
    def __enter__(self):
        _request_ctx_stack.push(self)
    def __exit__(self, exc_type, exc_value, tb):
        # do not pop the request stack if we are in debug mode and an
        # exception happened.  This will allow the debugger to still
        # access the request object in the interactive shell.
        if tb is None or not self.app.debug:
            _request_ctx_stack.pop()





def url_for(endpoint, **values):
    external = values.pop('_external', False)
    return _request_ctx_stack.top.url_adapter.build(endpoint, values,
                                                    force_external=external)


def get_template_attribute(template_name, attribute):
    """Loads a macro (or variable) a template exports.  This can be used to
    invoke a macro from within Python code.  If you for example have a
    template named `_foo.html` with the following contents:

    .. sourcecode:: html+jinja

       {% macro hello(name) %}Hello {{ name }}!{% endmacro %}

    You can access this from Python code like this::

        hello = get_template_attribute('_foo.html', 'hello')
        return hello('World')

    .. versionadded:: 0.2

    :param template_name: the name of the template
    :param attribute: the name of the variable of macro to acccess
    """
    return getattr(current_app.jinja_env.get_template(template_name).module,
                   attribute)


def flash(message):
    """Flashes a message to the next request.  In order to remove the
    flashed message from the session and to display it to the user,
    the template has to call :func:`get_flashed_messages`.

    :param message: the message to be flashed.
    """
    session.setdefault('_flashes', []).append(message)


def get_flashed_messages():
    """Pulls all flashed messages from the session and returns them.
    Further calls in the same request to the function will return
    the same messages.
    """
    flashes = _request_ctx_stack.top.flashes
    if flashes is None:
        _request_ctx_stack.top.flashes = flashes = session.pop('_flashes', [])
    return flashes


def jsonify(*args, **kwargs):
    """Creates a :class:`~flask.Response` with the JSON representation of
    the given arguments with an `application/json` mimetype.  The arguments
    to this function are the same as to the :class:`dict` constructor.

    Example usage::

        @app.route('/_get_current_user')
        def get_current_user():
            return jsonify(username=g.user.username,
                           email=g.user.email,
                           id=g.user.id)

    This will send a JSON response like this to the browser::

        {
            "username": "admin",
            "email": "admin@localhost",
            "id": 42
        }

    This requires Python 2.6 or an installed version of simplejson.

    .. versionadded:: 0.2
    """
    if __debug__:
        _assert_have_json()
    return current_app.response_class(json.dumps(dict(*args, **kwargs),
        indent=None if request.is_xhr else 2), mimetype='application/json')


def render_template(template_name, **context):
    """Renders a template from the template folder with the given
    context.

    :param template_name: the name of the template to be rendered
    :param context: the variables that should be available in the
                    context of the template.
    """
    current_app.update_template_context(context)
    return current_app.jinja_env.get_template(template_name).render(context)


def render_template_string(source, **context):
    """Renders a template from the given template source string
    with the given context.

    :param template_name: the sourcecode of the template to be
                          rendered
    :param context: the variables that should be available in the
                    context of the template.
    """
    current_app.update_template_context(context)
    return current_app.jinja_env.from_string(source).render(context)


def _default_template_ctx_processor():
    """Default template context processor.  Injects `request`,
    `session` and `g`.
    """
    reqctx = _request_ctx_stack.top
    return dict(
        request=reqctx.request,
        session=reqctx.session,
        g=reqctx.g
    )


def _assert_have_json():
    """Helper function that fails if JSON is unavailable."""
    if not json_available:
        raise RuntimeError('simplejson not installed')


def _get_package_path(name):
    """Returns the path to a package or cwd if that cannot be found."""
    except (KeyError, AttributeError):
        return os.getcwd()


# figure out if simplejson escapes slashes.  This behaviour was changed
# from one version to another without reason.
if not json_available or '\\/' not in json.dumps('/'):
    def _tojson_filter(*args, **kwargs):
        if __debug__:
            _assert_have_json()
        return json.dumps(*args, **kwargs).replace('/', '\\/')

else:
    _tojson_filter = json.dumps













































# context locals
_request_ctx_stack = LocalStack()
current_app = LocalProxy(lambda: _request_ctx_stack.top.app)
request = LocalProxy(lambda: _request_ctx_stack.top.request)
session = LocalProxy(lambda: _request_ctx_stack.top.session)
g = LocalProxy(lambda: _request_ctx_stack.top.g)

