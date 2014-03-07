
__author__ = 'Kamilion@gmail.com'
########################################################################################################################
## Site Specific Configuration Definitions
########################################################################################################################

# Open Registration?
allow_new_users = False

########################################################################################################################
## Flask Configuration Definitions
########################################################################################################################

# CSRF protection
secret_key = "isaidcomeonfhqwhgadseverybodytothelimitthecheatistothelimiteverybodycomeonfhqwhgads"

# API Endpoint protection
api_key = "fhqwhgads"

# Debugging?
debug = True


########################################################################################################################
## RethinkDB Configuration Definitions
########################################################################################################################
# rethink config
rdb = {
    'host': 'localhost',
    'port': 28015,
    'userdb': 'zurfauth:users',
    'ticketsdb': 'zurfauth:tickets',
    'statedb': 'wanwipe:machine_state',
    'wipedb': 'wanwipe:wipe_results',
    'jobdb': 'wanwipe:job_results',
    'diskdb': 'wanwipe:disk_results'
}

########################################################################################################################
## YubiCo Configuration Definitions
########################################################################################################################

yubico_keys = {  # Used in authmodel.py
    'client_id': '14656',
    'secret_key': 'lSVH6X36vIF9c+kiB0Ikoj05LoU='
}

########################################################################################################################
## Stripe Configuration Definitions
########################################################################################################################

stripe_keys = {  # Used in billingmodel.py
    'secret_key': 'sk_test_JCpSAX6gOBRa3LDVJwrrTTbi',
    'publishable_key': 'pk_test_LhrTHEeEDuR0LoJpMCpvbPM6'
}
