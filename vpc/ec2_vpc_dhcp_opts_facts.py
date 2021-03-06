#!/usr/bin/python
#
# This is a free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This Ansible library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this library.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = '''
---
module: ec2_vpc_dhcp_opts_facts
short_description: Gather facts about ec2 VPC DHCP option sets in AWS
description:
    - Gather facts about ec2 VPC DHCP option sets in AWS
version_added: "2.0"
author: "Rob White (@wimnat)"
options:
  filters:
    description:
      - A dict of filters to apply. Each dict item consists of a filter key and a filter value. See U(http://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeDhcpOptions.html) for possible filters.
    required: false
    default: null
  region:
    description:
      - The AWS region to use. If not specified then the value of the EC2_REGION environment variable, if any, is used. See U(http://docs.aws.amazon.com/general/latest/gr/rande.html#ec2_region)
    required: false
    default: null
    aliases: [ 'aws_region', 'ec2_region' ]

extends_documentation_fragment: aws
'''

EXAMPLES = '''
# Note: These examples do not set authentication details, see the AWS Guide for details.

# Gather facts about all VPC DHCP option sets
- ec2_vpc_dhcp_opts_facts:

# Gather facts about a particular VPC DHCP options set using option set ID
- ec2_vpc_dhcp_opts_facts:
    filters:
      - dhcp-options-id: dopt-00112233

# Gather facts about any VPC DHCP options set with a tag key Name and value Example
- ec2_vpc_dhcp_opts_facts:
    filters:
      - "tag:Name": Example

'''

try:
    import boto.vpc
    from boto.exception import BotoServerError
    HAS_BOTO = True
except ImportError:
    HAS_BOTO = False

def get_dhcp_opt_set_info(dhcp_opt_set):

    dhcp_opt_set_info = { 'id': dhcp_opt_set.id,
                          'options': dhcp_opt_set.options,
                          'tags': dhcp_opt_set.tags
                        }

    return dhcp_opt_set_info


def list_ec2_vpc_dhcp_option_sets(connection, module):
    
    filters = module.params.get("filters")
    dhcp_opts_dict_array = []
    
    try:
        all_dhcp_opt_sets = connection.get_all_dhcp_options(filters=filters)
    except BotoServerError as e:
        module.fail_json(msg=e.message)
        
    for dhcp_opt_set in all_dhcp_opt_sets:
        dhcp_opts_dict_array.append(get_dhcp_opt_set_info(dhcp_opt_set))
        
    module.exit_json(dhcp_opt_sets=dhcp_opts_dict_array)

    
def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update(
        dict(
            filters = dict(default=None, type='dict')
        )
    )

    module = AnsibleModule(argument_spec=argument_spec)

    if not HAS_BOTO:
        module.fail_json(msg='boto required for this module')

    region, ec2_url, aws_connect_params = get_aws_connection_info(module)

    if region:
        try:
            connection = connect_to_aws(boto.vpc, region, **aws_connect_params)
        except (boto.exception.NoAuthHandlerFound, StandardError), e:
            module.fail_json(msg=str(e))
    else:
        module.fail_json(msg="region must be specified")

    list_ec2_vpc_dhcp_option_sets(connection, module)

from ansible.module_utils.basic import *
from ansible.module_utils.ec2 import *

if __name__ == '__main__':
    main()
