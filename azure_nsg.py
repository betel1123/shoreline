# The best way to create/update NSG on Azure from a data structure 
# would be using python invoking Azure CLI.

# Necessary dependencies in order to run this: 
# 1. Azure CLI
# 2. Python
# 3. pip install azure-identity
# 4. pip install azure-mgmt-network==19.0.0 (needs to be latest)
# 4. az login (run from shell, simplest way to authenticate)

from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.network.v2020_06_01.models import NetworkSecurityGroup
from azure.mgmt.network.v2020_06_01.models import SecurityRule
import json

# Pulls Azure creds from Azure CLI (az login).
credential = DefaultAzureCredential()

# Subscription ID. Using the one from my personal Azure account here for example:
subscription_id = 'c1af1e2f-c85f-4cef-b12b-0f18b927dccd'

# This will be used later to apply changes to Azure NSG resource.
network_client = NetworkManagementClient(credential, subscription_id)

# Azure resource specification
resource_group_name = "rg001"
nsg_name = "test-nsg"
region = "East US 2"

# Import data structure defined in a JSON file, and load it as JSON.
file = open("rules_list.json","r")
rules_json = json.load(file)

# Initiate NSG parameter object.
nsg_params = NetworkSecurityGroup()
nsg_params.location = region
nsg_params.security_rules = []

# For each rule found in the data structure, append it to the NSG parameter object from above. 
# Using ternary to do things with less code. 
for rule in rules_json["rules"]:
    nsg_params.security_rules.append(
        SecurityRule(
            direction = rule["direction"],
            priority = rule["priority"],
            name = rule["name"],
            description = rule["description"],
            source_address_prefix = (None, rule["source_address_prefix"])[rule["source_address_prefix"] != "" ],
            source_address_prefixes = (None, rule["source_address_prefixes"])[rule["source_address_prefixes"] != "" ],
            source_port_range = rule["source_port_range"],
            destination_address_prefix = (None, rule["destination_address_prefix"])[rule["destination_address_prefix"] != "" ],
            destination_address_prefixes = (None, rule["destination_address_prefixes"])[rule["destination_address_prefixes"] != "" ],
            destination_port_range = rule["destination_port_range"],
            protocol = rule["protocol"],
            access = rule["access"]
        )
    )

# Print rules added for a quick sanity check.
print("Rules added:")
for rule in nsg_params.security_rules:
    print("-", rule)

# Apply update to NSG and print returned output.
nsg = network_client.network_security_groups.begin_create_or_update(resource_group_name, nsg_name, nsg_params)
print(nsg.result().as_dict())

# 1. How do you map the network rules to each platform i.e. how are the rules applied on each platform and to what types of resources on that platform?  
#    Azure - NSG can be attached to subnet or VM NIC. 
#    AWS - Security Group needs to be associated with EC2 instance. 
#    GCP - Firewall rules can be applied to any existing network.
#
# 2. What are the differences between the platforms from a networking perspective? How does this impact your ability to create an abstraction across the platforms?
#    As each platform offers a slightly different way to control traffic, that needs to be taken into account when doing a system design. 
#    Also, each has different best practices around scaling, so that needs to be taken into consideration as well.
#  
# 3. How fine grained do you provide control over network flow? How would you go about extending this for finer grain control?  Per instance? Per group? Per network? 
#    It really depends on what you are trying to achieve security-wise. 
#    For example, you can even create a whitelist per employee-basis to make sure they can only access assets behind firewall from designated locations when working remotely.