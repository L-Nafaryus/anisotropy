# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from peewee import (
    TextField,
    ColumnBase,
    Value,
    fn,
    Node,
    Expression,
    OP,
    Field
)
import json
from numpy import ndarray

class ListField(TextField):
    field_type = "list"

    def db_value(self, value):
        return str(value)

    def python_value(self, value):
        pval = []

        for entry in value[1 : -1].split(","):
            try:
                pval.append(float(entry))

            except:
                pval.append(entry.strip().replace("'", ""))

        return pval

"""
class JSONField(TextField):
    # TODO: fix double quotes when use __eq__ in 'where' method
    field_type = "TEXT"

    def db_value(self, value):
        if isinstance(value, ndarray):
            formatted = list(value)
        
        else:
            formatted = value
            
        return json.dumps(formatted)

    def python_value(self, value):
        if value is not None:
            return json.loads(value)
"""

class JSONPath(ColumnBase):
    def __init__(self, field, path=None):
        super(JSONPath, self).__init__()
        self._field = field
        self._path = path or ()

    @property
    def path(self):
        return Value('$%s' % ''.join(self._path))

    def __getitem__(self, idx):
        if isinstance(idx, int):
            item = '[%s]' % idx
        else:
            item = '.%s' % idx
        return JSONPath(self._field, self._path + (item,))

    def set(self, value, as_json=None):
        if as_json or isinstance(value, (list, dict)):
            value = fn.json(self._field._json_dumps(value))
        return fn.json_set(self._field, self.path, value)

    def update(self, value):
        return self.set(fn.json_patch(self, self._field._json_dumps(value)))

    def remove(self):
        return fn.json_remove(self._field, self.path)

    def json_type(self):
        return fn.json_type(self._field, self.path)

    def length(self):
        return fn.json_array_length(self._field, self.path)

    def children(self):
        return fn.json_each(self._field, self.path)

    def tree(self):
        return fn.json_tree(self._field, self.path)

    def __sql__(self, ctx):
        return ctx.sql(fn.json_extract(self._field, self.path)
                       if self._path else self._field)


class JSONField(TextField):
    field_type = 'TEXT'
    unpack = False

    def __init__(self, json_dumps=None, json_loads=None, **kwargs):
        self._json_dumps = json_dumps or json.dumps
        self._json_loads = json_loads or json.loads
        super(JSONField, self).__init__(**kwargs)

    def python_value(self, value):
        if value is not None:
            try:
                return json.loads(value)
            except (TypeError, ValueError):
                return value

    def db_value(self, value):
        if value is not None:
            if isinstance(value, ndarray):
                value = list(value)

            if not isinstance(value, Node):
                value = json.dumps(value)
            return value

    def _e(op):
        def inner(self, rhs):
            if isinstance(rhs, (list, dict)):
                rhs = Value(rhs, converter=self.db_value, unpack=False)
            return Expression(self, op, rhs)
        return inner
    __eq__ = _e(OP.EQ)
    __ne__ = _e(OP.NE)
    __gt__ = _e(OP.GT)
    __ge__ = _e(OP.GTE)
    __lt__ = _e(OP.LT)
    __le__ = _e(OP.LTE)
    __hash__ = Field.__hash__

    def __getitem__(self, item):
        return JSONPath(self)[item]

    def set(self, value, as_json=None):
        return JSONPath(self).set(value, as_json)

    def update(self, data):
        return JSONPath(self).update(data)

    def remove(self):
        return JSONPath(self).remove()

    def json_type(self):
        return fn.json_type(self)

    def length(self):
        return fn.json_array_length(self)

    def children(self):
        """
        Schema of `json_each` and `json_tree`:

        key,
        value,
        type TEXT (object, array, string, etc),
        atom (value for primitive/scalar types, NULL for array and object)
        id INTEGER (unique identifier for element)
        parent INTEGER (unique identifier of parent element or NULL)
        fullkey TEXT (full path describing element)
        path TEXT (path to the container of the current element)
        json JSON hidden (1st input parameter to function)
        root TEXT hidden (2nd input parameter, path at which to start)
        """
        return fn.json_each(self)

    def tree(self):
        return fn.json_tree(self)