from flask.views import MethodView
from website.db import db

def rows_as_dicts(cursor):
    """convert tuple result to dict with cursor"""
    col_names = [i[0] for i in cursor.description]
    rows = [dict(zip(col_names, row)) for row in cursor]
    cursor.close()
    return rows, col_names

def _now(tz=None, n=None):
    """Returns the current (or given) datetime in various timezones (or a specific one)."""

    import maya
    if n is None:
        n = maya.now()
    result = {}
    result['kst'] = n.datetime(to_timezone='Asia/Seoul')
    result['seoul'] = n.datetime(to_timezone='Asia/Seoul')
    result['ny'] = n.datetime(to_timezone='America/New_York')
    result['eastern'] = n.datetime(to_timezone='America/New_York')
    result['cet'] = n.datetime(to_timezone='Europe/Berlin')
    result['berlin'] = n.datetime(to_timezone='Europe/Berlin')
    result['rome'] = n.datetime(to_timezone='Europe/Rome')
    if tz:
        return result[tz]
    else:
        return result

def has_permission(user, permission):
    """Returns True is the user has the given permission, False otherwise."""

    from flask import current_app
    for role in user.roles:
        try:
            if role.name=='administrator' or permission in role.permissions.split(' '):
                return True
        except TypeError:
            continue
    return False

def build_permission_from_request(request):
    """Returns the permission string associated with the current request.
    Parameters
    ----------
    request : falsk.Request
        The request to build the permission string for.
    """
    from flask import current_app
    return build_permission(request.blueprint, request.endpoint, request.method)

def build_permission(blueprint, endpoint, method):
    """Returns the permission string associated with the given bluprint, endpoint and method.
    Parameters
    ----------
    blueprint : string
        The blueprint name.
    endpoint : string
        The enpoint, including the blueprint name.
    method : string
        The method used. Can be one of ['GET','POST','PUT','DELETE'].
    """
    if not blueprint:
        blueprint = 'default'
        endpoint = f"{blueprint}.{endpoint}"
    method = method.upper()
    permission = f'{endpoint}-{method}'
    return (blueprint,endpoint,permission)

def current_user_has_permission(blueprint,endpoint,method):
    """Returns True is the user has permission to access the specified enpoint, False otherwise.
    Parameters
    ----------
    blueprint : string
        The blueprint name.
    endpoint : string
        The enpoint, including the blueprint name.
    method : string
        The method used. Can be one of ['GET','POST','PUT','DELETE'].
    """

    from flask_security import current_user
    (blueprint,endpoint,permission) = build_permission(blueprint,endpoint,method)
    return has_permission(current_user,permission)

def jsgridview_factory(Model):
    def init(self): 
        super(new_class,self).__init__(self.Model)
    new_class = type(
        f'{Model.__qualname__}JsGridView',
        (JsGridView,),
        {
            '__init__': init,
            'Model': Model
        }
    )
    return new_class

def rename_keys(data_dict, keys_dict):
    result = {}
    for k, v in data_dict.items():
        try:
            result[keys_dict[k]] = v
        except KeyError:
            result[k] = v
    return result

