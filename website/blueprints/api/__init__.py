# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present One Asset Management
"""

from flask import Blueprint, current_app, make_response
from flask.json import dumps, jsonify
from flask.views import MethodView

from webargs import fields
from webargs.flaskparser import use_args

from flask_security import login_required, current_user
from website.utils import JsGridView

blueprint = Blueprint(
    'api',
    __name__,
    template_folder='templates',
    url_prefix='/api'
)

class RoleView(JsGridView):
    def __init__(self):
        from website.db.models.security_models import Role
        super().__init__(Role)

    def delete(self):
        from flask import request, abort
        abort(406)
    # def delete(self):
    #     from flask import request, abort
    #     from simplejson import loads
    #     from webargs.flaskparser import parser
    #     from website.security import user_datastore
    #     from website.db.models.security_models import Role, RoleSchema
    #     try:
    #         if 'application/json' in request.content_type:
    #             args = parser.load_json(request, self.s)
    #             args = dict(filter(lambda t: t if bool(t[1]) else None, args.items()))
    #         else:
    #             abort(406)
    #         r1 = Role.query.filter(Role.name==args['name']).one()
    #         user_datastore.delete_role(r1)
    #         return jsonify(args)
    #     except Exception as e:
    #         current_app.logger.error(e)
    #         abort(406, dumps(f'Unexpected error: {e}'))

    def post(self):
        from flask import request, abort
        from simplejson import loads
        from webargs.flaskparser import parser
        from website.security import user_datastore
        # current_app.logger.debug("==============> POST")
        try:
            if 'application/json' in request.content_type:
                args = parser.load_json(request, self.s)
                args = dict(filter(lambda t: t if bool(t[1]) else None, args.items()))
            else:
                abort(406)
            # current_app.logger.debug(f'===args===> {args}')
            
            r1 = user_datastore.create_role(name=args['name'],
                                            description=args['description'])
            user_datastore.commit()            
            
            return jsonify(args)
        except Exception as e:
            current_app.logger.error(e)
            abort(406, dumps(f'Unexpected error: {e}'))

class UserView(JsGridView):
    def __init__(self):
        from website.db.models.security_models import User
        super().__init__(User)

    def delete(self):
        from flask import request, abort
        abort(406)

    def post(self):
        from flask import request, abort
        from simplejson import loads
        from webargs.flaskparser import parser
        from website.security import user_datastore
        # current_app.logger.debug("==============> POST")
        try:
            if 'application/json' in request.content_type:
                args = parser.load_json(request, self.s)
                args = dict(filter(lambda t: t if bool(t[1]) else None, args.items()))
            else:
                abort(406)
            # current_app.logger.debug(f'===args===> {args}')
            
            u1 = user_datastore.create_user(username=args['username'],
                                            email=args['email'],
                                            password='&*IO^TR)B*&YTEFEW')
            user_datastore.commit()            
            
            return jsonify(args)
        except Exception as e:
            current_app.logger.error(e)
            abort(406, dumps(f'Unexpected error: {e}'))

############# JsGrid CopyControl
#    var CopyField = function(config) {
#     jsGrid.Field.call(this, config);
# };
#  
# CopyField.prototype = new jsGrid.Field({ 
#     css: "copy-field",            // redefine general property 'css'
#     align: "center",              // redefine general property 'align'
  
#     itemTemplate: function(value, item) {
#          return $("<button>")
#                 .text("Copy")
#                 .on("click", function(e) {
#                     var copy = $.extend({}, item, {Name: item.Name+" (Copy)"});
#                     $("#jsGrid").jsGrid("insertItem",copy);
#                     e.stopPropagation();
#                 });
#     }
# });
# jsGrid.fields.copycontrol = CopyField;

# var clients = [
#         { "Name": "Otto Clay", "Birthday": "December, 17 2014" },
#         { "Name": "Connor Johnston", "Birthday": "March, 5 2012" },
#         { "Name": "Lacey Hess", "Birthday": "August, 2 2000" }
#     ];
 
#     $("#jsGrid").jsGrid({
#         width: "600px",
#         height: "400px",
 
#         inserting: true,
#         editing: true,
#         sorting: true,
#         paging: true, 
#         data: clients, 
#         fields: [
#             { name: "Name", type: "text", width: 150, validate: "required" },
#             { name: "Birthday", 
#               type: "text",
#               align: "right",
#               width: 150
#             },
#           {
#             type: "control"
#           },
#           {
#             type: "copycontrol"
#           }
#           ]
#     });