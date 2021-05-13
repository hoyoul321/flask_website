
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate

# Make sure the SQLAlchemy session is initialized
engine_options = {
    'convert_unicode': True, 
    'pool_pre_ping': True, 
    'pool_size': 20, 
    'max_overflow': 30,
    'pool_timeout': 5,
    'pool_recycle': 30
}
db = SQLAlchemy(engine_options=engine_options)
db.__setattr__('metadata_dict', {})
db.__setattr__('models_dict', {})
marshmallow = Marshmallow()
migrate = Migrate()

def declarative_model(db, bind_key):
    '''Registers a new MetaData instance in the custom db.metadata_dict and return a new declarative base'''
    from sqlalchemy import MetaData
    try: 
        model = db.models_dict[bind_key]
    except KeyError:
        metadata = MetaData(db.get_engine(bind=bind_key))
        db.metadata_dict[bind_key] = metadata
        model = db.make_declarative_base(db.Model, metadata)    
        setattr(model,'__bind_key__', bind_key)
        db.models_dict[bind_key] = model
    return model

class PaginatedMixin(object):
    from sqlalchemy import Column, Integer
    pageIndex = Column(Integer())
    pageSize = Column(Integer())