class JsGridView(MethodView):
    """Creates a standard flask.MethodView based controller for jsGridView interaction.
    Parameters
    ----------
    Model : sqlalchemy.Model
        SQLAlchemy model to build the controller for.
    """
    def __init__(self, Model):
        super().__init__()
        self.Model = Model
        self.Schema = get_schema(Model)
        try:
            self.s = self.Schema()
        except TypeError:
            self.s = self.Schema
        # current_app.logger.debug("==============> JsGridView")

    def jsonify(self, data):
        return self.s.jsonify(data)

    def getPagingAndSorting(self, args):
        """Returns the paging base index and size, and sorting field and order if present in the query string."""
        pIndex = int(args.pop('pageIndex',1))
        pSize = int(args.pop('pageSize',10))
        sField = args.pop('sortField', None)
        sOrder = args.pop('sortOrder', None)
        # current_app.logger.debug(f"{pIndex}, {pSize}, {sField}, {sOrder}")
        return pIndex, pSize, sField, sOrder
    
    def get_columns(self):
        """Returns a tuple of lists containing the primary key names, column names and column types."""
        
        from sqlalchemy import inspect
        inspector = inspect(db.get_engine(bind=self.Model.__bind_key__))
        pk_constraint = inspector.get_pk_constraint(self.Model.__tablename__)
        cols = inspector.get_columns(self.Model.__tablename__)
        col_mapping = {}
        for k, v in dict(inspect(self.Model).c).items():
            col_mapping[v.name] = k
        # col_names = [x['name'] for x in cols]
        col_names = [x for x in dict(inspect(self.Model).c).keys()]
        col_types = dict([ (x['name'],x['type']) for x in cols ])
        pks = [col_mapping[x] for x in pk_constraint['constrained_columns']]
        # current_app.logger.debug(f'== cols===> {cols}')
        # current_app.logger.debug(f'== pks ===> {pks}')
        return pks, col_names, col_types, col_mapping

    def get(self):
        """Returns the filtered and paginated data set as JSON"""
        from flask import request, abort, current_app
        from simplejson import loads, dumps
        from sqlalchemy import asc, desc, types
        from webargs.flaskparser import parser
        from marshmallow.fields import Field
        # current_app.logger.debug("==============> GET")
        pks, cols, col_types, col_mapping = self.get_columns()
        try:
            args = dict(request.args)
            # current_app.logger.debug(f'==  req.args   ==> {args}')
            pageIndex, pageSize, sortField, sortOrder = self.getPagingAndSorting(args)
            args = dict(filter(lambda t: t if t[0] else None, args.items()))
            # current_app.logger.debug(f'==  kwargs   ==> {args}')
            limit = pageSize if pageSize else None
            offset = (pageIndex-1)*pageSize if pageIndex and pageSize else 0            
            # current_app.logger.debug(f'==  pageIndex,  pageSize  ==> {pageIndex}, {pageSize}')
            valid_args = dict(filter(lambda t: t if bool(t[1]) else None, args.items()))
            d = self.s.load(valid_args,partial=True)
            d = loads(self.s.dumps(d))
            valid_args = dict(filter(lambda t: t if bool(t[1]) else None, d.items()))
            # current_app.logger.debug(f'==  valid_args  ==> {valid_args}')
            like = list()
            filter_by = dict()
            # current_app.logger.debug(f'==  XXXXXXXXXXXXXXXXXX  ==>')
            for k, v in valid_args.items():
                # current_app.logger.debug(f'==  col  ==> {k}, {v}')
                col = eval(f'self.Model.{k}')
                if type(v) is str:
                    expr = col.contains(v, autoescape=True)
                    # current_app.logger.debug(f'==  expr  ==> {expr}')
                    like.append( expr )
                else:
                    filter_by[k] = v
            # current_app.logger.debug(f'==  like  ==> {like}')
            # current_app.logger.debug(f'==  _filter  ==> {filter_by}')
            
            query =  self.Model.query       
            if filter_by:
                query =  query.filter_by(**filter_by)      
            if like:
                query = query.filter(*like)           
            if sortField:
                if sortOrder and sortOrder == 'desc':
                    query = query.order_by(desc(sortField))
                else:
                    query = query.order_by(asc(sortField))
            else:
                #query.order_by(self.Model.id)
                query = query.order_by(getattr(self.Model, pks[0])) 
            count = query.count()
            # if _filter:            
            #     query =  self.Model.filter_by(**_filter)
            #     count = query.count()
            data = query.limit(limit).offset(offset)

            json = f'{{ "data": {self.s.dumps(data,many=True)}, "itemsCount": {count} }}'
            # current_app.logger.debug(f'==========> {json}')
            response = self.jsonify(data)
            response.set_data(json)
            return response
        except Exception as e:
            current_app.logger.error(e)
            abort(409, description=e)

    def put(self):
        """Updates an existing record and returns it as JSON"""
        from flask import request, abort, current_app
        from simplejson import loads, dumps
        from sqlalchemy import asc, desc, types
        from webargs.flaskparser import parser
        
        # current_app.logger.debug("==============> PUT")
        pks, cols, col_types, col_mapping = self.get_columns()
        # current_app.logger.debug(f"=====pks======> {pks}")
        # current_app.logger.debug(f"=====cols=====> {cols}")
        try:
            if 'application/json' in request.content_type:
                args = parser.load_json(request, self.s)
            else:
                abort(406)
            # current_app.logger.debug(f'== args====> {args}')
            _filter = dict(filter(lambda t: t if t[0] in pks else None, args.items()))
            # current_app.logger.debug(f'== _filter=> {_filter}')
            updates = dict(filter(lambda t: t if t[0] in cols and \
                t[0] not in pks and \
                t[1] is not None else None, args.items()))
            # current_app.logger.debug(f'== updates=> {updates}')
            items = loads(self.s.dumps(self.s.load(updates))).items()
            # current_app.logger.debug(f'== items=> {items}')
            updates = dict(filter(lambda t: t if t[1] and t[0] in cols else None, items ))
            partial = self.s.load(updates, partial=True)
            # current_app.logger.debug(f'== updates  => {updates}')
            # current_app.logger.debug(f'== partial  => {partial}')
            # current_app.logger.debug(f'== cols     => {cols}')
            # current_app.logger.debug(f'== col_types=> {col_types}')
            d = self.Model.query.filter_by(**_filter)
            o = d.first()
            # current_app.logger.debug(f'===PRE ====> {self.s.dumps(d.one())}')
            db.session.add(o)
            # We cannot do d.update(updates) otherwise the Session will not be dirty
            # and the after_update event will not be triggered
            for k,v in partial.items():
                setattr(o,k,v)
            # current_app.logger.debug(f'===POST====> {self.s.dumps(d.one())}')            
            db.session.commit()
            return ('',204)
        except Exception as e:
            current_app.logger.error(e)
            abort(409, description=e)

    def post(self):     
        """Inserts the passed record and returns it  as JSON"""   
        from flask import request, abort, current_app
        from simplejson import loads, dumps
        from sqlalchemy import asc, desc, types
        from webargs.flaskparser import parser

        #current_app.logger.debug("==============> POST")
        try:
            if 'application/json' in request.content_type:
                args = parser.load_json(request, self.s)
            else:
                abort(406, description="Invalid format")
            # current_app.logger.debug(f'=== args ===> {args}')            
            _filter = dict(filter(lambda t: t if t[1] else None, args.items()))
            # current_app.logger.debug(f'== _filter==> {_filter}')
            d = self.s.load(_filter)
            db.session.add(d)
            db.session.commit()
            # The dict will be output to JSON by Flask
            return args
        except Exception as e:
            current_app.logger.error(e)
            abort(406, description=e)

    def delete(self):     
        """Deletes the record matching with the passed filter and returns it as JSON"""      
        from flask import request, abort, current_app
        from simplejson import loads, dumps
        from sqlalchemy import asc, desc, types
        from webargs.flaskparser import parser

        # current_app.logger.debug("==============> DELETE")
        pks, cols, col_types, col_mapping = self.get_columns()
        try:
            if 'application/json' in request.content_type:
                args = parser.load_json(request, self.s)
                # current_app.logger.debug(f'==========> {args}')
                _filter = dict(filter(lambda t: t if t[0] in pks else None, args.items()))
                # current_app.logger.debug(f'===_filter==> {_filter}')
            else:
                abort(406, description="Invalid format")
            
            q = self.Model.query.filter_by(**_filter)
            d = q.first()
            # current_app.logger.debug(f'==To Be Deleted===> {self.s.dumps(d)}')
            db.session.delete(d)
            db.session.commit()
            # The dict will be output to JSON by Flask
            return args

        except Exception as e:
            current_app.logger.error(e)
            abort(406, description=e)


