from typing import Any
from flask_restful import request, abort


def obj_to_dict(obj, *fields):
    data = {}
    for field in fields:
        data[field] = getattr(obj, field, None)
    return data


class JsonParser:
    def __init__(self, allow_empty_data=False):
        self.checks = {}
        self.allow_empty_data = allow_empty_data

    def add_arg(self, name:str, required=True):
        def check(value):
            if not (value and required):
                raise ValueError(f'{name} must not be empty!')
        self.checks[name] = check

    def parse_args(self):
        data = request.get_json() or {}
        if not data:
            if not self.allow_empty_data:
                abort(400, message='No data received!')

        for arg, check in self.checks.items():
            try:
                check(data.get(arg, None))
            except Exception as e:
                abort(400, message=str(e))

        return data
