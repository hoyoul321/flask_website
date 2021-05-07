from alembic import op
from alembic.operations import Operations, MigrateOperation


def create_replaceables(functions: list =[], views: list=[], procedures: list=[]):
    '''Creates functions, then views and procedures passed, in the order they are passed.
    Parameters
    ----------
    functions: list of MySQLFunction, optional
    views: list of MySQLView, optional
    procedures: list of MySQLProcedure, optional
    '''
    for f in functions:
        op.create_function(f)
    for v in views:
        op.create_view(v)
    for p in procedures:
        op.create_sp(p)


def drop_replaceables(functions: list=[], views: list=[], procedures: list=[]):
    '''Drops procedures, then views and functions passed, in reverse order.
    
    Parameters
    ----------
    functions: list of MySQLFunction, optional
    views: list of MySQLView, optional
    procedures: list of MySQLProcedure, optional
    '''
    for p in reversed(procedures):
        op.drop_sp(p)
    for v in reversed(views):
        op.drop_view(v)
    for f in reversed(functions):
        op.drop_function(f)

class ReplaceableObject(object):
    def __init__(self, name, parameters='', sqltext='', return_type='', characteristics=''):
        self.name = name
        self.sqltext = sqltext
        self.characteristics = characteristics
        self.parameters = parameters
        self.return_type = return_type

class MySQLView(ReplaceableObject):
    def __init__(self, name, sqltext):
        super().__init__(
            name=name,
            parameters='',
            return_type='',
            characteristics='',
            sqltext=sqltext)

class MySQLFunction(ReplaceableObject):
    def __init__(self, name, parameters, return_type, characteristics, sqltext):
        super().__init__(
            name=name,
            parameters=parameters,
            return_type=return_type,
            characteristics=characteristics,
            sqltext=sqltext)

class MySQLProcedure(ReplaceableObject):
    def __init__(self, name, parameters, sqltext, characteristics=''):
        super().__init__(
            name=name,
            parameters=parameters,
            return_type='',
            characteristics=characteristics,
            sqltext=sqltext)

        

class ReversibleOp(MigrateOperation):
    def __init__(self, target):
        self.target = target

    @classmethod
    def invoke_for_target(cls, operations, target):
        op = cls(target)
        return operations.invoke(op)

    def reverse(self):
        raise NotImplementedError()

    @classmethod
    def _get_object_from_version(cls, operations, ident):
        version, objname = ident.split(".")

        module = operations.get_context().script.get_revision(version).module
        obj = getattr(module, objname)
        return obj

    @classmethod
    def replace(cls, operations, target, replaces=None, replace_with=None):

        if replaces:
            old_obj = cls._get_object_from_version(operations, replaces)
            drop_old = cls(old_obj).reverse()
            create_new = cls(target)
        elif replace_with:
            old_obj = cls._get_object_from_version(operations, replace_with)
            drop_old = cls(target).reverse()
            create_new = cls(old_obj)
        else:
            raise TypeError("replaces or replace_with is required")

        operations.invoke(drop_old)
        operations.invoke(create_new)

@Operations.register_operation("create_view", "invoke_for_target")
@Operations.register_operation("replace_view", "replace")
class CreateViewOp(ReversibleOp):
    def reverse(self):
        return DropViewOp(self.target)

@Operations.register_operation("drop_view", "invoke_for_target")
class DropViewOp(ReversibleOp):
    def reverse(self):
        return CreateViewOp(self.target)

@Operations.register_operation("create_sp", "invoke_for_target")
@Operations.register_operation("replace_sp", "replace")
class CreateSPOp(ReversibleOp):
    def reverse(self):
        return DropSPOp(self.target)

@Operations.register_operation("drop_sp", "invoke_for_target")
class DropSPOp(ReversibleOp):
    def reverse(self):
        return CreateSPOp(self.target)


@Operations.register_operation("create_function", "invoke_for_target")
@Operations.register_operation("replace_function", "replace")
class CreateFuncOp(ReversibleOp):
    def reverse(self):
        return DropFuncOp(self.target)

@Operations.register_operation("drop_function", "invoke_for_target")
class DropFuncOp(ReversibleOp):
    def reverse(self):
        return CreateFuncOp(self.target)


@Operations.implementation_for(CreateViewOp)
def create_view(operations, operation):
    operations.execute(f"""
CREATE VIEW `{operation.target.name}` AS
{operation.target.sqltext}
""")

@Operations.implementation_for(DropViewOp)
def drop_view(operations, operation):
    operations.execute(f"DROP VIEW `{operation.target.name}`" )

@Operations.implementation_for(CreateSPOp)
def create_sp(operations, operation):
    operations.execute(f"""
CREATE PROCEDURE `{operation.target.name}`(
    {operation.target.parameters}
)
{operation.target.characteristics}
BEGIN
{operation.target.sqltext}
END
""")

@Operations.implementation_for(DropSPOp)
def drop_sp(operations, operation):
    operations.execute(f"DROP PROCEDURE `{operation.target.name}`")


@Operations.implementation_for(CreateFuncOp)
def create_function(operations, operation):
    operations.execute(f"""
CREATE FUNCTION `{operation.target.name}`(
    {operation.target.parameters}
) RETURNS {operation.target.return_type}
{operation.target.characteristics}
BEGIN
{operation.target.sqltext}
END
""")

@Operations.implementation_for(DropFuncOp)
def drop_function(operations, operation):
    operations.execute(f"DROP FUNCTION `{operation.target.name}`")