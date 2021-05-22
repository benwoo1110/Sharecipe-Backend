from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity
from models import User, Recipe

parser = reqparse.RequestParser()
parser.add_argument('username', help = 'This field cannot be blank', required = True)
parser.add_argument('password', help = 'This field cannot be blank', required = True)


class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}, 200


class AccountRegister(Resource):
    def post(self):
        data = parser.parse_args()

        if User.get_by_username(data['username']):
            return {'error': 'Username already exist.'}, 400

        user = User(username=data['username'],  password_hash=User.hash_password(data['password']))
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
        data = parser.parse_args()
        user = User.get_by_username(data['username'])
        if not user:
            return {'error': 'Username not found.'}, 404

        if not user.verify_password(data['password']):
            return {'error': 'Invalid password.'}, 403

        access_token = create_access_token(identity=user.user_id)
        refresh_token = create_refresh_token(identity=user.user_id)

        return {
            'user_id': user.user_id,
            'access_token': access_token,
            'refresh_token': refresh_token
        }


class AccountDelete(Resource):
    @jwt_required()
    def delete(self):
        user_id = get_jwt_identity()
        user = User.get_by_id(user_id)
        if not user:
            return {'error': 'Username not found.'}, 404

        user.remove_from_db()
        return 200


class UserData(Resource):
    @jwt_required()
    def get(self, user_id):
        pass
    
    @jwt_required()
    def patch(self, user_id):
        pass


class RecipeCreate(Resource):
    @jwt_required()
    def post(self):
        pass

class RecipeData(Resource):
    @jwt_required()
    def get(self, recipe_id):
        pass

    @jwt_required()
    def patch(self, user_id):
        pass

    @jwt_required
    def delete(self, user_id):
        pass
