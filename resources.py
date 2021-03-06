import re
import typing
import zipfile
import random
from flask import json, jsonify, make_response, send_file
from flask.json import tag
from flask_restful import Resource, request
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt
from models import DiscoverSection, RecipeImage, RecipeIngredient, RecipeLike, RecipeStep, RecipeTag, Stats, User, UserFollow, Recipe, RecipeReview, RevokedToken
from utils import JsonParser, obj_to_dict, sanitize_image_with_pillow, DEFAULT_TAG_NAMES
from file_manager import file_manager
from middleware import check_recipe_exists, check_user_exists, get_account_user, get_account_user_id, get_query_string, get_recipe, get_recipe_image, get_recipe_images, get_recipe_like, get_recipe_likes, get_recipe_step, get_recipe_steps, get_user, get_user_follow, get_user_followers, get_user_recipes, validate_account_recipe, validate_account_user, get_user_follows, get_user_recipe_likes
import config


account_parser = JsonParser()
account_parser.add_arg('username')
account_parser.add_arg('password')
account_parser.add_arg('bio', required=False)


account_password_parser = JsonParser()
account_password_parser.add_arg('old_password')
account_password_parser.add_arg('new_password')


account_delete_parser = JsonParser()
account_delete_parser.add_arg('user_id', ctype=int)
account_delete_parser.add_arg('password')


users_parser = JsonParser()
users_parser.add_arg('user_ids', required=False, ctype=list)


user_parser = JsonParser()
user_parser.add_arg('username')
user_parser.add_arg('bio', required=False)


user_follows_parser = JsonParser()
user_follows_parser.add_arg('follow_id', ctype=int)


recipes_parser = JsonParser(allow_empty_data=True)
recipes_parser.add_arg('recipe_ids', required=False, ctype=list)


recipe_images_parser = JsonParser(allow_empty_data=True)
recipe_images_parser.add_arg('recipe_images_ids', required=False, ctype=list)


recipe_ingredients_parser = JsonParser()
recipe_ingredients_parser.add_arg('name')
recipe_ingredients_parser.add_arg('quantity', ctype=float)
recipe_ingredients_parser.add_arg('unit', required=False)


recipe_step_parser = JsonParser()
recipe_step_parser.add_arg('step_number', ctype=int)
recipe_step_parser.add_arg('description')


recipe_image_parser = JsonParser()
recipe_image_parser.add_arg('image_ids', ctype=list)


recipe_tag_parser = JsonParser()
recipe_tag_parser.add_arg('name')


recipe_review_parser = JsonParser()
recipe_review_parser.add_arg('rating', ctype=int)
recipe_review_parser.add_arg('comment')


recipe_parser = JsonParser()
recipe_parser.add_arg('name')
recipe_parser.add_arg('description', required=False)
recipe_parser.add_arg('portion', required=False, ctype=int)
recipe_parser.add_arg('difficulty', required=False, ctype=int)
recipe_parser.add_arg('total_time_needed', required=False, ctype=int)
recipe_parser.add_arg('is_public', required=False, ctype=bool)
recipe_parser.add_nested_parser('steps', recipe_step_parser, required=False)
recipe_parser.add_nested_parser('ingredients', recipe_ingredients_parser, required=False)
recipe_parser.add_nested_parser('tags', recipe_tag_parser, required=False)


class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}, 200


class AccountRegister(Resource):
    @account_parser.parse()
    def post(self, parsed_data: dict):
        if User.get_by_username(parsed_data['username']):
            return make_response(jsonify(message='Username already exist.'), 400)

        password = parsed_data.pop('password')
        password_hash = User.hash_password(password)

        user = User(password_hash=password_hash, **parsed_data)
        user.add_to_db()

        access_token = create_access_token(identity=user.user_id)
        refresh_token = create_refresh_token(identity=user.user_id)

        return make_response(jsonify(user_id=user.user_id, access_token=access_token, refresh_token=refresh_token), 201)


class AccountLogin(Resource):
    @account_parser.parse()
    def post(self, parsed_data: dict):
        user = User.get_by_username(parsed_data['username'])
        if not user or not user.verify_password(parsed_data['password']):
            return make_response(jsonify(message='Invalid username or password.'), 400)

        access_token = create_access_token(identity=user.user_id)
        refresh_token = create_refresh_token(identity=user.user_id)

        return make_response(jsonify(user_id=user.user_id, access_token=access_token, refresh_token=refresh_token), 200)


