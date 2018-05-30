# (c) 2012-2014, Michael DeHaan <michael.dehaan@gmail.com>
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

#############################################
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import fnmatch
import os
import sys
import re
import stat

from ansible import constants as C
from ansible.errors import AnsibleError

from ansible.inventory.dir import InventoryDirectory, get_file_parser
from ansible.inventory.group import Group
from ansible.inventory.host import Host
from ansible.plugins import vars_loader
from ansible.utils.vars import combine_vars

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()

class Inventory(object):
    """
    Host inventory for ansible.
    """



<<<<<<< REMOTE

=======
    def get_hosts(self, pattern="all", ignore_limits_and_restrictions=False):
        """ 
        Takes a pattern or list of patterns and returns a list of matching
        inventory host names, taking into account any active restrictions
        or applied subsets
        """

        # Enumerate all hosts matching the given pattern (which may be
        # either a list of patterns or a string like 'pat1:pat2').
        if isinstance(pattern, list):
            pattern = ':'.join(pattern)

        if ';' in pattern or ',' in pattern:
            display.deprecated("Use ':' instead of ',' or ';' to separate host patterns", version=2.0, removed=True)

        patterns = self._split_pattern(pattern)
        hosts = self._evaluate_patterns(patterns)

        # mainly useful for hostvars[host] access
        if not ignore_limits_and_restrictions:
            # exclude hosts not in a subset, if defined
            if self._subset:
                subset = self._evaluate_patterns(self._subset)
                hosts = [ h for h in hosts if h in subset ]

            # exclude hosts mentioned in any restriction (ex: failed hosts)
            if self._restriction is not None:
                hosts = [ h for h in hosts if h in self._restriction ]

        return hosts


