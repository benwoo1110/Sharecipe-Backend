from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, create_access_token
from models import User, Recipe

parser = reqparse.RequestParser()
parser.add_argument('username', help = 'This field cannot be blank', required = True)
parser.add_argument('password', help = 'This field cannot be blank', required = True)


class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}, 200


class UserCreate(Resource):
    def post(self):
        pass


class UserLogin(Resource):
    def post(self):
        pass


class UserData(Resource):
    @jwt_required
    def get(self, user_id):
        pass
    
    @jwt_required
    def patch(self, user_id):
        pass

    @jwt_required
    def delete(self, user_id):
        pass


class RecipeCreate(Resource):
    @jwt_required
    def post(self):
        pass

class RecipeData(Resource):
    @jwt_required
    def get(self, recipe_id):
        pass

    @jwt_required
    def patch(self, user_id):
        pass

    @jwt_required
    def delete(self, user_id):
        pass
