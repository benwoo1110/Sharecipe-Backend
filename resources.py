import typing
import zipfile
from flask import jsonify, make_response, send_file
from flask_restful import Resource, request
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt
from models import RecipeImage, RecipeIngredient, RecipeStep, User, UserFollow, Recipe, RevokedToken
from utils import JsonParser, obj_to_dict
from file_manager import S3FileManager, LocalFileManager
from middleware import check_recipe_exists, check_user_exists, get_account_user_id, get_query_string, get_recipe, get_recipe_image, get_recipe_images, get_recipe_step, get_user, check_account_user, get_user_follows
import config


file_manager = S3FileManager() if config.PRODUCTION_MODE else LocalFileManager()


account_parser = JsonParser()
account_parser.add_arg('username')
account_parser.add_arg('password')
account_parser.add_arg('bio', required=False)


user_parser = JsonParser()
user_parser.add_arg('username')
user_parser.add_arg('bio')


user_follows_parser = JsonParser()
user_follows_parser.add_arg('follow_id')


recipe_parser = JsonParser()
recipe_parser.add_arg('name')
recipe_parser.add_arg('portion', required=False)
recipe_parser.add_arg('difficulty', required=False)
recipe_parser.add_arg('total_time_needed', required=False)
recipe_parser.add_arg('steps', required=False)
recipe_parser.add_arg('ingredients', required=False)


recipe_step_parser = JsonParser()
recipe_step_parser.add_arg('step_number')
recipe_step_parser.add_arg('name', required=False)
recipe_step_parser.add_arg('description', required=False)
recipe_step_parser.add_arg('time_needed', required=False)


recipe_image_parser = JsonParser()
recipe_image_parser.add_arg('image_ids')


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
    @get_account_user_id
    @get_user
    def post(self, user_id: int, user: User):
        access_token = create_access_token(identity=user.user_id)
        return make_response(jsonify(user_id=user.user_id, access_token=access_token), 200)


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
    @get_account_user_id
    @get_user
    def delete(self, user_id: int, user: User):
        user.remove_from_db()
        return make_response('', 204)


class UserSearch(Resource):
    @jwt_required()
    @get_query_string('username', '')
    def get(self, username: str):
        users = User.search_username(username)
        return make_response(jsonify(users), 200)


class UserData(Resource):
    @jwt_required()
    @get_user
    def get(self, user_id: int, user: User):
        return make_response(jsonify(user), 200)

    @jwt_required()
    @check_account_user
    @get_user
    @user_parser.parse()
    def patch(self, user_id: int, user: User, parsed_data: dict):
        user.update(**parsed_data)
        return obj_to_dict(user, 'user_id', 'username', 'bio'), 200


class UserProfileImage(Resource):
    @jwt_required()
    @get_user
    def get(self, user_id: int, user: User):
        if not user.profile_image_id:
            return make_response(jsonify(message='User does not have a profile picture'), 404)

        output = file_manager.download(user.profile_image_id)
        return make_response(send_file(output, as_attachment=True), 200)

    @jwt_required()
    @check_account_user
    @get_user
    def put(self, user_id: int, user: User):
        uploaded_file = request.files.get("image")
        if not uploaded_file or uploaded_file.filename == '':
            return make_response(jsonify(message='No image uploaded.'), 400)
        
        #TODO Make sure its a loadable image.

        file_id = file_manager.save(uploaded_file)
        user.update(profile_image_id=file_id)
        return make_response(jsonify(message='Profile picture uploaded.'), 200)

    @jwt_required()
    @check_account_user
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


class UserFollowing(Resource):
    @jwt_required()
    @check_user_exists
    @get_user_follows
    def get(self, user_id: int, user_follows: typing.List[UserFollow]):
        return make_response(jsonify(user_follows), 200)

    @jwt_required()
    @check_account_user
    @user_follows_parser.parse()
    def put(self, user_id: int, parsed_data: dict):
        user_follow = UserFollow(user_id=user_id, **parsed_data)
        user_follow.add_to_db()
        return make_response(jsonify(user_follow), 201)

    @jwt_required()
    @check_account_user
    @user_follows_parser.parse()
    def delete(self, user_id: int, parsed_data: dict):
        user_follow: UserFollow = UserFollow.get_by_id(user_id, parsed_data['follow_id'])
        if not user_follow:
            return make_response(jsonify(message='Not following that user.'), 404)
        user_follow.remove_from_db()
        return make_response('', 204)


class UserRecipe(Resource):
    @jwt_required()
    def get(self, user_id: int):
        recipes = Recipe.get_for_user_id(user_id)
        return make_response(jsonify(recipes), 200)

    @jwt_required()
    @check_account_user
    @recipe_parser.parse()
    def put(self, user_id: int, parsed_data: dict):
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

        recipe = Recipe(user_id=user_id, **parsed_data)
        recipe.add_to_db()

        return make_response(jsonify(recipe), 201)


