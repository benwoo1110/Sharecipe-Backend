from flask import jsonify, make_response, send_file
from flask_restful import Resource, request
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity, get_jwt
from models import Ingredient, RecipeStep, User, Recipe, RevokedToken
from utils import JsonParser, obj_to_dict
import file_manager


account_parser = JsonParser()
account_parser.add_arg('username')
account_parser.add_arg('password')
account_parser.add_arg('bio', required=False)


user_parser = JsonParser()
user_parser.add_arg('username')
user_parser.add_arg('bio')


recipe_parser = JsonParser()
recipe_parser.add_arg('name')
recipe_parser.add_arg('portion', required=False)
recipe_parser.add_arg('difficulty', required=False)
recipe_parser.add_arg('total_time_needed', required=False)
recipe_parser.add_arg('steps', required=False)
recipe_parser.add_arg('ingredients', required=False)


recipe_step_parser = JsonParser()
recipe_step_parser.add_arg('step_number')
recipe_step_parser.add_arg('name')
recipe_step_parser.add_arg('description', required=False)
recipe_step_parser.add_arg('time_needed', required=False)


class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}, 200


class AccountRegister(Resource):
    def post(self):
        data = account_parser.parse_args()
        if User.get_by_username(data['username']):
            return make_response(jsonify(message='Username already exist.'), 400)

        password = data.pop('password')
        password_hash = User.hash_password(password)

        user = User(password_hash=password_hash, **data)
        user.add_to_db()

        access_token = create_access_token(identity=user.user_id)
        refresh_token = create_refresh_token(identity=user.user_id)

        return make_response(jsonify(user_id=user.user_id, access_token=access_token, refresh_token=refresh_token), 201)


class AccountLogin(Resource):
    def post(self):
        data = account_parser.parse_args()
        user = User.get_by_username(data['username'])
        if not user or not user.verify_password(data['password']):
            return make_response(jsonify(message='Invalid username or password.'), 400)

        access_token = create_access_token(identity=user.user_id)
        refresh_token = create_refresh_token(identity=user.user_id)

        return make_response(jsonify(user_id=user.user_id, access_token=access_token, refresh_token=refresh_token), 200)


class AccountRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        user_id = get_jwt_identity()
        user = User.get_by_id(user_id)
        if not user:
            return make_response(jsonify(message='Invalid token. No such user!'), 400)

        access_token = create_access_token(identity=user_id)
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
    def delete(self):
        user_id = get_jwt_identity()
        user = User.get_by_id(user_id)
        if not user:
            return make_response(jsonify(message='Invalid token. No such user!'), 400)

        user.remove_from_db()
        return make_response('', 204)


class UserSearch(Resource):
    @jwt_required()
    def get(self):
        username = request.args.get('username', '')
        users = User.search_username(username)
        return make_response(jsonify(users), 200)


class UserData(Resource):
    @jwt_required()
    def get(self, user_id):
        user = User.get_by_id(user_id)
        if not user:
            return make_response(jsonify(message='No users found.'), 404)
    
        return obj_to_dict(user, 'user_id', 'username', 'bio'), 200

    @jwt_required()
    def patch(self, user_id):
        account_user_id = get_jwt_identity()
        if account_user_id != user_id:
            return make_response(jsonify(message='You can only modify your own user data!'), 403)

        data = user_parser.parse_args()
        user = User.get_by_id(user_id)
        if not user:
            return make_response(jsonify(message='No users found.'), 404)

        user.update(**data)
        return obj_to_dict(user, 'user_id', 'username', 'bio'), 200


class UserProfileImage(Resource):
    @jwt_required()
    def get(self, user_id):
        user = User.get_by_id(user_id)
        if not user:
            return make_response(jsonify(message='No users found.'), 404)
        if not user.profile_image:
            return make_response(jsonify(message='User does not have a profile picture'), 404)

        output = file_manager.download(user.profile_image)
        return make_response(send_file(output, as_attachment=True), 200)

    @jwt_required()
    def put(self, user_id):
        account_user_id = get_jwt_identity()
        if account_user_id != user_id:
            return make_response(jsonify(message='You can only modify your own user data!'), 403)

        user = User.get_by_id(user_id)
        if not user:
            return make_response(jsonify(message='No users found.'), 404)
        
        uploaded_file = request.files['image']
        if not uploaded_file or uploaded_file.filename == '':
            return make_response(jsonify(message='No image uploaded.'), 404)

        file_id = file_manager.save(uploaded_file)
        user.update(profile_image=file_id)
        return make_response(jsonify(message='Profile picture uploaded.'), 200)

    @jwt_required()
    def delete(self, user_id):
        account_user_id = get_jwt_identity()
        if account_user_id != user_id:
            return make_response(jsonify(message='You can only modify your own user data!'), 403)

        user = User.get_by_id(user_id)
        if not user:
            return make_response(jsonify(message='No users found.'), 404)
        if not user.profile_image:
            return make_response(jsonify(message='Nothing to delete'), 304)

        file_manager.delete(user.profile_image)
        user.update(profile_image=None)
        return make_response(jsonify(message='Profile picture deleted.'), 200)


