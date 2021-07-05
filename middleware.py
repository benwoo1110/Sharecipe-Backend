import re
from flask import jsonify, make_response, request
from flask_jwt_extended.utils import get_jwt_identity
from models import Recipe, RecipeStep, User


def get_query_string(key, default=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            kwargs[key] = request.args.get(key, default)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def check_account_user(func):
    def wrapper(*args, **kwargs):
        account_user_id = get_jwt_identity()
        if account_user_id != kwargs['user_id']:
            return make_response(jsonify(message='You can only modify your own user data!'), 403)
        return func(*args, **kwargs)
    return wrapper


def get_account_user_id(func):
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        return func(*args, user_id=user_id, **kwargs)
    return wrapper


def get_user(func):
    def wrapper(*args, **kwargs):
        user = User.get_by_id(kwargs['user_id'])
        if not user:
            return make_response(jsonify(message='No such user.'), 404)
        return func(*args, user=user, **kwargs)
    return wrapper


def get_recipe(func):
    def wrapper(*args, **kwargs):
        recipe = Recipe.get_by_id(kwargs['recipe_id'], kwargs.get('user_id', None))
        if not recipe:
            return make_response(jsonify(message='No such recipe found.'), 404)
        return func(*args, recipe=recipe, **kwargs)
    return wrapper


def check_recipe_exists(func):
    def wrapper(*args, **kwargs):
        if not Recipe.check_exist(kwargs['recipe_id'], kwargs.get('user_id', None)):
            return make_response(jsonify(message='No such recipe found.'), 404)
        return func(*args, **kwargs)
    return wrapper


def get_recipe_step(func):
    def wrapper(*args, **kwargs):
        recipe_step = RecipeStep.get_by_id(kwargs['recipe_id'], kwargs['step_num'])
        if not recipe_step:
            return make_response(jsonify(message='No such recipe step found.'), 404)
        return func(*args, recipe_step=recipe_step, **kwargs)
    return wrapper