class AccountRefresh(Resource):
    @jwt_required(refresh=True)
    @get_account_user
    def post(self, user: User):
        access_token = create_access_token(identity=user.user_id)
        return make_response(jsonify(user_id=user.user_id, access_token=access_token), 200)


class AccountPassword(Resource):
    @jwt_required(refresh=True)
    @get_account_user
    @account_password_parser.parse()
    def post(self, user: User, parsed_data: dict):
        if not user.verify_password(parsed_data.get('old_password')):
            return make_response(jsonify(message='Incorrect password. Change aborted.'), 400)

        password_hash = User.hash_password(parsed_data.get('new_password'))
        user.update(password_hash=password_hash)
        return make_response('', 204)


class AccountLogout(Resource):
    @jwt_required(refresh=True)
    def post(self):
        jti = get_jwt()['jti']
        try:
            revoked_token = RevokedToken(jti = jti)
            revoked_token.add()
            return make_response(jsonify(message='Access token has been revoked.'), 200)
        except:
            return make_response(jsonify(message='Something went wrong.'), 500)


class AccountDelete(Resource):
    @jwt_required(refresh=True)
    @get_account_user
    @account_delete_parser.parse()
    def delete(self, user: User, parsed_data: dict):
        if parsed_data.get('user_id') != user.user_id:
            return make_response('Invalid account user.', 400)
        
        if not user.verify_password(parsed_data.get('password', '')):
            return make_response('Incorrect password.', 400)

        jti = get_jwt()['jti']
        revoked_token = RevokedToken(jti = jti)
        revoked_token.add()

        user.remove_from_db()
        return make_response('', 204)


class Users(Resource):
    @jwt_required()
    @users_parser.parse()
    def get(self, parsed_data: dict):
        users = User.get_all_of_ids(parsed_data.get('user_ids', None))
        return make_response(jsonify(users), 200)


class UserData(Resource):
    @jwt_required()
    @get_user
    def get(self, user_id: int, user: User):
        return make_response(jsonify(user), 200)

    @jwt_required()
    @validate_account_user
    @get_user
    @user_parser.parse()
    def patch(self, user_id: int, user: User, parsed_data: dict):
        if user.username != parsed_data['username'] and User.get_by_username(parsed_data['username']):
            return make_response(jsonify(message='Username already exist.'), 400)

        user.update(**parsed_data)
        return make_response(jsonify(user), 200)


class UserStats(Resource):
    @jwt_required()
    @check_user_exists
    @get_account_user_id
    def get(self, user_id: int, account_id: int):
        stats = []
        stats.append(Stats(name="Follows", stats_type="follow", number=UserFollow.get_follows_count(user_id)))
        stats.append(Stats(name="Follower", stats_type="follower", number=UserFollow.get_follower_count(user_id)))
        stats.append(Stats(name="Liked recipes", stats_type="liked_recipe", number=RecipeLike.get_count_for_user(user_id)))
        stats.append(Stats(name="Created recipes", stats_type="user_recipe", number=Recipe.get_count_for_user(user_id, user_id != account_id)))
        return make_response(jsonify(stats), 200)


class UserProfileImage(Resource):
    @jwt_required()
    @get_user
    def get(self, user_id: int, user: User):
        if not user.profile_image_id:
            return make_response(jsonify(message='User does not have a profile picture'), 404)

        output = file_manager.download(user.profile_image_id)
        return make_response(send_file(output, as_attachment=True), 200)

    @jwt_required()
    @validate_account_user
    @get_user
    def put(self, user_id: int, user: User):
        uploaded_file = request.files.get("image")
        if not uploaded_file or uploaded_file.filename == '':
            return make_response(jsonify(message='No image uploaded.'), 400)
        
        profile_image = sanitize_image_with_pillow(uploaded_file)
        file_id = file_manager.save(profile_image)

        if user.profile_image_id:
            file_id = file_manager.delete(user.profile_image_id)

        user.update(profile_image_id=file_id)
        return make_response(jsonify(message='Profile picture uploaded.'), 200)

    @jwt_required()
    @validate_account_user
    @get_user
    def delete(self, user_id: int, user: User):
        if not user.profile_image_id:
            return make_response(jsonify(message='Nothing to delete'), 304)

        file_manager.delete(user.profile_image_id)
        user.update(profile_image_id=None)
        return make_response(jsonify(message='Profile picture deleted.'), 200)


