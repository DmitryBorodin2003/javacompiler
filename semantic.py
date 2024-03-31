from typing import Tuple, Any, Dict, Optional
from enum import Enum


class BinaryOperation(Enum):
    ADD = '+'
    SUB = '-'
    MULT = '*'
    DIV = '/'
    MOD = '%'
    GT = '>'
    LT = '<'
    GE = '>='
    LE = '<='
    EQUALS = '=='
    NOTEQUALS = '!='
    BIT_AND = '&'
    BIT_OR = '|'
    LOGICAL_AND = '&&'
    LOGICAL_OR = '||'

    def __str__(self):
        return self.value


class PrimitiveType(Enum):
    VOID = 'void'
    INT = 'int'
    DOUBLE = 'double'
    BOOLEAN = 'boolean'
    STRING = 'String'

    def __str__(self):
        return self.value


VOID, INT, DOUBLE, BOOLEAN, STRING = PrimitiveType.VOID, PrimitiveType.INT, PrimitiveType.DOUBLE, \
    PrimitiveType.BOOLEAN, PrimitiveType.STRING


class DataType:
    VOID: 'DataType'
    INT: 'DataType'
    DOUBLE: 'DataType'
    BOOLEAN: 'DataType'
    STRING: 'DataType'

    def __init__(self, primitive_type_: Optional[PrimitiveType] = None,
                 return_type: Optional['DataType'] = None, params: Optional[Tuple['DataType']] = None):
        self.primitive_type = primitive_type_
        self.return_type = return_type
        self.params = params

    @property
    def function(self):
        return self.return_type is not None

    @property
    def simple(self):
        return not self.function

    def __eq__(self, other: 'DataType'):
        if self.function != other.function:
            return False
        if not self.function:
            return self.primitive_type == other.primitive_type
        else:
            if self.return_type != other.return_type:
                return False
            if len(self.params) != len(other.params):
                return False
            for i in range(len(self.params)):
                if self.params[i] != other.params[i]:
                    return False
            return True

    @staticmethod
    def from_primitive_type(primitive_type_: PrimitiveType):
        return getattr(DataType, primitive_type_.name)

    @staticmethod
    def from_string(type_string: str):
        try:
            primitive_type_ = PrimitiveType(type_string)
            return DataType.from_primitive_type(primitive_type_)
        except ValueError:
            raise SemanticException('Невозможно преобразовать строку {} в тип данных'.format(type_string))

    def __str__(self):
        if not self.function:
            return str(self.primitive_type)
        else:
            res = str(self.return_type)
            res += ' ('
            for param in self.params:
                if res[-1] != '(':
                    res += ', '
                res += str(param)
            res += ')'
        return res


for primitive_type in PrimitiveType:
    setattr(DataType, primitive_type.name, DataType(primitive_type))


class VariableScope(Enum):
    PARAM = 'param'
    LOCAL = 'local'

    def __str__(self):
        return self.value


class IdentDesc:
    def __init__(self, name: str, type_: DataType, scope: VariableScope = VariableScope.LOCAL, index: int = 0):
        self.name = name
        self.type = type_
        self.scope = scope
        self.index = index
        self.built_in = False

    def __str__(self):
        return '{}, {}, {}'.format(self.type, self.scope, 'built-in' if self.built_in else self.index)


class IdentScope:
    def __init__(self, parent: Optional['IdentScope'] = None):
        self.idents: Dict[str, IdentDesc] = {}
        self.function: Optional[IdentDesc] = None
        self.parent = parent
        self.var_index = 0
        self.param_index = 0

    @property
    def curr_func(self):
        curr = self
        while curr and not curr.function:
            curr = curr.parent
        return curr

    def add_ident(self, new_ident: IdentDesc):
        func_scope = self.curr_func

        if new_ident.scope != VariableScope.PARAM:
            new_ident.scope = VariableScope.LOCAL
        existing_ident = self.get_ident(new_ident.name)
        if existing_ident:
            error = False
            if new_ident.scope == VariableScope.PARAM:
                if existing_ident.scope == VariableScope.PARAM:
                    error = True
            else:
                error = True
            if error:
                raise SemanticException('Идентификатор {} уже объявлен'.format(new_ident.name))
        if not new_ident.type.function:
            if new_ident.scope == VariableScope.PARAM:
                new_ident.index = func_scope.param_index
                func_scope.param_index += 1
            else:
                ident_scope = func_scope
                new_ident.index = ident_scope.var_index
                ident_scope.var_index += 1
        self.idents[new_ident.name] = new_ident
        return new_ident

    def get_ident(self, name: str):
        scope = self
        ident = None
        while scope:
            ident = scope.idents.get(name)
            if ident:
                break
            scope = scope.parent
        return ident


