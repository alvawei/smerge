# (c) 2013, Michael DeHaan <michael.dehaan@gmail.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# from python and deps
from cStringIO import StringIO
import inspect
import os
import shlex

# from Ansible
from ansible import errors
from ansible import utils
from ansible import constants as C

REPLACER = "#<<INCLUDE_ANSIBLE_MODULE_COMMON>>"
REPLACER_ARGS = "\"<<INCLUDE_ANSIBLE_MODULE_ARGS>>\""
REPLACER_LANG = "\"<<INCLUDE_ANSIBLE_MODULE_LANG>>\""
REPLACER_COMPLEX = "\"<<INCLUDE_ANSIBLE_MODULE_COMPLEX_ARGS>>\""

class ModuleReplacer(object):

    """
    The Replacer is used to insert chunks of code into modules before
    transfer.  Rather than doing classical python imports, this allows for more
    efficient transfer in a no-bootstrapping scenario by not moving extra files
    over the wire, and also takes care of embedding arguments in the transferred
    modules.  

    This version is done in such a way that local imports can still be
    used in the module code, so IDEs don't have to be aware of what is going on.

    Example:

    from ansible.module_utils.basic import * 

    will result in a template evaluation of

    {{ include 'basic.py' }} 

    from the module_utils/ directory in the source tree.

    All modules are required to import at least basic, though there will also
    be other snippets.
    """

    # ******************************************************************************

    def __init__(self, strip_comments=False):
        this_file = inspect.getfile(inspect.currentframe())
        self.snippet_path = os.path.join(os.path.dirname(this_file), 'module_utils')
        self.strip_comments = strip_comments # TODO: implement

    # ******************************************************************************


    def slurp(self, path):
        if not os.path.exists(path):
            raise errors.AnsibleError("imported module support code does not exist at %s" % path)
        fd = open(path)
        data = fd.read()
        fd.close()
        return data

    def _find_snippet_imports(self, module_data, module_path):
        """
        Given the source of the module, convert it to a Jinja2 template to insert
        module code and return whether it's a new or old style module.
        """

        module_style = 'old'
        if REPLACER in module_data:
            module_style = 'new'
        elif 'from ansible.snippets.' in module_data:
            module_style = 'new'
        elif 'WANT_JSON' in module_data:
            module_style = 'non_native_want_json'
      
        output = StringIO()
        lines = module_data.split('\n')
        snippet_names = []

        for line in lines:

            if line.find(REPLACER) != -1:
                output.write(self.slurp(os.path.join(self.snippet_path, "basic.py")))
                snippet_names.append('basic')
            elif line.startswith('from ansible.module_utils.'):
                tokens=line.split(".")
                import_error = False
                if len(tokens) != 3:
                    import_error = True
                if line.find(" import *") == -1:
                    import_error = True
                if import_error:
                    raise errors.AnsibleError("error importing module in %s, expecting format like 'from ansible.module_utils.basic import *'" % module_path)
                snippet_name = tokens[2].split()[0]
                snippet_names.append(snippet_name)
                output.write(self.slurp(os.path.join(self.snippet_path, snippet_name + ".py")))

            else:
                if self.strip_comments and line.startswith("#") or line == '':
                    pass
                output.write(line)
                output.write("\n")

        if len(snippet_names) > 0 and not 'basic' in snippet_names:
            raise errors.AnsibleError("missing required import in %s: from ansible.module_utils.basic import *" % module_path) 

        return (output.getvalue(), module_style)

    # ******************************************************************************

    def modify_module(self, module_path, complex_args, module_args, inject):

        with open(module_path) as f:

            # read in the module source
            module_data = f.read()

            (module_data, module_style) = self._find_snippet_imports(module_data, module_path)

            complex_args_json = utils.jsonify(complex_args)
            # We force conversion of module_args to str because module_common calls shlex.split,
            # a standard library function that incorrectly handles Unicode input before Python 2.7.3.
            encoded_args = repr(module_args.encode('utf-8'))
            encoded_lang = repr(C.DEFAULT_MODULE_LANG)
            encoded_complex = repr(complex_args_json)

            # these strings should be part of the 'basic' snippet which is required to be included
            module_data = module_data.replace(REPLACER_ARGS, encoded_args)
            module_data = module_data.replace(REPLACER_LANG, encoded_lang)
            module_data = module_data.replace(REPLACER_COMPLEX, encoded_complex)

            if module_style == 'new':
                facility = C.DEFAULT_SYSLOG_FACILITY
                if 'ansible_syslog_facility' in inject:
                    facility = inject['ansible_syslog_facility']
                module_data = module_data.replace('syslog.LOG_USER', "syslog.%s" % facility)


            lines = module_data.split("\n")
            shebang = None
            if lines[0].startswith("#!"):
                shebang = lines[0].strip()
                args = shlex.split(str(shebang[2:]))
                interpreter = args[0]
                interpreter_config = 'ansible_%s_interpreter' % os.path.basename(interpreter)

                if interpreter_config in inject:
                    lines[0] = shebang = "#!%s %s" % (inject[interpreter_config], " ".join(args[1:]))
                    module_data = "\n".join(lines)

            return (module_data, module_style, shebang)