class UserProfileImageId(Resource):
    @jwt_required()
    @get_user
    def get(self, user_id: int, user: User):
        if not user.profile_image_id:
            return make_response(jsonify(message='User does not have a profile picture'), 404)

        return make_response(jsonify(id=user.profile_image_id), 200)


class UserFollows(Resource):
    @jwt_required()
    @check_user_exists
    @get_user_follows
    def get(self, user_id: int, user_follows: typing.List[UserFollow]):
        user_ids = set(follow.follow_id for follow in user_follows)
        users = User.get_all_of_ids(user_ids)
        return make_response(jsonify(users), 200)


class UserFollowers(Resource):
    @jwt_required()
    @check_user_exists
    @get_user_followers
    def get(self, user_id: int, user_followers: typing.List[UserFollow]):
        user_ids = set(follow.user_id for follow in user_followers)
        users = User.get_all_of_ids(user_ids)
        return make_response(jsonify(users), 200)


class UserFollowUser(Resource):
    @jwt_required()
    @check_user_exists
    @get_user_follow
    def get(self, user_id: int, follow_id, user_follow: UserFollow):
        state: bool = user_follow is not None
        return make_response(jsonify(state=state), 200)

    @jwt_required()
    @validate_account_user
    @get_user_follow
    def post(self, user_id: int, follow_id, user_follow: UserFollow):
        if user_follow is not None:
            return make_response(jsonify(message='Account already follow that user.'), 400)

        follow = UserFollow(user_id=user_id, follow_id=follow_id)
        follow.add_to_db()
        return make_response(jsonify(follow), 201)

    @jwt_required()
    @validate_account_user
    @get_user_follow
    def delete(self, user_id: int, follow_id, user_follow: UserFollow):
        if user_follow is None:
            return make_response(jsonify(message='Account is not follow that user.'), 400)

        user_follow.remove_from_db()
        return make_response('', 204)


class UserRecipes(Resource):
    @jwt_required()
    @get_user_recipes
    def get(self, user_id: int, recipes: typing.List[dict]):
        return make_response(jsonify(recipes), 200)


class UserRecipeLikes(Resource):
    @jwt_required()
    @check_user_exists
    @get_user_recipe_likes
    def get(self, user_id: int, likes: typing.List[RecipeLike]):
        recipes = []
        for like in likes:
            recipes.append(Recipe.get_by_id(like.recipe_id))

        return make_response(jsonify(recipes), 200)


class Recipes(Resource):
    @jwt_required()
    def get(self):
        pass

    @jwt_required()
    @get_account_user_id
    @recipe_parser.parse()
    def put(self, account_id: int, parsed_data: dict):
        if parsed_data.get('steps'):
            steps = []
            for step_data in parsed_data.get('steps'):
                steps.append(RecipeStep(**step_data))
            parsed_data['steps'] = steps

        if parsed_data.get('ingredients'):
            ingredients = []
            for ingredient_data in parsed_data.get('ingredients'):
                ingredients.append(RecipeIngredient(**ingredient_data))
            parsed_data['ingredients'] = ingredients

        if parsed_data.get('tags'):
            tags = []
            for tag_data in parsed_data.get('tags'):
                tags.append(RecipeTag(**tag_data))
            parsed_data['tags'] = tags

        recipe = Recipe(user_id=account_id, **parsed_data)
        recipe.add_to_db()

        return make_response(jsonify(recipe), 201)


class RecipeTagSuggestions(Resource):
    @jwt_required()
    def get(self):
        tagNames = set(DEFAULT_TAG_NAMES)
        for tag, in RecipeTag.get_top_of(100):
            tagNames.add(tag.lower())

        return make_response(jsonify(list(tagNames)), 200)