class UserProfileImageId(Resource):
    @jwt_required()
    def get(self, user_id):
        user = User.get_by_id(user_id)
        if not user:
            return make_response(jsonify(message='No users found.'), 404)
        if not user.profile_image:
            return make_response(jsonify(message='User does not have a profile picture'), 404)

        return make_response(jsonify(id=user.profile_image), 200)


class UserRecipe(Resource):
    @jwt_required()
    def get(self, user_id):
        pass

    @jwt_required()
    def put(self, user_id):
        account_user_id = get_jwt_identity()
        if account_user_id != user_id:
            return make_response(jsonify(message='You can only modify your own user data!'), 403)

        data = recipe_parser.parse_args()
        if data.get('steps'):
            steps = []
            for step_data in data.get('steps'):
                steps.append(RecipeStep(**step_data))
            data['steps'] = steps

        if data.get('ingredients'):
            steps = []
            for step_data in data.get('ingredients'):
                steps.append(Ingredient(**step_data))
            data['ingredients'] = steps

        recipe = Recipe(user_id=account_user_id, **data)
        recipe.add_to_db()

        return make_response(jsonify(recipe), 201)


class UserRecipeData(Resource):
    @jwt_required()
    def get(self, user_id, recipe_id):
        recipe = Recipe.get_by_id(recipe_id)
        if not recipe or recipe.user_id != user_id:
            return make_response(jsonify(message='No recipe found.'), 404)
        
        return make_response(jsonify(recipe), 200)

    @jwt_required()
    def patch(self, user_id, recipe_id):
        recipe = Recipe.get_by_id(recipe_id)
        if not recipe or recipe.user_id != user_id:
            return make_response(jsonify(message='No recipe found.'), 404)
        
        data = recipe_parser.parse_args()
        if data.get('steps'):
            steps = []
            for step_data in data.get('steps'):
                steps.append(RecipeStep(**step_data))
            data['steps'] = steps

        recipe.update(**data)
        return make_response(jsonify(recipe), 200)

    @jwt_required()
    def delete(self, user_id, recipe_id):
        recipe = Recipe.get_by_id(recipe_id)
        if not recipe or recipe.user_id != user_id:
            return make_response(jsonify(message='User not found.'), 404)

        recipe.remove_from_db()
        return make_response('', 204)


class RecipeStepData(Resource):
    @jwt_required()
    def get(self, user_id, recipe_id, step_num):
        step: RecipeStep = RecipeStep.get_by_id(recipe_id, step_num)
        if not step:
            return make_response(jsonify(message='No such step found.'), 404)

        return make_response(jsonify(step), 200)

    @jwt_required()
    def put(self, user_id, recipe_id, step_num):
        account_user_id = get_jwt_identity()
        if account_user_id != user_id:
            return make_response(jsonify(message='You can only modify your own user data!'), 403)

        data = recipe_parser.parse_args()
        recipeStep = RecipeStep(recipe_id=recipe_id, step_num=step_num, **data)
        recipeStep.add_to_db()

        return make_response(jsonify(recipeStep), 201)

    @jwt_required()
    def patch(self, user_id, recipe_id, step_num):
        step: RecipeStep = RecipeStep.get_by_id(recipe_id, step_num)
        if not step:
            return make_response(jsonify(message='No such step found.'), 404)

        data = recipe_parser.parse_args()
        step.update(data)
        return make_response(jsonify(step), 200)

    @jwt_required()
    def delete(self, user_id, recipe_id, step_num):
        step: RecipeStep = RecipeStep.get_by_id(recipe_id, step_num)
        if not step:
            return make_response(jsonify(message='No such step found.'), 404)

        step.remove_from_db()
        return make_response('', 204)