<<<<<<< HEAD
=======
import os
import re
import shlex
import subprocess
import sys
import syslog
import types
import time
import shutil
import stat
import traceback
import grp
import pwd
import platform
import errno

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        sys.stderr.write('Error: ansible requires a json module, none found!')
        sys.exit(1)
    except SyntaxError:
        sys.stderr.write('SyntaxError: probably due to json and python being for different versions')
        sys.exit(1)

HAVE_SELINUX=False
try:
    import selinux
    HAVE_SELINUX=True
except ImportError:
    pass

HAVE_HASHLIB=False
try:
    from hashlib import md5 as _md5
    HAVE_HASHLIB=True
except ImportError:
    from md5 import md5 as _md5

try:
    from hashlib import sha256 as _sha256
except ImportError:
    pass

try:
  from systemd import journal
  has_journal = True
except ImportError:
  import syslog
  has_journal = False

FILE_COMMON_ARGUMENTS=dict(
    src = dict(),
    mode = dict(),
    owner = dict(),
    group = dict(),
    seuser = dict(),
    serole = dict(),
    selevel = dict(),
    setype = dict(),
    # not taken by the file module, but other modules call file so it must ignore them.
    content = dict(),
    backup = dict(),
    force = dict(),
)

def get_platform():
    ''' what's the platform?  example: Linux is a platform. '''
    return platform.system()

def get_distribution():
    ''' return the distribution name '''
    if platform.system() == 'Linux':
        try:
            distribution = platform.linux_distribution()[0].capitalize()
            if distribution == 'NA':
                if os.path.is_file('/etc/system-release'):
                    distribution = 'OtherLinux'
        except:
            # FIXME: MethodMissing, I assume?
            distribution = platform.dist()[0].capitalize()
    else:
        distribution = None
    return distribution

def load_platform_subclass(cls, *args, **kwargs):
    '''
    used by modules like User to have different implementations based on detected platform.  See User
    module for an example.
    '''

    this_platform = get_platform()
    distribution = get_distribution()
    subclass = None

    # get the most specific superclass for this platform
    if distribution is not None:
        for sc in cls.__subclasses__():
            if sc.distribution is not None and sc.distribution == distribution and sc.platform == this_platform:
                subclass = sc
    if subclass is None:
        for sc in cls.__subclasses__():
            if sc.platform == this_platform and sc.distribution is None:
                subclass = sc
    if subclass is None:
        subclass = cls

    return super(cls, subclass).__new__(subclass)


