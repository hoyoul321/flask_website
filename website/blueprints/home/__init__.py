# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present One Asset Management
"""

from flask import Blueprint

blueprint = Blueprint(
    'home',
    __name__,
    template_folder='templates'
)