class RecipeData(Resource):
    @jwt_required()
    @get_recipe
    def get(self, recipe_id: int, recipe: Recipe):
        return make_response(jsonify(recipe), 200)

    @jwt_required()
    @validate_account_recipe
    @get_recipe
    @recipe_parser.parse()
    def patch(self, recipe_id: int, recipe: Recipe, parsed_data: dict):
        if 'steps' in parsed_data:
            steps = []
            for step_data in parsed_data.get('steps'):
                steps.append(RecipeStep(**step_data))
            parsed_data['steps'] = steps

        if 'ingredients' in parsed_data:
            steps = []
            for step_data in parsed_data.get('ingredients'):
                steps.append(RecipeIngredient(**step_data))
            parsed_data['ingredients'] = steps

        if parsed_data.get('tags'):
            tags = []
            for tag_data in parsed_data.get('tags'):
                tags.append(RecipeTag(**tag_data))
            parsed_data['tags'] = tags

        recipe.update(**parsed_data)
        return make_response(jsonify(recipe), 200)

    @jwt_required()
    @validate_account_recipe
    @get_recipe
    def delete(self, recipe_id: int, recipe: Recipe):
        recipe.remove_from_db()
        return make_response('', 204)


class RecipeSteps(Resource):
    @jwt_required()
    @get_recipe_steps
    def get(self, recipe_id: int, recipe_steps: typing.List[RecipeStep]):
        return make_response(jsonify(recipe_steps), 200)

    @jwt_required()
    @validate_account_recipe
    @recipe_step_parser.parse()
    def put(self, recipe_id: int, parsed_data: dict):
        recipeStep = RecipeStep(recipe_id=recipe_id, **parsed_data)
        recipeStep.add_to_db()
        return make_response(jsonify(recipeStep), 201)


class RecipeStepData(Resource):
    @jwt_required()
    @check_recipe_exists
    @get_recipe_step
    def get(self, recipe_id: int, step_num: int, recipe_step: RecipeStep):
        return make_response(jsonify(recipe_step), 200)

    @jwt_required()
    @validate_account_recipe
    @get_recipe_step
    @recipe_step_parser.parse()
    def patch(self, recipe_id: int, step_num: int, recipe_step: RecipeStep, parsed_data: dict):
        recipe_step.update(parsed_data)
        return make_response(jsonify(recipe_step), 200)

    @jwt_required()
    @validate_account_recipe
    @get_recipe_step
    def delete(self, recipe_id: int, step_num: int, recipe_step: RecipeStep):
        recipe_step.remove_from_db()
        return make_response('', 204)


class RecipeImages(Resource):
    @jwt_required()
    @check_recipe_exists
    @recipe_images_parser.parse()
    def post(self, recipe_id: int, parsed_data: dict):
        target = parsed_data.get('recipe_images_ids', None)
        target = set(target) if target else None
        recipe_images: list = RecipeImage.get_for_recipe_id(recipe_id)

        zipfolder = zipfile.ZipFile('downloads/images.zip', 'w', compression = zipfile.ZIP_DEFLATED)
        for recipe_image in recipe_images:
            if not target or recipe_image.file_id in target:
                zipfolder.write(file_manager.download(recipe_image.file_id), recipe_image.file_id)
        zipfolder.close()

        return send_file('downloads/images.zip',  as_attachment = True)

    @jwt_required()
    @validate_account_recipe
    def put(self, recipe_id: int):
        image_files = request.files.getlist("images")
        if not image_files:
            return make_response(jsonify(message='No image uploaded.'), 400)

        for image_file in image_files:
            image = sanitize_image_with_pillow(image_file)
            file_id = file_manager.save(image)
            recipe_image = RecipeImage(file_id=file_id, recipe_id=recipe_id)
            recipe_image.add_to_db()
        
        return make_response('', 204)

    @jwt_required()
    @validate_account_recipe
    @recipe_image_parser.parse()
    def delete(self, recipe_id: int, parsed_data: dict):
        for image in parsed_data['image_ids']:
            recipe_image = RecipeImage.get_by_id(recipe_id, image["file_id"])
            file_manager.delete(recipe_image.file_id)
            recipe_image.remove_from_db()

        return make_response('', 204)


