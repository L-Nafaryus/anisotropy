# -*- coding: utf-8 -*-
# This file is part of anisotropy.
# License: GNU GPL version 3, see the file "LICENSE" for details.

from peewee import TextField
import json


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


class JSONField(TextField):
    def db_value(self, value):
        return json.dumps(value)

    def python_value(self, value):
        if value is not None:
            return json.loads(value)