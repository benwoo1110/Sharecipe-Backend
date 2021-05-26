from flask_restful import Resource, request
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity, get_jwt
from models import RecipeStep, User, Recipe, RevokedToken
from utils import JsonParser, obj_to_dict


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


class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}, 200


class AccountRegister(Resource):
    def post(self):
        data = account_parser.parse_args()
        if User.get_by_username(data['username']):
            return {'message': 'Username already exist.'}, 400

        password = data.pop('password')
        password_hash = User.hash_password(password)

        user = User(password_hash=password_hash, **data)
        user.add_to_db()

        access_token = create_access_token(identity=user.user_id)
        refresh_token = create_refresh_token(identity=user.user_id)

        return {
            'user_id': user.user_id,
            'access_token': access_token,
            'refresh_token': refresh_token
        }


class AccountLogin(Resource):
    def post(self):
        data = account_parser.parse_args()
        user = User.get_by_username(data['username'])
        if not user or not user.verify_password(data['password']):
            return {'message': 'Invalid username or password.'}, 400

        access_token = create_access_token(identity=user.user_id)
        refresh_token = create_refresh_token(identity=user.user_id)

        return {
            'user_id': user.user_id,
            'access_token': access_token,
            'refresh_token': refresh_token
        }


class AccountRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        user_id = get_jwt_identity()
        user = User.get_by_id(user_id)
        if not user:
            return {'message': 'Invalid token. No such user!'}, 400

        access_token = create_access_token(identity=user_id)
        return {'access_token': access_token}


class AccountLogout(Resource):
    @jwt_required(refresh=True)
    def post(self):
        jti = get_jwt()['jti']
        try:
            revoked_token = RevokedToken(jti = jti)
            revoked_token.add()
            return {'message': 'Access token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class AccountDelete(Resource):
    @jwt_required(refresh=True)
    def delete(self):
        user_id = get_jwt_identity()
        user = User.get_by_id(user_id)
        if not user:
            return {'message': 'Invalid token. No such user!'}, 400

        user.remove_from_db()
        return 204


class UserSearch(Resource):
    @jwt_required()
    def get(self):
        username = request.args.get('username', '')
        users = User.search_username(username)

        if not users:
            return {'message': 'No users found.'}, 404

        data = []
        for user in users:
            data.append(obj_to_dict(user, 'user_id', 'username', 'bio'))

        return data, 200


class UserData(Resource):
    @jwt_required()
    def get(self, user_id):
        user = User.get_by_id(user_id)
        if not user:
            return {'message': 'User not found.'}, 404
    
        return obj_to_dict(user, 'user_id', 'username', 'bio'), 200

    @jwt_required()
    def patch(self, user_id):
        account_user_id = get_jwt_identity()
        if account_user_id != user_id:
            return {'message': 'You can only modify your own user data!'}, 403

        data = user_parser.parse_args()
        user = User.get_by_id(user_id)
        if not user:
            return {'message': 'User not found.'}, 404

        user.update(**data)
        return obj_to_dict(user, 'user_id', 'username', 'bio'), 200


class UserRecipe(Resource):
    @jwt_required()
    def get(self, user_id):
        pass

    @jwt_required()
    def put(self, user_id):
        account_user_id = get_jwt_identity()
        if account_user_id != user_id:
            return {'message': 'You can only modify your own user data!'}, 403

        data = recipe_parser.parse_args()
        if data.get('steps'):
            steps = []
            for step_data in data.get('steps'):
                steps.append(RecipeStep(**step_data))
            data['steps'] = steps

        recipe = Recipe(user_id=user_id, **data)
        recipe.add_to_db()

        return obj_to_dict(recipe, 'recipe_id', 'user_id', 'name', 'portion', 'difficulty', 'total_time_needed'), 200


class UserRecipeData(Resource):
    @jwt_required()
    def get(self, user_id, recipe_id):
        pass

    @jwt_required()
    def patch(self, user_id, recipe_id):
        pass

    @jwt_required
    def delete(self, user_id, recipe_id):
        pass