>>>>>>> LOCAL
    def _split_subscript(self, pattern):
        """
        Takes a pattern, checks if it has a subscript, and returns the pattern
        without the subscript and a (start,end) tuple representing the given
        subscript (or None if there is no subscript).

        Validates that the subscript is in the right syntax, but doesn't make
        sure the actual indices make sense in context.
        """

        # Do not parse regexes for enumeration info
        if pattern.startswith('~'):
            return (pattern, None)

        # We want a pattern followed by an integer or range subscript.
        # (We can't be more restrictive about the expression because the
        # fnmatch semantics permit [\[:\]] to occur.)

        pattern_with_subscript = re.compile(
            r'''^
                (.+)                    # A pattern expression ending with...
                \[(?:                   # A [subscript] expression comprising:
                    (-?[0-9]+)          # A single positive or negative number
                    |                   # Or a numeric range
                    ([0-9]+)([:-])([0-9]+)
                )\]
                $
            ''', re.X
        )

        subscript = None
        m = pattern_with_subscript.match(pattern)
        if m:
            (pattern, idx, start, sep, end) = m.groups()
            if idx:
                subscript = (int(idx), None)
            else:
                subscript = (int(start), int(end))
                if sep == '-':
                    display.deprecated("Use [x:y] inclusive subscripts instead of [x-y]", version=2.0, removed=True)

        return (pattern, subscript)

    def _apply_subscript(self, hosts, subscript):
        """
        Takes a list of hosts and a (start,end) tuple and returns the subset of
        hosts based on the subscript (which may be None to return all hosts).
        """

        if not hosts or not subscript:
            return hosts

        (start, end) = subscript

        if end:
            return hosts[start:end+1]
        else:
            return [ hosts[start] ]

    def _enumerate_matches(self, pattern):
        """
        Returns a list of host names matching the given pattern according to the
        rules explained above in _match_one_pattern.
        """

        results = []
        hosts = []
        hostnames = set()

        def __append_host_to_results(host):
            if host.name not in hostnames:
                hostnames.add(host.name)
                results.append(host)

        groups = self.get_groups()
        for group in groups:
            if pattern == 'all':
                for host in group.get_hosts():
                    __append_host_to_results(host)
            else:
                if self._match(group.name, pattern) and group.name not in ('all', 'ungrouped'):
                    for host in group.get_hosts():
                        __append_host_to_results(host)
                else:
                    matching_hosts = self._match_list(group.get_hosts(), 'name', pattern)
                    for host in matching_hosts:
                        __append_host_to_results(host)

        if pattern in C.LOCALHOST and len(results) == 0:
            new_host = self._create_implicit_localhost(pattern)
            results.append(new_host)
        return results



    def __init__(self, loader, variable_manager, host_list=C.DEFAULT_HOST_LIST):
        # the host file file, or script path, or list of hosts
        # if a list, inventory data will NOT be loaded
        self.host_list = host_list
        self._loader = loader
        self._variable_manager = variable_manager

        # caching to avoid repeated calculations, particularly with
        # external inventory scripts.

        self._vars_per_host  = {}
        self._vars_per_group = {}
        self._hosts_cache    = {}
        self._groups_list    = {}
        self._pattern_cache  = {}
        self._vars_plugins   = []
        self._groups_cache   = {}

        # to be set by calling set_playbook_basedir by playbook code
        self._playbook_basedir = None

        # the inventory object holds a list of groups
        self.groups = []

        # a list of host(names) to contain current inquiries to
        self._restriction = None
        self._subset = None

        self.parse_inventory(host_list)



    def parse_inventory(self, host_list):
        if isinstance(host_list, basestring):
            if "," in host_list:
                host_list = host_list.split(",")
                host_list = [ h for h in host_list if h and h.strip() ]

        if host_list is None:
            self.parser = None
        elif isinstance(host_list, list):
            self.parser = None
            all = Group('all')
            self.groups = [ all ]
            ipv6_re = re.compile('\[([a-f:A-F0-9]*[%[0-z]+]?)\](?::(\d+))?')
            for x in host_list:
                m = ipv6_re.match(x)
                if m:
                    all.add_host(Host(m.groups()[0], m.groups()[1]))
                else:
                    if ":" in x:
                        tokens = x.rsplit(":", 1)
                        # if there is ':' in the address, then this is an ipv6
                        if ':' in tokens[0]:
                            all.add_host(Host(x))
                        else:
                            all.add_host(Host(tokens[0], tokens[1]))
                    else:
                        all.add_host(Host(x))
        elif os.path.exists(host_list):
            #TODO: switch this to a plugin loader and a 'condition' per plugin on which it should be tried, restoring 'inventory pllugins'
            if os.path.isdir(host_list):
                # Ensure basedir is inside the directory
                host_list = os.path.join(self.host_list, "")
                self.parser = InventoryDirectory(loader=self._loader, filename=host_list)
            else:
                self.parser = get_file_parser(host_list, self._loader)
                vars_loader.add_directory(self.basedir(), with_subdir=True)

            if self.parser:
                self.groups = self.parser.groups.values()
            else:
                # should never happen, but JIC
                raise AnsibleError("Unable to parse %s as an inventory source" % host_list)

        # FIXME: shouldn't be required, since the group/host vars file
        #        management will be done in VariableManager
        # get group vars from group_vars/ files and vars plugins
        for group in self.groups:
            group.vars = combine_vars(group.vars, self.get_group_variables(group.name))

        # get host vars from host_vars/ files and vars plugins
        for host in self.get_hosts():
            host.vars = combine_vars(host.vars, self.get_host_variables(host.name))





    def _match(self, str, pattern_str):
            try:
            if pattern_str.startswith('~'):
                return re.search(pattern_str[1:], str)
            else:
                return fnmatch.fnmatch(str, pattern_str)
        except Exception as e:
            raise AnsibleError('invalid host pattern: %s' % pattern_str)

    def _split_pattern(self, pattern):
        """
        takes e.g. "webservers[0:5]:dbservers:others"
        and returns ["webservers[0:5]", "dbservers", "others"]
        """


        term = re.compile(
            r'''(?:             # We want to match something comprising:
                    [^:\[\]]    # (anything other than ':', '[', or ']'
                    |           # ...or...
                    \[[^\]]*\]  # a single complete bracketed expression)
                )*              # repeated as many times as possible
            ''', re.X
        )

        return [x for x in term.findall(pattern) if x]
    def _evaluate_patterns(self, patterns):
        """
        Takes a list of patterns and returns a list of matching host names,
        taking into account any negative and intersection patterns.
        """

        # Host specifiers should be sorted to ensure consistent behavior
        pattern_regular = []
        pattern_intersection = []
        pattern_exclude = []
        for p in patterns:
            if p.startswith("!"):
                pattern_exclude.append(p)
            elif p.startswith("&"):
                pattern_intersection.append(p)
            elif p:
                pattern_regular.append(p)

        # if no regular pattern was given, hence only exclude and/or intersection
        # make that magically work
        if pattern_regular == []:
            pattern_regular = ['all']

        # when applying the host selectors, run those without the "&" or "!"
        # first, then the &s, then the !s.

        patterns = pattern_regular + pattern_intersection + pattern_exclude

        hosts = []

        for p in patterns:
            # avoid resolving a pattern that is a plain host
            if p in self._hosts_cache:
                hosts.append(self.get_host(p))
            else:
                that = self._match_one_pattern(p)
                if p.startswith("!"):
                    hosts = [ h for h in hosts if h not in that ]
                elif p.startswith("&"):
                    hosts = [ h for h in hosts if h in that ]
                else:
                    to_append = [ h for h in that if h.name not in [ y.name for y in hosts ] ]
                    hosts.extend(to_append)
        return hosts
    def _match_one_pattern(self, pattern):
        """ 
        Takes a single pattern (i.e., not "p1:p2") and returns a list of
        matching hosts names. Does not take negatives or intersections
        into account.
        """

        if pattern not in self._pattern_cache:
        return self._pattern_cache[pattern]

        (name, enumeration_details) = self._enumeration_info(pattern)
        hpat = self._hosts_in_unenumerated_pattern(name)
        result = self._apply_ranges(pattern, hpat)
            self._pattern_cache[pattern] = hosts

        return result

    def clear_pattern_cache(self):
        ''' called exclusively by the add_host plugin to allow patterns to be recalculated '''
        self._pattern_cache = {}


    def groups_for_host(self, host):
        if host in self._hosts_cache:
            return self._hosts_cache[host].get_groups()
        else:
            return []

    def groups_list(self):
        if not self._groups_list:
            groups = {}
            for g in self.groups:
                groups[g.name] = [h.name for h in g.get_hosts()]
                ancestors = g.get_ancestors()
                for a in ancestors:
                    if a.name not in groups:
                        groups[a.name] = [h.name for h in a.get_hosts()]
            self._groups_list = groups
            self._groups_cache = {}
        return self._groups_list

    def get_groups(self):
        return self.groups

    def get_host(self, hostname):
        if hostname not in self._hosts_cache:
            self._hosts_cache[hostname] = self._get_host(hostname)
            if hostname in C.LOCALHOST:
                for host in C.LOCALHOST.difference((hostname,)):
                    self._hosts_cache[host] = self._hosts_cache[hostname]
        return self._hosts_cache[hostname]

    def _get_host(self, hostname):
        if hostname in C.LOCALHOST:
            for host in self.get_group('all').get_hosts():
                if host.name in C.LOCALHOST:
                    return host
            return self._create_implicit_localhost(hostname)
        matching_host = None
        for group in self.groups:
            for host in group.get_hosts():
                if hostname == host.name:
                    matching_host = host
                self._hosts_cache[host.name] = host
        return matching_host

    def get_group(self, groupname):
        if not self._groups_cache:
            for group in self.groups:
                self._groups_cache[group.name] = group

        return self._groups_cache.get(groupname)

    def get_group_variables(self, groupname, update_cached=False, vault_password=None):
        if groupname not in self._vars_per_group or update_cached:
            self._vars_per_group[groupname] = self._get_group_variables(groupname, vault_password=vault_password)
        return self._vars_per_group[groupname]

    def _get_group_variables(self, groupname, vault_password=None):
        group = self.get_group(groupname)
        if group is None:
            raise Exception("group not found: %s" % groupname)

        vars = {}

        # plugin.get_group_vars retrieves just vars for specific group
        vars_results = [ plugin.get_group_vars(group, vault_password=vault_password) for plugin in self._vars_plugins if hasattr(plugin, 'get_group_vars')]
        for updated in vars_results:
            if updated is not None:
                vars = combine_vars(vars, updated)

        # Read group_vars/ files
        vars = combine_vars(vars, self.get_group_vars(group))

        return vars

    def get_vars(self, hostname, update_cached=False, vault_password=None):
        host = self.get_host(hostname)
        if not host:
            raise Exception("host not found: %s" % hostname)
        return host.get_vars()

    def get_host_variables(self, hostname, update_cached=False, vault_password=None):
        if hostname not in self._vars_per_host or update_cached:
            self._vars_per_host[hostname] = self._get_host_variables(hostname, vault_password=vault_password)
        return self._vars_per_host[hostname]

    def _get_host_variables(self, hostname, vault_password=None):
        host = self.get_host(hostname)
        if host is None:
            raise AnsibleError("host not found: %s" % hostname)

        vars = {}

        # plugin.run retrieves all vars (also from groups) for host
        vars_results = [ plugin.run(host, vault_password=vault_password) for plugin in self._vars_plugins if hasattr(plugin, 'run')]
        for updated in vars_results:
            if updated is not None:
                vars = combine_vars(vars, updated)

        # plugin.get_host_vars retrieves just vars for specific host
        vars_results = [ plugin.get_host_vars(host, vault_password=vault_password) for plugin in self._vars_plugins if hasattr(plugin, 'get_host_vars')]
        for updated in vars_results:
            if updated is not None:
                vars = combine_vars(vars, updated)

        # still need to check InventoryParser per host vars
        # which actually means InventoryScript per host,
        # which is not performant
        if self.parser is not None:
            vars = combine_vars(vars, self.parser.get_host_variables(host))

        # Read host_vars/ files

        vars = combine_vars(vars, self.get_host_vars(host))
        return vars
    def add_group(self, group):
        if group.name not in self.groups_list():
            self.groups.append(group)
            self._groups_list = None  # invalidate internal cache
            self._groups_cache = {}
        else:
            raise AnsibleError("group already in inventory: %s" % group.name)

    def list_hosts(self, pattern="all"):
        """ return a list of hostnames for a pattern """

        result = [ h for h in self.get_hosts(pattern) ]
        return result
        if len(result) == 0 and pattern in C.LOCALHOST:
            result = [pattern]
    def list_groups(self):
        return sorted([ g.name for g in self.groups ], key=lambda x: x)

    def restrict_to_hosts(self, restriction):
        """ 
        Restrict list operations to the hosts given in restriction.  This is used
        to batch serial operations in main playbook code, don't use this for other
        reasons.
        """
        if restriction is None:
            return
        elif not isinstance(restriction, list):
            restriction = [ restriction ]
        self._restriction = restriction

    def subset(self, subset_pattern):
        """ 
        Limits inventory results to a subset of inventory that matches a given
        pattern, such as to select a given geographic of numeric slice amongst
        a previous 'hosts' selection that only select roles, or vice versa.  
        Corresponds to --limit parameter to ansible-playbook
        """
        if subset_pattern is None:
            self._subset = None
        else:
            if ';' in subset_pattern or ',' in subset_pattern:
                display.deprecated("Use ':' instead of ',' or ';' to separate host patterns", version=2.0, removed=True)

            subset_patterns = self._split_pattern(subset_pattern)
            results = []
            # allow Unix style @filename data
            for x in subset_patterns:
                if x.startswith("@"):
                    fd = open(x[1:])
                    results.extend(fd.read().split("\n"))
                    fd.close()
                else:
                    results.append(x)
            self._subset = results

    def remove_restriction(self):
        """ Do not restrict list operations """
        self._restriction = None

    def is_file(self):
        """ did inventory come from a file? """
        if not isinstance(self.host_list, basestring):
            return False
        return os.path.exists(self.host_list)

    def basedir(self):
        """ if inventory came from a file, what's the directory? """
        dname = self.host_list
        if not self.is_file():
            dname = None
        elif os.path.isdir(self.host_list):
            dname = self.host_list
        else:
            dname = os.path.dirname(self.host_list)
            if dname is None or dname == '' or dname == '.':
                cwd = os.getcwd()
                dname = cwd
        if dname:
            dname = os.path.abspath(dname)
