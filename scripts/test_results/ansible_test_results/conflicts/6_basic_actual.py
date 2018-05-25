# This code is part of Ansible, but is an independent component.
# This particular file snippet, and this file snippet only, is BSD licensed.
# Modules you write using this snippet, which is embedded dynamically by Ansible
# still belong to the author of the module, and may assign their own license
# to the complete work.
#
# Copyright (c), Michael DeHaan <michael.dehaan@gmail.com>, 2012-2013
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice,
#      this list of conditions and the following disclaimer in the documentation
#      and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# == BEGIN DYNAMICALLY INSERTED CODE ==

ANSIBLE_VERSION = "<<ANSIBLE_VERSION>>"

MODULE_ARGS = "<<INCLUDE_ANSIBLE_MODULE_ARGS>>"
MODULE_COMPLEX_ARGS = "<<INCLUDE_ANSIBLE_MODULE_COMPLEX_ARGS>>"

BOOLEANS_TRUE = ['yes', 'on', '1', 'true', 1]
BOOLEANS_FALSE = ['no', 'off', '0', 'false', 0]
BOOLEANS = BOOLEANS_TRUE + BOOLEANS_FALSE

# ansible modules can be written in any language.  To simplify
# development of Python modules, the functions available here
# can be inserted in any module source automatically by including
# #<<INCLUDE_ANSIBLE_MODULE_COMMON>> on a blank line by itself inside
# of an ansible module. The source of this common code lives

import locale
import os
import re
import pipes
import shlex
import subprocess
import sys
import types
import time
import select
import shutil
import stat
import tempfile
import traceback
import grp
import pwd
import platform
import errno

try:
import syslog
    HAS_SYSLOG=True
except ImportError:
    HAS_SYSLOG=False

HAVE_SELINUX=False
try:
except ImportError:

try:
except ImportError:

try:
    # Python 2.6+
    bytes

try:
    dict.iteritems
except ImportError:
    pass

try:
except ImportError:
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
    content = dict(no_log=True),
    backup = dict(),
    force = dict(),
    remote_src = dict(), # used by assemble
    regexp = dict(), # used by assemble
    delimiter = dict(), # used by assemble
    directory_mode = dict(), # used by copy
)


def get_platform():
    ''' what's the platform?  example: Linux is a platform. '''
    return platform.system()

def get_distribution():
    ''' return the distribution name '''
    if platform.system() == 'Linux':
        except:
            # FIXME: MethodMissing, I assume?
            distribution = platform.dist()[0].capitalize()
    return distribution

