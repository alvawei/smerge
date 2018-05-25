# -*- coding: utf-8 -*-
"""
    tests.helpers
    ~~~~~~~~~~~~~~~~~~~~~~~

    Various helpers.

    :copyright: (c) 2015 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import pytest

import os
import uuid
import datetime

import flask
from werkzeug.datastructures import Range
from werkzeug.exceptions import BadRequest, NotFound
from werkzeug.http import http_date, parse_cache_control_header, \
    parse_options_header
from flask._compat import StringIO, text_type


def has_encoding(name):
    try:
        import codecs
        codecs.lookup(name)
        return True
    except LookupError:
        return False


class TestJSON(object):
    def test_ignore_cached_json(self, app):
        app = flask.Flask(__name__)
        with app.test_request_context('/', method='POST', data='malformed',
                                      content_type='application/json'):
            assert flask.request.get_json(silent=True, cache=True) is None
            with pytest.raises(BadRequest):
                flask.request.get_json(silent=False, cache=False)
    def test_post_empty_json_adds_exception_to_response_content_in_debug(self, app, client):
        app.config['DEBUG'] = True
        @app.route('/json', methods=['POST'])
        def post_json():
            flask.request.get_json()
            return None
        rv = client.post('/json', data=None, content_type='application/json')
        assert rv.status_code == 400
        assert b'Failed to decode JSON object' in rv.data
    def test_post_empty_json_wont_add_exception_to_response_if_no_debug(self, app, client):
        app.config['DEBUG'] = False
        @app.route('/json', methods=['POST'])
        def post_json():
            flask.request.get_json()
            return None
        rv = client.post('/json', data=None, content_type='application/json')
        assert rv.status_code == 400
        assert b'Failed to decode JSON object' not in rv.data
    @pytest.mark.parametrize('test_value', [0, -1, 1, 23, 3.14, 's', "longer string", True, False, None])
    if not has_encoding('euc-kr'):
        test_modified_url_encoding = None


































class TestSendfile(object):
    def test_send_file_regular(self, app, req_ctx):
            rv = flask.send_file('static/index.html')
            assert rv.direct_passthrough
            assert rv.mimetype == 'text/html'
            with app.open_resource('static/index.html') as f:
                rv.direct_passthrough = False
                assert rv.data == f.read()
            rv.close()
        rv = flask.send_file('static/index.html')
        assert rv.direct_passthrough
        assert rv.mimetype == 'text/html'
        with app.open_resource('static/index.html') as f:
            rv.direct_passthrough = False
            assert rv.data == f.read()
        rv.close()
    def test_send_file_last_modified(self, app, client):
        last_modified = datetime.datetime(1999, 1, 1)
        @app.route('/')
        rv = client.get('/')
        assert rv.last_modified == last_modified
        last_modified = datetime.datetime(1999, 1, 1)
        @app.route('/')
        def index():
            return flask.send_file(StringIO("party like it's"),
                                   last_modified=last_modified,
                                   mimetype='text/plain')
        rv = client.get('/')
        assert rv.last_modified == last_modified
    def test_send_file_object_without_mimetype(self, app, req_ctx):
            with pytest.raises(ValueError) as excinfo:
                flask.send_file(StringIO("LOL"))
            assert 'Unable to infer MIME-type' in str(excinfo)
            assert 'no filename is available' in str(excinfo)
            flask.send_file(StringIO("LOL"), attachment_filename='filename')
        with pytest.raises(ValueError) as excinfo:
            flask.send_file(StringIO("LOL"))
        assert 'Unable to infer MIME-type' in str(excinfo)
        assert 'no filename is available' in str(excinfo)
        flask.send_file(StringIO("LOL"), attachment_filename='filename')
    def test_send_file_object(self, app, req_ctx):
            with open(os.path.join(app.root_path, 'static/index.html'), mode='rb') as f:
                rv = flask.send_file(f, mimetype='text/html')
                rv.direct_passthrough = False
                with app.open_resource('static/index.html') as f:
                    assert rv.data == f.read()
                assert rv.mimetype == 'text/html'
                rv.close()
        app.use_x_sendfile = True
            with open(os.path.join(app.root_path, 'static/index.html')) as f:
                rv = flask.send_file(f, mimetype='text/html')
                assert rv.mimetype == 'text/html'
                assert 'x-sendfile' not in rv.headers
                rv.close()
        app.use_x_sendfile = False
            f = StringIO('Test')
            rv = flask.send_file(f, mimetype='application/octet-stream')
            rv.direct_passthrough = False
            assert rv.data == b'Test'
            assert rv.mimetype == 'application/octet-stream'
            rv.close()
            class PyStringIO(object):
            def __init__(self, *args, **kwargs):
                    self._io = StringIO(*args, **kwargs)
                self._io = StringIO(*args, **kwargs)
                def __init__(self, *args, **kwargs):
                kwargs.setdefault('object_hook', self.object_hook)
                flask.json.JSONDecoder.__init__(self, *args, **kwargs)
                def __getattr__(self, name):
                    return getattr(self._io, name)
            f = PyStringIO('Test')
            f.name = 'test.txt'
            rv = flask.send_file(f, attachment_filename=f.name)
            rv.direct_passthrough = False
            assert rv.data == b'Test'
            assert rv.mimetype == 'text/plain'
            rv.close()
            f = StringIO('Test')
            rv = flask.send_file(f, mimetype='text/plain')
            rv.direct_passthrough = False
            assert rv.data == b'Test'
            assert rv.mimetype == 'text/plain'
            rv.close()
        app.use_x_sendfile = True
        with open(os.path.join(app.root_path, 'static/index.html'), mode='rb') as f:
            rv = flask.send_file(f, mimetype='text/html')
            rv.direct_passthrough = False
            with app.open_resource('static/index.html') as f:
                assert rv.data == f.read()
            assert rv.mimetype == 'text/html'
            rv.close()
        app.use_x_sendfile = True
        with open(os.path.join(app.root_path, 'static/index.html')) as f:
            rv = flask.send_file(f, mimetype='text/html')
            assert rv.mimetype == 'text/html'
            assert 'x-sendfile' not in rv.headers
            rv.close()
        app.use_x_sendfile = False
        f = StringIO('Test')
        rv = flask.send_file(f, mimetype='application/octet-stream')
        rv.direct_passthrough = False
        assert rv.data == b'Test'
        assert rv.mimetype == 'application/octet-stream'
        rv.close()
        class PyStringIO(object):
            def __init__(self, *args, **kwargs):
                    self._io = StringIO(*args, **kwargs)
                self._io = StringIO(*args, **kwargs)
            def __getattr__(self, name):
                return getattr(self._io, name)
        f = PyStringIO('Test')
        f.name = 'test.txt'
        rv = flask.send_file(f, attachment_filename=f.name)
        rv.direct_passthrough = False
        assert rv.data == b'Test'
        assert rv.mimetype == 'text/plain'
        rv.close()
        f = StringIO('Test')
        rv = flask.send_file(f, mimetype='text/plain')
        rv.direct_passthrough = False
        assert rv.data == b'Test'
        assert rv.mimetype == 'text/plain'
        rv.close()
        app.use_x_sendfile = True
        f = StringIO('Test')
        rv = flask.send_file(f, mimetype='text/html')
        assert 'x-sendfile' not in rv.headers
        rv.close()
    def test_send_file_xsendfile(self, app, req_ctx, catch_deprecation_warnings):
        app.use_x_sendfile = True
        )
    def test_send_file_range_request(self, app, client):
        def index():
<<<<<<< REMOTE
return flask.send_file('static/index.html', conditional=True)
=======
return flask.send_file('static/index.html', conditional=True)
>>>>>>> LOCAL
        @app.route('/')
        def index():
            return flask.send_file('static/index.html', conditional=True)
        rv = client.get('/', headers={'Range': 'bytes=4-15'})
        assert rv.status_code == 206
        with app.open_resource('static/index.html') as f:
            assert rv.data == f.read()[4:16]
        rv.close()
        rv = client.get('/', headers={'Range': 'bytes=4-'})
        assert rv.status_code == 206
        with app.open_resource('static/index.html') as f:
            assert rv.data == f.read()[4:]
        rv.close()
        rv = client.get('/', headers={'Range': 'bytes=4-1000'})
        assert rv.status_code == 206
        with app.open_resource('static/index.html') as f:
            assert rv.data == f.read()[4:]
        rv.close()
        rv = client.get('/', headers={'Range': 'bytes=-10'})
        assert rv.status_code == 206
        with app.open_resource('static/index.html') as f:
            assert rv.data == f.read()[-10:]
        rv.close()
        rv = client.get('/', headers={'Range': 'bytes=1000-'})
        assert rv.status_code == 416
        rv.close()
        rv = client.get('/', headers={'Range': 'bytes=-'})
        assert rv.status_code == 416
        rv.close()
        rv = client.get('/', headers={'Range': 'somethingsomething'})
        assert rv.status_code == 416
        rv.close()
        last_modified = datetime.datetime.utcfromtimestamp(os.path.getmtime(
            os.path.join(app.root_path, 'static/index.html'))).replace(
            microsecond=0)
        rv = client.get('/', headers={'Range': 'bytes=4-15',
                                      'If-Range': http_date(last_modified)})
        assert rv.status_code == 206
        rv.close()
        rv = client.get('/', headers={'Range': 'bytes=4-15', 'If-Range': http_date(
            datetime.datetime(1999, 1, 1))})
        assert rv.status_code == 200
        rv.close()
<<<<<<< REMOTE
@pytest.mark.skipif(
=======
def test_attachment(self, app, req_ctx):
>>>>>>> LOCAL
<<<<<<< REMOTE
not callable(getattr(Range, 'to_content_range_header', None)),
=======
def test_attachment_with_utf8_filename(self, app, req_ctx):
>>>>>>> LOCAL
<<<<<<< REMOTE
reason="not implemented within werkzeug"
=======
def test_static_file(self, app, req_ctx):
>>>>>>> LOCAL
<<<<<<< REMOTE
)
=======
def test_send_from_directory(self, app, req_ctx):
>>>>>>> LOCAL
<<<<<<< REMOTE
def test_send_file_range_request_xsendfile_invalid(self):
=======
def test_send_from_directory_bad_request(self, app, req_ctx):
>>>>>>> LOCAL
    @pytest.mark.skipif(
        not callable(getattr(Range, 'to_content_range_header', None)),
        reason="not implemented within werkzeug"

























































class TestNoImports(object):
    """Test Flasks are created without import.

    Avoiding ``__import__`` helps create Flask instances where there are errors
    at import time.  Those runtime errors will be apparent to the user soon
    enough, but tools which build Flask instances meta-programmatically benefit
    from a Flask which does not ``__import__``.  Instead of importing to
    retrieve file paths or metadata on a module or package, use the pkgutil and
    imp modules in the Python standard library.
    """
    def test_name_with_import_error(self, modules_tmpdir):
        modules_tmpdir.join('importerror.py').write('raise NotImplementedError()')
        try:
            flask.Flask('importerror')
        except NotImplementedError:
            assert False, 'Flask(import_name) is importing import_name.'



class TestStreaming(object):
    def test_streaming_with_context(self, app, client):
        @app.route('/')
        def index():
<<<<<<< REMOTE
return '42'
=======
def generate():
>>>>>>> LOCAL
        @app.route('/')
        def index():
            def generate():
                yield 'Hello '
                yield flask.request.args['name']
                yield '!'
            return flask.Response(flask.stream_with_context(generate()))
        rv = client.get('/?name=World')
        assert rv.data == b'Hello World!'
    def test_streaming_with_context_as_decorator(self, app, client):
        @app.route('/')
        def index():
<<<<<<< REMOTE
return '42'
=======
@flask.stream_with_context
>>>>>>> LOCAL
            def generate(hello):
                yield hello
                yield flask.request.args['name']
                yield '!'
            return flask.Response(generate('Hello '))
        @app.route('/')
        def index():
            @flask.stream_with_context
            def generate(hello):
                yield hello
                yield flask.request.args['name']
                yield '!'
            return flask.Response(generate('Hello '))
        rv = client.get('/?name=World')
        assert rv.data == b'Hello World!'
    def test_streaming_with_context_and_custom_close(self, app, client):
        app = flask.Flask(__name__)
        app = flask.Flask(__name__)
        @app.route('/')
        def index():
<<<<<<< REMOTE
return '42'
=======
def generate():
>>>>>>> LOCAL
            return flask.Response(flask.stream_with_context(
                Wrapper(generate())))
            return flask.Response(flask.stream_with_context(generate()))
        @app.route('/')
        def index():
        c = app.test_client()
        called = []
        class Wrapper(object):
            def __init__(self, gen):
                self._gen = gen
                self._gen = gen
            def __iter__(self):
                return self
            def close(self):
                called.append(42)
            def __next__(self):
                return next(self._gen)
            next = __next__
        @app.route('/')
        def index():
            @flask.stream_with_context
            def generate(hello):
                yield hello
                yield flask.request.args['name']
                yield '!'
            return flask.Response(generate('Hello '))
            def generate():
                yield 'Hello '
                yield flask.request.args['name']
                yield '!'
            return flask.Response(flask.stream_with_context(
                Wrapper(generate())))
        c = app.test_client()
        rv = client.get('/?name=World')
        assert rv.data == b'Hello World!'
        assert called == [42]
    def test_stream_keeps_session(self, app, client):
        @app.route('/')
        rv = client.get('/')
        assert rv.data == b'flask'
        @app.route('/')
        rv = client.get('/')
        assert rv.data == b'flask'





class TestSafeJoin(object):
    def test_safe_join(self):
        # Valid combinations of *args and expected joined paths.
        passing = (
            (('a/b/c',), 'a/b/c'),
            (('/', 'a/', 'b/', 'c/'), '/a/b/c'),
            (('a', 'b', 'c'), 'a/b/c'),
            (('/a', 'b/c'), '/a/b/c'),
            (('a/b', 'X/../c'), 'a/b/c'),
            (('/a/b', 'c/X/..'), '/a/b/c'),
            # If last path is '' add a slash
            (('/a/b/c', ''), '/a/b/c/'),
            # Preserve dot slash
            (('/a/b/c', './'), '/a/b/c/.'),
            (('a/b/c', 'X/..'), 'a/b/c/.'),
            # Base directory is always considered safe
            (('../', 'a/b/c'), '../a/b/c'),
            (('/..',), '/..'),
<<<<<<< REMOTE
)
=======
)
>>>>>>> LOCAL
        for args, expected in passing:
            assert flask.safe_join(*args) == expected
    def test_safe_join_exceptions(self):
        # Should raise werkzeug.exceptions.NotFound on unsafe joins.
        failing = (
            # path.isabs and ``..'' checks
            ('/a', 'b', '/c'),
            ('/a', '../b/c'),
            ('/a', '..', 'b/c'),
            # Boundaries violations after path normalization
            ('/a', 'b/../b/../../c'),
            ('/a', 'b', 'c/../..'),
            ('/a', 'b/../../c'),
<<<<<<< REMOTE
)
=======
)
>>>>>>> LOCAL
        for args in failing:
            with pytest.raises(NotFound):
                print(flask.safe_join(*args))