class SemanticException(Exception):
    def __init__(self, message, row: int = None, col: int = None, **kwargs: Any):
        if row or col:
            message += " ("
            if row:
                message += 'строка: {}'.format(row)
                if col:
                    message += ', '
            if row:
                message += 'позиция: {}'.format(col)
            message += ")"
        self.message = message


TYPE_CONVERTIBILITY = {
    INT: (DOUBLE, BOOLEAN, STRING),
    DOUBLE: (STRING,),
    BOOLEAN: (STRING,)
}


def can_type_convert_to(from_type: DataType, to_type: DataType):
    if not from_type.simple or not to_type.simple:
        return False
    return from_type.primitive_type in TYPE_CONVERTIBILITY and to_type.primitive_type in TYPE_CONVERTIBILITY[
        to_type.primitive_type]


BINARY_OPERATION_TYPE_COMPATIBILITY = {
    BinaryOperation.ADD: {
        (INT, INT): INT,
        (DOUBLE, DOUBLE): DOUBLE,
        (STRING, STRING): STRING,
        (INT, DOUBLE): DOUBLE,
        (DOUBLE, INT): DOUBLE
    },
    BinaryOperation.SUB: {
        (INT, INT): INT,
        (DOUBLE, DOUBLE): DOUBLE,
        (INT, DOUBLE): DOUBLE,
        (DOUBLE, INT): DOUBLE
    },
    BinaryOperation.MULT: {
        (INT, INT): INT,
        (DOUBLE, DOUBLE): DOUBLE,
        (INT, DOUBLE): DOUBLE,
        (DOUBLE, INT): DOUBLE
    },
    BinaryOperation.DIV: {
        (INT, INT): INT,
        (DOUBLE, DOUBLE): DOUBLE,
        (INT, DOUBLE): DOUBLE,
        (DOUBLE, INT): DOUBLE
    },
    BinaryOperation.MOD: {
        (INT, INT): INT,
        (DOUBLE, DOUBLE): DOUBLE,
        (INT, DOUBLE): DOUBLE,
        (DOUBLE, INT): DOUBLE
    },

    BinaryOperation.GT: {
        (INT, INT): BOOLEAN,
        (DOUBLE, DOUBLE): BOOLEAN,
        (STRING, STRING): BOOLEAN,
    },
    BinaryOperation.LT: {
        (INT, INT): BOOLEAN,
        (DOUBLE, DOUBLE): BOOLEAN,
        (STRING, STRING): BOOLEAN,
    },
    BinaryOperation.GE: {
        (INT, INT): BOOLEAN,
        (DOUBLE, DOUBLE): BOOLEAN,
        (STRING, STRING): BOOLEAN,
    },
    BinaryOperation.LE: {
        (INT, INT): BOOLEAN,
        (DOUBLE, DOUBLE): BOOLEAN,
        (STRING, STRING): BOOLEAN,
    },
    BinaryOperation.EQUALS: {
        (INT, INT): BOOLEAN,
        (DOUBLE, DOUBLE): BOOLEAN,
        (STRING, STRING): BOOLEAN,
    },
    BinaryOperation.NOTEQUALS: {
        (INT, INT): BOOLEAN,
        (DOUBLE, DOUBLE): BOOLEAN,
        (STRING, STRING): BOOLEAN,
    },

    BinaryOperation.BIT_AND: {
        (INT, INT): INT
    },
    BinaryOperation.BIT_OR: {
        (INT, INT): INT
    },

    BinaryOperation.LOGICAL_AND: {
        (BOOLEAN, BOOLEAN): BOOLEAN
    },
    BinaryOperation.LOGICAL_OR: {
        (BOOLEAN, BOOLEAN): BOOLEAN
    },
}


def create_scope():
    scope = IdentScope()
    for name, ident in scope.idents.items():
        ident.built_in = True
    scope.var_index = 0
    return scope