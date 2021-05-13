# -*- encoding: utf-8 -*-
"""
"""

from flask import (
    jsonify,
    render_template,
    redirect,
    request,
    url_for,
    current_app as a,
    g,
    session
)
from flask_sqlalchemy import SQLAlchemy
from flask_security import login_required
from flask_security.utils import login_user, logout_user

from json import loads, dumps

from website.security import security, user_datastore
from website.blueprints.auth import blueprint
from website.blueprints.auth.util import verify_pass
from website.blueprints.auth.forms import LoginForm, CreateAccountForm
from website.db.models.security_models import User

@security.login_context_processor
def login_context_processor():
    msg = session.pop('msg',None)
    return dict(msg=msg)

@blueprint.route('/')
def route_default():
    return redirect(url_for('home.index'))
    
@blueprint.route('/azure/login', methods=['GET', 'POST'])
def azure_login():
    from website.sso import oauth
    client = oauth.create_client('azure')
    redirect_uri = url_for('auth.azure_authorize',_external=True)
    return client.authorize_redirect(redirect_uri)

@blueprint.route('/azure/authorize', methods=['GET', 'POST'])
def azure_authorize():
    from website.sso import oauth
    from flask import session
    client = oauth.create_client('azure')
    try:
        token = client.authorize_access_token()
        resp = client.get('oidc/userinfo')
        profile = resp.json()
        # a.logger.debug(dumps(profile))
        # Locate user
        user = User.query.filter_by(email=profile['email']).first()
        # a.logger.debug(user)
        if user is not None:
            if user.username is None:
                user.username = profile['name']
                user_datastore.commit()
            login_user(user)
            user_datastore.commit()
            return redirect(url_for('home.index'))
        else:
            session['msg'] = 'Could not sign in with MS Account'
            return redirect( url_for('security.login'))
    except Exception as e:
        if a.config['DEBUG']:
            session['msg'] = f'Could not sign in with MS Account ({e})'
        else:
            session['msg'] = 'Could not sign in with MS Account'
        return redirect(url_for('security.login'))

@blueprint.route('/_logout')
def logout():
    session.pop('msg',None)
    logout_user()
    user_datastore.commit()
    return redirect(url_for('security.login'))

@blueprint.route('/shutdown')
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'

## Errors
@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('page-403.html'), 403

@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('page-404.html'), 404

@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('page-500.html'), 500