def init_app(app):    
    @app.errorhandler(406)
    def resource_not_found(e):
        from flask import jsonify
        return jsonify(error=str(e)), 406

    @app.errorhandler(409)
    def resource_not_found(e):
        from flask import jsonify
        return jsonify(error=str(e)), 409

    @app.context_processor
    def context_processor():
        return dict(
            current_user_has_permission=current_user_has_permission
        )

    @app.before_request
    def before_request():
        from flask import g, request, current_app, redirect, url_for, abort
        from flask_security import current_user
        from website.db.models.security_models import Role
        g.now= _now()

        blueprint,endpoint,permission = build_permission_from_request(request)
                
        excluded_endpoints = []
        excluded_blueprints = ['home','default', 'auth','security']

        try:
            if endpoint not in excluded_endpoints \
                and blueprint not in excluded_blueprints \
                and not has_permission(current_user, permission):            
                return abort(401)
        except AttributeError:
            if endpoint not in excluded_endpoints \
                and blueprint not in excluded_blueprints:
                return redirect(url_for('home.index'))

def my_import(name):
    """Imports and returns a specified class."""
    from importlib import import_module
    components = name.split('.')
    module = import_module('.'.join(components[:-1]))   
    return getattr(module,components[-1])

def get_schema(target):
    """Retruns and existing Schema for a given Model, or a default built on SQLAlchemyAutoSchema."""  
    
    from flask import current_app
    try:
        module = target.__module__
        qualname = target.__qualname__
        name = '.'.join([module, qualname])
    except AttributeError:
        module = target.__class__.__module__
        qualname =target.__class__.__qualname__
    name = '.'.join([module,qualname])
    # current_app.logger.debug(f'get_schema({target}) =====> name: {name}')
    model = my_import(name)
    schema_name = f'{name}Schema'    
    try:
        schema = my_import(schema_name)
    except AttributeError:
        from website.db import marshmallow
        Meta = type(
            'Meta',
            (object,),
            {'model': model,
             'load_instance': True, 
             'include_fk': True}
        )
        schema = type(
            schema_name,
            (marshmallow.SQLAlchemyAutoSchema,),
            {'Meta': Meta}
        )
    instance = schema()
    return instance
