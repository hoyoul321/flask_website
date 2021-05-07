
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
from oam_intranet.db import db, marshmallow, PaginatedMixin, declarative_model
from oam_intranet.audit import AuditableMixin

bind_key = 'OAM_MARKET_INDEX'
Model = declarative_model(db, bind_key)

class MarketIndex(Model, AuditableMixin):  
    __bind_key__ = bind_key
    __tablename__ = 'daily_market_index'    
    date = Column(Date(), primary_key=True)
    ticker = Column(String(45), primary_key=True)
    description = Column(String(45))
    open = Column(Float())
    close = Column(Float())
    high = Column(Float())
    low = Column(Float())

class MartketIndexSymbol(Model, AuditableMixin): 
    __bind_key__ = bind_key   
    __tablename__ = 'ipo_brokers'    
    inner_ticker = Column(String(45))
    description = Column(String(45), primary_key=True)
    bloomberg_ticker = Column(String(45))
    yahoo_ticker = Column(String(45))
    bloomburg_ticker = Column(String(45))
    market_stack_ticker = Column(String(45))