#!/usr/bin/env python

'''
EC2 external inventory script
=================================

Generates inventory that Ansible can understand by making API request to
AWS EC2 using the Boto library.

NOTE: This script assumes Ansible is being executed where the environment
variables needed for Boto have already been set:
    export AWS_ACCESS_KEY_ID='AK123'
    export AWS_SECRET_ACCESS_KEY='abc123'

This script also assumes there is an ec2.ini file alongside it.  To specify a
different path to ec2.ini, define the EC2_INI_PATH environment variable:
    export EC2_INI_PATH=/path/to/my_ec2.ini



# (c) 2012, Peter Sankauskas
#
# This file is part of Ansible,
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

######################################################################

import sys
import os
import argparse
import re
from time import time
import boto
from boto import ec2
from boto import rds
from boto import elasticache
from boto import route53
import six

from six.moves import configparser
from collections import defaultdict

try:
    import json
except ImportError:
    import simplejson as json


class Ec2Inventory(object):
    def _empty_inventory(self):
        return {"_meta" : {"hostvars" : {}}}
    def __init__(self):
        ''' Main execution path '''
        # Inventory grouped by instance IDs, tags, security groups, regions,
        # and availability zones
        self.inventory = self._empty_inventory()
        # Index of hostname (address) to instance ID
        self.index = {}
        # Boto profile to use (if any)
        self.boto_profile = None
        # Read settings and parse CLI arguments
        self.read_settings()
        self.parse_cli_args()
        # Make sure that profile_name is not passed at all if not set
        # as pre 2.24 boto will fall over otherwise
        if self.boto_profile:
            if not hasattr(boto.ec2.EC2Connection, 'profile_name'):
                self.fail_with_error("boto version must be >= 2.24 to use profile")
                self.fail_with_error("boto version must be >= 2.24 to use profile")
            if not hasattr(boto.ec2.EC2Connection, 'profile_name'):
                self.fail_with_error("boto version must be >= 2.24 to use profile")
                self.fail_with_error("boto version must be >= 2.24 to use profile")
        # Cache
        if self.args.refresh_cache:
            self.do_api_calls_update_cache()
        elif not self.is_cache_valid():
            self.do_api_calls_update_cache()
        # Data to print
        if self.args.host:
            data_to_print = self.get_host_info()
        elif self.args.list:
            # Display list of instances for inventory
            if self.inventory == self._empty_inventory():
                data_to_print = self.get_inventory_from_cache()
            else:
                data_to_print = self.json_format_dict(self.inventory, True)
        print(data_to_print)
    def is_cache_valid(self):
        ''' Determines if the cache files have expired, or if it is still valid '''
        if os.path.isfile(self.cache_path_cache):
            mod_time = os.path.getmtime(self.cache_path_cache)
            current_time = time()
            if (mod_time + self.cache_max_age) > current_time:
                if os.path.isfile(self.cache_path_index):
                    return True
        return False
    def read_settings(self):
        ''' Reads the settings from the ec2.ini file '''
        if six.PY3:
        else:
            config = configparser.SafeConfigParser()
            config = configparser.ConfigParser()
        ec2_default_ini_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'ec2.ini')
        ec2_ini_path = os.path.expanduser(os.path.expandvars(os.environ.get('EC2_INI_PATH', ec2_default_ini_path)))
        config.read(ec2_ini_path)
        # is eucalyptus?
        self.eucalyptus_host = None
        self.eucalyptus = False
        if config.has_option('ec2', 'eucalyptus'):
            self.eucalyptus = config.getboolean('ec2', 'eucalyptus')
        if self.eucalyptus and config.has_option('ec2', 'eucalyptus_host'):
            self.eucalyptus_host = config.get('ec2', 'eucalyptus_host')
        # Regions
        self.regions = []
        configRegions = config.get('ec2', 'regions')
        configRegions_exclude = config.get('ec2', 'regions_exclude')
        if (configRegions == 'all'):
            if self.eucalyptus_host:
                self.regions.append(boto.connect_euca(host=self.eucalyptus_host).region.name)
            else:
                for regionInfo in ec2.regions():
                    if regionInfo.name not in configRegions_exclude:
                        self.regions.append(regionInfo.name)
        else:
            self.regions = configRegions.split(",")
        # Destination addresses
        self.destination_variable = config.get('ec2', 'destination_variable')
        self.vpc_destination_variable = config.get('ec2', 'vpc_destination_variable')
<<<<<<< REMOTE
if config.has_option('ec2', 'destination_format') and \
           config.has_option('ec2', 'destination_format_tags'):
=======
if config.has_option('ec2', 'hostname_variable'):
>>>>>>> LOCAL
        # Route53
        self.route53_enabled = config.getboolean('ec2', 'route53')
        self.route53_excluded_zones = []
        if config.has_option('ec2', 'route53_excluded_zones'):
            self.route53_excluded_zones.extend(
                config.get('ec2', 'route53_excluded_zones', '').split(','))
        # Include RDS instances?
        self.rds_enabled = True
        if config.has_option('ec2', 'rds'):
            self.rds_enabled = config.getboolean('ec2', 'rds')
        # Include ElastiCache instances?
        self.elasticache_enabled = True
        if config.has_option('ec2', 'elasticache'):
            self.elasticache_enabled = config.getboolean('ec2', 'elasticache')
        # Return all EC2 instances?
        if config.has_option('ec2', 'all_instances'):
            self.all_instances = config.getboolean('ec2', 'all_instances')
        else:
<<<<<<< REMOTE
self.destination_format = None
=======
self.hostname_variable = None
>>>>>>> LOCAL
            self.destination_format_tags = None
        # Return all RDS instances? (if RDS is enabled)
        # Instance states to be gathered in inventory. Default is 'running'.
        # Setting 'all_instances' to 'yes' overrides this option.
        ec2_valid_instance_states = [
            'pending',
            'running',
            'shutting-down',
            'terminated',
            'stopping',
            'stopped'
        if config.has_option('ec2', 'all_rds_instances') and self.rds_enabled:
            self.all_rds_instances = config.getboolean('ec2', 'all_rds_instances')
        self.ec2_instance_states = []
        if self.all_instances:
            self.ec2_instance_states = ec2_valid_instance_states
            self.ec2_instance_states = ec2_valid_instance_states
        elif config.has_option('ec2', 'instance_states'):
          for instance_state in config.get('ec2', 'instance_states').split(','):
            instance_state = instance_state.strip()
            if instance_state not in ec2_valid_instance_states:
              continue
            self.ec2_instance_states.append(instance_state)
        else:
<<<<<<< REMOTE
self.all_instances = False
=======
self.all_instances = False
>>>>>>> LOCAL
        # Return all ElastiCache replication groups? (if ElastiCache is enabled)
        if config.has_option('ec2', 'all_elasticache_replication_groups') and self.elasticache_enabled:
            self.all_elasticache_replication_groups = config.getboolean('ec2', 'all_elasticache_replication_groups')
        else:
<<<<<<< REMOTE
self.all_rds_instances = False
=======
self.ec2_instance_states = ['running']
>>>>>>> LOCAL
        # Return all ElastiCache clusters? (if ElastiCache is enabled)
        if config.has_option('ec2', 'all_elasticache_clusters') and self.elasticache_enabled:
            self.all_elasticache_clusters = config.getboolean('ec2', 'all_elasticache_clusters')
        else:
<<<<<<< REMOTE
self.all_elasticache_replication_groups = False
=======
self.all_rds_instances = False
>>>>>>> LOCAL
        # Return all ElastiCache nodes? (if ElastiCache is enabled)
        if config.has_option('ec2', 'all_elasticache_nodes') and self.elasticache_enabled:
            self.all_elasticache_nodes = config.getboolean('ec2', 'all_elasticache_nodes')
        else:
<<<<<<< REMOTE
self.all_elasticache_clusters = False
=======
self.all_elasticache_replication_groups = False
>>>>>>> LOCAL
        # Cache related
        # boto configuration profile (prefer CLI argument)
        self.boto_profile = self.args.boto_profile
        if config.has_option('ec2', 'boto_profile') and not self.boto_profile:
            self.boto_profile = config.get('ec2', 'boto_profile')
            self.boto_profile = config.get('ec2', 'boto_profile')
        cache_dir = os.path.expanduser(config.get('ec2', 'cache_path'))
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        if self.boto_profile:
            cache_dir = os.path.join(cache_dir, 'profile_' + self.boto_profile)
            cache_dir = os.path.join(cache_dir, 'profile_' + self.boto_profile)
        self.cache_path_cache = cache_dir + "/ansible-ec2.cache"
        self.cache_path_index = cache_dir + "/ansible-ec2.index"
        self.cache_max_age = config.getint('ec2', 'cache_max_age')
        # Configure nested groups instead of flat namespace.
        if config.has_option('ec2', 'expand_csv_tags'):
            self.expand_csv_tags = config.getboolean('ec2', 'expand_csv_tags')
            self.expand_csv_tags = config.getboolean('ec2', 'expand_csv_tags')
        if config.has_option('ec2', 'nested_groups'):
            self.nested_groups = config.getboolean('ec2', 'nested_groups')
        else:
<<<<<<< REMOTE
self.all_elasticache_nodes = False
=======
self.all_elasticache_clusters = False
>>>>>>> LOCAL
        # Replace dash or not in group names
        if config.has_option('ec2', 'replace_dash_in_groups'):
            self.replace_dash_in_groups = config.getboolean('ec2', 'replace_dash_in_groups')
            self.replace_dash_in_groups = config.getboolean('ec2', 'replace_dash_in_groups')
        else:
<<<<<<< REMOTE
self.pattern_exclude = None
=======
self.replace_dash_in_groups = True
>>>>>>> LOCAL
        # Configure which groups should be created.
        group_by_options = [
            'group_by_instance_id',
            'group_by_region',
            'group_by_availability_zone',
            'group_by_ami_id',
            'group_by_instance_type',
            'group_by_key_pair',
            'group_by_vpc_id',
            'group_by_security_group',
            'group_by_tag_keys',
            'group_by_tag_none',
            'group_by_route53_names',
            'group_by_rds_engine',
            'group_by_rds_parameter_group',
            'group_by_elasticache_engine',
            'group_by_elasticache_cluster',
            'group_by_elasticache_parameter_group',
            'group_by_elasticache_replication_group',
        ]
        ]
        for option in group_by_options:
            if config.has_option('ec2', option):
                setattr(self, option, config.getboolean('ec2', option))
<<<<<<< REMOTE
else:
=======
else:
>>>>>>> LOCAL
            else:
<<<<<<< REMOTE
self.nested_groups = False
=======
self.all_elasticache_nodes = False
>>>>>>> LOCAL
        # Do we need to just include hosts that match a pattern?
        try:
            pattern_include = config.get('ec2', 'pattern_include')
            if pattern_include and len(pattern_include) > 0:
                self.pattern_include = re.compile(pattern_include)
<<<<<<< REMOTE
else:
=======
else:
>>>>>>> LOCAL
            else:
<<<<<<< REMOTE
setattr(self, option, True)
=======
self.expand_csv_tags = False
>>>>>>> LOCAL
        except configparser.NoOptionError:
            self.pattern_include = None
        # Do we need to exclude hosts that match a pattern?
        try:
            pattern_exclude = config.get('ec2', 'pattern_exclude');
            if pattern_exclude and len(pattern_exclude) > 0:
                self.pattern_exclude = re.compile(pattern_exclude)
<<<<<<< REMOTE
else:
=======
else:
>>>>>>> LOCAL
            else:
<<<<<<< REMOTE
self.pattern_include = None
=======
self.nested_groups = False
>>>>>>> LOCAL
        except configparser.NoOptionError:
            self.pattern_exclude = None
        # Instance filters (see boto and EC2 API docs). Ignore invalid filters.
        self.ec2_instance_filters = defaultdict(list)
        if config.has_option('ec2', 'instance_filters'):
            filters = [f for f in config.get('ec2', 'instance_filters').split(',') if f]
            for instance_filter in filters:
                instance_filter = instance_filter.strip()
                if not instance_filter or '=' not in instance_filter:
                    continue
                filter_key, filter_value = [x.strip() for x in instance_filter.split('=', 1)]
                if not filter_key:
                    continue
                self.ec2_instance_filters[filter_key].append(filter_value)
                instance_filter = instance_filter.strip()
                if not instance_filter or '=' not in instance_filter:
                    continue
                filter_key, filter_value = [x.strip() for x in instance_filter.split('=', 1)]
                if not filter_key:
                    continue
                self.ec2_instance_filters[filter_key].append(filter_value)
          for instance_state in config.get('ec2', 'instance_states').split(','):
            instance_state = instance_state.strip()
            if instance_state not in ec2_valid_instance_states:
              continue
            self.ec2_instance_states.append(instance_state)
    def parse_cli_args(self):
        ''' Command line argument processing '''
        parser = argparse.ArgumentParser(description='Produce an Ansible Inventory file based on EC2')
        parser.add_argument('--list', action='store_true', default=True,
                           help='List instances (default: True)')
        parser.add_argument('--host', action='store',
                           help='Get all the variables about a specific instance')
        parser.add_argument('--refresh-cache', action='store_true', default=False,
                           help='Force refresh of cache by making API requests to EC2 (default: False - use cache files)')
        parser.add_argument('--profile', '--boto-profile', action='store', dest='boto_profile',
                           help='Use boto profile for connections to EC2')
        self.args = parser.parse_args()
    def do_api_calls_update_cache(self):
        ''' Do API calls to each region, and save data in cache files '''
        if self.route53_enabled:
            self.get_route53_records()
        for region in self.regions:
            self.get_instances_by_region(region)
            if self.rds_enabled:
                self.get_rds_instances_by_region(region)
            if self.elasticache_enabled:
                self.get_elasticache_clusters_by_region(region)
                self.get_elasticache_replication_groups_by_region(region)
        self.write_to_cache(self.inventory, self.cache_path_cache)
        self.write_to_cache(self.index, self.cache_path_index)
    def connect(self, region):
        ''' create connection to api server'''
        if self.eucalyptus:
            conn = boto.connect_euca(host=self.eucalyptus_host)
            conn.APIVersion = '2010-08-31'
<<<<<<< REMOTE
else:
=======
else:
>>>>>>> LOCAL
        # connect_to_region will fail "silently" by returning None if the region name is wrong or not supported
        if conn is None:
            self.fail_with_error("region name: %s likely not supported, or AWS is down.  connection to region failed." % region)
        return conn
    def get_instances_by_region(self, region):
        ''' Makes an AWS EC2 API call to the list of instances in a particular
        region '''
        try:
            conn = self.connect(region)
            reservations = []
            if self.ec2_instance_filters:
                for filter_key, filter_values in self.ec2_instance_filters.items():
                    reservations.extend(conn.get_all_instances(filters = { filter_key : filter_values }))
<<<<<<< REMOTE
else:
=======
else:
>>>>>>> LOCAL
            for reservation in reservations:
                for instance in reservation.instances:
                    self.add_instance(instance, region)
        except boto.exception.BotoServerError as e:
            if e.error_code == 'AuthFailure':
                error = self.get_auth_error_message()
<<<<<<< REMOTE
else:
=======
else:
>>>>>>> LOCAL
            self.fail_with_error(error, 'getting EC2 instances')
    def get_rds_instances_by_region(self, region):
        ''' Makes an AWS API call to the list of RDS instances in a particular
        region '''
        try:
            if conn:
        except boto.exception.BotoServerError as e:
            error = e.reason
            if e.error_code == 'AuthFailure':
                error = self.get_auth_error_message()
            if not e.reason == "Forbidden":
                error = "Looks like AWS RDS is down:\n%s" % e.message
    def get_elasticache_clusters_by_region(self, region):
        ''' Makes an AWS API call to the list of ElastiCache clusters (with
        nodes' info) in a particular region.'''
        # ElastiCache boto module doesn't provide a get_all_intances method,
        # that's why we need to call describe directly (it would be called by
        # the shorthand method anyway...)
        try:
            if conn:
                # show_cache_node_info = True
                # because we also want nodes' information
                response = conn.describe_cache_clusters(None, None, None, True)
        except boto.exception.BotoServerError as e:
            error = e.reason
            if e.error_code == 'AuthFailure':
                error = self.get_auth_error_message()
            if not e.reason == "Forbidden":
                error = "Looks like AWS ElastiCache is down:\n%s" % e.message
            self.fail_with_error(error, 'getting ElastiCache clusters')
        try:
            # Boto also doesn't provide wrapper classes to CacheClusters or
            # CacheNodes. Because of that wo can't make use of the get_list
            # method in the AWSQueryConnection. Let's do the work manually
            clusters = response['DescribeCacheClustersResponse']['DescribeCacheClustersResult']['CacheClusters']
        except KeyError as e:
            error = "ElastiCache query to AWS failed (unexpected format)."
            self.fail_with_error(error, 'getting ElastiCache clusters')
        for cluster in clusters:
            self.add_elasticache_cluster(cluster, region)
    def get_elasticache_replication_groups_by_region(self, region):
        ''' Makes an AWS API call to the list of ElastiCache replication groups
        in a particular region.'''
        # ElastiCache boto module doesn't provide a get_all_intances method,
        # that's why we need to call describe directly (it would be called by
        # the shorthand method anyway...)
        try:
            conn = self.connect_to_aws(elasticache, region)
            if conn:
                response = conn.describe_replication_groups()
        except boto.exception.BotoServerError as e:
            error = e.reason
            if e.error_code == 'AuthFailure':
                error = self.get_auth_error_message()
            if not e.reason == "Forbidden":
                error = "Looks like AWS ElastiCache [Replication Groups] is down:\n%s" % e.message
            self.fail_with_error(error, 'getting ElastiCache clusters')
        try:
            # Boto also doesn't provide wrapper classes to ReplicationGroups
            # Because of that wo can't make use of the get_list method in the
            # AWSQueryConnection. Let's do the work manually
            replication_groups = response['DescribeReplicationGroupsResponse']['DescribeReplicationGroupsResult']['ReplicationGroups']
        except KeyError as e:
            error = "ElastiCache [Replication Groups] query to AWS failed (unexpected format)."
            self.fail_with_error(error, 'getting ElastiCache clusters')
        for replication_group in replication_groups:
            self.add_elasticache_replication_group(replication_group, region)
    def get_auth_error_message(self):
        ''' create an informative error message if there is an issue authenticating'''
        errors = ["Authentication error retrieving ec2 inventory."]
        if None in [os.environ.get('AWS_ACCESS_KEY_ID'), os.environ.get('AWS_SECRET_ACCESS_KEY')]:
            errors.append(' - No AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY environment vars found')
        else:
<<<<<<< REMOTE
key = self.to_safe("tag_" + k)
=======
errors.append(' - AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment vars found but may not be correct')
>>>>>>> LOCAL
            # Redis sigle node cluster
            # Because all Redis clusters are single nodes, we'll merge the
            # info from the cluster with info about the node
            dest = cluster['CacheNodes'][0]['Endpoint']['Address']
            is_redis = True
        boto_paths = ['/etc/boto.cfg', '~/.boto', '~/.aws/credentials']
        boto_config_found = list(p for p in boto_paths if os.path.isfile(os.path.expanduser(p)))
<<<<<<< REMOTE
else:
=======
else:
>>>>>>> LOCAL
        if len(boto_config_found) > 0:
            errors.append(" - Boto configs found at '%s', but the credentials contained may not be correct" % ', '.join(boto_config_found))
        return '\n'.join(errors)
    def get_instance(self, region, instance_id):
        conn = self.connect(region)
        reservations = conn.get_all_instances([instance_id])
        for reservation in reservations:
            for instance in reservation.instances:
                return instance
    def add_instance(self, instance, region):
        ''' Adds an instance to the inventory and index, as long as it is
        addressable '''
        # Only return instances with desired instance states
        if instance.state not in self.ec2_instance_states:
            return
        if self.destination_format and self.destination_format_tags:
            dest = self.destination_format.format(*[ getattr(instance, 'tags').get(tag, '') for tag in self.destination_format_tags ])
            dest = self.destination_format.format(*[ getattr(instance, 'tags').get(tag, '') for tag in self.destination_format_tags ])
<<<<<<< REMOTE
elif instance.subnet_id:
=======
else:
>>>>>>> LOCAL
        # Set the inventory name
        hostname = None
        if self.hostname_variable:
            if self.hostname_variable.startswith('tag_'):
                hostname = instance.tags.get(self.hostname_variable[4:], None)
                hostname = instance.tags.get(self.hostname_variable[4:], None)
            if self.hostname_variable.startswith('tag_'):
                hostname = instance.tags.get(self.hostname_variable[4:], None)
                hostname = instance.tags.get(self.hostname_variable[4:], None)
        # If we can't get a nice hostname, use the destination address
        if not hostname:
            hostname = dest
            hostname = dest
        hostname = self.to_safe(hostname).lower()
        # Select the best destination address
        if not dest:
            # Skip instances we cannot address (e.g. private VPC subnet)
            return
        # if we only want to include hosts that match a pattern, skip those that don't
        if self.pattern_include and not self.pattern_include.match(hostname):
            return
        # if we need to exclude hosts that match a pattern, skip those
        if self.pattern_exclude and self.pattern_exclude.match(hostname):
            return
        # Add to index
        self.index[hostname] = [region, instance.id]
        # Inventory: Group by instance ID (always a group of 1)
        if self.group_by_instance_id:
            self.inventory[instance.id] = [hostname]
            if self.nested_groups:
                self.push_group(self.inventory, 'instances', instance.id)
        # Inventory: Group by region
        if self.group_by_region:
            self.push(self.inventory, region, hostname)
            if self.nested_groups:
                self.push_group(self.inventory, 'regions', region)
        # Inventory: Group by availability zone
        if self.group_by_availability_zone:
            self.push(self.inventory, instance.placement, hostname)
            if self.nested_groups:
                if self.group_by_region:
                    self.push_group(self.inventory, region, instance.placement)
                self.push_group(self.inventory, 'zones', instance.placement)
        # Inventory: Group by Amazon Machine Image (AMI) ID
        if self.group_by_ami_id:
            ami_id = self.to_safe(instance.image_id)
            self.push(self.inventory, ami_id, hostname)
            if self.nested_groups:
                self.push_group(self.inventory, 'images', ami_id)
        # Inventory: Group by instance type
        if self.group_by_instance_type:
            type_name = self.to_safe('type_' + instance.instance_type)
            self.push(self.inventory, type_name, hostname)
            if self.nested_groups:
                self.push_group(self.inventory, 'types', type_name)
        # Inventory: Group by key pair
        if self.group_by_key_pair and instance.key_name:
            key_name = self.to_safe('key_' + instance.key_name)
            self.push(self.inventory, key_name, hostname)
            if self.nested_groups:
                self.push_group(self.inventory, 'keys', key_name)
        # Inventory: Group by VPC
        if self.group_by_vpc_id and instance.vpc_id:
            vpc_id_name = self.to_safe('vpc_id_' + instance.vpc_id)
            self.push(self.inventory, vpc_id_name, hostname)
            if self.nested_groups:
                self.push_group(self.inventory, 'vpcs', vpc_id_name)
        # Inventory: Group by security group
        if self.group_by_security_group:
            try:
                for group in instance.groups:
                    key = self.to_safe("security_group_" + group.name)
                    self.push(self.inventory, key, hostname)
                    if self.nested_groups:
                        self.push_group(self.inventory, 'security_groups', key)
            except AttributeError:
                self.fail_with_error('\n'.join(['Package boto seems a bit older.', 
                                            'Please upgrade boto >= 2.3.0.']))
        # Inventory: Group by tag keys
        if self.group_by_tag_keys:
            for k, v in instance.tags.items():
                if self.expand_csv_tags and v and ',' in v:
                    values = map(lambda x: x.strip(), v.split(','))
                    values = map(lambda x: x.strip(), v.split(','))
<<<<<<< REMOTE
else:
=======
else:
>>>>>>> LOCAL
                for v in values:
                        sg_ids.append(sg['SecurityGroupId'])
                if v:
                    key = self.to_safe("tag_" + k + "=" + v)
                else:
<<<<<<< REMOTE
dest = getattr(instance, self.destination_variable, None)
=======
backend = 'Eucalyptus' if self.eucalyptus else 'AWS'
>>>>>>> LOCAL
<<<<<<< REMOTE
if dest is None:
=======
error = "Error connecting to %s backend.\n%s" % (backend, e.message)
>>>>>>> LOCAL
                    self.push(self.inventory, key, hostname)
                if self.nested_groups:
                    self.push_group(self.inventory, 'tags', self.to_safe("tag_" + k))
                        if v:
                            self.push_group(self.inventory, self.to_safe("tag_" + k), key)
                    self.push_group(self.inventory, self.to_safe("tag_" + k), key)
        # Inventory: Group by Route53 domain names if enabled
        if self.route53_enabled and self.group_by_route53_names:
            route53_names = self.get_instance_route53_names(instance)
            for name in route53_names:
                self.push(self.inventory, name, hostname)
                if self.nested_groups:
                    self.push_group(self.inventory, 'route53', name)
        self.inventory["_meta"]["hostvars"][hostname]['ansible_ssh_host'] = dest
        # Global Tag: instances without tags
        if self.group_by_tag_none and len(instance.tags) == 0:
            self.push(self.inventory, 'tag_none', hostname)
            if self.nested_groups:
                self.push_group(self.inventory, 'tags', 'tag_none')
        # Global Tag: tag all EC2 instances
        self.push(self.inventory, 'ec2', hostname)
        self.inventory["_meta"]["hostvars"][hostname] = self.get_host_info_dict_from_instance(instance)
    def add_rds_instance(self, instance, region):
        ''' Adds an RDS instance to the inventory and index, as long as it is
        addressable '''
        # Only want available instances unless all_rds_instances is True
        if not self.all_rds_instances and instance.status != 'available':
            return
        # Select the best destination address
        dest = instance.endpoint[0]
        if not dest:
            # Skip instances we cannot address (e.g. private VPC subnet)
            return
        # Set the inventory name
        hostname = None
        if self.hostname_variable:
            if self.hostname_variable.startswith('tag_'):
                hostname = instance.tags.get(self.hostname_variable[4:], None)
                hostname = instance.tags.get(self.hostname_variable[4:], None)
            else:
                hostname = getattr(instance, self.hostname_variable)
                hostname = getattr(instance, self.hostname_variable)
            if self.hostname_variable.startswith('tag_'):
                hostname = instance.tags.get(self.hostname_variable[4:], None)
                hostname = instance.tags.get(self.hostname_variable[4:], None)
            else:
                hostname = getattr(instance, self.hostname_variable)
                hostname = getattr(instance, self.hostname_variable)
        # If we can't get a nice hostname, use the destination address
        if not hostname:
            hostname = dest
            hostname = dest
        hostname = self.to_safe(hostname).lower()
        # Add to index
        self.index[hostname] = [region, instance.id]
        # Inventory: Group by instance ID (always a group of 1)
        if self.group_by_instance_id:
            self.inventory[instance.id] = [hostname]
            if self.nested_groups:
                self.push_group(self.inventory, 'instances', instance.id)
        # Inventory: Group by region
        if self.group_by_region:
            self.push(self.inventory, region, hostname)
            if self.nested_groups:
                self.push_group(self.inventory, 'regions', region)
        # Inventory: Group by availability zone
        if self.group_by_availability_zone:
            self.push(self.inventory, instance.availability_zone, hostname)
            if self.nested_groups:
                if self.group_by_region:
                    self.push_group(self.inventory, region, instance.availability_zone)
                self.push_group(self.inventory, 'zones', instance.availability_zone)
        # Inventory: Group by instance type
        if self.group_by_instance_type:
            type_name = self.to_safe('type_' + instance.instance_class)
            self.push(self.inventory, type_name, hostname)
            if self.nested_groups:
                self.push_group(self.inventory, 'types', type_name)
        # Inventory: Group by VPC
        if self.group_by_vpc_id and instance.subnet_group and instance.subnet_group.vpc_id:
            vpc_id_name = self.to_safe('vpc_id_' + instance.subnet_group.vpc_id)
            self.push(self.inventory, vpc_id_name, hostname)
            if self.nested_groups:
                self.push_group(self.inventory, 'vpcs', vpc_id_name)
        # Inventory: Group by security group
        if self.group_by_security_group:
            try:
                if instance.security_group:
                    key = self.to_safe("security_group_" + instance.security_group.name)
                    self.push(self.inventory, key, hostname)
                    if self.nested_groups:
                        self.push_group(self.inventory, 'security_groups', key)
            except AttributeError:
                self.fail_with_error('\n'.join(['Package boto seems a bit older.', 
                                            'Please upgrade boto >= 2.3.0.']))
        # Inventory: Group by engine
        if self.group_by_rds_engine:
            self.push(self.inventory, self.to_safe("rds_" + instance.engine), hostname)
            if self.nested_groups:
                self.push_group(self.inventory, 'rds_engines', self.to_safe("rds_" + instance.engine))
        # Inventory: Group by parameter group
        if self.group_by_rds_parameter_group:
            self.push(self.inventory, self.to_safe("rds_parameter_group_" + instance.parameter_group.name), hostname)
            if self.nested_groups:
                self.push_group(self.inventory, 'rds_parameter_groups', self.to_safe("rds_parameter_group_" + instance.parameter_group.name))
        # Global Tag: all RDS instances
        self.push(self.inventory, 'rds', hostname)
        self.inventory["_meta"]["hostvars"][hostname] = self.get_host_info_dict_from_instance(instance)
        self.inventory["_meta"]["hostvars"][hostname]['ansible_ssh_host'] = dest
    def add_elasticache_cluster(self, cluster, region):
        ''' Adds an ElastiCache cluster to the inventory and index, as long as
        it's nodes are addressable '''
        # Only want available clusters unless all_elasticache_clusters is True
        if not self.all_elasticache_clusters and cluster['CacheClusterStatus'] != 'available':
            return
        # Select the best destination address
        if 'ConfigurationEndpoint' in cluster and cluster['ConfigurationEndpoint']:
            # Memcached cluster
            dest = cluster['ConfigurationEndpoint']['Address']
            is_redis = False
<<<<<<< REMOTE
else:
=======
else:
>>>>>>> LOCAL
        if not dest:
            # Skip clusters we cannot address (e.g. private VPC subnet)
            return
        # Add to index
        self.index[dest] = [region, cluster['CacheClusterId']]
        # Inventory: Group by instance ID (always a group of 1)
        if self.group_by_instance_id:
            self.inventory[cluster['CacheClusterId']] = [dest]
            if self.nested_groups:
                self.push_group(self.inventory, 'instances', cluster['CacheClusterId'])
        # Inventory: Group by region
        if self.group_by_region and not is_redis:
            self.push(self.inventory, region, dest)
            if self.nested_groups:
                self.push_group(self.inventory, 'regions', region)
        # Inventory: Group by availability zone
        if self.group_by_availability_zone and not is_redis:
            self.push(self.inventory, cluster['PreferredAvailabilityZone'], dest)
            if self.nested_groups:
                if self.group_by_region:
                    self.push_group(self.inventory, region, cluster['PreferredAvailabilityZone'])
                self.push_group(self.inventory, 'zones', cluster['PreferredAvailabilityZone'])
        # Inventory: Group by node type
        if self.group_by_instance_type and not is_redis:
            type_name = self.to_safe('type_' + cluster['CacheNodeType'])
            self.push(self.inventory, type_name, dest)
            if self.nested_groups:
                self.push_group(self.inventory, 'types', type_name)
        # Inventory: Group by VPC (information not available in the current
        # AWS API version for ElastiCache)
        # Inventory: Group by security group
        if self.group_by_security_group and not is_redis:
            # Check for the existence of the 'SecurityGroups' key and also if
            # this key has some value. When the cluster is not placed in a SG
            # the query can return None here and cause an error.
            if 'SecurityGroups' in cluster and cluster['SecurityGroups'] is not None:
                for security_group in cluster['SecurityGroups']:
                    key = self.to_safe("security_group_" + security_group['SecurityGroupId'])
                    self.push(self.inventory, key, dest)
                    if self.nested_groups:
                        self.push_group(self.inventory, 'security_groups', key)
        # Inventory: Group by engine
        if self.group_by_elasticache_engine and not is_redis:
            self.push(self.inventory, self.to_safe("elasticache_" + cluster['Engine']), dest)
            if self.nested_groups:
                self.push_group(self.inventory, 'elasticache_engines', self.to_safe(cluster['Engine']))
        # Inventory: Group by parameter group
        if self.group_by_elasticache_parameter_group:
            self.push(self.inventory, self.to_safe("elasticache_parameter_group_" + cluster['CacheParameterGroup']['CacheParameterGroupName']), dest)
            if self.nested_groups:
                self.push_group(self.inventory, 'elasticache_parameter_groups', self.to_safe(cluster['CacheParameterGroup']['CacheParameterGroupName']))
        # Inventory: Group by replication group
        if self.group_by_elasticache_replication_group and 'ReplicationGroupId' in cluster and cluster['ReplicationGroupId']:
            self.push(self.inventory, self.to_safe("elasticache_replication_group_" + cluster['ReplicationGroupId']), dest)
            if self.nested_groups:
                self.push_group(self.inventory, 'elasticache_replication_groups', self.to_safe(cluster['ReplicationGroupId']))
        # Global Tag: all ElastiCache clusters
        self.push(self.inventory, 'elasticache_clusters', cluster['CacheClusterId'])
        host_info = self.get_host_info_dict_from_describe_dict(cluster)
        self.inventory["_meta"]["hostvars"][dest] = host_info
        # Add the nodes
        for node in cluster['CacheNodes']:
            self.add_elasticache_node(node, cluster, region)
    def add_elasticache_node(self, node, cluster, region):
        ''' Adds an ElastiCache node to the inventory and index, as long as
        it is addressable '''
        # Only want available nodes unless all_elasticache_nodes is True
        if not self.all_elasticache_nodes and node['CacheNodeStatus'] != 'available':
            return
        # Select the best destination address
        dest = node['Endpoint']['Address']
        if not dest:
            # Skip nodes we cannot address (e.g. private VPC subnet)
            return
        node_id = self.to_safe(cluster['CacheClusterId'] + '_' + node['CacheNodeId'])
        # Add to index
        self.index[dest] = [region, node_id]
        # Inventory: Group by node ID (always a group of 1)
        if self.group_by_instance_id:
            self.inventory[node_id] = [dest]
            if self.nested_groups:
                self.push_group(self.inventory, 'instances', node_id)
        # Inventory: Group by region
        if self.group_by_region:
            self.push(self.inventory, region, dest)
            if self.nested_groups:
                self.push_group(self.inventory, 'regions', region)
        # Inventory: Group by availability zone
        if self.group_by_availability_zone:
            self.push(self.inventory, cluster['PreferredAvailabilityZone'], dest)
            if self.nested_groups:
                if self.group_by_region:
                    self.push_group(self.inventory, region, cluster['PreferredAvailabilityZone'])
                self.push_group(self.inventory, 'zones', cluster['PreferredAvailabilityZone'])
        # Inventory: Group by node type
        if self.group_by_instance_type:
            type_name = self.to_safe('type_' + cluster['CacheNodeType'])
            self.push(self.inventory, type_name, dest)
            if self.nested_groups:
                self.push_group(self.inventory, 'types', type_name)
        # Inventory: Group by VPC (information not available in the current
        # AWS API version for ElastiCache)
        # Inventory: Group by security group
        if self.group_by_security_group:
            # Check for the existence of the 'SecurityGroups' key and also if
            # this key has some value. When the cluster is not placed in a SG
            # the query can return None here and cause an error.
            if 'SecurityGroups' in cluster and cluster['SecurityGroups'] is not None:
                for security_group in cluster['SecurityGroups']:
                    key = self.to_safe("security_group_" + security_group['SecurityGroupId'])
                    self.push(self.inventory, key, dest)
                    if self.nested_groups:
                        self.push_group(self.inventory, 'security_groups', key)
        # Inventory: Group by engine
        if self.group_by_elasticache_engine:
            self.push(self.inventory, self.to_safe("elasticache_" + cluster['Engine']), dest)
            if self.nested_groups:
                self.push_group(self.inventory, 'elasticache_engines', self.to_safe("elasticache_" + cluster['Engine']))
        # Inventory: Group by parameter group (done at cluster level)
        # Inventory: Group by replication group (done at cluster level)
        # Inventory: Group by ElastiCache Cluster
        if self.group_by_elasticache_cluster:
            self.push(self.inventory, self.to_safe("elasticache_cluster_" + cluster['CacheClusterId']), dest)
        # Global Tag: all ElastiCache nodes
        self.push(self.inventory, 'elasticache_nodes', dest)
        host_info = self.get_host_info_dict_from_describe_dict(node)
        if dest in self.inventory["_meta"]["hostvars"]:
            self.inventory["_meta"]["hostvars"][dest].update(host_info)
<<<<<<< REMOTE
else:
=======
else:
>>>>>>> LOCAL
    def add_elasticache_replication_group(self, replication_group, region):
        ''' Adds an ElastiCache replication group to the inventory and index '''
        # Only want available clusters unless all_elasticache_replication_groups is True
        if not self.all_elasticache_replication_groups and replication_group['Status'] != 'available':
            return
        # Select the best destination address (PrimaryEndpoint)
        dest = replication_group['NodeGroups'][0]['PrimaryEndpoint']['Address']
        if not dest:
            # Skip clusters we cannot address (e.g. private VPC subnet)
            return
        # Add to index
        self.index[dest] = [region, replication_group['ReplicationGroupId']]
        # Inventory: Group by ID (always a group of 1)
        if self.group_by_instance_id:
            self.inventory[replication_group['ReplicationGroupId']] = [dest]
            if self.nested_groups:
                self.push_group(self.inventory, 'instances', replication_group['ReplicationGroupId'])
        # Inventory: Group by region
        if self.group_by_region:
            self.push(self.inventory, region, dest)
            if self.nested_groups:
                self.push_group(self.inventory, 'regions', region)
        # Inventory: Group by availability zone (doesn't apply to replication groups)
        # Inventory: Group by node type (doesn't apply to replication groups)
        # Inventory: Group by VPC (information not available in the current
        # AWS API version for replication groups
        # Inventory: Group by security group (doesn't apply to replication groups)
        # Check this value in cluster level
        # Inventory: Group by engine (replication groups are always Redis)
        if self.group_by_elasticache_engine:
            self.push(self.inventory, 'elasticache_redis', dest)
            if self.nested_groups:
                self.push_group(self.inventory, 'elasticache_engines', 'redis')
        # Global Tag: all ElastiCache clusters
        self.push(self.inventory, 'elasticache_replication_groups', replication_group['ReplicationGroupId'])
        host_info = self.get_host_info_dict_from_describe_dict(replication_group)
        self.inventory["_meta"]["hostvars"][dest] = host_info
    def get_route53_records(self):
        ''' Get and store the map of resource records to domain names that
        point to them. '''
        r53_conn = route53.Route53Connection()
        all_zones = r53_conn.get_zones()
        route53_zones = [ zone for zone in all_zones if zone.name[:-1]
                          not in self.route53_excluded_zones ]
        self.route53_records = {}
        for zone in route53_zones:
            rrsets = r53_conn.get_all_rrsets(zone.id)
            for record_set in rrsets:
                record_name = record_set.name
                if record_name.endswith('.'):
                    record_name = record_name[:-1]
                for resource in record_set.resource_records:
                    self.route53_records.setdefault(resource, set())
                    self.route53_records[resource].add(record_name)
    def get_instance_route53_names(self, instance):
        ''' Check if an instance is referenced in the records we have from
        Route53. If it is, return the list of domain names pointing to said
        instance. If nothing points to it, return an empty list. '''
        instance_attributes = [ 'public_dns_name', 'private_dns_name',
                                'ip_address', 'private_ip_address' ]
        name_list = set()
        for attrib in instance_attributes:
            try:
                value = getattr(instance, attrib)
            except AttributeError:
                continue
                continue
            if value in self.route53_records:
                name_list.update(self.route53_records[value])
        return list(name_list)
    def get_host_info_dict_from_instance(self, instance):
        instance_vars = {}
        for key in vars(instance):
            value = getattr(instance, key)
            key = self.to_safe('ec2_' + key)
            # Handle complex types
            # state/previous_state changed to properties in boto in https://github.com/boto/boto/commit/a23c379837f698212252720d2af8dec0325c9518
            if key == 'ec2__state':
                instance_vars['ec2_state'] = instance.state or ''
                instance_vars['ec2_state_code'] = instance.state_code
            elif key == 'ec2__previous_state':
                instance_vars['ec2_previous_state'] = instance.previous_state or ''
                instance_vars['ec2_previous_state_code'] = instance.previous_state_code
            elif type(value) in [int, bool]:
                instance_vars[key] = value
            elif isinstance(value, six.string_types):
                instance_vars[key] = value.strip()
            elif type(value) == type(None):
                instance_vars[key] = ''
            elif key == 'ec2_region':
                instance_vars[key] = value.name
            elif key == 'ec2__placement':
                instance_vars['ec2_placement'] = value.zone
            elif key == 'ec2_tags':
                for k, v in value.items():
                    if self.expand_csv_tags and ',' in v:
                        v = map(lambda x: x.strip(), v.split(','))
                        v = map(lambda x: x.strip(), v.split(','))
                    key = self.to_safe('ec2_tag_' + k)
                    instance_vars[key] = v
            elif key == 'ec2_groups':
                group_ids = []
                group_names = []
                for group in value:
                    group_ids.append(group.id)
                    group_names.append(group.name)
                instance_vars["ec2_security_group_ids"] = ','.join([str(i) for i in group_ids])
                instance_vars["ec2_security_group_names"] = ','.join([str(i) for i in group_names])
<<<<<<< REMOTE
else:
=======
else:
>>>>>>> LOCAL
        return instance_vars
    def get_host_info_dict_from_describe_dict(self, describe_dict):
        ''' Parses the dictionary returned by the API call into a flat list
            of parameters. This method should be used only when 'describe' is
            used directly because Boto doesn't provide specific classes. '''
        # I really don't agree with prefixing everything with 'ec2'
        # because EC2, RDS and ElastiCache are different services.
        # I'm just following the pattern used until now to not break any
        # compatibility.
        host_info = {}
        for key in describe_dict:
            value = describe_dict[key]
            key = self.to_safe('ec2_' + self.uncammelize(key))
            # Handle complex types
            # Target: Memcached Cache Clusters
            if key == 'ec2_configuration_endpoint' and value:
                host_info['ec2_configuration_endpoint_address'] = value['Address']
                host_info['ec2_configuration_endpoint_port'] = value['Port']
            # Target: Cache Nodes and Redis Cache Clusters (single node)
            if key == 'ec2_endpoint' and value:
                host_info['ec2_endpoint_address'] = value['Address']
                host_info['ec2_endpoint_port'] = value['Port']
            # Target: Redis Replication Groups
            if key == 'ec2_node_groups' and value:
                host_info['ec2_endpoint_address'] = value[0]['PrimaryEndpoint']['Address']
                host_info['ec2_endpoint_port'] = value[0]['PrimaryEndpoint']['Port']
                replica_count = 0
                for node in value[0]['NodeGroupMembers']:
                    if node['CurrentRole'] == 'primary':
                        host_info['ec2_primary_cluster_address'] = node['ReadEndpoint']['Address']
                        host_info['ec2_primary_cluster_port'] = node['ReadEndpoint']['Port']
                        host_info['ec2_primary_cluster_id'] = node['CacheClusterId']
                    elif node['CurrentRole'] == 'replica':
                        host_info['ec2_replica_cluster_address_'+ str(replica_count)] = node['ReadEndpoint']['Address']
                        host_info['ec2_replica_cluster_port_'+ str(replica_count)] = node['ReadEndpoint']['Port']
                        host_info['ec2_replica_cluster_id_'+ str(replica_count)] = node['CacheClusterId']
                        replica_count += 1
            # Target: Redis Replication Groups
            if key == 'ec2_member_clusters' and value:
                host_info['ec2_member_clusters'] = ','.join([str(i) for i in value])
            # Target: All Cache Clusters
            elif key == 'ec2_cache_parameter_group':
                host_info["ec2_cache_node_ids_to_reboot"] = ','.join([str(i) for i in value['CacheNodeIdsToReboot']])
                host_info['ec2_cache_parameter_group_name'] = value['CacheParameterGroupName']
                host_info['ec2_cache_parameter_apply_status'] = value['ParameterApplyStatus']
            # Target: Almost everything
            elif key == 'ec2_security_groups':
                # Skip if SecurityGroups is None
                # (it is possible to have the key defined but no value in it).
                if value is not None:
                    sg_ids = []
                    for sg in value:
                        sg_ids.append(sg['SecurityGroupId'])
                    host_info["ec2_security_group_ids"] = ','.join([str(i) for i in sg_ids])
            # Target: Everything
            # Preserve booleans and integers
            elif type(value) in [int, bool]:
                host_info[key] = value
            # Target: Everything
            # Sanitize string values
            elif isinstance(value, six.string_types):
                host_info[key] = value.strip()
            # Target: Everything
            # Replace None by an empty string
            elif type(value) == type(None):
                host_info[key] = ''
<<<<<<< REMOTE
else:
=======
else:
>>>>>>> LOCAL
            else:
<<<<<<< REMOTE
pass
=======
hostname = getattr(instance, self.hostname_variable)
>>>>>>> LOCAL
                # TODO Product codes if someone finds them useful
                #print key
                #print type(value)
                #print value
                # Remove non-processed complex types
                pass
        return host_info
    def get_host_info(self):
        ''' Get variables about a specific host '''
        if len(self.index) == 0:
            # Need to load index from cache
            self.load_index_from_cache()
        if not self.args.host in self.index:
            # try updating the cache
            self.do_api_calls_update_cache()
            if not self.args.host in self.index:
                # host might not exist anymore
                return self.json_format_dict({}, True)
        (region, instance_id) = self.index[self.args.host]
        instance = self.get_instance(region, instance_id)
        return self.json_format_dict(self.get_host_info_dict_from_instance(instance), True)
    def push(self, my_dict, key, element):
        ''' Push an element onto an array that may not have been defined in
        the dict '''
        group_info = my_dict.setdefault(key, [])
        if isinstance(group_info, dict):
            host_list = group_info.setdefault('hosts', [])
            host_list.append(element)
<<<<<<< REMOTE
else:
=======
else:
>>>>>>> LOCAL
    def push_group(self, my_dict, key, element):
        ''' Push a group as a child of another group. '''
        parent_group = my_dict.setdefault(key, {})
        if not isinstance(parent_group, dict):
            parent_group = my_dict[key] = {'hosts': parent_group}
        child_groups = parent_group.setdefault('children', [])
        if element not in child_groups:
            child_groups.append(element)
    def get_inventory_from_cache(self):
        ''' Reads the inventory from the cache file and returns it as a JSON
        object '''
        cache = open(self.cache_path_cache, 'r')
        json_inventory = cache.read()
        return json_inventory
    def load_index_from_cache(self):
        ''' Reads the index from the cache file sets self.index '''
        cache = open(self.cache_path_index, 'r')
        json_index = cache.read()
        self.index = json.loads(json_index)
    def write_to_cache(self, data, filename):
        ''' Writes data in JSON format to a file '''
        json_data = self.json_format_dict(data, True)
        cache = open(filename, 'w')
        cache.write(json_data)
        cache.close()
    def uncammelize(self, key):
        temp = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', key)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', temp).lower()
    def to_safe(self, word):
        ''' Converts 'bad' characters in a string to underscores so they can be used as Ansible groups '''
        regex = "[^A-Za-z0-9\_"
        if not self.replace_dash_in_groups:
            regex += "\-"
            regex += "\-"
        return re.sub(regex + "]", "_", word)
    def json_format_dict(self, data, pretty=False):
        ''' Converts a dict to a JSON object and dumps it as a formatted
        string '''
        if pretty:
            return json.dumps(data, sort_keys=True, indent=2)
<<<<<<< REMOTE
else:
=======
else:
>>>>>>> LOCAL
        else:
<<<<<<< REMOTE
group_info.append(element)
=======
key = self.to_safe("tag_" + k)
>>>>>>> LOCAL
            return json.dumps(data)























































































































































































































# Run the script
Ec2Inventory()
