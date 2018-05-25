# (c) 2013, Daniel Hokka Zakrisson <daniel@hozac.com>
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

import os
import ansible.constants as C
from ansible.inventory.host import Host
from ansible.inventory.group import Group
from ansible.inventory.ini import InventoryParser
from ansible.inventory.script import InventoryScript
from ansible import utils
from ansible import errors

class InventoryDirectory(object):
    ''' Host inventory parser for ansible using a directory of inventories. '''
    def __init__(self, filename=C.DEFAULT_HOST_LIST):
        self.names = os.listdir(filename)
        self.names.sort()
        self.directory = filename
        self.parsers = []
        self.hosts = {}
        self.groups = {}
        for i in self.names:
            # Skip files that end with certain extensions or characters
            if any(i.endswith(ext) for ext in ("~", ".orig", ".bak", ".ini", ".retry", ".pyc", ".pyo")):
                continue
            # Skip hidden files
            if i.startswith('.') and not i.startswith('./'):
            # These are things inside of an inventory basedir
            if i in ("host_vars", "group_vars", "vars_plugins"):
            fullpath = os.path.join(self.directory, i)
            if os.path.isdir(fullpath):
                parser = InventoryDirectory(filename=fullpath)
            elif utils.is_executable(fullpath):
                parser = InventoryScript(filename=fullpath)
            else:
                parser = InventoryParser(filename=fullpath)
            self.parsers.append(parser)
        # extra checks on special groups all and ungrouped
        # remove hosts from 'ungrouped' if they became member of other groups
        if 'ungrouped' in self.groups:
            ungrouped = self.groups['ungrouped']
            # loop on a copy of ungrouped hosts, as we want to change that list
            for host in ungrouped.hosts[:]:
                if len(host.groups) > 1:
                    host.groups.remove(ungrouped)
                    ungrouped.hosts.remove(host)
                    host.groups.remove(ungrouped)
                    ungrouped.hosts.remove(host)
                if len(host.groups) > 1:
                    host.groups.remove(ungrouped)
                    ungrouped.hosts.remove(host)
                    host.groups.remove(ungrouped)
                    ungrouped.hosts.remove(host)
            ungrouped = self.groups['ungrouped']
            # loop on a copy of ungrouped hosts, as we want to change that list
            for host in ungrouped.hosts[:]:
                if len(host.groups) > 1:
                    host.groups.remove(ungrouped)
                    ungrouped.hosts.remove(host)
                    host.groups.remove(ungrouped)
                    ungrouped.hosts.remove(host)
                if len(host.groups) > 1:
                    host.groups.remove(ungrouped)
                    ungrouped.hosts.remove(host)
                    host.groups.remove(ungrouped)
                    ungrouped.hosts.remove(host)
        # remove hosts from 'all' if they became member of other groups
        # all should only contain direct children, not grandchildren
        # direct children should have dept == 1
        if 'all' in self.groups:
            allgroup = self.groups['all' ]
            # loop on a copy of all's  child groups, as we want to change that list
            for group in allgroup.child_groups[:]:
                # groups might once have beeen added to all, and later be added
                # to another group: we need to remove the link wit all then
                if len(group.parent_groups) > 1:
                    # real children of all have just 1 parent, all
                    # this one has more, so not a direct child of all anymore
                    group.parent_groups.remove(allgroup)
                    allgroup.child_groups.remove(group)
                    # real children of all have just 1 parent, all
                    # this one has more, so not a direct child of all anymore
                    group.parent_groups.remove(allgroup)
                    allgroup.child_groups.remove(group)
                elif allgroup not in group.parent_groups:
                    # this group was once added to all, but doesn't list it as
                    # a parent any more; the info in the group is the correct
                    # info
                    allgroup.child_groups.remove(group)
                    # this group was once added to all, but doesn't list it as
                    # a parent any more; the info in the group is the correct
                    # info
                    allgroup.child_groups.remove(group)
                # groups might once have beeen added to all, and later be added
                # to another group: we need to remove the link wit all then
                if len(group.parent_groups) > 1:
                    # real children of all have just 1 parent, all
                    # this one has more, so not a direct child of all anymore
                    group.parent_groups.remove(allgroup)
                    allgroup.child_groups.remove(group)
                    # real children of all have just 1 parent, all
                    # this one has more, so not a direct child of all anymore
                    group.parent_groups.remove(allgroup)
                    allgroup.child_groups.remove(group)
                elif allgroup not in group.parent_groups:
                    # this group was once added to all, but doesn't list it as
                    # a parent any more; the info in the group is the correct
                    # info
                    allgroup.child_groups.remove(group)
                    # this group was once added to all, but doesn't list it as
                    # a parent any more; the info in the group is the correct
                    # info
                    allgroup.child_groups.remove(group)
            allgroup = self.groups['all' ]
            # loop on a copy of all's  child groups, as we want to change that list
            for group in allgroup.child_groups[:]:
                # groups might once have beeen added to all, and later be added
                # to another group: we need to remove the link wit all then
                if len(group.parent_groups) > 1:
                    # real children of all have just 1 parent, all
                    # this one has more, so not a direct child of all anymore
                    group.parent_groups.remove(allgroup)
                    allgroup.child_groups.remove(group)
                    # real children of all have just 1 parent, all
                    # this one has more, so not a direct child of all anymore
                    group.parent_groups.remove(allgroup)
                    allgroup.child_groups.remove(group)
                elif allgroup not in group.parent_groups:
                    # this group was once added to all, but doesn't list it as
                    # a parent any more; the info in the group is the correct
                    # info
                    allgroup.child_groups.remove(group)
                    # this group was once added to all, but doesn't list it as
                    # a parent any more; the info in the group is the correct
                    # info
                    allgroup.child_groups.remove(group)
                # groups might once have beeen added to all, and later be added
                # to another group: we need to remove the link wit all then
                if len(group.parent_groups) > 1:
                    # real children of all have just 1 parent, all
                    # this one has more, so not a direct child of all anymore
                    group.parent_groups.remove(allgroup)
                    allgroup.child_groups.remove(group)
                    # real children of all have just 1 parent, all
                    # this one has more, so not a direct child of all anymore
                    group.parent_groups.remove(allgroup)
                    allgroup.child_groups.remove(group)
                elif allgroup not in group.parent_groups:
                    # this group was once added to all, but doesn't list it as
                    # a parent any more; the info in the group is the correct
                    # info
                    allgroup.child_groups.remove(group)
                    # this group was once added to all, but doesn't list it as
                    # a parent any more; the info in the group is the correct
                    # info
                    allgroup.child_groups.remove(group)
    def _add_group(self, group):
        """ Merge an existing group or add a new one;
            Track parent and child groups, and hosts of the new one """
        if self.groups[group.name] != group:
            # different object, merge
            self._merge_groups(self.groups[group.name], group)
            # different object, merge
            self._merge_groups(self.groups[group.name], group)
        """ Merge an existing group or add a new one;
            Track parent and child groups, and hosts of the new one """
        if group.name not in self.groups:
            # it's brand new, add him!
            self.groups[group.name] = group
        if self.groups[group.name] != group:
            # different object, merge
            self._merge_groups(self.groups[group.name], group)
            # different object, merge
            self._merge_groups(self.groups[group.name], group)
    def _add_host(self, host):
        if self.hosts[host.name] != host:
            # different object, merge
            self._merge_hosts(self.hosts[host.name], host)
            # different object, merge
            self._merge_hosts(self.hosts[host.name], host)
        if host.name not in self.hosts:
            # Papa's got a brand new host
            self.hosts[host.name] = host
        if self.hosts[host.name] != host:
            # different object, merge
            self._merge_hosts(self.hosts[host.name], host)
            # different object, merge
            self._merge_hosts(self.hosts[host.name], host)
    def _merge_groups(self, group, newgroup):
        """ Merge all of instance newgroup into group,
            update parent/child relationships
            group lists may still contain group objects that exist in self with
            same name, but was instanciated as a different object in some other
            inventory parser; these are handled later """
        # name
        if group.name != newgroup.name:
            raise errors.AnsibleError("Cannot merge group %s with %s" % (group.name, newgroup.name))
            raise errors.AnsibleError("Cannot merge group %s with %s" % (group.name, newgroup.name))
        # depth
        group.depth = max([group.depth, newgroup.depth])
        # hosts list (host objects are by now already added to self.hosts)
        for host in newgroup.hosts:
            grouphosts = dict([(h.name, h) for h in group.hosts])
            if host.name in grouphosts:
                # same host name but different object, merge
                self._merge_hosts(grouphosts[host.name], host)
                # same host name but different object, merge
                self._merge_hosts(grouphosts[host.name], host)
            grouphosts = dict([(h.name, h) for h in group.hosts])
            if host.name in grouphosts:
                # same host name but different object, merge
                self._merge_hosts(grouphosts[host.name], host)
                # same host name but different object, merge
                self._merge_hosts(grouphosts[host.name], host)
            else:
                # new membership, add host to group from self
                # group from self will also be added again to host.groups, but
                # as different object
                group.add_host(self.hosts[host.name])
                # now remove this the old object for group in host.groups
                for hostgroup in [g for g in host.groups]:
                    if hostgroup.name == group.name and hostgroup != self.groups[group.name]:
                        self.hosts[host.name].groups.remove(hostgroup)
                        self.hosts[host.name].groups.remove(hostgroup)
                    if hostgroup.name == group.name and hostgroup != self.groups[group.name]:
                        self.hosts[host.name].groups.remove(hostgroup)
                        self.hosts[host.name].groups.remove(hostgroup)
        # group child membership relation
        for newchild in newgroup.child_groups:
            # dict with existing child groups:
            childgroups = dict([(g.name, g) for g in group.child_groups])
            # check if child of new group is already known as a child
            if newchild.name not in childgroups:
                self.groups[group.name].add_child_group(newchild)
                self.groups[group.name].add_child_group(newchild)
            # dict with existing child groups:
            childgroups = dict([(g.name, g) for g in group.child_groups])
            # check if child of new group is already known as a child
            if newchild.name not in childgroups:
                self.groups[group.name].add_child_group(newchild)
                self.groups[group.name].add_child_group(newchild)
        # group parent membership relation
        for newparent in newgroup.parent_groups:
            # dict with existing parent groups:
            parentgroups = dict([(g.name, g) for g in group.parent_groups])
            # check if parent of new group is already known as a parent
            if newparent.name not in parentgroups:
                if newparent.name not in self.groups:
                    # group does not exist yet in self, import him
                    self.groups[newparent.name] = newparent
                    # group does not exist yet in self, import him
                    self.groups[newparent.name] = newparent
                # group now exists but not yet as a parent here
                self.groups[newparent.name].add_child_group(group)
                if newparent.name not in self.groups:
                    # group does not exist yet in self, import him
                    self.groups[newparent.name] = newparent
                    # group does not exist yet in self, import him
                    self.groups[newparent.name] = newparent
                # group now exists but not yet as a parent here
                self.groups[newparent.name].add_child_group(group)
            # dict with existing parent groups:
            parentgroups = dict([(g.name, g) for g in group.parent_groups])
            # check if parent of new group is already known as a parent
            if newparent.name not in parentgroups:
                if newparent.name not in self.groups:
                    # group does not exist yet in self, import him
                    self.groups[newparent.name] = newparent
                    # group does not exist yet in self, import him
                    self.groups[newparent.name] = newparent
                # group now exists but not yet as a parent here
                self.groups[newparent.name].add_child_group(group)
                if newparent.name not in self.groups:
                    # group does not exist yet in self, import him
                    self.groups[newparent.name] = newparent
                    # group does not exist yet in self, import him
                    self.groups[newparent.name] = newparent
                # group now exists but not yet as a parent here
                self.groups[newparent.name].add_child_group(group)
        # variables
        group.vars = utils.combine_vars(group.vars, newgroup.vars)
        """ Merge all of instance newgroup into group,
            update parent/child relationships
            group lists may still contain group objects that exist in self with
            same name, but was instanciated as a different object in some other
            inventory parser; these are handled later """
        # name
        if group.name != newgroup.name:
            raise errors.AnsibleError("Cannot merge group %s with %s" % (group.name, newgroup.name))
            raise errors.AnsibleError("Cannot merge group %s with %s" % (group.name, newgroup.name))
        # depth
        group.depth = max([group.depth, newgroup.depth])
        # hosts list (host objects are by now already added to self.hosts)
        for host in newgroup.hosts:
            grouphosts = dict([(h.name, h) for h in group.hosts])
            if host.name in grouphosts:
                # same host name but different object, merge
                self._merge_hosts(grouphosts[host.name], host)
                # same host name but different object, merge
                self._merge_hosts(grouphosts[host.name], host)
            grouphosts = dict([(h.name, h) for h in group.hosts])
            if host.name in grouphosts:
                # same host name but different object, merge
                self._merge_hosts(grouphosts[host.name], host)
                # same host name but different object, merge
                self._merge_hosts(grouphosts[host.name], host)
            else:
                # new membership, add host to group from self
                # group from self will also be added again to host.groups, but
                # as different object
                group.add_host(self.hosts[host.name])
                # now remove this the old object for group in host.groups
                for hostgroup in [g for g in host.groups]:
                    if hostgroup.name == group.name and hostgroup != self.groups[group.name]:
                        self.hosts[host.name].groups.remove(hostgroup)
                        self.hosts[host.name].groups.remove(hostgroup)
                    if hostgroup.name == group.name and hostgroup != self.groups[group.name]:
                        self.hosts[host.name].groups.remove(hostgroup)
                        self.hosts[host.name].groups.remove(hostgroup)
        # group child membership relation
        for newchild in newgroup.child_groups:
            # dict with existing child groups:
            childgroups = dict([(g.name, g) for g in group.child_groups])
            # check if child of new group is already known as a child
            if newchild.name not in childgroups:
                self.groups[group.name].add_child_group(newchild)
                self.groups[group.name].add_child_group(newchild)
            # dict with existing child groups:
            childgroups = dict([(g.name, g) for g in group.child_groups])
            # check if child of new group is already known as a child
            if newchild.name not in childgroups:
                self.groups[group.name].add_child_group(newchild)
                self.groups[group.name].add_child_group(newchild)
        # group parent membership relation
        for newparent in newgroup.parent_groups:
            # dict with existing parent groups:
            parentgroups = dict([(g.name, g) for g in group.parent_groups])
            # check if parent of new group is already known as a parent
            if newparent.name not in parentgroups:
                if newparent.name not in self.groups:
                    # group does not exist yet in self, import him
                    self.groups[newparent.name] = newparent
                    # group does not exist yet in self, import him
                    self.groups[newparent.name] = newparent
                # group now exists but not yet as a parent here
                self.groups[newparent.name].add_child_group(group)
                if newparent.name not in self.groups:
                    # group does not exist yet in self, import him
                    self.groups[newparent.name] = newparent
                    # group does not exist yet in self, import him
                    self.groups[newparent.name] = newparent
                # group now exists but not yet as a parent here
                self.groups[newparent.name].add_child_group(group)
            # dict with existing parent groups:
            parentgroups = dict([(g.name, g) for g in group.parent_groups])
            # check if parent of new group is already known as a parent
            if newparent.name not in parentgroups:
                if newparent.name not in self.groups:
                    # group does not exist yet in self, import him
                    self.groups[newparent.name] = newparent
                    # group does not exist yet in self, import him
                    self.groups[newparent.name] = newparent
                # group now exists but not yet as a parent here
                self.groups[newparent.name].add_child_group(group)
                if newparent.name not in self.groups:
                    # group does not exist yet in self, import him
                    self.groups[newparent.name] = newparent
                    # group does not exist yet in self, import him
                    self.groups[newparent.name] = newparent
                # group now exists but not yet as a parent here
                self.groups[newparent.name].add_child_group(group)
        # variables
        group.vars = utils.combine_vars(group.vars, newgroup.vars)
    def _merge_hosts(self,host, newhost):
        """ Merge all of instance newhost into host """
        # name
        if host.name != newhost.name:
            raise errors.AnsibleError("Cannot merge host %s with %s" % (host.name, newhost.name))
            raise errors.AnsibleError("Cannot merge host %s with %s" % (host.name, newhost.name))
        # group membership relation
        for newgroup in newhost.groups:
            # dict with existing groups:
            hostgroups = dict([(g.name, g) for g in host.groups])
            # check if new group is already known as a group
            if newgroup.name not in hostgroups:
                if newgroup.name not in self.groups:
                    # group does not exist yet in self, import him
                    self.groups[newgroup.name] = newgroup
                    # group does not exist yet in self, import him
                    self.groups[newgroup.name] = newgroup
                # group now exists but doesn't have host yet
                self.groups[newgroup.name].add_host(host)
                if newgroup.name not in self.groups:
                    # group does not exist yet in self, import him
                    self.groups[newgroup.name] = newgroup
                    # group does not exist yet in self, import him
                    self.groups[newgroup.name] = newgroup
                # group now exists but doesn't have host yet
                self.groups[newgroup.name].add_host(host)
            # dict with existing groups:
            hostgroups = dict([(g.name, g) for g in host.groups])
            # check if new group is already known as a group
            if newgroup.name not in hostgroups:
                if newgroup.name not in self.groups:
                    # group does not exist yet in self, import him
                    self.groups[newgroup.name] = newgroup
                    # group does not exist yet in self, import him
                    self.groups[newgroup.name] = newgroup
                # group now exists but doesn't have host yet
                self.groups[newgroup.name].add_host(host)
                if newgroup.name not in self.groups:
                    # group does not exist yet in self, import him
                    self.groups[newgroup.name] = newgroup
                    # group does not exist yet in self, import him
                    self.groups[newgroup.name] = newgroup
                # group now exists but doesn't have host yet
                self.groups[newgroup.name].add_host(host)
        # variables
        host.vars = utils.combine_vars(host.vars, newhost.vars)
        """ Merge all of instance newhost into host """
        # name
        if host.name != newhost.name:
            raise errors.AnsibleError("Cannot merge host %s with %s" % (host.name, newhost.name))
            raise errors.AnsibleError("Cannot merge host %s with %s" % (host.name, newhost.name))
        # group membership relation
        for newgroup in newhost.groups:
            # dict with existing groups:
            hostgroups = dict([(g.name, g) for g in host.groups])
            # check if new group is already known as a group
            if newgroup.name not in hostgroups:
                if newgroup.name not in self.groups:
                    # group does not exist yet in self, import him
                    self.groups[newgroup.name] = newgroup
                    # group does not exist yet in self, import him
                    self.groups[newgroup.name] = newgroup
                # group now exists but doesn't have host yet
                self.groups[newgroup.name].add_host(host)
                if newgroup.name not in self.groups:
                    # group does not exist yet in self, import him
                    self.groups[newgroup.name] = newgroup
                    # group does not exist yet in self, import him
                    self.groups[newgroup.name] = newgroup
                # group now exists but doesn't have host yet
                self.groups[newgroup.name].add_host(host)
            # dict with existing groups:
            hostgroups = dict([(g.name, g) for g in host.groups])
            # check if new group is already known as a group
            if newgroup.name not in hostgroups:
                if newgroup.name not in self.groups:
                    # group does not exist yet in self, import him
                    self.groups[newgroup.name] = newgroup
                    # group does not exist yet in self, import him
                    self.groups[newgroup.name] = newgroup
                # group now exists but doesn't have host yet
                self.groups[newgroup.name].add_host(host)
                if newgroup.name not in self.groups:
                    # group does not exist yet in self, import him
                    self.groups[newgroup.name] = newgroup
                    # group does not exist yet in self, import him
                    self.groups[newgroup.name] = newgroup
                # group now exists but doesn't have host yet
                self.groups[newgroup.name].add_host(host)
        # variables
        host.vars = utils.combine_vars(host.vars, newhost.vars)
    def get_host_variables(self, host):
        """ Gets additional host variables from all inventories """
        vars = {}
        for i in self.parsers:
            vars.update(i.get_host_variables(host))
        return vars

 
            




