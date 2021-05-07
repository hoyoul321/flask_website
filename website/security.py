from flask_security import Security, SQLAlchemySessionUserDatastore
from website.config import c
from website.db import db
from website.db.models.security_models import User, Role
from sqlalchemy.exc import OperationalError

user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)
security = Security(datastore=user_datastore)

def setup_hooks(a):        
    with a.app_context():
        from flask import current_app as app
            
        @app.before_first_request
        def before_first_request():
            from flask import current_app
            from website.db.models.security_models import Setting, SettingSchema
            
            current_app.logger.debug("before_first_request()")

            try:
                first_run_complete = Setting.query.filter_by(id='first_run_complete').one_or_none()
                first_run_complete = first_run_complete.value if first_run_complete else False
            except OperationalError:
                first_run_complete = False
            # current_app.logger.debug(first_run_complete)

            if not first_run_complete:            
                admin_role = user_datastore.find_or_create_role(
                    name='administrator',
                    description="Administrator Role")
                
                user_role = user_datastore.find_or_create_role(
                    name='user',
                    description="User Role",
                    permissions='trading_monitor_viewer')    
                
                u1 = user_datastore.find_user(email='admin@gmail.com')
                if not u1:
                    u1 = user_datastore.create_user(username='admin',
                                                    email='admin@gmail.com',
                                                    password='admin')
                    user_datastore.add_role_to_user(u1,admin_role)
                    user_datastore.commit()
                
                u3 = user_datastore.find_user(email='test@gmail.co.kr')
                if not u3:
                    u3 = user_datastore.create_user(username='test',
                                                    email='test@gmail.com',
                                                    password='test')
                    user_datastore.commit()

                complete = Setting(id='first_run_complete', value='True')
                db.session.add(complete)
                db.session.commit()
                

                # app.logger.debug('--------------------- Users and Roles ---------------------------')
                # app.logger.debug(f'{admin_role} Permisisons: {list(admin_role.get_permissions())}')
                # app.logger.debug(f'{user_role} Permisisons: {list(admin_role.get_permissions())}')
                # for u in [u1,u2,u3]:
                #     app.logger.debug(f'{u} Roles: {u.roles}')
                #     for p in ['trading_monitor_viewer','trading_monitor_admin']:
                #         app.logger.debug(f'{u} has {p}: {u.has_permission(p)}')
                # app.logger.debug('-----------------------------------------------------------------')
