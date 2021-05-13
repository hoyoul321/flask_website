# -*- encoding: utf-8 -*-
"""
"""

from flask import Blueprint, current_app

blueprint = Blueprint(
    'admin',
    __name__,
    template_folder='templates',
    url_prefix='/admin'
)

def get_blueprints():
    blueprints = set() 
    for k,v in current_app.blueprints.items():
        blueprints.add(k.strip())
    return blueprints

def get_permissions():
    blueprints = get_blueprints()    
    permissions = {'default':{}}
    rules = current_app.url_map.iter_rules()
    for rule in rules:
        for method in ['GET','POST','PUT','DELETE']:
            if method not in rule.methods:
                continue
            try:
                tokens = rule.endpoint.split('.')
                bp_name = tokens[0]
                if bp_name == 'security':
                    continue
                if bp_name in blueprints:
                    if bp_name not in permissions.keys():
                        permissions[bp_name] = {}
                    endpoint = f"{'.'.join(tokens[1:])}"
                    if endpoint not in permissions[bp_name]:
                        permissions[bp_name][endpoint] = {}
                    permissions[bp_name][endpoint][method] = ""
                else:
                    raise Exception('Bogus')
            except:
                bp_name = 'default'
                endpoint = f"{rule.endpoint}"
                if endpoint not in permissions[bp_name]:
                    permissions[bp_name][endpoint] = {}
                permissions[bp_name][endpoint][method] = ""
    return permissions