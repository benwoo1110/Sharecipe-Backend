from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, create_access_token
from models import User, Recipe

parser = reqparse.RequestParser()
parser.add_argument('username', help = 'This field cannot be blank', required = True)
parser.add_argument('password', help = 'This field cannot be blank', required = True)


class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}, 200


class UserRegistration(Resource):
    def post(self):
        data = parser.parse_args()
        print(data)
