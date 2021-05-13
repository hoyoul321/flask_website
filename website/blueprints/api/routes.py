from website.blueprints.api import blueprint, UserView, RoleView

from flask_security import login_required
from flask_security import roles_required

from webargs import fields, missing
from webargs.flaskparser import use_args, use_kwargs

from website.utils import jsgridview_factory


######################### From the docs
# class UserAPI(MethodView)
#     def get(self, user_id):
#         if user_id is None:
#             # return a list of users
#             pass
#         else:
#             # expose a single user
#             pass
#     def post(self):
#         # create a new user
#         pass
#     def delete(self, user_id):
#         # delete a single user
#         pass
#     def put(self, user_id):
#         # update a single user
#         pass
# user_view = UserAPI.as_view('user_api')
# app.add_url_rule('/users/', defaults={'user_id': None},
#                  view_func=user_view, methods=['GET',])
# app.add_url_rule('/users/', view_func=user_view, methods=['POST',])
# app.add_url_rule('/users/<int:user_id>', view_func=user_view,
#                  methods=['GET', 'PUT', 'DELETE'])
# If you have a lot of APIs that look similar you can refactor that registration code:

# def register_api(view, endpoint, url, pk='id', pk_type='int'):
#     view_func = view.as_view(endpoint)
#     app.add_url_rule(url, defaults={pk: None},
#                      view_func=view_func, methods=['GET',])
#     app.add_url_rule(url, view_func=view_func, methods=['POST',])
#     app.add_url_rule('%s<%s:%s>' % (url, pk_type, pk), view_func=view_func,
#                      methods=['GET', 'PUT', 'DELETE'])
# register_api(UserAPI, 'user_api', '/users/', pk='user_id')

blueprint.add_url_rule('/users',
    view_func=UserView.as_view('users'),
    methods=['GET','POST','PUT','DELETE'])

blueprint.add_url_rule('/roles',
    view_func=RoleView.as_view('roles'),
    methods=['GET','POST','PUT','DELETE'])

@blueprint.route('/validate/date')
@use_kwargs({ "value": fields.String(required=True),
    "allow_empty": fields.Bool(required=False, missing=True) },
    location="query")
def validate_date(value, allow_empty):
    from flask import jsonify,current_app
    from maya import parse
    current_app.logger.debug(f"== value, allow_empty ==> {value}, {allow_empty}")
    try:
        parse(value)
    except:
        if allow_empty and not value:
            value = ""
            return jsonify({"value": value, "result": True})
        return jsonify({"value": value, "result": False})
    return jsonify({"value": value, "result": True})

@blueprint.route('/validate/integer')
@use_kwargs({ "value": fields.String(required=True),
    "allow_empty": fields.Bool(required=False,missing=True)  },
    location="query")
def validate_integer(value, allow_empty):
    from flask import jsonify
    try:
        int(value)
    except:
        if allow_empty and not value:
            value = 0
            return jsonify({"value": value, "result": True})
        return jsonify({"value": value, "result": False})
    return jsonify({"value": value, "result": True})

@blueprint.route('/validate/float')
@use_kwargs({ "value": fields.String(required=True),
    "allow_empty": fields.Bool(required=False,missing=True)  },
    location="query")
def validate_float(value, allow_empty):
    from flask import jsonify
    try:
        float(value)
    except:
        if allow_empty and not value:
            value = 0.0
            return jsonify({"value": value, "result": True})
        return jsonify({"value": value, "result": False})
    return jsonify({"value": value, "result": True})
