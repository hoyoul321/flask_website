
from marshmallow import fields, INCLUDE
from flask_marshmallow import Marshmallow
from flask_security import UserMixin, RoleMixin

from simplejson import dumps

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    Column,
    Integer,
    String,
    UnicodeText,
    ForeignKey
)
from sqlalchemy.orm import relationship, backref

# Current project
from website.db import db, marshmallow, PaginatedMixin, declarative_model
from website.audit import AuditableMixin

#bind_key = 'FLASK_WEBSITE'
#Model = declarative_model(db, bind_key)

#class User(Model, AuditableMixin):  
#    __bind_key__ = bind_key
#    __tablename__ = 'user'    
#    id = Column(String(45), primary_key=True)
#    password = Column(String(255))
#    user_name = Column(String(255))
#    extra = Column(string(255))