# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present One Asset Management
"""

from website.blueprints.home import blueprint
from flask import render_template, redirect, url_for, current_app, jsonify
#from flask_login import login_required, current_user
from flask_security import login_required
from jinja2 import TemplateNotFound

import sys

@blueprint.route('/index')
@login_required
def index():
    return render_template('index.j2')
