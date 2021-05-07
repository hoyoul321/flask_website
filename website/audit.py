##################### This might be useful for Auditing
## Taken from https://gist.github.com/ngse/c20058116b8044c65d3fbceda3fdf423
## Possible issue with the integer ID for each table, not flexible


# Requires use of Flask Login for the user tracking
# Implement by using AuditableMixin in your model class declarations
# e.g. class ImportantThing(AuditableMixin, Base):
import json
from sqlalchemy import Column, ForeignKey, Integer, String, UnicodeText, Boolean, Date, DateTime
from sqlalchemy import event, inspect, text
from sqlalchemy.event import listens_for
from sqlalchemy.orm import class_mapper
from sqlalchemy.orm.attributes import get_history
from flask import current_app
from website.db import db, declarative_model
import datetime 

ACTION_CREATE = 1
ACTION_UPDATE = 2
ACTION_DELETE = 3

AUDITED_ACTIONS = [ACTION_CREATE, ACTION_UPDATE, ACTION_DELETE]

def _current_user_id_or_none():
    from flask_login import current_user
    try:
        return current_user.id
    except:
        return None


bind_key = 'AUDIT'
Model = declarative_model(db, bind_key)
pending_audits = []

@event.listens_for(db.session, 'after_flush')
def after_flush(session, flush_context):
    pending_audits.clear()

class AuditLog(Model):
    __bind_key__ = bind_key
    __tablename__ = 'audit_log'
    """Model an audit log of user actions"""
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    datetime = Column(DateTime, default=datetime.datetime.now())
    user_id = Column(Integer, doc="The ID of the user who made the change")
    target_type = Column(String(100), nullable=False, doc="The table name of the altered object")
    target_id = Column(UnicodeText, doc="The PK dict of the altered object as JSON string")
    action = Column(Integer, doc="Create (1), update (2), or delete (3)")
    state_before = Column(UnicodeText, doc="Stores a JSON string representation of a dict containing the altered column "
                                          "names and original values")
    state_after = Column(UnicodeText, doc="Stores a JSON string representation of a dict containing the altered column "
                                         "names and new values")
    

    def __init__(self, target, action, state_before, state_after):
        self.datetime = datetime.datetime.now()
        self.user_id = _current_user_id_or_none()
        self.target_type = target.__tablename__
        self.target_id = json.dumps(inspect(target).identity)
        self.action = action
        self.state_before = state_before
        self.state_after = state_after
        self.target = target
    
    def to_dict(self):      
        import datetime   
        return  {
            'datetime': self.datetime.strftime('%Y-%m-%d %H:%M:%S'),
            'user_id':self.user_id,
            'target_type':self.target_type,
            'target_id':self.target_id,
            'action':self.action,
            'state_before':self.state_before,
            'state_after':self.state_after,
        }

    def __repr__(self):
        return '<AuditLog %r: %r -> %r>' % (self.user_id, self.target_type, self.action)

    def save(self,connection):
        with connection.begin() as transaction:
            connection.execute(text(
            """
            INSERT INTO audit_log
            (datetime, user_id, target_type, target_id, action, state_before, state_after)
            VALUES(:datetime, :user_id, :target_type, :target_id, :action, :state_before, :state_after)
            """), self.to_dict())

from website.db import marshmallow
class AuditLogSchema(marshmallow.SQLAlchemyAutoSchema):
    class Meta:
        model = AuditLog

def get_state_after(target):
    result = {}
    inspector = inspect(target)
    attrs = class_mapper(target.__class__).column_attrs
    for attr in attrs:
        hist = getattr(inspector.attrs, attr.key).history
        if hist.has_changes():
            result[attr.key] = getattr(target, attr.key)
    return result

def get_state_before(target):
    result = {}
    inspector = inspect(target)
    attrs = class_mapper(target.__class__).column_attrs
    for attr in attrs:
        hist = getattr(inspector.attrs, attr.key).history
        if hist.has_changes():
            result[attr.key] = get_history(target, attr.key)[2].pop()
    return result

def create_audit(connection, target, action, **kwargs):
    # current_app.logger.debug(f'=======> create_audit')
    audit = AuditLog(
        target,
        action,
        kwargs.get('state_before'),
        kwargs.get('state_after')
    )
    d = audit.to_dict()
    log = db.session.query(AuditLog).filter_by(
        **d
    ).one_or_none()

    from deepdiff import grep
    pending = pending_audits | grep(d)
    if (not log) and (not pending):
        #db.session.add(audit)
        audit.save(connection)
        pending_audits.append(d)

class AuditableMixin(object):
    import datetime
    """Allow a model to be automatically audited"""
    from website.audit import create_audit

    @classmethod
    def __declare_last__(cls):
        
        @listens_for(cls, 'after_insert')
        def audit_insert(mapper, connection, target): 
            """Listen for the `after_insert` event and create an AuditLog entry"""
            from website.utils import get_schema  
                 
            # current_app.logger.debug(f'=======> audit_insert')
            state_after = get_state_after(target)
            if ACTION_CREATE in AUDITED_ACTIONS:
                s = get_schema(target)
                create_audit(db.get_engine(bind=bind_key), target, ACTION_CREATE, state_after=s.dumps(state_after))

        @listens_for(cls, 'after_delete')
        def audit_delete(mapper, connection, target):
            """Listen for the `after_delete` event and create an AuditLog entry"""
            from website.utils import get_schema

            # current_app.logger.debug(f'=======> audit_delete')
            state_before = get_state_before(target)
            if ACTION_DELETE in AUDITED_ACTIONS:
                tid = json.dumps(inspect(target).identity)
                s = get_schema(target)
                create_audit(db.get_engine(bind=bind_key), target, ACTION_DELETE, state_before=s.dumps(state_before))
        
        @listens_for(cls, 'after_update')
        def audit_update(mapper, connection, target):
            """Listen for the `after_update` event and create an AuditLog entry with before and after state changes"""
            from deepdiff import DeepDiff
            from websiteq.utils import get_schema

            # current_app.logger.debug(f'=======> after_update')
            s = get_schema(target)
            
            if ACTION_UPDATE in AUDITED_ACTIONS:
                tid = s.dumps(inspect(target).identity)
                state_before = get_state_before(target)
                state_after = get_state_after(target)
                changed = False
                # current_app.logger.debug(f'state_before ---------> {state_before}')
                # current_app.logger.debug(f'state_after ---------> {state_after}')

                changed = DeepDiff(state_before, state_after, ignore_order=True)
                # current_app.logger.debug(f'changed ---------> {changed}')
            
                if changed:
                    create_audit(db.get_engine(bind=bind_key), target, ACTION_UPDATE,
                                state_before=s.dumps(state_before),
                                state_after=s.dumps(state_after))