class AnsibleModule(object):

    def __init__(self, argument_spec, bypass_checks=False, no_log=False,
        check_invalid_arguments=True, mutually_exclusive=None, required_together=None,
        required_one_of=None, add_file_common_args=False, supports_check_mode=False):

        '''
        common code for quickly building an ansible module in Python
        (although you can write modules in anything that can return JSON)
        see library/* for examples
        '''

        self.argument_spec = argument_spec
        self.supports_check_mode = supports_check_mode
        self.check_mode = False
        
        self.aliases = {}
        
        if add_file_common_args:
            for k, v in FILE_COMMON_ARGUMENTS.iteritems():
                if k not in self.argument_spec:
                    self.argument_spec[k] = v

        os.environ['LANG'] = MODULE_LANG
        (self.params, self.args) = self._load_params()

        self._legal_inputs = [ 'CHECKMODE' ]
        
        self.aliases = self._handle_aliases()

        if check_invalid_arguments:
            self._check_invalid_arguments()
        self._check_for_check_mode()

        self._set_defaults(pre=True)

        if not bypass_checks:
            self._check_required_arguments()
            self._check_argument_values()
            self._check_argument_types()
            self._check_mutually_exclusive(mutually_exclusive)
            self._check_required_together(required_together)
            self._check_required_one_of(required_one_of)

        self._set_defaults(pre=False)
        if not no_log:
            self._log_invocation()

    def load_file_common_arguments(self, params):
        '''
        many modules deal with files, this encapsulates common
        options that the file module accepts such that it is directly
        available to all modules and they can share code.
        '''

        path = params.get('path', params.get('dest', None))
        if path is None:
            return {}
        else:
            path = os.path.expanduser(path)

        mode   = params.get('mode', None)
        owner  = params.get('owner', None)
        group  = params.get('group', None)

        # selinux related options
        seuser    = params.get('seuser', None)
        serole    = params.get('serole', None)
        setype    = params.get('setype', None)
        selevel   = params.get('selevel', None)
        secontext = [seuser, serole, setype]

        if self.selinux_mls_enabled():
            secontext.append(selevel)

        default_secontext = self.selinux_default_context(path)
        for i in range(len(default_secontext)):
            if i is not None and secontext[i] == '_default':
                secontext[i] = default_secontext[i]

        return dict(
            path=path, mode=mode, owner=owner, group=group,
            seuser=seuser, serole=serole, setype=setype,
            selevel=selevel, secontext=secontext,
        )


    # Detect whether using selinux that is MLS-aware.
    # While this means you can set the level/range with
    # selinux.lsetfilecon(), it may or may not mean that you
    # will get the selevel as part of the context returned
    # by selinux.lgetfilecon().

    def selinux_mls_enabled(self):
        if not HAVE_SELINUX:
            return False
        if selinux.is_selinux_mls_enabled() == 1:
            return True
        else:
            return False

    def selinux_enabled(self):
        if not HAVE_SELINUX:
            seenabled = self.get_bin_path('selinuxenabled')
            if seenabled is not None:
                (rc,out,err) = self.run_command(seenabled)
                if rc == 0:
                    self.fail_json(msg="Aborting, target uses selinux but python bindings (libselinux-python) aren't installed!")
            return False
        if selinux.is_selinux_enabled() == 1:
            return True
        else:
            return False

    # Determine whether we need a placeholder for selevel/mls
    def selinux_initial_context(self):
        context = [None, None, None]
        if self.selinux_mls_enabled():
            context.append(None)
        return context

    def _to_filesystem_str(self, path):
        '''Returns filesystem path as a str, if it wasn't already.

        Used in selinux interactions because it cannot accept unicode
        instances, and specifying complex args in a playbook leaves
        you with unicode instances.  This method currently assumes
        that your filesystem encoding is UTF-8.

        '''
        if isinstance(path, unicode):
            path = path.encode("utf-8")
        return path

    # If selinux fails to find a default, return an array of None
    def selinux_default_context(self, path, mode=0):
        context = self.selinux_initial_context()
        if not HAVE_SELINUX or not self.selinux_enabled():
            return context
        try:
            ret = selinux.matchpathcon(self._to_filesystem_str(path), mode)
        except OSError:
            return context
        if ret[0] == -1:
            return context
        # Limit split to 4 because the selevel, the last in the list,
        # may contain ':' characters
        context = ret[1].split(':', 3)
        return context

    def selinux_context(self, path):
        context = self.selinux_initial_context()
        if not HAVE_SELINUX or not self.selinux_enabled():
            return context
        try:
            ret = selinux.lgetfilecon_raw(self._to_filesystem_str(path))
        except OSError, e:
            if e.errno == errno.ENOENT:
                self.fail_json(path=path, msg='path %s does not exist' % path)
            else:
                self.fail_json(path=path, msg='failed to retrieve selinux context')
        if ret[0] == -1:
            return context
        # Limit split to 4 because the selevel, the last in the list,
        # may contain ':' characters
        context = ret[1].split(':', 3)
        return context

    def user_and_group(self, filename):
        filename = os.path.expanduser(filename)
        st = os.lstat(filename)
        uid = st.st_uid
        gid = st.st_gid
        return (uid, gid)

    def set_default_selinux_context(self, path, changed):
        if not HAVE_SELINUX or not self.selinux_enabled():
            return changed
        context = self.selinux_default_context(path)
        return self.set_context_if_different(path, context, False)

    def set_context_if_different(self, path, context, changed):

        if not HAVE_SELINUX or not self.selinux_enabled():
            return changed
        cur_context = self.selinux_context(path)
        new_context = list(cur_context)
        # Iterate over the current context instead of the
        # argument context, which may have selevel.

        for i in range(len(cur_context)):
            if context[i] is not None and context[i] != cur_context[i]:
                new_context[i] = context[i]
            if context[i] is None:
                new_context[i] = cur_context[i]
        if cur_context != new_context:
            try:
                if self.check_mode:
                    return True
                rc = selinux.lsetfilecon(self._to_filesystem_str(path),
                                         str(':'.join(new_context)))
            except OSError:
                self.fail_json(path=path, msg='invalid selinux context', new_context=new_context, cur_context=cur_context, input_was=context)
            if rc != 0:
                self.fail_json(path=path, msg='set selinux context failed')
            changed = True
        return changed

    def set_owner_if_different(self, path, owner, changed):
        path = os.path.expanduser(path)
        if owner is None:
            return changed
        orig_uid, orig_gid = self.user_and_group(path)
        try:
            uid = int(owner)
        except ValueError:
            try:
                uid = pwd.getpwnam(owner).pw_uid
            except KeyError:
                self.fail_json(path=path, msg='chown failed: failed to look up user %s' % owner)
        if orig_uid != uid:
            if self.check_mode:
                return True
            try:
                os.lchown(path, uid, -1)
            except OSError:
                self.fail_json(path=path, msg='chown failed')
            changed = True
        return changed

    def set_group_if_different(self, path, group, changed):
        path = os.path.expanduser(path)
        if group is None:
            return changed
        orig_uid, orig_gid = self.user_and_group(path)
        try:
            gid = int(group)
        except ValueError:
            try:
                gid = grp.getgrnam(group).gr_gid
            except KeyError:
                self.fail_json(path=path, msg='chgrp failed: failed to look up group %s' % group)
        if orig_gid != gid:
            if self.check_mode:
                return True
            try:
                os.lchown(path, -1, gid)
            except OSError:
                self.fail_json(path=path, msg='chgrp failed')
            changed = True
        return changed

    def set_mode_if_different(self, path, mode, changed):
        path = os.path.expanduser(path)
        if mode is None:
            return changed
        try:
            # FIXME: support English modes
            if not isinstance(mode, int):
                mode = int(mode, 8)
        except Exception, e:
            self.fail_json(path=path, msg='mode needs to be something octalish', details=str(e))

        st = os.lstat(path)
        prev_mode = stat.S_IMODE(st[stat.ST_MODE])

        if prev_mode != mode:
            if self.check_mode:
                return True
            # FIXME: comparison against string above will cause this to be executed
            # every time
            try:
                if 'lchmod' in dir(os):
                    os.lchmod(path, mode)
                else:
                    os.chmod(path, mode)
            except OSError, e:
                if os.path.islink(path) and e.errno == errno.EPERM:  # Can't set mode on symbolic links
                    pass
                elif e.errno == errno.ENOENT: # Can't set mode on broken symbolic links
                    pass
                else:
                    raise e
            except Exception, e:
                self.fail_json(path=path, msg='chmod failed', details=str(e))

            st = os.lstat(path)
            new_mode = stat.S_IMODE(st[stat.ST_MODE])

            if new_mode != prev_mode:
                changed = True
        return changed

    def set_file_attributes_if_different(self, file_args, changed):
        # set modes owners and context as needed
        changed = self.set_context_if_different(
            file_args['path'], file_args['secontext'], changed
        )
        changed = self.set_owner_if_different(
            file_args['path'], file_args['owner'], changed
        )
        changed = self.set_group_if_different(
            file_args['path'], file_args['group'], changed
        )
        changed = self.set_mode_if_different(
            file_args['path'], file_args['mode'], changed
        )
        return changed

    def set_directory_attributes_if_different(self, file_args, changed):
        changed = self.set_context_if_different(
            file_args['path'], file_args['secontext'], changed
        )
        changed = self.set_owner_if_different(
            file_args['path'], file_args['owner'], changed
        )
        changed = self.set_group_if_different(
            file_args['path'], file_args['group'], changed
        )
        changed = self.set_mode_if_different(
            file_args['path'], file_args['mode'], changed
        )
        return changed

    def add_path_info(self, kwargs):
        '''
        for results that are files, supplement the info about the file
        in the return path with stats about the file path.
        '''

        path = kwargs.get('path', kwargs.get('dest', None))
        if path is None:
            return kwargs
        if os.path.exists(path):
            (uid, gid) = self.user_and_group(path)
            kwargs['uid'] = uid
            kwargs['gid'] = gid
            try:
                user = pwd.getpwuid(uid)[0]
            except KeyError:
                user = str(uid)
            try:
                group = grp.getgrgid(gid)[0]
            except KeyError:
                group = str(gid)
            kwargs['owner'] = user
            kwargs['group'] = group
            st = os.lstat(path)
            kwargs['mode']  = oct(stat.S_IMODE(st[stat.ST_MODE]))
            # secontext not yet supported
            if os.path.islink(path):
                kwargs['state'] = 'link'
            elif os.path.isdir(path):
                kwargs['state'] = 'directory'
            else:
                kwargs['state'] = 'file'
            if HAVE_SELINUX and self.selinux_enabled():
                kwargs['secontext'] = ':'.join(self.selinux_context(path))
            kwargs['size'] = st[stat.ST_SIZE]
        else:
            kwargs['state'] = 'absent'
        return kwargs


    def _handle_aliases(self):
        aliases_results = {} #alias:canon
        for (k,v) in self.argument_spec.iteritems():
            self._legal_inputs.append(k)
            aliases = v.get('aliases', None)
            default = v.get('default', None)
            required = v.get('required', False)
            if default is not None and required:
                # not alias specific but this is a good place to check this
                self.fail_json(msg="internal error: required and default are mutally exclusive for %s" % k)
            if aliases is None:
                continue
            if type(aliases) != list:
                self.fail_json(msg='internal error: aliases must be a list')
            for alias in aliases:
                self._legal_inputs.append(alias)
                aliases_results[alias] = k
                if alias in self.params:
                    self.params[k] = self.params[alias]
        
        return aliases_results

    def _check_for_check_mode(self):
        for (k,v) in self.params.iteritems():
            if k == 'CHECKMODE':
                if not self.supports_check_mode:
                    self.exit_json(skipped=True, msg="remote module does not support check mode")
                if self.supports_check_mode:
                    self.check_mode = True

    def _check_invalid_arguments(self):
        for (k,v) in self.params.iteritems():
            if k == 'CHECKMODE':
                continue
            if k not in self._legal_inputs:
                self.fail_json(msg="unsupported parameter for module: %s" % k)

    def _count_terms(self, check):
        count = 0
        for term in check:
           if term in self.params:
               count += 1
        return count

    def _check_mutually_exclusive(self, spec):
        if spec is None:
            return
        for check in spec:
            count = self._count_terms(check)
            if count > 1:
                self.fail_json(msg="parameters are mutually exclusive: %s" % check)

    def _check_required_one_of(self, spec):
        if spec is None:
            return
        for check in spec:
            count = self._count_terms(check)
            if count == 0:
                self.fail_json(msg="one of the following is required: %s" % ','.join(check))

    def _check_required_together(self, spec):
        if spec is None:
            return
        for check in spec:
            counts = [ self._count_terms([field]) for field in check ]
            non_zero = [ c for c in counts if c > 0 ]
            if len(non_zero) > 0:
                if 0 in counts:
                    self.fail_json(msg="parameters are required together: %s" % check)

    def _check_required_arguments(self):
        ''' ensure all required arguments are present '''
        missing = []
        for (k,v) in self.argument_spec.iteritems():
            required = v.get('required', False)
            if required and k not in self.params:
                missing.append(k)
        if len(missing) > 0:
            self.fail_json(msg="missing required arguments: %s" % ",".join(missing))

    def _check_argument_values(self):
        ''' ensure all arguments have the requested values, and there are no stray arguments '''
        for (k,v) in self.argument_spec.iteritems():
            choices = v.get('choices',None)
            if choices is None:
                continue
            if type(choices) == list:
                if k in self.params:
                    if self.params[k] not in choices:
                        choices_str=",".join([str(c) for c in choices])
                        msg="value of %s must be one of: %s, got: %s" % (k, choices_str, self.params[k])
                        self.fail_json(msg=msg)
            else:
                self.fail_json(msg="internal error: do not know how to interpret argument_spec")

    def _check_argument_types(self):
        ''' ensure all arguments have the requested type '''
        for (k, v) in self.argument_spec.iteritems():
            wanted = v.get('type', None)
            if wanted is None:
                continue
            if k not in self.params:
                continue

            value = self.params[k]
            is_invalid = False

            if wanted == 'str':
                if not isinstance(value, basestring):
                    self.params[k] = str(value)
            elif wanted == 'list':
                if not isinstance(value, list):
                    if isinstance(value, basestring):
                        self.params[k] = value.split(",")
                    else:
                        is_invalid = True
            elif wanted == 'dict':
                if not isinstance(value, dict):
                    if isinstance(value, basestring):
                        self.params[k] = dict([x.split("=", 1) for x in value.split(",")])
                    else:
                        is_invalid = True
            elif wanted == 'bool':
                if not isinstance(value, bool):
                    if isinstance(value, basestring):
                        self.params[k] = self.boolean(value)
                    else:
                        is_invalid = True
            elif wanted == 'int':
                if not isinstance(value, int):
                    if isinstance(value, basestring):
                        self.params[k] = int(value)
                    else:
                        is_invalid = True
            else:
                self.fail_json(msg="implementation error: unknown type %s requested for %s" % (wanted, k))

            if is_invalid:
                self.fail_json(msg="argument %s is of invalid type: %s, required: %s" % (k, type(value), wanted))

    def _set_defaults(self, pre=True):
         for (k,v) in self.argument_spec.iteritems():
             default = v.get('default', None)
             if pre == True:
                 # this prevents setting defaults on required items
                 if default is not None and k not in self.params:
                     self.params[k] = default
             else:
                 # make sure things without a default still get set None
                 if k not in self.params:
                     self.params[k] = default

    def _load_params(self):
        ''' read the input and return a dictionary and the arguments string '''
        args = MODULE_ARGS
        items   = shlex.split(args)
        params = {}
        for x in items:
            try:
                (k, v) = x.split("=",1)
            except Exception, e:
                self.fail_json(msg="this module requires key=value arguments (%s)" % items)
            params[k] = v
        params2 = json.loads(MODULE_COMPLEX_ARGS)
        params2.update(params)
        return (params2, args)

    def _log_invocation(self):
        ''' log that ansible ran the module '''
        # TODO: generalize a separate log function and make log_invocation use it
        # Sanitize possible password argument when logging.
        log_args = dict()
        passwd_keys = ['password', 'login_password']
        
        for param in self.params:
            canon  = self.aliases.get(param, param)
            arg_opts = self.argument_spec.get(canon, {})
            no_log = arg_opts.get('no_log', False)
                
            if no_log:
                log_args[param] = 'NOT_LOGGING_PARAMETER'
            elif param in passwd_keys:
                log_args[param] = 'NOT_LOGGING_PASSWORD'
            else:
                log_args[param] = self.params[param]

        module = 'ansible-%s' % os.path.basename(__file__)
        msg = ''
        for arg in log_args:
            msg = msg + arg + '=' + str(log_args[arg]) + ' '
        if msg:
            msg = 'Invoked with %s' % msg
        else:
            msg = 'Invoked'

        if (has_journal):
            journal_args = ["MESSAGE=%s %s" % (module, msg)]
            journal_args.append("MODULE=%s" % os.path.basename(__file__))
            for arg in log_args:
                journal_args.append(arg.upper() + "=" + str(log_args[arg]))
            try:
                journal.sendv(*journal_args)
            except IOError, e:
                # fall back to syslog since logging to journal failed
                syslog.openlog(module, 0, syslog.LOG_USER)
                syslog.syslog(syslog.LOG_NOTICE, msg)
        else:
            syslog.openlog(module, 0, syslog.LOG_USER)
            syslog.syslog(syslog.LOG_NOTICE, msg)

    def get_bin_path(self, arg, required=False, opt_dirs=[]):
        '''
        find system executable in PATH.
        Optional arguments:
           - required:  if executable is not found and required is true, fail_json
           - opt_dirs:  optional list of directories to search in addition to PATH
        if found return full path; otherwise return None
        '''
        sbin_paths = ['/sbin', '/usr/sbin', '/usr/local/sbin']
        paths = []
        for d in opt_dirs:
            if d is not None and os.path.exists(d):
                paths.append(d)
        paths += os.environ.get('PATH', '').split(os.pathsep)
        bin_path = None
        # mangle PATH to include /sbin dirs
        for p in sbin_paths:
            if p not in paths and os.path.exists(p):
                paths.append(p)
        for d in paths:
            path = os.path.join(d, arg)
            if os.path.exists(path) and self.is_executable(path):
                bin_path = path
                break
        if required and bin_path is None:
            self.fail_json(msg='Failed to find required executable %s' % arg)
        return bin_path

    def boolean(self, arg):
        ''' return a bool for the arg '''
        if arg is None or type(arg) == bool:
            return arg
        if type(arg) in types.StringTypes:
            arg = arg.lower()
        if arg in BOOLEANS_TRUE:
            return True
        elif arg in BOOLEANS_FALSE:
            return False
        else:
            self.fail_json(msg='Boolean %s not in either boolean list' % arg)

    def jsonify(self, data):
        return json.dumps(data)

    def from_json(self, data):
        return json.loads(data)

    def exit_json(self, **kwargs):
        ''' return from the module, without error '''
        self.add_path_info(kwargs)
        if not kwargs.has_key('changed'):
            kwargs['changed'] = False
        print self.jsonify(kwargs)
        sys.exit(0)

    def fail_json(self, **kwargs):
        ''' return from the module, with an error message '''
        self.add_path_info(kwargs)
        assert 'msg' in kwargs, "implementation error -- msg to explain the error is required"
        kwargs['failed'] = True
        print self.jsonify(kwargs)
        sys.exit(1)

    def is_executable(self, path):
        '''is the given path executable?'''
        return (stat.S_IXUSR & os.stat(path)[stat.ST_MODE]
                or stat.S_IXGRP & os.stat(path)[stat.ST_MODE]
                or stat.S_IXOTH & os.stat(path)[stat.ST_MODE])

    def digest_from_file(self, filename, digest_method):
        ''' Return hex digest of local file for a given digest_method, or None if file is not present. '''
        if not os.path.exists(filename):
            return None
        if os.path.isdir(filename):
            self.fail_json(msg="attempted to take checksum of directory: %s" % filename)
        digest = digest_method
        blocksize = 64 * 1024
        infile = open(filename, 'rb')
        block = infile.read(blocksize)
        while block:
            digest.update(block)
            block = infile.read(blocksize)
        infile.close()
        return digest.hexdigest()

    def md5(self, filename):
        ''' Return MD5 hex digest of local file using digest_from_file(). '''
        return self.digest_from_file(filename, _md5())

    def sha256(self, filename):
        ''' Return SHA-256 hex digest of local file using digest_from_file(). '''
        if not HAVE_HASHLIB:
            self.fail_json(msg="SHA-256 checksums require hashlib, which is available in Python 2.5 and higher")
        return self.digest_from_file(filename, _sha256())

    def backup_local(self, fn):
        '''make a date-marked backup of the specified file, return True or False on success or failure'''
        # backups named basename-YYYY-MM-DD@HH:MM~
        ext = time.strftime("%Y-%m-%d@%H:%M~", time.localtime(time.time()))
        backupdest = '%s.%s' % (fn, ext)

        try:
            shutil.copy2(fn, backupdest)
        except shutil.Error, e:
            self.fail_json(msg='Could not make backup of %s to %s: %s' % (fn, backupdest, e))
        return backupdest

    def cleanup(self,tmpfile):
        if os.path.exists(tmpfile):
            try:
                os.unlink(tmpfile)
            except OSError, e:
                sys.stderr.write("could not cleanup %s: %s" % (tmpfile, e))

    def atomic_move(self, src, dest):
        '''atomically move src to dest, copying attributes from dest, returns true on success
        it uses os.rename to ensure this as it is an atomic operation, rest of the function is
        to work around limitations, corner cases and ensure selinux context is saved if possible'''
        context = None
        if os.path.exists(dest):
            try:
                st = os.stat(dest)
                os.chmod(src, st.st_mode & 07777)
                os.chown(src, st.st_uid, st.st_gid)
            except OSError, e:
                if e.errno != errno.EPERM:
                    raise
            if self.selinux_enabled():
                context = self.selinux_context(dest)
        else:
            if self.selinux_enabled():
                context = self.selinux_default_context(dest)

        try:
            # Optimistically try a rename, solves some corner cases and can avoid useless work.
            os.rename(src, dest)
        except (IOError,OSError), e:
            # only try workarounds for errno 18 (cross device), 1 (not permited) and 13 (permission denied)
            if e.errno != errno.EPERM and e.errno != errno.EXDEV and e.errno != errno.EACCES:
                self.fail_json(msg='Could not replace file: %s to %s: %s' % (src, dest, e))

            dest_dir = os.path.dirname(dest)
            dest_file = os.path.basename(dest)
            tmp_dest = "%s/.%s.%s.%s" % (dest_dir,dest_file,os.getpid(),time.time())

            try: # leaves tmp file behind when sudo and  not root
                if os.getenv("SUDO_USER") and os.getuid() != 0:
                   # cleanup will happen by 'rm' of tempdir
                   shutil.copy(src, tmp_dest)
                else:
                   shutil.move(src, tmp_dest)
                if self.selinux_enabled():
                    self.set_context_if_different(tmp_dest, context, False)
                os.rename(tmp_dest, dest)
            except (shutil.Error, OSError, IOError), e:
                self.cleanup(tmp_dest)
                self.fail_json(msg='Could not replace file: %s to %s: %s' % (src, dest, e))

        if self.selinux_enabled():
            # rename might not preserve context
            self.set_context_if_different(dest, context, False)

    def run_command(self, args, check_rc=False, close_fds=False, executable=None, data=None, binary_data=False, path_prefix=None):
        '''
        Execute a command, returns rc, stdout, and stderr.
        args is the command to run
        If args is a list, the command will be run with shell=False.
        Otherwise, the command will be run with shell=True when args is a string.
        Other arguments:
        - check_rc (boolean)  Whether to call fail_json in case of
                              non zero RC.  Default is False.
        - close_fds (boolean) See documentation for subprocess.Popen().
                              Default is False.
        - executable (string) See documentation for subprocess.Popen().
                              Default is None.
        '''
        if isinstance(args, list):
            shell = False
        elif isinstance(args, basestring):
            shell = True
        else:
            msg = "Argument 'args' to run_command must be list or string"
            self.fail_json(rc=257, cmd=args, msg=msg)
        rc = 0
        msg = None
        st_in = None
        env=os.environ
        if path_prefix:
            env['PATH']="%s:%s" % (path_prefix, env['PATH'])

        if data:
            st_in = subprocess.PIPE
        try:
            cmd = subprocess.Popen(args,
                                   executable=executable,
                                   shell=shell,
                                   close_fds=close_fds,
                                   stdin=st_in,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   env=env)
            if data:
                if not binary_data:
                    data += '\\n'
            out, err = cmd.communicate(input=data)
            rc = cmd.returncode
        except (OSError, IOError), e:
            self.fail_json(rc=e.errno, msg=str(e), cmd=args)
        except:
            self.fail_json(rc=257, msg=traceback.format_exc(), cmd=args)
        if rc != 0 and check_rc:
            msg = err.rstrip()
            self.fail_json(cmd=args, rc=rc, stdout=out, stderr=err, msg=msg)
        return (rc, out, err)

    def pretty_bytes(self,size):
        ranges = (
                (1<<70L, 'ZB'),
                (1<<60L, 'EB'),
                (1<<50L, 'PB'),
                (1<<40L, 'TB'),
                (1<<30L, 'GB'),
                (1<<20L, 'MB'),
                (1<<10L, 'KB'),
                (1, 'Bytes')
            )
        for limit, suffix in ranges:
            if size >= limit:
                break
        return '%.2f %s' % (float(size)/ limit, suffix)

# == END DYNAMICALLY INSERTED CODE ===

"""
>>>>>>> remote
