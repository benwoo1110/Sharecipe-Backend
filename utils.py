from datetime import datetime
from flask import jsonify
from flask.helpers import make_response
from flask.json import JSONEncoder
from flask_restful import request, abort, Api
from jwt.exceptions import ExpiredSignatureError
from PIL import Image
import config


DEFAULT_TAG_NAMES = [
    'chinese',
    'malay',
    'indian',
    'american',
    'japanese',
    'korean',
    'italian',
    'vietnamese',
    'thai',
    'rice',
    'noodles',
    'sandwich',
    'burger',
    'meat',
    'vegetarian',
    'seafood',
    'snack',
    'drink',
    'dessert'
]


def obj_to_dict(obj, *fields):
    data = {}
    for field in fields:
        data[field] = getattr(obj, field, None)
    return data


def sanitize_image_with_pillow(image):
    img = Image.open(image)
    img.thumbnail((1080, 1080))

    if img.mode in ("RGBA", "P"):
        alpha = img.convert('RGBA').split()[-1]
        background = Image.new("RGB", img.size, (248, 170, 157))
        background.paste(img, mask=alpha)
        img = background

    return img


class JsonParser:
    def __init__(self, allow_empty_data=False):
        self.checks = {}
        self.allow_empty_data = allow_empty_data

    def add_arg(self, name:str, required=True, ctype=str):
        def check(value):
            if not value:
                if required:
                    raise ValueError(f'{name} must not be empty!')
                return value

            if ctype is not None and not isinstance(value, ctype):
                print(value, type(value))
                raise ValueError(f'{name} is of incorrect format!')
            return value

        self.checks[name] = check

    def add_nested_parser(self, name:str, parser: 'JsonParser', required=True):
        def check(value):
            if not value:
                if required:
                    raise ValueError(f'{name} must not be empty!')
                return value
            
            if isinstance(value, list):
                parsed_data = []
                for item in value:
                    parsed_data.append(parser.parse_args(item))
                return parsed_data
            else:
                return parser.parse_args(value)

        self.checks[name] = check

    def parse_args(self, data):
        if not data:
            if not self.allow_empty_data:
                raise ValueError(f'No data received!')
            return data

        parsed_data = {}

        for arg, check in self.checks.items():
            value = check(data.get(arg, None))
            if value:
                parsed_data[arg] = value

        return parsed_data

    def parse(self):
        def decorator(func):
            def wrapper(*args, **kwargs):
                data = request.get_json() or {}
                try:
                    parsed_data = self.parse_args(data)
                except Exception as e:
                    return make_response(jsonify(message=str(e)), 400)

                return func(*args, parsed_data=parsed_data, **kwargs)

            return wrapper
        
        return decorator


class BetterJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.astimezone().isoformat()

        return super().default(o)


class ApiHandler(Api):
    def error_router(self, original_handler, e):
        if self._has_fr_route() and isinstance(e, ExpiredSignatureError):
            return make_response(jsonify(message='Access token expired! Please re-login.'), 403)
        
        elif isinstance(e, Exception):
            if config.PRODUCTION_MODE:
                return make_response(jsonify(message='An unknown error occurred!'), 500)
            else:
                return make_response(jsonify(message=str(e)), 500)

        return original_handler(e)