class UserRecipeData(Resource):
    @jwt_required()
    @get_recipe
    def get(self, user_id: int, recipe_id: int, recipe: Recipe):
        return make_response(jsonify(recipe), 200)

    @jwt_required()
    @check_account_user
    @get_recipe
    @recipe_parser.parse()
    def patch(self, user_id: int, recipe_id: int, recipe: Recipe, parsed_data: dict):
        if parsed_data.get('steps'):
            steps = []
            for step_data in parsed_data.get('steps'):
                steps.append(RecipeStep(**step_data))
            parsed_data['steps'] = steps

        #TODO patch ingredients

        recipe.update(**parsed_data)
        return make_response(jsonify(recipe), 200)

    @jwt_required()
    @check_account_user
    @get_recipe
    def delete(self, user_id: int, recipe_id: int, recipe: Recipe):
        recipe.remove_from_db()
        return make_response('', 204)


class UserRecipeStep(Resource):
    @jwt_required()
    @get_recipe
    def get(self, user_id: int, recipe_id: int, recipe: Recipe):
        return make_response(jsonify(recipe.steps), 200)

    @jwt_required()
    @check_account_user
    @check_recipe_exists
    @recipe_step_parser.parse()
    def put(self, user_id: int, recipe_id: int, parsed_data: dict):
        recipeStep = RecipeStep(recipe_id=recipe_id, **parsed_data)
        recipeStep.add_to_db()
        return make_response(jsonify(recipeStep), 201)


class UserRecipeStepData(Resource):
    @jwt_required()
    @check_recipe_exists
    @get_recipe_step
    def get(self, user_id: int, recipe_id: int, step_num: int, recipe_step: RecipeStep):
        return make_response(jsonify(recipe_step), 200)

    @jwt_required()
    @check_account_user
    @check_recipe_exists
    @get_recipe_step
    @recipe_step_parser.parse()
    def patch(self, user_id: int, recipe_id: int, step_num: int, recipe_step: RecipeStep, parsed_data: dict):
        recipe_step.update(parsed_data)
        return make_response(jsonify(recipe_step), 200)

    @jwt_required()
    @check_account_user
    @check_recipe_exists
    @get_recipe_step
    def delete(self, user_id: int, recipe_id: int, step_num: int, recipe_step: RecipeStep):
        recipe_step.remove_from_db()
        return make_response('', 204)


class UserRecipeImage(Resource):
    @jwt_required()
    @check_recipe_exists
    @get_recipe_images
    def get(self, user_id: int, recipe_id: int, recipe_images: list):
        zipfolder = zipfile.ZipFile('downloads/images.zip', 'w', compression = zipfile.ZIP_STORED)
        for recipe_image in recipe_images:
            zipfolder.write(file_manager.get_local_path(recipe_image.file_id), recipe_image.file_id)
        zipfolder.close()

        return send_file('downloads/images.zip',  as_attachment = True)

    @jwt_required()
    @check_account_user
    @check_recipe_exists
    def put(self, user_id: int, recipe_id: int):
        image_files = request.files.getlist("images")
        if not image_files:
            return make_response(jsonify(message='No image uploaded.'), 400)

        for image_file in image_files:
            file_id = file_manager.save(image_file)
            recipe_image = RecipeImage(file_id=file_id, recipe_id=recipe_id)
            recipe_image.add_to_db()
        
        return make_response('', 204)

    @jwt_required()
    @check_account_user
    @check_recipe_exists
    @recipe_image_parser.parse()
    def delete(self, user_id: int, recipe_id: int, parsed_data: dict):
        recipe_images = RecipeImage.get_for_ids(set(parsed_data['image_ids']))
        for recipe_image in recipe_images:
            file_manager.delete(recipe_image.file_id)
            recipe_image.remove_from_db()

        return make_response('', 204)


class UserRecipeImageData(Resource):
    @jwt_required()
    @check_recipe_exists
    @get_recipe_image
    def get(self, user_id: int, recipe_id: int, file_id: str, recipe_image: RecipeImage):
        output = file_manager.download(recipe_image.file_id)
        return make_response(send_file(output, as_attachment=True), 200)

    @jwt_required()
    @check_account_user
    @check_recipe_exists
    @get_recipe_image
    def delete(self, user_id: int, recipe_id: int, file_id: str, recipe_image: RecipeImage):
        file_manager.delete(recipe_image.file_id)
        recipe_image.remove_from_db()
        return make_response('', 204)


class UserRecipeIcon(Resource):
    @jwt_required()
    @check_recipe_exists
    @get_recipe_image
    def get(self, user_id: int, recipe_id: int, recipe_image: RecipeImage):
        output = file_manager.download(recipe_image.file_id)
        return make_response(send_file(output, as_attachment=True), 200)


class Search(Resource):
    @jwt_required()
    @get_query_string('search_string', '')
    def get(self, search_string: str):
        result_data = {}
        result_data["recipes"] = Recipe.get_all_public(search_string)
        result_data["users"] = User.get_all_public(search_string)
        return make_response(jsonify(result_data), 200)
 