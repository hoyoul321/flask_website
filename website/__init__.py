from importlib import import_module
from os import environ, path
from simplejson import dumps
from sys import exit
from flask import Flask
from flask_babel import Babel
from oam_intranet.config import c
import oam_intranet.utils
import click
from yaml import dump

from oam_intranet.sso import oauth
from oam_intranet.db import db, marshmallow, migrate    
from flask_sqlalchemy import get_state

babel = Babel()

def create_app():

    app = Flask(__name__.split('.')[0])
    app.config.from_object(c)

    with app.app_context():
        babel.init_app(app)
        oauth.init_app(app)
        db.init_app(app)
        # NOTE(max): Import security after SQLAlchemy is initialized
        from oam_intranet.security import security, setup_hooks
        from os import walk
        for root, dirs, files in walk('oam_intranet/db/models'):
            for name in files:
                if '_models.py' in name:
                    # NOTE(max): Moved all DB handling to Flask-Migrate/Alembic
                    # importing the models is enough
                    n = name[:-3]
                    import_module(f'oam_intranet.db.models.{n}')    
    
        migrate.init_app(app, db)
        marshmallow.init_app(app)
        security.init_app(app)
        setup_hooks(app)
        utils.init_app(app)    

    from pathlib import Path
    p = Path('oam_intranet/blueprints')
    for x in p.iterdir():
        l = list(x.glob('routes.py'))
        if x.is_dir() and len(l)==1:
            module_name = x.parts[-1]
            app.logger.debug(f"About to import Blueprint {module_name}")
            module = import_module(f'oam_intranet.blueprints.{module_name}.routes')    
            try:
                app.register_blueprint(module.blueprint)
            except:
                pass 

    app.logger.info(app.url_map)

    def get_tables_for_bind(bind=None):
        """Returns a list of all tables relevant for a bind."""
        result = []
        for table in db.metadata_dict[bind].tables.values():
            result.append(table)
        return result

    def get_tables():
        """Returns a dictionary of all tables for the configured binds."""
        tables = {}
        for k in get_bind_keys():
            tables[k] = get_tables_for_bind(k)
        return tables

    def get_bind_keys():
        return [None]+list(app.config['SQLALCHEMY_BINDS'].keys())
    
    def populate_model_data(model, data):
        from flask import current_app
        from oam_intranet.utils import get_schema
        try:
            current_app.logger.info(f"Populating {model.__qualname__}")
        except:
            current_app.logger.info(f"Populating {model.__class__.__qualname__}")
        data = get_schema(model).load(data, many=True, session=db.session)
        db.session.bulk_save_objects(data)
        # for datum in data:
        #     db.session.add(datum)

    # @app.cli.command("db-print-tables")
    # def print_tables():
    #     # for k,v in db.models_dict.items():
    #     #     print(f'{k} => {v.metadata}')
    #     # print(db.metadata_dict)
    #     tables = {}
    #     for k in get_bind_keys():
    #         tables[k] = get_tables_for_bind(k)
    #     print(tables)        

    # @app.cli.command("db-print-binds")
    # def print_binds():        
    #     binds = {}
    #     for k in get_bind_keys():
    #         binds[k] = db.get_engine(bind=k)
    #     print(binds)

    @app.cli.command("populate")
    def populate_db():
        from oam_intranet.db.models.xxx import (
            bind name, FuturesMarginRequirement            
        )
        from simplejson import loads

        # ### FUTURES ###

    
        d = loads("""
        [
            {"code":"BB","description":"Bloomberg"},
            {"code":"KIS","description":"Korea Investments And Securities"},
            {"code":"SS","description":"Samsung Futures"}
        ]
        """)
        populate_model_data(FuturesBroker, d)

        

        db.session.commit()

    return app