class RecipeImageData(Resource):
    @jwt_required()
    @check_recipe_exists
    @get_recipe_image
    def get(self, recipe_id: int, file_id: str, recipe_image: RecipeImage):
        output = file_manager.download(recipe_image.file_id)
        return make_response(send_file(output, as_attachment=True), 200)

    @jwt_required()
    @validate_account_recipe
    @get_recipe_image
    def delete(self, recipe_id: int, file_id: str, recipe_image: RecipeImage):
        file_manager.delete(recipe_image.file_id)
        recipe_image.remove_from_db()
        return make_response('', 204)


class RecipeIcon(Resource):
    @jwt_required()
    @check_recipe_exists
    @get_recipe_image
    def get(self, recipe_id: int, recipe_image: RecipeImage):
        output = file_manager.download(recipe_image.file_id)
        return make_response(send_file(output, as_attachment=True), 200)


class RecipeLikes(Resource):
    @jwt_required()
    @check_recipe_exists
    @get_recipe_likes
    def get(self, recipe_id: int, likes: typing.List[RecipeLike]):
        return make_response(jsonify(likes), 200)


class RecipeLikeUser(Resource):
    @jwt_required()
    @check_recipe_exists
    @check_user_exists
    @get_recipe_like
    def get(self, recipe_id: int, user_id: int, like: RecipeLike):
        state = like is not None
        return make_response(jsonify(state=state), 200)

    @jwt_required()
    @validate_account_user
    @check_recipe_exists
    @get_recipe_like
    def post(self, recipe_id: int, user_id: int, like: RecipeLike):
        if like is not None:
            make_response(jsonify(message='Account already like that recipe.'), 400)

        new_like = RecipeLike(recipe_id=recipe_id, user_id=user_id)
        new_like.add_to_db()
        return make_response(jsonify(new_like), 201)

    @jwt_required()
    @validate_account_user
    @check_recipe_exists
    @get_recipe_like
    def delete(self, recipe_id: int, user_id: int, like: RecipeLike):
        if like is None:
            make_response(jsonify(message='Account did not like that recipe.'), 400)

        like.remove_from_db()
        return make_response('', 204)


class RecipeReviews(Resource):
    @jwt_required()
    @check_recipe_exists
    def get(self, recipe_id: int):
        reviews = RecipeReview.get_for_recipe(recipe_id)
        return make_response(jsonify(reviews), 200)

    @jwt_required()
    @get_account_user_id
    @recipe_review_parser.parse()
    def put(self, recipe_id: int, account_id, parsed_data: dict):
        review: RecipeReview = RecipeReview.get_by_id(recipe_id, account_id)
        if review is not None:
            review.update(**parsed_data)
            return make_response(jsonify(review), 200)

        new_review = RecipeReview(recipe_id=recipe_id, user_id=account_id, **parsed_data)
        new_review.add_to_db()
        return make_response(jsonify(new_review), 201)


class Search(Resource):
    @jwt_required()
    @get_query_string('search_string', '')
    def get(self, search_string: str):

        #TODO Search by categories 

        result_data = {}
        result_data["recipes"] = Recipe.get_all_public(search_string)
        result_data["users"] = User.get_all_public(search_string)
        return make_response(jsonify(result_data), 200)


class Discover(Resource):
    @jwt_required()
    @get_account_user_id
    def get(self, account_id: int):
        discovers = []

        tag_names = RecipeTag.get_top_of(20)
        random.shuffle(tag_names)
        if len(tag_names) > 8:
            tag_names = tag_names[:8]

        for name, in tag_names:
            recipe_ids = [int(tag.recipe_id) for tag in RecipeTag.get_for_name(name)]
            recipes = Recipe.get_for_ids(recipe_ids)
            discovers.append(DiscoverSection(header=name.capitalize(), size="normal", recipes=recipes))

        follows: typing.List[UserFollow] = UserFollow.get_for_user_id(account_id)
        random.shuffle(follows)
        if len(follows) > 8:
            follows = follows[:8]

        for follow in follows:
            user: User = User.get_by_id(follow.follow_id)
            recipes = Recipe.get_for_user_id(follow.follow_id)
            if recipes:
                discovers.append(DiscoverSection(
                    header="Made by " + user.username, 
                    size="normal", 
                    recipes=recipes
                ))

        random.shuffle(discovers)
        discovers.insert(0, DiscoverSection(header="Latest", size="large", recipes=Recipe.get_all_public('', 5)))

        return make_response(jsonify(sections=discovers), 200)
