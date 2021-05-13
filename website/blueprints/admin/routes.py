# -*- encoding: utf-8 -*-
"""
"""

from flask import render_template, redirect, url_for, current_app, jsonify
from flask.json import dumps
from flask_security import login_required, roles_required
from jinja2 import TemplateNotFound
from webargs.flaskparser import parser, use_args, use_kwargs
import sys

from website.blueprints.admin import blueprint

@blueprint.route('/users')
@login_required
@roles_required('administrator')
def users_admin():
    from website.db.models.security_models import User, UserSchema
    u = User.query.all()
    return render_template('users_admin.j2', count=len(u), api_endpoint='/api/users')

@blueprint.route('/roles')
@login_required
@roles_required('administrator')
def roles_admin():
    from website.db.models.security_models import Role, RoleSchema
    r = Role.query.all()
    return render_template('roles_admin.j2', count=len(r), api_endpoint='/api/roles')

@blueprint.route('/role_membership', methods=['GET', 'POST'])
@login_required
@roles_required('administrator')
def role_membership_admin():
    from flask import request
    from website.db.models.security_models import Role, User, RolesUsers
    from website.security import user_datastore
    from simplejson import loads, dumps
    from werkzeug.datastructures import MultiDict

    # current_app.logger.debug(f"VALUES {request.values}")
    
    if request.method == 'GET':
        kwargs = MultiDict(request.args)
        user_id = kwargs.pop('user_id',1)
    elif request.method == 'POST':
        kwargs = MultiDict(request.form)
        select_user = kwargs.pop('select-user',False)
        if select_user:
            user_id = kwargs.pop('user-selector')
        else:
            kwargs.pop('user-selector')
            user_id = kwargs.pop('user_id')

    # current_app.logger.debug(f"kwargs {kwargs}")

    selected_user = User.query.filter(User.id==user_id).first()
    selected_user_roles = {}

    roles = Role.query.filter().all()
    user_roles = RolesUsers.query.filter(RolesUsers.user_id==selected_user.id).all()
    for match in user_roles:
        selected_user_roles[match.role_id] = Role.query.filter(Role.id==match.role_id).all()
    
    if request.method == 'POST' and not select_user:
        new_roles = []
        for role in kwargs:
            tokens = role.split('_')
            role_id = tokens[0]
            role_name = '_'.join(tokens[1:])
            role = Role.query.filter(Role.id==role_id).first()            
            new_roles.append(role)
            # current_app.logger.debug(f"selected_user {selected_user}")
            # current_app.logger.debug(f"role {role}")
            if role_id not in selected_user_roles.keys():
                # current_app.logger.debug(f"Adding role {role_name} to user {selected_user.email}")
                user_datastore.add_role_to_user(selected_user, role)
        
        current_app.logger.debug(new_roles)
        for role in roles:
            # current_app.logger.debug(f"{selected_user.email} has role {role.name}: {selected_user.has_role(role)} ")
            if selected_user.has_role(role) and role not in new_roles:
                # current_app.logger.debug(f"Removing role {role.name} from user {selected_user.email}")
                user_datastore.remove_role_from_user(selected_user, role)
        
        user_datastore.commit()
        selected_user_roles.clear()
        user_roles = RolesUsers.query.filter(RolesUsers.user_id==selected_user.id).all()
        for match in user_roles:
            selected_user_roles[match.role_id] = Role.query.filter(Role.id==match.role_id).all()

    users = User.query.all()
    roles = Role.query.all()

    return render_template('role_membership_admin.j2',
        selected_user=selected_user,
        selected_user_roles=selected_user_roles,
        users=users,
        roles=roles)

@blueprint.route('/permissions', methods=['GET', 'POST'])
@login_required
@roles_required('administrator')
def permissions_admin():
    from . import get_permissions
    from flask import request
    from website.db.models.security_models import Role, RoleSchema
    from website.security import user_datastore
    from simplejson import loads, dumps
    from werkzeug.datastructures import MultiDict

    # current_app.logger.debug(f'==  request.method   ==> {request.method}')
    # current_app.logger.debug(f'==  request.args   ==> {request.args}')
    # current_app.logger.debug(f'==  request.form   ==> {request.form}')
    
    if request.method == 'GET':
        kwargs = MultiDict(request.args)
        role_id = kwargs.get('role_id',1)
    elif request.method == 'POST':
        kwargs = MultiDict(request.form)
        select_role = kwargs.pop('select-role',False)
        if select_role:
            role_id = kwargs.pop('role-selector')
        else:
            role_id = kwargs.pop('role_id')
            kwargs.pop('role-selector')

    roles = Role.query.all()
    # current_app.logger.debug(f'==  roles      ==> {roles}')
    selected_role = Role.query.filter(Role.id==role_id).one()
    if request.method == 'POST' and not select_role:
        selected_role.permissions = " ".join(kwargs.keys())
    user_datastore.commit()

    # current_app.logger.debug(f'==selected_role==> {selected_role}')
    permissions = get_permissions()
    
    # Administrator
    role_permissions = []
    if selected_role.id == 1:
        selected_role.permissions=''
        for bp in permissions:
            for ep in permissions[bp]:
                for m in permissions[bp][ep]:
                    role_permissions.append(f'{bp}.{ep}-{m}')
    else:
        try:
            role_permissions = selected_role.permissions.split(' ')
        except AttributeError:
            role_permissions = []
        role_permissions = list(map(lambda x: x.strip(), role_permissions))
    # current_app.logger.debug(f'==role_permissions==> {role_permissions}')

    return render_template('permissions_admin.j2',
        permissions=permissions,
        role_id=selected_role.id,
        role_permissions=role_permissions,
        role_name=selected_role.name,
        roles=roles)