<<<<<<< REMOTE

=======
return dname
>>>>>>> LOCAL

    def src(self):
        """ if inventory came from a file, what's the directory and file name? """
        if not self.is_file():
            return None
        return self.host_list

    def playbook_basedir(self):
        """ returns the directory of the current playbook """
        return self._playbook_basedir

    def set_playbook_basedir(self, dir_name):
        """
        sets the base directory of the playbook so inventory can use it as a
        basedir for host_ and group_vars, and other things.
        """
        # Only update things if dir is a different playbook basedir
        if dir_name != self._playbook_basedir:
            self._playbook_basedir = dir_name
            # get group vars from group_vars/ files
            # FIXME: excluding the new_pb_basedir directory may result in group_vars
            #        files loading more than they should, however with the file caching
            #        we do this shouldn't be too much of an issue. Still, this should
            #        be fixed at some point to allow a "first load" to touch all of the
            #        directories, then later runs only touch the new basedir specified
            for group in self.groups:
                #group.vars = combine_vars(group.vars, self.get_group_vars(group, new_pb_basedir=True))
                group.vars = combine_vars(group.vars, self.get_group_vars(group))
            # get host vars from host_vars/ files
            for host in self.get_hosts():
                #host.vars = combine_vars(host.vars, self.get_host_vars(host, new_pb_basedir=True))
                host.vars = combine_vars(host.vars, self.get_host_vars(host))
            # invalidate cache
            self._vars_per_host = {}
            self._vars_per_group = {}

    def get_host_vars(self, host, new_pb_basedir=False):
        """ Read host_vars/ files """
        return self._get_hostgroup_vars(host=host, group=None, new_pb_basedir=new_pb_basedir)

    def get_group_vars(self, group, new_pb_basedir=False):
        """ Read group_vars/ files """
        return self._get_hostgroup_vars(host=None, group=group, new_pb_basedir=new_pb_basedir)

    def _get_hostgroup_vars(self, host=None, group=None, new_pb_basedir=False):
        """
        Loads variables from group_vars/<groupname> and host_vars/<hostname> in directories parallel
        to the inventory base directory or in the same directory as the playbook.  Variables in the playbook
        dir will win over the inventory dir if files are in both.
        """

        results = {}
        scan_pass = 0
        _basedir = self.basedir()
        # look in both the inventory base directory and the playbook base directory
        else:
            basedirs = [self._playbook_basedir]

        # unless we do an update for a new playbook base dir
        if not new_pb_basedir:
            basedirs = [_basedir, self._playbook_basedir]

        for basedir in basedirs:
            display.debug('getting vars from %s' % basedir)

            # this can happen from particular API usages, particularly if not run
            # from /usr/bin/ansible-playbook
            if basedir is None:
                basedir = './'


            scan_pass = scan_pass + 1
            # it's not an eror if the directory does not exist, keep moving
            if not os.path.exists(basedir):
                continue

            # save work of second scan if the directories are the same
            if _basedir == self._playbook_basedir and scan_pass != 1:
                continue

            # FIXME: these should go to VariableManager
            if group and host is None:
                # load vars in dir/group_vars/name_of_group
                base_path = os.path.realpath(os.path.join(basedir, "group_vars/%s" % group.name))
                results = self._variable_manager.add_group_vars_file(base_path, self._loader)
            elif host and group is None:
                # same for hostvars in dir/host_vars/name_of_host
                base_path = os.path.realpath(os.path.join(basedir, "host_vars/%s" % host.name))
                results = self._variable_manager.add_host_vars_file(base_path, self._loader)

        # all done, results is a dictionary of variables for this particular host.
        return results
    def refresh_inventory(self):
        self.clear_pattern_cache()

        self._hosts_cache    = {}
        self._vars_per_host  = {}
        self._vars_per_group = {}
        self._groups_list    = {}
        self._groups_cache   = {}
        self.groups = []
        self.parse_inventory(self.host_list)

