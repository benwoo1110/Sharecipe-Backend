import typing
from flask import jsonify, make_response, request
from flask_jwt_extended.utils import get_jwt_identity
from models import Recipe, RecipeImage, RecipeLike, RecipeStep, User, UserFollow


def get_query_string(key: str, default=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            kwargs[key] = request.args.get(key, default)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def get_account_user_id(func):
    def wrapper(*args, **kwargs):
        account_id: int = get_jwt_identity()
        return func(*args, account_id=account_id, **kwargs)
    return wrapper


def get_account_user(func):
    def wrapper(*args, **kwargs):
        account_id: int = get_jwt_identity()
        user: User = User.get_by_id(account_id)
        if not user:
            return make_response(jsonify(message='No such user.'), 404)
        return func(*args, user=user, **kwargs)
    return wrapper


def validate_account_user(func):
    def wrapper(*args, **kwargs):
        account_user_id: int = get_jwt_identity()
        if account_user_id != kwargs['user_id']:
            return make_response(jsonify(message='You can only modify your own user data!'), 403)
        return func(*args, **kwargs)
    return wrapper


def validate_account_recipe(func):
    def wrapper(*args, **kwargs):
        account_user_id: int = get_jwt_identity()
        if not Recipe.check_exist(kwargs['recipe_id'], account_user_id):
            return make_response(jsonify(message='You can only modify your own recipe data!'), 403)
        return func(*args, **kwargs)
    return wrapper


def get_user(func):
    def wrapper(*args, **kwargs):
        user: User = User.get_by_id(kwargs['user_id'])
        if not user:
            return make_response(jsonify(message='No such user.'), 404)
        return func(*args, user=user, **kwargs)
    return wrapper


def check_user_exists(func):
    def wrapper(*args, **kwargs):
        if not User.check_exist(kwargs['user_id']):
            return make_response(jsonify(message='No such user.'), 404)
        return func(*args, **kwargs)
    return wrapper


def get_user_follows(func):
    def wrapper(*args, **kwargs):
        user_follows: typing.List[UserFollow] = UserFollow.get_for_user_id(kwargs['user_id'])
        return func(*args, user_follows=user_follows, **kwargs)
    return wrapper


def get_user_followers(func):
    def wrapper(*args, **kwargs):
        user_followers: typing.List[UserFollow] = UserFollow.get_for_follow_id(kwargs['user_id'])
        return func(*args, user_followers=user_followers, **kwargs)
    return wrapper


def get_user_follow(func):
    def wrapper(*args, **kwargs):
        user_follow: UserFollow = UserFollow.get_by_id(kwargs['user_id'], kwargs['follow_id'])
        return func(*args, user_follow=user_follow, **kwargs)
    return wrapper


def get_user_recipes(func):
    def wrapper(*args, **kwargs):
        recipes: typing.List[dict] = Recipe.get_for_user_id(kwargs['user_id'])
        return func(*args, recipes=recipes, **kwargs)
    return wrapper


def get_user_recipe_likes(func):
    def wrapper(*args, **kwargs):
        likes: typing.List[RecipeLike] = RecipeLike.get_for_user_id(kwargs['user_id'])
        return func(*args, likes=likes, **kwargs)
    return wrapper


def get_recipe(func):
    def wrapper(*args, **kwargs):
        recipe: Recipe = Recipe.get_by_id(kwargs['recipe_id'])
        if not recipe:
            return make_response(jsonify(message='No such recipe found.'), 404)
        return func(*args, recipe=recipe, **kwargs)
    return wrapper


def check_recipe_exists(func):
    def wrapper(*args, **kwargs):
        if not Recipe.check_exist(kwargs['recipe_id']):
            return make_response(jsonify(message='No such recipe found.'), 404)
        return func(*args, **kwargs)
    return wrapper


def get_recipe_steps(func):
    def wrapper(*args, **kwargs):
        recipe_steps = RecipeStep.get_for_recipe_id(kwargs['recipe_id'])
        return func(*args, recipe_steps=recipe_steps, **kwargs)
    return wrapper


def get_recipe_step(func):
    def wrapper(*args, **kwargs):
        recipe_step: RecipeStep = RecipeStep.get_by_id(kwargs['recipe_id'], kwargs['step_num'])
        if not recipe_step:
            return make_response(jsonify(message='No such recipe step found.'), 404)
        return func(*args, recipe_step=recipe_step, **kwargs)
    return wrapper


def get_recipe_images(func):
    def wrapper(*args, **kwargs):
        recipe_images: list = RecipeImage.get_for_recipe_id(kwargs['recipe_id'])
        return func(*args, recipe_images=recipe_images, **kwargs)
    return wrapper


def get_recipe_image(func):
    def wrapper(*args, **kwargs):
        recipe_image: RecipeImage = RecipeImage.get_by_id(kwargs['recipe_id'], kwargs.get('file_id', None))
        if not recipe_image:
            return make_response(jsonify(message='No such recipe image found.'), 404)
        return func(*args, recipe_image=recipe_image, **kwargs)
    return wrapper


def get_recipe_likes(func):
    def wrapper(*args, **kwargs):
        likes: typing.List[RecipeLike] = RecipeLike.get_for_recipe_id(kwargs['recipe_id'])
        return func(*args, likes=likes, **kwargs)
    return wrapper


def get_recipe_like(func):
    def wrapper(*args, **kwargs):
        like: RecipeLike = RecipeLike.get_by_id(kwargs['recipe_id'], kwargs['user_id'])
        return func(*args, like=like, **kwargs)
    return wrapper
