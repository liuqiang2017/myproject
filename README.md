accounts distribute policy

python for accounts distribute policy

Config

you should touch a default.py for config,  

# default.py
class Config(object):
    accounts_list = [{"admin":"XXXX", "password":"XXXX"},{"admin":"XXXX", "password":"XXXX"}]
    acc_timeout = 620
#acc_timeout : account is in use, when the timeout is reach, acc is forced to release 

there are two policy