def get_distribution_version():
    ''' return the distribution version '''
    if platform.system() == 'Linux':
        except:
            # FIXME: MethodMissing, I assume?
            distribution_version = platform.dist()[1]
    return distribution_version

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
        required_one_of=None, add_file_common_args=False, supports_check_mode=False,
        required_if=None):
        '''
        common code for quickly building an ansible module in Python
        (although you can write modules in anything that can return JSON)
        see library/* for examples
        '''
        self.argument_spec = argument_spec
        self.supports_check_mode = supports_check_mode
        self.check_mode = False
        self.no_log = no_log
        self.cleanup_files = []
        self._debug = False
        self.aliases = {}
        if add_file_common_args:
            for k, v in FILE_COMMON_ARGUMENTS.items():
                if k not in self.argument_spec:
                    self.argument_spec[k] = v
        self.params = self._load_params()
        # Save parameter values that should never be logged
        self.no_log_values = set()
        # Use the argspec to determine which args are no_log
        for arg_name, arg_opts in self.argument_spec.items():
            if arg_opts.get('no_log', False):
                # Find the value for the no_log'd param
                no_log_object = self.params.get(arg_name, None)
                if no_log_object:
                    self.no_log_values.update(return_values(no_log_object))
                    self.no_log_values.update(return_values(no_log_object))
                # Find the value for the no_log'd param
                no_log_object = self.params.get(arg_name, None)
                if no_log_object:
                    self.no_log_values.update(return_values(no_log_object))
                    self.no_log_values.update(return_values(no_log_object))
            if arg_opts.get('no_log', False):
                # Find the value for the no_log'd param
                no_log_object = self.params.get(arg_name, None)
                if no_log_object:
                    self.no_log_values.update(return_values(no_log_object))
                    self.no_log_values.update(return_values(no_log_object))
                # Find the value for the no_log'd param
                no_log_object = self.params.get(arg_name, None)
                if no_log_object:
                    self.no_log_values.update(return_values(no_log_object))
                    self.no_log_values.update(return_values(no_log_object))
        # check the locale as set by the current environment, and
        # reset to LANG=C if it's an invalid/unavailable locale
        self._check_locale()
        self._legal_inputs = ['_ansible_check_mode', '_ansible_no_log', '_ansible_debug']
        # append to legal_inputs and then possibly check against them
        self.aliases = self._handle_aliases()
        self._check_arguments(check_invalid_arguments)
        # check exclusive early
        if not bypass_checks:
            self._check_mutually_exclusive(mutually_exclusive)
        self._set_defaults(pre=True)
        self._CHECK_ARGUMENT_TYPES_DISPATCHER = {
                'str': self._check_type_str,
                'list': self._check_type_list,
                'dict': self._check_type_dict,
                'bool': self._check_type_bool,
                'int': self._check_type_int,
                'float': self._check_type_float,
                'path': self._check_type_path,
            }
        if not bypass_checks:
            self._check_required_arguments()
            self._check_argument_values()
            self._check_argument_types()
            self._check_required_together(required_together)
            self._check_required_one_of(required_one_of)
            self._check_required_if(required_if)
        self._set_defaults(pre=False)
        if not self.no_log:
            self._log_invocation()
        # finally, make sure we're in a sane working dir
        self._set_cwd()
    def load_file_common_arguments(self, params):
        '''
        many modules deal with files, this encapsulates common
        options that the file module accepts such that it is directly
        available to all modules and they can share code.
        '''
        path = params.get('path', params.get('dest', None))
        if path is None:
            return {}
        # if the path is a symlink, and we're following links, get
        # the target of the link instead for testing
        if params.get('follow', False) and os.path.islink(path):
            path = os.path.realpath(path)
            path = os.path.realpath(path)
        else:
        distribution_version = None
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
    return value
        if selinux.is_selinux_mls_enabled() == 1:
            return True
    def selinux_enabled(self):
        if not HAVE_SELINUX:
            seenabled = self.get_bin_path('selinuxenabled')
            if seenabled is not None:
                (rc,out,err) = self.run_command(seenabled)
                if rc == 0:
                    self.fail_json(msg="Aborting, target uses selinux but python bindings (libselinux-python) aren't installed!")
        if selinux.is_selinux_enabled() == 1:
            return True
        else:
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
        if not isinstance(json.loads, types.FunctionType) or not isinstance(json.dumps, types.FunctionType):
            raise ImportError
            raise ImportError
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
                user = pwd.getpwuid(uid)[0]
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
    def find_mount_point(self, path):
        path = os.path.abspath(os.path.expanduser(os.path.expandvars(path)))
        while not os.path.ismount(path):
            path = os.path.dirname(path)
        return path
    def is_special_selinux_path(self, path):
        NFS or other 'special' fs  mount point, otherwise the return will be (False, None).
        """
        Returns a tuple containing (True, selinux_context) if the given path is on a
        NFS or other 'special' fs  mount point, otherwise the return will be (False, None).
        """
        try:
            f = open('/proc/mounts', 'r')
            mount_data = f.readlines()
            f.close()
        except:
            return (False, None)
        path_mount_point = self.find_mount_point(path)
        for line in mount_data:
            (device, mount_point, fstype, options, rest) = line.split(' ', 4)
            if path_mount_point == mount_point:
                for fs in SELINUX_SPECIAL_FS.split(','):
                    if fs in fstype:
                        return (True, special_context)
                        special_context = self.selinux_context(path_mount_point)
                        return (True, special_context)
                    if fs in fstype:
                        return (True, special_context)
                        special_context = self.selinux_context(path_mount_point)
                        return (True, special_context)
                for fs in SELINUX_SPECIAL_FS.split(','):
                    if fs in fstype:
                        return (True, special_context)
                        special_context = self.selinux_context(path_mount_point)
                        return (True, special_context)
                    if fs in fstype:
                        return (True, special_context)
                        special_context = self.selinux_context(path_mount_point)
                        return (True, special_context)
        return (False, None)
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
        (is_special_se, sp_context) = self.is_special_selinux_path(path)
        if is_special_se:
            new_context = sp_context
            else:
        else:
        raise TypeError('Value of unknown type: %s, %s' % (type(value), value))
            for i in range(len(cur_context)):
                if len(context) > i:
                    if context[i] is not None and context[i] != cur_context[i]:
                        new_context[i] = context[i]
                    elif context[i] is None:
                        new_context[i] = cur_context[i]
        if cur_context != new_context:
        try:
            # setting the locale to '' uses the default locale
            # as it would be returned by locale.getdefaultlocale()
            locale.setlocale(locale.LC_ALL, '')
            except OSError:
            e = get_exception()
            if e.errno == errno.ENOENT:
                self.fail_json(path=path, msg='path %s does not exist' % path)
        else:
            }
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
            result = None
            if not locals:
                result = _literal_eval(str)
            if include_exceptions:
                return (result, None)
        except ValueError:
            try:
                uid = pwd.getpwnam(owner).pw_uid
            except KeyError:
                self.fail_json(path=path, msg='chown failed: failed to look up user %s' % owner)
        if orig_uid != uid:
            if self.check_mode:
                return True
            try:
            except OSError:
                e = get_exception()
                self.fail_json(path=path, msg='invalid selinux context: %s' % str(e), new_context=new_context, cur_context=cur_context, input_was=context)
            changed = True
        return changed
    def set_group_if_different(self, path, group, changed):
        path = os.path.expanduser(path)
        if group is None:
            return changed
        orig_uid, orig_gid = self.user_and_group(path)
            try:
        except ValueError:
            try:
                gid = grp.getgrnam(group).gr_gid
            except KeyError:
                self.fail_json(path=path, msg='chgrp failed: failed to look up group %s' % group)
        if orig_gid != gid:
            if self.check_mode:
                return True
                try:
        except OSError:
            # not having a tty can cause the above to fail, so
            # just get the LOGNAME environment variable instead
            login_name = os.environ.get('LOGNAME', None)
            try:
                end = data.rindex('@', 0, begin)
                os.lchown(path, -1, gid)
            except OSError:
                self.fail_json(path=path, msg='chown failed')
                self.fail_json(path=path, msg='chgrp failed')
            changed = True
        return changed
    def set_mode_if_different(self, path, mode, changed):
        path = os.path.expanduser(path)
        path_stat = os.lstat(path)
        if mode is None:
            return changed
        if not isinstance(mode, int):
            try:
            try:
                    begin = data.rindex('://', 0, sep_search_end)
                mode = int(mode, 8)
            except Exception:
        try:
                try:
                    sep = data.index(':', begin + 3, end)
                    mode = self._symbolic_mode_to_octal(path_stat, mode)
                except Exception:
                    e = get_exception()
                    self.fail_json(path=path,
                                   msg="mode must be in octal or symbolic form",
                                   details=str(e))
        prev_mode = stat.S_IMODE(path_stat.st_mode)
        if prev_mode != mode:
            if self.check_mode:
                return True
            # FIXME: comparison against string above will cause this to be executed
            # every time
                try:
                if hasattr(os, 'lchmod'):
                    os.lchmod(path, mode)
        else:
                    if not os.path.islink(path):
                kwargs['state'] = 'link'
            except OSError:
                e = get_exception()
            else:
            else:
        raise TypeError('Unknown parameter type: %s, %s' % (type(obj), obj))
                self.fail_json(path=path, msg='failed to retrieve selinux context')
            try:
            ret = selinux.matchpathcon(self._to_filesystem_str(path), mode)
                else:
            path = os.path.expanduser(path)
                    os.chmod(path, mode)
            except OSError:
                e = get_exception()
                sys.stderr.write("could not cleanup %s: %s" % (tmpfile, e))
                if os.path.islink(path) and e.errno == errno.EPERM:  # Can't set mode on symbolic links
                    pass
                elif e.errno in (errno.ENOENT, errno.ELOOP): # Can't set mode on broken symbolic links
                    pass
            except Exception:
                e = get_exception()
                self.fail_json(path=path, msg='chmod failed', details=str(e))
            path_stat = os.lstat(path)
            new_mode = stat.S_IMODE(path_stat.st_mode)
            if new_mode != prev_mode:
                changed = True
        return changed
    def _symbolic_mode_to_octal(self, path_stat, symbolic_mode):
        new_mode = stat.S_IMODE(path_stat.st_mode)
        mode_re = re.compile(r'^(?P<users>[ugoa]+)(?P<operator>[-+=])(?P<perms>[rwxXst]*|[ugo])$')
        for mode in symbolic_mode.split(','):
            match = mode_re.match(mode)
            if match:
                users = match.group('users')
                operator = match.group('operator')
                perms = match.group('perms')
                if users == 'a':
                    users = 'ugo'
                    users = 'ugo'
                for user in users:
                    mode_to_apply = self._get_octal_mode_from_symbolic_perms(path_stat, user, perms)
                    new_mode = self._apply_operation_to_mode(user, operator, mode_to_apply, new_mode)
            else:
                raise ValueError("bad symbolic permission for mode: %s" % mode)
        return new_mode
    def _apply_operation_to_mode(self, user, operator, mode_to_apply, current_mode):
        if operator  ==  '=':
            if user == 'u': mask = stat.S_IRWXU | stat.S_ISUID
            elif user == 'g': mask = stat.S_IRWXG | stat.S_ISGID
            elif user == 'o': mask = stat.S_IRWXO | stat.S_ISVTX
            # mask out u, g, or o permissions from current_mode and apply new permissions
            inverse_mask = mask ^ PERM_BITS
            new_mode = (current_mode & inverse_mask) | mode_to_apply
        elif operator == '+':
            new_mode = current_mode | mode_to_apply
        elif operator == '-':
            new_mode = current_mode - (current_mode & mode_to_apply)
        return new_mode
    def _get_octal_mode_from_symbolic_perms(self, path_stat, user, perms):
        prev_mode = stat.S_IMODE(path_stat.st_mode)
        is_directory = stat.S_ISDIR(path_stat.st_mode)
        has_x_permissions = (prev_mode & EXEC_PERM_BITS) > 0
        apply_X_permission = is_directory or has_x_permissions
        # Permission bits constants documented at:
        # http://docs.python.org/2/library/stat.html#stat.S_ISUID
        if apply_X_permission:
            X_perms = {
                'u': {'X': stat.S_IXUSR},
                'g': {'X': stat.S_IXGRP},
                'o': {'X': stat.S_IXOTH}
        user_perms_to_modes = {
            'u': {
                'r': stat.S_IRUSR,
                'w': stat.S_IWUSR,
                'x': stat.S_IXUSR,
                's': stat.S_ISUID,
                't': 0,
                'u': prev_mode & stat.S_IRWXU,
                'g': (prev_mode & stat.S_IRWXG) << 3,
                'o': (prev_mode & stat.S_IRWXO) << 6 },
            'g': {
                'r': stat.S_IRGRP,
                'w': stat.S_IWGRP,
                'x': stat.S_IXGRP,
                's': stat.S_ISGID,
                't': 0,
                'u': (prev_mode & stat.S_IRWXU) >> 3,
                'g': prev_mode & stat.S_IRWXG,
                'o': (prev_mode & stat.S_IRWXO) << 3 },
            'o': {
                'r': stat.S_IROTH,
                'w': stat.S_IWOTH,
                'x': stat.S_IXOTH,
                's': 0,
                't': stat.S_ISVTX,
                'u': (prev_mode & stat.S_IRWXU) >> 6,
                'g': (prev_mode & stat.S_IRWXG) >> 3,
                'o': prev_mode & stat.S_IRWXO }
        }
        # Insert X_perms into user_perms_to_modes
        for key, value in X_perms.items():
            user_perms_to_modes[key].update(value)
        or_reduce = lambda mode, perm: mode | user_perms_to_modes[user][perm]
        return reduce(or_reduce, perms, 0)
    def set_fs_attributes_if_different(self, file_args, changed):
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
        return self.set_fs_attributes_if_different(file_args, changed)
    def set_file_attributes_if_different(self, file_args, changed):
        return self.set_fs_attributes_if_different(file_args, changed)
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
            except KeyError:
                user = str(uid)
        try:
            try:
                group = grp.getgrgid(gid)[0]
            except KeyError:
                group = str(gid)
            kwargs['owner'] = user
            kwargs['group'] = group
            st = os.lstat(path)
            kwargs['mode']  = oct(stat.S_IMODE(st[stat.ST_MODE]))
            if os.path.islink(path):
                kwargs['state'] = 'link'
            # secontext not yet supported
            elif os.path.isdir(path):
                kwargs['state'] = 'directory'
            elif os.stat(path).st_nlink > 1:
                kwargs['state'] = 'hard'
            if HAVE_SELINUX and self.selinux_enabled():
                kwargs['secontext'] = ':'.join(self.selinux_context(path))
            kwargs['size'] = st[stat.ST_SIZE]
        return kwargs
    def _check_locale(self):
        '''
        Uses the locale module to test the currently set locale
        (per the LANG and LC_CTYPE environment settings)
        '''
            try:
        except locale.Error:
            e = get_exception()
            # fallback to the 'C' locale, which may cause unicode
            # issues but is preferable to simply failing because
            # of an unknown locale
            locale.setlocale(locale.LC_ALL, 'C')
            os.environ['LANG']   = 'C'
            os.environ['LC_ALL'] = 'C'
            os.environ['LC_MESSAGES'] = 'C'
        except Exception:
            e = get_exception()
            self.fail_json(msg="An unknown error was encountered while attempting to validate the locale: %s" % e)
    def _handle_aliases(self):
        aliases_results = {} #alias:canon
        for (k,v) in self.argument_spec.items():
            self._legal_inputs.append(k)
            aliases = v.get('aliases', None)
            default = v.get('default', None)
            required = v.get('required', False)
            if default is not None and required:
                # not alias specific but this is a good place to check this
                self.fail_json(msg="internal error: required and default are mutually exclusive for %s" % k)
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
    def _check_arguments(self, check_invalid_arguments):
        for (k,v) in self.params.items():
            if k == '_ansible_check_mode' and v:
                if not self.supports_check_mode:
                    self.exit_json(skipped=True, msg="remote module does not support check mode")
                self.check_mode = True
            elif k == '_ansible_no_log':
                self.no_log = self.boolean(v)
            elif k == '_ansible_debug':
                self._debug = self.boolean(v)
                self._debug = self.boolean(v)
            elif check_invalid_arguments and k not in self._legal_inputs:
                self.fail_json(msg="unsupported parameter for module: %s" % k)
    def _count_terms(self, check):
        count = 0
        for term in check:
            if term in self.params:
                count += 1
        return count
    def _check_mutually_exclusive(self, spec):
        if spec is None:
        for check in spec:
            count = self._count_terms(check)
            if count > 1:
                self.fail_json(msg="parameters are mutually exclusive: %s" % (check,))
    def _check_required_one_of(self, spec):
        if spec is None:
            return
            return
        for check in spec:
            count = self._count_terms(check)
            if count == 0:
                self.fail_json(msg="one of the following is required: %s" % ','.join(check))
    def _check_required_together(self, spec):
        if spec is None:
            return
            return
        for check in spec:
            counts = [ self._count_terms([field]) for field in check ]
            non_zero = [ c for c in counts if c > 0 ]
            if len(non_zero) > 0:
                if 0 in counts:
                    self.fail_json(msg="parameters are required together: %s" % (check,))
    def _check_required_arguments(self):
        ''' ensure all required arguments are present '''
        missing = []
        for (k,v) in self.argument_spec.items():
            required = v.get('required', False)
            if required and k not in self.params:
                missing.append(k)
        if len(missing) > 0:
            self.fail_json(msg="missing required arguments: %s" % ",".join(missing))
    def _check_required_if(self, spec):
        ''' ensure that parameters which conditionally required are present '''
        if spec is None:
            return
            return
        for (key, val, requirements) in spec:
            missing = []
            if key in self.params and self.params[key] == val:
                for check in requirements:
                    count = self._count_terms((check,))
                    if count == 0:
                        missing.append(check)
                        missing.append(check)
                    count = self._count_terms((check,))
                    if count == 0:
                        missing.append(check)
                        missing.append(check)
                for check in requirements:
                    count = self._count_terms((check,))
                    if count == 0:
                        missing.append(check)
                        missing.append(check)
                    count = self._count_terms((check,))
                    if count == 0:
                        missing.append(check)
                        missing.append(check)
            if len(missing) > 0:
                self.fail_json(msg="%s is %s but the following are missing: %s" % (key, val, ','.join(missing)))
                self.fail_json(msg="%s is %s but the following are missing: %s" % (key, val, ','.join(missing)))
            missing = []
            if key in self.params and self.params[key] == val:
                for check in requirements:
                    count = self._count_terms((check,))
                    if count == 0:
                        missing.append(check)
                        missing.append(check)
                    count = self._count_terms((check,))
                    if count == 0:
                        missing.append(check)
                        missing.append(check)
                for check in requirements:
                    count = self._count_terms((check,))
                    if count == 0:
                        missing.append(check)
                        missing.append(check)
                    count = self._count_terms((check,))
                    if count == 0:
                        missing.append(check)
                        missing.append(check)
            if len(missing) > 0:
                self.fail_json(msg="%s is %s but the following are missing: %s" % (key, val, ','.join(missing)))
                self.fail_json(msg="%s is %s but the following are missing: %s" % (key, val, ','.join(missing)))
        ''' ensure that parameters which conditionally required are present '''
        if spec is None:
            return
            return
        for (key, val, requirements) in spec:
            missing = []
            if key in self.params and self.params[key] == val:
                for check in requirements:
                    count = self._count_terms((check,))
                    if count == 0:
                        missing.append(check)
                        missing.append(check)
                    count = self._count_terms((check,))
                    if count == 0:
                        missing.append(check)
                        missing.append(check)
                for check in requirements:
                    count = self._count_terms((check,))
                    if count == 0:
                        missing.append(check)
                        missing.append(check)
                    count = self._count_terms((check,))
                    if count == 0:
                        missing.append(check)
                        missing.append(check)
            if len(missing) > 0:
                self.fail_json(msg="%s is %s but the following are missing: %s" % (key, val, ','.join(missing)))
                self.fail_json(msg="%s is %s but the following are missing: %s" % (key, val, ','.join(missing)))
            missing = []
            if key in self.params and self.params[key] == val:
                for check in requirements:
                    count = self._count_terms((check,))
                    if count == 0:
                        missing.append(check)
                        missing.append(check)
                    count = self._count_terms((check,))
                    if count == 0:
                        missing.append(check)
                        missing.append(check)
                for check in requirements:
                    count = self._count_terms((check,))
                    if count == 0:
                        missing.append(check)
                        missing.append(check)
                    count = self._count_terms((check,))
                    if count == 0:
                        missing.append(check)
                        missing.append(check)
            if len(missing) > 0:
                self.fail_json(msg="%s is %s but the following are missing: %s" % (key, val, ','.join(missing)))
                self.fail_json(msg="%s is %s but the following are missing: %s" % (key, val, ','.join(missing)))
    def _check_argument_values(self):
        ''' ensure all arguments have the requested values, and there are no stray arguments '''
        for (k,v) in self.argument_spec.items():
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
                        # Attempt to set the perms of the symlink but be
                        # careful not to change the perms of the underlying
                        # file while trying
                        underlying_stat = os.stat(path)
                        os.chmod(path, mode)
                        new_underlying_stat = os.stat(path)
                        if underlying_stat.st_mode != new_underlying_stat.st_mode:
                            os.chmod(path, stat.S_IMODE(underlying_stat.st_mode))
                            os.chmod(path, stat.S_IMODE(underlying_stat.st_mode))
    def safe_eval(self, str, locals=None, include_exceptions=False):
        # do not allow method calls to modules
        if not isinstance(str, basestring):
            # already templated to a datastructure, perhaps?
            if include_exceptions:
                return (str, None)
            return str
        if re.search(r'\w\.\w+\(', str):
            if include_exceptions:
                return (str, None)
            return str
        # do not allow imports
        if re.search(r'import \w+', str):
            if include_exceptions:
                return (str, None)
            return str
            try:
        except Exception:
            e = get_exception()
            if include_exceptions:
                return (str, e)
            return str
    def _check_type_str(self, value):
        # Note: This could throw a unicode error if value's __str__() method
        # returns non-ascii.  Have to port utils.to_bytes() if that happens
        return str(value)
        if isinstance(value, basestring):
            return value
        # Note: This could throw a unicode error if value's __str__() method
        # returns non-ascii.  Have to port utils.to_bytes() if that happens
        return str(value)
    def _check_type_list(self, value):
        raise TypeError('%s cannot be converted to a list' % type(value))
        if isinstance(value, list):
            return value
        if isinstance(value, basestring):
            return value.split(",")
        elif isinstance(value, int) or isinstance(value, float):
            return [ str(value) ]
        raise TypeError('%s cannot be converted to a list' % type(value))
    def _check_type_dict(self, value):
        kwargs['failed'] = True
        kwargs = remove_values(kwargs, self.no_log_values)
        self.do_cleanup_files()
        print(self.jsonify(kwargs))
        sys.exit(1)
        if isinstance(value, dict):
            return value
        if isinstance(value, basestring):
            if value.startswith("{"):
                try:
                    return json.loads(value)
                except:
                    (result, exc) = self.safe_eval(value, dict(), include_exceptions=True)
                    if exc is not None:
                        raise TypeError('unable to evaluate string as dictionary')
                    return result
            elif '=' in value:
                fields = []
                field_buffer = []
                in_quote = False
                in_escape = False
                for c in value.strip():
                    if in_escape:
                        field_buffer.append(c)
                        in_escape = False
                        field_buffer.append(c)
                        in_escape = False
                    elif c == '\\':
                        in_escape = True
                        in_escape = True
                    elif not in_quote and c in ('\'', '"'):
                        in_quote = c
                    elif in_quote and in_quote == c:
                        in_quote = False
                    elif not in_quote and c in (',', ' '):
                        field = ''.join(field_buffer)
                        if field:
                            fields.append(field)
                        field_buffer = []
                    else:
                        field_buffer.append(c)

                field = ''.join(field_buffer)
                if field:
                    fields.append(field)
                return dict(x.split("=", 1) for x in fields)
            else:
                raise TypeError("dictionary requested, could not parse JSON or key=value")

        raise TypeError('%s cannot be converted to a dict' % type(value))

    def _check_type_bool(self, value):
        if isinstance(value, bool):
            return value

        if isinstance(value, basestring):
            return self.boolean(value)

        raise TypeError('%s cannot be converted to a bool' % type(value))

    def _check_type_int(self, value):
        if isinstance(value, int):
            return value

        if isinstance(value, basestring):
            return int(value)

        raise TypeError('%s cannot be converted to an int' % type(value))

    def _check_type_float(self, value):
        if isinstance(value, float):
            return value

        if isinstance(value, basestring):
            return float(value)

        raise TypeError('%s cannot be converted to a float' % type(value))

    def _check_type_path(self, value):
        value = self._check_type_str(value)
        return os.path.expanduser(os.path.expandvars(value))


    def _check_argument_types(self):
        ''' ensure all arguments have the requested type '''
        for (k, v) in self.argument_spec.items():
            wanted = v.get('type', None)
            if wanted is None:
                continue
            if k not in self.params:
                continue

            value = self.params[k]

            try:
                type_checker = self._CHECK_ARGUMENT_TYPES_DISPATCHER[wanted]
            except KeyError:
                self.fail_json(msg="implementation error: unknown type %s requested for %s" % (wanted, k))
            try:
                self.params[k] = type_checker(value)
            except (TypeError, ValueError):
                self.fail_json(msg="argument %s is of type %s and we were unable to convert to %s" % (k, type(value), wanted))

    def _set_defaults(self, pre=True):
        for (k,v) in self.argument_spec.items():
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
        params = json_dict_unicode_to_bytes(json.loads(MODULE_COMPLEX_ARGS))
        if params is None:
            params = dict()
        return params

    def _log_to_syslog(self, msg):
        if HAS_SYSLOG:
            module = 'ansible-%s' % os.path.basename(__file__)
            syslog.openlog(str(module), 0, syslog.LOG_USER)
            syslog.syslog(syslog.LOG_INFO, msg)

    def debug(self, msg):
        if self._debug:
            self.log(msg)

    def log(self, msg, log_args=None):

        if not self.no_log:

            if log_args is None:
                log_args = dict()

            module = 'ansible-%s' % os.path.basename(__file__)
            if isinstance(module, bytes):
                module = module.decode('utf-8', 'replace')

            # 6655 - allow for accented characters
            if not isinstance(msg, (bytes, unicode)):
                raise TypeError("msg should be a string (got %s)" % type(msg))

            # We want journal to always take text type
            # syslog takes bytes on py2, text type on py3
            if isinstance(msg, bytes):
                journal_msg = remove_values(msg.decode('utf-8', 'replace'), self.no_log_values)
            else:
                # TODO: surrogateescape is a danger here on Py3
                journal_msg = remove_values(msg, self.no_log_values)

            if sys.version_info >= (3,):
                syslog_msg = journal_msg
            else:
                syslog_msg = journal_msg.encode('utf-8', 'replace')

            if has_journal:
                journal_args = [("MODULE", os.path.basename(__file__))]
                for arg in log_args:
                    journal_args.append((arg.upper(), str(log_args[arg])))
                try:
                    journal.send(u"%s %s" % (module, journal_msg), **dict(journal_args))
                except IOError:
                    # fall back to syslog since logging to journal failed
                    self._log_to_syslog(syslog_msg)
            else:
                self._log_to_syslog(syslog_msg)

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

            if self.boolean(no_log):
                log_args[param] = 'NOT_LOGGING_PARAMETER'
            elif param in passwd_keys:
                log_args[param] = 'NOT_LOGGING_PASSWORD'
            else:
                param_val = self.params[param]
                if not isinstance(param_val, basestring):
                    param_val = str(param_val)
                elif isinstance(param_val, unicode):
                    param_val = param_val.encode('utf-8')
                log_args[param] = heuristic_log_sanitize(param_val, self.no_log_values)

        msg = []
        for arg in log_args:
            arg_val = log_args[arg]
            if not isinstance(arg_val, basestring):
                arg_val = str(arg_val)
            elif isinstance(arg_val, unicode):
                arg_val = arg_val.encode('utf-8')
            msg.append('%s=%s ' % (arg, arg_val))
        if msg:
            msg = 'Invoked with %s' % ''.join(msg)
        else:
            msg = 'Invoked'

        self.log(msg, log_args=log_args)



    def _set_cwd(self):
        try:
            cwd = os.getcwd()
            if not os.access(cwd, os.F_OK|os.R_OK):
                raise
            return cwd
        except:
            # we don't have access to the cwd, probably because of sudo. 
            # Try and move to a neutral location to prevent errors
            for cwd in [os.path.expandvars('$HOME'), tempfile.gettempdir()]:
                try:
                    if os.access(cwd, os.F_OK|os.R_OK):
                        os.chdir(cwd)
                        return cwd
                except:
                    pass
        # we won't error here, as it may *not* be a problem, 
        # and we don't want to break modules unnecessarily
        return None    

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
            if os.path.exists(path) and is_executable(path):
                bin_path = path
                break
        if required and bin_path is None:
            self.fail_json(msg='Failed to find required executable %s' % arg)
        return bin_path

    def boolean(self, arg):
        ''' return a bool for the arg '''
        if arg is None or type(arg) == bool:
            return arg
        if isinstance(arg, basestring):
            arg = arg.lower()
        if arg in BOOLEANS_TRUE:
            return True
        elif arg in BOOLEANS_FALSE:
            return False
        else:
            self.fail_json(msg='Boolean %s not in either boolean list' % arg)

    def jsonify(self, data):
        for encoding in ("utf-8", "latin-1"):
            try:
                return json.dumps(data, encoding=encoding)
            # Old systems using old simplejson module does not support encoding keyword.
            except TypeError:
                try:
                    new_data = json_dict_bytes_to_unicode(data, encoding=encoding)
                except UnicodeDecodeError:
                    continue
                return json.dumps(new_data)
            except UnicodeDecodeError:
                continue
        self.fail_json(msg='Invalid unicode encoding encountered')

    def from_json(self, data):
        return json.loads(data)

    def add_cleanup_file(self, path):
        if path not in self.cleanup_files:
            self.cleanup_files.append(path)

    def do_cleanup_files(self):
        for path in self.cleanup_files:
            self.cleanup(path)

    def exit_json(self, **kwargs):
        ''' return from the module, without error '''
        self.add_path_info(kwargs)
        if not 'changed' in kwargs:
            kwargs['changed'] = False
        kwargs = remove_values(kwargs, self.no_log_values)
        self.do_cleanup_files()
        print(self.jsonify(kwargs))
        sys.exit(0)

    def fail_json(self, **kwargs):
        ''' return from the module, with an error message '''
        self.add_path_info(kwargs)
        assert 'msg' in kwargs, "implementation error -- msg to explain the error is required"
                    if in_escape:
                        field_buffer.append(c)
                        in_escape = False
                        field_buffer.append(c)
                        in_escape = False
                    elif c == '\\':
                        in_escape = True
                        in_escape = True
                    elif not in_quote and c in ('\'', '"'):
                        in_quote = c
                    elif in_quote and in_quote == c:
                        in_quote = False
                    elif not in_quote and c in (',', ' '):
                        field = ''.join(field_buffer)
                        if field:
                            fields.append(field)
                        field_buffer = []
                    else:
                        field_buffer.append(c)

                field = ''.join(field_buffer)
                if field:
                    fields.append(field)
                return dict(x.split("=", 1) for x in fields)
            else:
                raise TypeError("dictionary requested, could not parse JSON or key=value")

        raise TypeError('%s cannot be converted to a dict' % type(value))

    def _check_type_bool(self, value):
        if isinstance(value, bool):
            return value

        if isinstance(value, basestring):
            return self.boolean(value)

        raise TypeError('%s cannot be converted to a bool' % type(value))

    def _check_type_int(self, value):
        if isinstance(value, int):
            return value

        if isinstance(value, basestring):
            return int(value)

        raise TypeError('%s cannot be converted to an int' % type(value))

    def _check_type_float(self, value):
        if isinstance(value, float):
            return value

        if isinstance(value, basestring):
            return float(value)

        raise TypeError('%s cannot be converted to a float' % type(value))

    def _check_type_path(self, value):
        value = self._check_type_str(value)
        return os.path.expanduser(os.path.expandvars(value))


    def _check_argument_types(self):
        ''' ensure all arguments have the requested type '''
        for (k, v) in self.argument_spec.items():
            wanted = v.get('type', None)
            if wanted is None:
                continue
            if k not in self.params:
                continue

            value = self.params[k]

            try:
                type_checker = self._CHECK_ARGUMENT_TYPES_DISPATCHER[wanted]
            except KeyError:
                self.fail_json(msg="implementation error: unknown type %s requested for %s" % (wanted, k))
            try:
                self.params[k] = type_checker(value)
            except (TypeError, ValueError):
                self.fail_json(msg="argument %s is of type %s and we were unable to convert to %s" % (k, type(value), wanted))

    def _set_defaults(self, pre=True):
        for (k,v) in self.argument_spec.items():
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
        params = json_dict_unicode_to_bytes(json.loads(MODULE_COMPLEX_ARGS))
        if params is None:
            params = dict()
        return params

    def _log_to_syslog(self, msg):
        if HAS_SYSLOG:
            module = 'ansible-%s' % os.path.basename(__file__)
            syslog.openlog(str(module), 0, syslog.LOG_USER)
            syslog.syslog(syslog.LOG_INFO, msg)

    def debug(self, msg):
        if self._debug:
            self.log(msg)

    def log(self, msg, log_args=None):

        if not self.no_log:

            if log_args is None:
                log_args = dict()

            module = 'ansible-%s' % os.path.basename(__file__)
            if isinstance(module, bytes):
                module = module.decode('utf-8', 'replace')

            # 6655 - allow for accented characters
            if not isinstance(msg, (bytes, unicode)):
                raise TypeError("msg should be a string (got %s)" % type(msg))

            # We want journal to always take text type
            # syslog takes bytes on py2, text type on py3
            if isinstance(msg, bytes):
                journal_msg = remove_values(msg.decode('utf-8', 'replace'), self.no_log_values)
            else:
                # TODO: surrogateescape is a danger here on Py3
                journal_msg = remove_values(msg, self.no_log_values)

            if sys.version_info >= (3,):
                syslog_msg = journal_msg
            else:
                syslog_msg = journal_msg.encode('utf-8', 'replace')

            if has_journal:
                journal_args = [("MODULE", os.path.basename(__file__))]
                for arg in log_args:
                    journal_args.append((arg.upper(), str(log_args[arg])))
                try:
                    journal.send(u"%s %s" % (module, journal_msg), **dict(journal_args))
                except IOError:
                    # fall back to syslog since logging to journal failed
                    self._log_to_syslog(syslog_msg)
            else:
                self._log_to_syslog(syslog_msg)

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

            if self.boolean(no_log):
                log_args[param] = 'NOT_LOGGING_PARAMETER'
            elif param in passwd_keys:
                log_args[param] = 'NOT_LOGGING_PASSWORD'
            else:
                param_val = self.params[param]
                if not isinstance(param_val, basestring):
                    param_val = str(param_val)
                elif isinstance(param_val, unicode):
                    param_val = param_val.encode('utf-8')
                log_args[param] = heuristic_log_sanitize(param_val, self.no_log_values)

        msg = []
        for arg in log_args:
            arg_val = log_args[arg]
            if not isinstance(arg_val, basestring):
                arg_val = str(arg_val)
            elif isinstance(arg_val, unicode):
                arg_val = arg_val.encode('utf-8')
            msg.append('%s=%s ' % (arg, arg_val))
        if msg:
            msg = 'Invoked with %s' % ''.join(msg)
        else:
            msg = 'Invoked'

        self.log(msg, log_args=log_args)



    def _set_cwd(self):
        try:
            cwd = os.getcwd()
            if not os.access(cwd, os.F_OK|os.R_OK):
                raise
            return cwd
        except:
            # we don't have access to the cwd, probably because of sudo. 
            # Try and move to a neutral location to prevent errors
            for cwd in [os.path.expandvars('$HOME'), tempfile.gettempdir()]:
                try:
                    if os.access(cwd, os.F_OK|os.R_OK):
                        os.chdir(cwd)
                        return cwd
                except:
                    pass
        # we won't error here, as it may *not* be a problem, 
        # and we don't want to break modules unnecessarily
        return None    

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
            if os.path.exists(path) and is_executable(path):
                bin_path = path
                break
        if required and bin_path is None:
            self.fail_json(msg='Failed to find required executable %s' % arg)
        return bin_path

    def boolean(self, arg):
        ''' return a bool for the arg '''
        if arg is None or type(arg) == bool:
            return arg
        if isinstance(arg, basestring):
            arg = arg.lower()
        if arg in BOOLEANS_TRUE:
            return True
        elif arg in BOOLEANS_FALSE:
            return False
        else:
            self.fail_json(msg='Boolean %s not in either boolean list' % arg)

    def jsonify(self, data):
        for encoding in ("utf-8", "latin-1"):
            try:
                return json.dumps(data, encoding=encoding)
            # Old systems using old simplejson module does not support encoding keyword.
            except TypeError:
                try:
                    new_data = json_dict_bytes_to_unicode(data, encoding=encoding)
                except UnicodeDecodeError:
                    continue
                return json.dumps(new_data)
            except UnicodeDecodeError:
                continue
        self.fail_json(msg='Invalid unicode encoding encountered')

    def from_json(self, data):
        return json.loads(data)

    def add_cleanup_file(self, path):
        if path not in self.cleanup_files:
            self.cleanup_files.append(path)

    def do_cleanup_files(self):
        for path in self.cleanup_files:
            self.cleanup(path)

    def exit_json(self, **kwargs):
        ''' return from the module, without error '''
        self.add_path_info(kwargs)
        if not 'changed' in kwargs:
            kwargs['changed'] = False
        kwargs = remove_values(kwargs, self.no_log_values)
        self.do_cleanup_files()
        print(self.jsonify(kwargs))
        sys.exit(0)

    def fail_json(self, **kwargs):
        ''' return from the module, with an error message '''
        self.add_path_info(kwargs)
        assert 'msg' in kwargs, "implementation error -- msg to explain the error is required"
        kwargs['failed'] = True
        kwargs = remove_values(kwargs, self.no_log_values)
        self.do_cleanup_files()
        print(self.jsonify(kwargs))
        sys.exit(1)
    def digest_from_file(self, filename, algorithm):
        ''' Return hex digest of local file for a digest_method specified by name, or None if file is not present. '''
        if not os.path.exists(filename):
        if os.path.isdir(filename):
            self.fail_json(msg="attempted to take checksum of directory: %s" % filename)
        # preserve old behaviour where the third parameter was a hash algorithm object
        if hasattr(algorithm, 'hexdigest'):
            digest_method = algorithm
            digest_method = algorithm
        blocksize = 64 * 1024
        infile = open(filename, 'rb')
        block = infile.read(blocksize)
        while block:
            digest_method.update(block)
            block = infile.read(blocksize)
        infile.close()
        return digest_method.hexdigest()
    def md5(self, filename):
        ''' Return MD5 hex digest of local file using digest_from_file().

        Do not use this function unless you have no other choice for:
            1) Optional backwards compatibility
            2) Compatibility with a third party protocol

        This function will not work on systems complying with FIPS-140-2.

        Most uses of this function can use the module.sha1 function instead.
        '''
        if 'md5' not in AVAILABLE_HASH_ALGORITHMS:
            raise ValueError('MD5 not available.  Possibly running in FIPS mode')
            raise ValueError('MD5 not available.  Possibly running in FIPS mode')
        return self.digest_from_file(filename, 'md5')
    def sha1(self, filename):
        ''' Return SHA1 hex digest of local file using digest_from_file(). '''
        return self.digest_from_file(filename, 'sha1')
    def sha256(self, filename):
        ''' Return SHA-256 hex digest of local file using digest_from_file(). '''
        return self.digest_from_file(filename, 'sha256')
        ''' Return SHA-256 hex digest of local file using digest_from_file(). '''
        return self.digest_from_file(filename, 'sha256')
    def backup_local(self, fn):
        '''make a date-marked backup of the specified file, return True or False on success or failure'''
        backupdest = ''
        return backupdest
    def cleanup(self, tmpfile):
        if os.path.exists(tmpfile):
    def atomic_move(self, src, dest):
        '''atomically move src to dest, copying attributes from dest, returns true on success
        it uses os.rename to ensure this as it is an atomic operation, rest of the function is
        to work around limitations, corner cases and ensure selinux context is saved if possible'''
        context = None
        dest_stat = None
        if os.path.exists(dest):
            except OSError:
                e = get_exception()
            if self.selinux_enabled():
                context = self.selinux_context(dest)
            try:
                dest_stat = os.stat(dest)
                os.chmod(src, dest_stat.st_mode & PERM_BITS)
                os.chown(src, dest_stat.st_uid, dest_stat.st_gid)
            except OSError:
                e = get_exception()
                if e.errno != errno.EPERM:
                    raise
            if self.selinux_enabled():
                context = self.selinux_context(dest)
        if os.path.exists(fn):
            # backups named basename-YYYY-MM-DD@HH:MM:SS~
            ext = time.strftime("%Y-%m-%d@%H:%M:%S~", time.localtime(time.time()))
        backupdest = '%s.%s' % (fn, ext)
            except (shutil.Error, IOError):
                e = get_exception()
            self.fail_json(msg='Could not make backup of %s to %s: %s' % (fn, backupdest, e))
                e = get_exception()
                self.fail_json(msg='Could not make backup of %s to %s: %s' % (fn, backupdest, e))
        except OSError:
                if e.errno != errno.EPERM:
        creating = not os.path.exists(dest)
        # if the original login_name doesn't match the currently
        # logged-in user, or if the SUDO_USER environment variable
        # is set, then this user has switched their credentials
        try:
            # Optimistically try a rename, solves some corner cases and can avoid useless work, throws exception if not atomic.
            os.rename(src, dest)
            # Optimistically try a rename, solves some corner cases and can avoid useless work, throws exception if not atomic.
            os.rename(src, dest)
        switched_user = login_name and login_name != pwd.getpwuid(os.getuid())[0] or os.environ.get('SUDO_USER')
        except (IOError, OSError):
            e = get_exception()
            # only try workarounds for errno 18 (cross device), 1 (not permitted),  13 (permission denied)
            # and 26 (text file busy) which happens on vagrant synced folders
            if e.errno not in [errno.EPERM, errno.EXDEV, errno.EACCES, errno.ETXTBSY]:
                self.fail_json(msg='Could not replace file: %s to %s: %s' % (src, dest, e))
                self.fail_json(msg='Could not replace file: %s to %s: %s' % (src, dest, e))
            dest_dir = os.path.dirname(dest)
            dest_file = os.path.basename(dest)
            try:
                tmp_dest = tempfile.NamedTemporaryFile(
                    prefix=".ansible_tmp", dir=dest_dir, suffix=dest_file)
                tmp_dest = tempfile.NamedTemporaryFile(
                    prefix=".ansible_tmp", dir=dest_dir, suffix=dest_file)
            try:
            shutil.copy2(fn, backupdest)
            except (OSError, IOError):
                e = get_exception()
                self.fail_json(msg='The destination directory (%s) is not writable by the current user.' % dest_dir)
            try: # leaves tmp file behind when sudo and  not root
                if switched_user and os.getuid() != 0:
                    # cleanup will happen by 'rm' of tempdir
                    # copy2 will preserve some metadata
                    shutil.copy2(src, tmp_dest.name)
                try:
                    tmp_stat = os.stat(tmp_dest.name)
                    if dest_stat and (tmp_stat.st_uid != dest_stat.st_uid or tmp_stat.st_gid != dest_stat.st_gid):
                        os.chown(tmp_dest.name, dest_stat.st_uid, dest_stat.st_gid)
                    tmp_stat = os.stat(tmp_dest.name)
                    if dest_stat and (tmp_stat.st_uid != dest_stat.st_uid or tmp_stat.st_gid != dest_stat.st_gid):
                        os.chown(tmp_dest.name, dest_stat.st_uid, dest_stat.st_gid)
                if self.selinux_enabled():
                    self.set_context_if_different(
                        tmp_dest.name, context, False)
                try:
                os.unlink(tmpfile)
                except OSError:
                    e = get_exception()
                    if e.errno != errno.EPERM:
                    raise
                os.rename(tmp_dest.name, dest)
            except (shutil.Error, OSError, IOError):
                e = get_exception()
                self.cleanup(tmp_dest.name)
                self.fail_json(msg='Could not replace file: %s to %s: %s' % (src, dest, e))
        if creating:
            # make sure the file has the correct permissions
            # based on the current value of umask
            umask = os.umask(0)
            os.umask(umask)
            os.chmod(dest, DEFAULT_PERM & ~umask)
            if switched_user:
                os.chown(dest, os.getuid(), os.getgid())
        if self.selinux_enabled():
            # rename might not preserve context
            self.set_context_if_different(dest, context, False)
    def run_command(self, args, check_rc=False, close_fds=True, executable=None, data=None, binary_data=False, path_prefix=None, cwd=None, use_unsafe_shell=False, prompt_regex=None):
        Execute a command, returns rc, stdout, and stderr.
        args is the command to run
        If args is a list, the command will be run with shell=False.
        If args is a string and use_unsafe_shell=False it will split args to a list and run with shell=False
        If args is a string and use_unsafe_shell=True it run with shell=True.
        Other arguments:
        - check_rc (boolean)    Whether to call fail_json in case of
                              non zero RC.  Default is False.
        - close_fds (boolean)   See documentation for subprocess.Popen().
                              Default is True.
        - executable (string)   See documentation for subprocess.Popen().
                              Default is None.
        - prompt_regex (string) A regex string (not a compiled regex) which
                                can be used to detect prompts in the stdout
                                which would otherwise cause the execution
                                to hang (especially if no input data is
                                specified)
        shell = False
        if isinstance(args, list):
            if use_unsafe_shell:
                args = " ".join([pipes.quote(x) for x in args])
                shell = True
        elif isinstance(args, basestring) and use_unsafe_shell:
            shell = True
        elif isinstance(args, basestring):
            args = shlex.split(args.encode('utf-8'))
        prompt_re = None
        if prompt_regex:
            try:
                prompt_re = re.compile(prompt_regex, re.MULTILINE)
                prompt_re = re.compile(prompt_regex, re.MULTILINE)
            except re.error:
                self.fail_json(msg="invalid prompt regular expression given to run_command")
                self.fail_json(msg="invalid prompt regular expression given to run_command")
            try:
                prompt_re = re.compile(prompt_regex, re.MULTILINE)
                prompt_re = re.compile(prompt_regex, re.MULTILINE)
            except re.error:
                self.fail_json(msg="invalid prompt regular expression given to run_command")
                self.fail_json(msg="invalid prompt regular expression given to run_command")
        # expand things like $HOME and ~
        if not shell:
            args = [ os.path.expandvars(os.path.expanduser(x)) for x in args ]
        rc = 0
        msg = None
        st_in = None
        # Set a temporary env path if a prefix is passed
        env=os.environ
        if path_prefix:
            env['PATH']="%s:%s" % (path_prefix, env['PATH'])
        # create a printable version of the command for use
        # in reporting later, which strips out things like
        # passwords from the args list
        if isinstance(args, basestring):
            if isinstance(args, unicode):
                b_args = args.encode('utf-8')
                b_args = args.encode('utf-8')
            to_clean_args = shlex.split(b_args)
            del b_args
            if isinstance(args, unicode):
                b_args = args.encode('utf-8')
                b_args = args.encode('utf-8')
            else:
                b_args = args
            to_clean_args = shlex.split(b_args)
            del b_args
        clean_args = []
        is_passwd = False
        for arg in to_clean_args:
            if is_passwd:
                is_passwd = False
                clean_args.append('********')
                is_passwd = False
                clean_args.append('********')
                continue
            if PASSWD_ARG_RE.match(arg):
                sep_idx = arg.find('=')
                if sep_idx > -1:
                    clean_args.append('%s=********' % arg[:sep_idx])
                    clean_args.append('%s=********' % arg[:sep_idx])
                    continue
        else:
                    is_passwd = True
                sep_idx = arg.find('=')
                if sep_idx > -1:
                    clean_args.append('%s=********' % arg[:sep_idx])
                    clean_args.append('%s=********' % arg[:sep_idx])
                    continue
                else:
                    is_passwd = True
            arg = heuristic_log_sanitize(arg, self.no_log_values)
            clean_args.append(arg)
            if is_passwd:
                is_passwd = False
                clean_args.append('********')
                is_passwd = False
                clean_args.append('********')
                continue
            if PASSWD_ARG_RE.match(arg):
                sep_idx = arg.find('=')
                if sep_idx > -1:
                    clean_args.append('%s=********' % arg[:sep_idx])
                    clean_args.append('%s=********' % arg[:sep_idx])
                    continue
        else:
                    is_passwd = True
                sep_idx = arg.find('=')
                if sep_idx > -1:
                    clean_args.append('%s=********' % arg[:sep_idx])
                    clean_args.append('%s=********' % arg[:sep_idx])
                    continue
                else:
                    is_passwd = True
            arg = heuristic_log_sanitize(arg, self.no_log_values)
            clean_args.append(arg)
        kwargs = dict(
            executable=executable,
            shell=shell,
            close_fds=close_fds,
            stdin=st_in,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        if path_prefix:
            kwargs['env'] = env
            kwargs['env'] = env
        if cwd and os.path.isdir(cwd):
            kwargs['cwd'] = cwd
            try:
                dest_stat = os.stat(dest)
                os.chmod(src, dest_stat.st_mode & PERM_BITS)
                os.chown(src, dest_stat.st_uid, dest_stat.st_gid)
        # store the pwd
        prev_dir = os.getcwd()
        # make sure we're in the right working directory
        if cwd and os.path.isdir(cwd):
            try:
                os.chdir(cwd)
            except (OSError, IOError):
                e = get_exception()
                self.fail_json(rc=e.errno, msg="Could not open %s, %s" % (cwd, str(e)))
            try:
                os.chdir(cwd)
            except (OSError, IOError):
                e = get_exception()
                self.fail_json(rc=e.errno, msg="Could not open %s, %s" % (cwd, str(e)))
        try:
            if self._debug:
        if isinstance(args, list):
                    running = ' '.join(args)
        clean_args = ' '.join(pipes.quote(arg) for arg in clean_args)
                else:
                    running = args
                self.log('Executing: ' + running)
                if isinstance(args, list):
                    running = ' '.join(args)
                else:
                    running = args
                self.log('Executing: ' + running)
            cmd = subprocess.Popen(args, **kwargs)
            # the communication logic here is essentially taken from that
            # of the _communicate() function in ssh.py
            stdout = ''
            stderr = ''
            rpipes = [cmd.stdout, cmd.stderr]
            if data:
                if not binary_data:
                    data += '\n'
                cmd.stdin.write(data)
                cmd.stdin.close()
                if not binary_data:
                    data += '\n'
                cmd.stdin.write(data)
                cmd.stdin.close()
            while True:
                rfd, wfd, efd = select.select(rpipes, [], rpipes, 1)
                if cmd.stdout in rfd:
                    dat = os.read(cmd.stdout.fileno(), 9000)
                    stdout += dat
                    if dat == '':
                        rpipes.remove(cmd.stdout)
                if cmd.stderr in rfd:
                    dat = os.read(cmd.stderr.fileno(), 9000)
                    stderr += dat
                    if dat == '':
                        rpipes.remove(cmd.stderr)
                # if we're checking for prompts, do it now
                if prompt_re:
                    if prompt_re.search(stdout) and not data:
                        return (257, stdout, "A prompt was encountered while running a command, but no input data was specified")
                        return (257, stdout, "A prompt was encountered while running a command, but no input data was specified")
                    if prompt_re.search(stdout) and not data:
                        return (257, stdout, "A prompt was encountered while running a command, but no input data was specified")
                        return (257, stdout, "A prompt was encountered while running a command, but no input data was specified")
                # only break out if no pipes are left to read or
                # the pipes are completely read and
                # the process is terminated
                if (not rpipes or not rfd) and cmd.poll() is not None:
                    break
                # No pipes are left to read but process is not yet terminated
                # Only then it is safe to wait for the process to be finished
                # NOTE: Actually cmd.poll() is always None here if rpipes is empty
                elif not rpipes and cmd.poll() == None:
                    cmd.wait()
                    # The process is terminated. Since no pipes to read from are
                    # left, there is no need to call select() again.
                    break
            cmd.stdout.close()
            cmd.stderr.close()
            rc = cmd.returncode
            if self._debug:
        if isinstance(args, list):
                    running = ' '.join(args)
        clean_args = ' '.join(pipes.quote(arg) for arg in clean_args)
                else:
                    running = args
                self.log('Executing: ' + running)
                if isinstance(args, list):
                    running = ' '.join(args)
                else:
                    running = args
                self.log('Executing: ' + running)
            cmd = subprocess.Popen(args, **kwargs)
            # the communication logic here is essentially taken from that
            # of the _communicate() function in ssh.py
            stdout = ''
            stderr = ''
            rpipes = [cmd.stdout, cmd.stderr]
            if data:
                if not binary_data:
                    data += '\n'
                cmd.stdin.write(data)
                cmd.stdin.close()
                if not binary_data:
                    data += '\n'
                cmd.stdin.write(data)
                cmd.stdin.close()
            while True:
                rfd, wfd, efd = select.select(rpipes, [], rpipes, 1)
                if cmd.stdout in rfd:
                    dat = os.read(cmd.stdout.fileno(), 9000)
                    stdout += dat
                    if dat == '':
                        rpipes.remove(cmd.stdout)
                if cmd.stderr in rfd:
                    dat = os.read(cmd.stderr.fileno(), 9000)
                    stderr += dat
                    if dat == '':
                        rpipes.remove(cmd.stderr)
                # if we're checking for prompts, do it now
                if prompt_re:
                    if prompt_re.search(stdout) and not data:
                        return (257, stdout, "A prompt was encountered while running a command, but no input data was specified")
                        return (257, stdout, "A prompt was encountered while running a command, but no input data was specified")
                    if prompt_re.search(stdout) and not data:
                        return (257, stdout, "A prompt was encountered while running a command, but no input data was specified")
                        return (257, stdout, "A prompt was encountered while running a command, but no input data was specified")
                # only break out if no pipes are left to read or
                # the pipes are completely read and
                # the process is terminated
                if (not rpipes or not rfd) and cmd.poll() is not None:
                    break
                # No pipes are left to read but process is not yet terminated
                # Only then it is safe to wait for the process to be finished
                # NOTE: Actually cmd.poll() is always None here if rpipes is empty
                elif not rpipes and cmd.poll() == None:
                    cmd.wait()
                    # The process is terminated. Since no pipes to read from are
                    # left, there is no need to call select() again.
                    break
            cmd.stdout.close()
            cmd.stderr.close()
            rc = cmd.returncode
        try:
            login_name = os.getlogin()
            if data:
            st_in = subprocess.PIPE
        except (OSError, IOError):
            e = get_exception()
            self.fail_json(rc=e.errno, msg=str(e), cmd=clean_args)
        if rc != 0 and check_rc:
            msg = heuristic_log_sanitize(stderr.rstrip(), self.no_log_values)
            self.fail_json(cmd=clean_args, rc=rc, stdout=stdout, stderr=stderr, msg=msg)
        # reset the pwd
        os.chdir(prev_dir)
        return (rc, stdout, stderr)
    def append_to_file(self, filename, str):
        filename = os.path.expandvars(os.path.expanduser(filename))
        fh = open(filename, 'a')
        fh.write(str)
        fh.close()
    def pretty_bytes(self,size):
        ranges = (
                (1<<70, 'ZB'),
                (1<<60, 'EB'),
                (1<<50, 'PB'),
                (1<<40, 'TB'),
                (1<<30, 'GB'),
                (1<<20, 'MB'),
                (1<<10, 'KB'),
                (1, 'Bytes')
            )
            )
        for limit, suffix in ranges:
            if size >= limit:
                break
        return '%.2f %s' % (float(size)/ limit, suffix)
    #
    # Backwards compat
    #
    # In 2.0, moved from inside the module to the toplevel
    is_executable = is_executable



        
        



        










































    
            
        
        











        








































































def get_module_path():
    return os.path.dirname(os.path.realpath(__file__))

