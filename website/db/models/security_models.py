# -*- encoding: utf-8 -*-

# Other libs
from marshmallow import fields

from flask_marshmallow import Marshmallow
from flask_security import UserMixin, RoleMixin

from simplejson import dumps

from sqlalchemy import (
    Boolean,
    DateTime,
    Column,
    Integer,
    String,
    Text,
    UnicodeText,
    ForeignKey
)
from sqlalchemy.orm import relationship, backref

# Current project
from website.db import db, marshmallow, PaginatedMixin, declarative_model
from website.audit import AuditableMixin

bind_key = None
Model = declarative_model(db,bind_key)

class Setting(Model, AuditableMixin):
    __bind_key__ = bind_key
    __tablename__ = 'settings'
    id = Column(String(255), primary_key=True)
    value = Column(String(255))

class SettingSchema(marshmallow.SQLAlchemyAutoSchema): #noqa
    class Meta:
        model = Setting

class RolesUsers(Model, AuditableMixin):
    __bind_key__ = bind_key
    __tablename__ = 'roles_users'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    user_id = Column('user_id', Integer(), ForeignKey('user.id'))
    role_id = Column('role_id', Integer(), ForeignKey('role.id'))

class Role(Model, RoleMixin, AuditableMixin):
    __bind_key__ = bind_key
    from sqlalchemy.sql import func
    import datetime
    __tablename__ = 'role'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(80), unique=True, nullable=False)
    description = Column(String(255))
    # A comma separated list of strings
    permissions = Column(UnicodeText, nullable=True)
    update_datetime = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=datetime.datetime.utcnow,
    )
    def __repr__(self):
        # return f'Role [{self.id}] {self.name}, {self.description} => {self.permissions}'
        return f'Role [{self.id}] {self.name}, {self.description}'


class User(Model, UserMixin, AuditableMixin):
    __bind_key__ = bind_key
    from sqlalchemy.ext.declarative import declared_attr
    from sqlalchemy.sql import func
    import datetime
    __tablename__ = 'user'    
    """User information"""
    # flask_security basic fields
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    # Make username unique but not required.
    username = Column(String(255), unique=True, nullable=True)
    password = Column(String(255), nullable=False)
    active = Column(Boolean(), nullable=False)

    # Flask-Security user identifier
    fs_uniquifier = Column(String(64), unique=True, nullable=False)

    # confirmable
    confirmed_at = Column(DateTime())

    # trackable
    last_login_at = Column(DateTime())
    current_login_at = Column(DateTime())
    last_login_ip = Column(String(64))
    current_login_ip = Column(String(64))
    login_count = Column(Integer)

    # 2FA
    tf_primary_method = Column(String(64), nullable=True)
    tf_totp_secret = Column(String(255), nullable=True)
    tf_phone_number = Column(String(128), nullable=True)

    create_datetime = Column(DateTime, nullable=False, server_default=func.now())
    update_datetime = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=datetime.datetime.utcnow,
    )

    # unified sign in
    us_totp_secrets = Column(Text, nullable=True)
    us_phone_number = Column(String(128), nullable=True)

    roles = relationship('Role', secondary='roles_users',
                         backref=backref('users', lazy='dynamic'))

    def has_permission(self, p):
        if self.username is not None and self.has_role('administrator'):
            return True
        return super().has_permission(p)
    
    def __repr__(self):
        return f'User [{self.id}] {self.username}, {self.email}'


class RoleSchema(marshmallow.SQLAlchemyAutoSchema): #noqa
    class Meta:
        model = Role

class UserSchema(marshmallow.SQLAlchemyAutoSchema): #noqa
    class Meta:
        model = User

class JsGridUserItemSchema(marshmallow.SQLAlchemyAutoSchema): #noqa
    class Meta:
        item = fields.Nested(UserSchema)