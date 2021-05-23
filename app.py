from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager


app = Flask(__name__)
app.config.from_pyfile('config.py')


api = Api(app)
db = SQLAlchemy(app)
jwt = JWTManager(app)


@app.before_first_request
def create_tables():
    db.create_all()


@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_data):
    jti = jwt_data['jti']
    return models.RevokedTokenModel.is_jti_blacklisted(jti)


import resources, models


api.add_resource(resources.HelloWorld,      '/hello')
api.add_resource(resources.AccountRegister, '/account/register')
api.add_resource(resources.AccountLogin,    '/account/login')
api.add_resource(resources.AccountRefresh,  '/account/refresh')
api.add_resource(resources.AccountDelete,   '/account/delete')
api.add_resource(resources.UserSearch,      '/users')
api.add_resource(resources.UserData,        '/users/<int:user_id>')
api.add_resource(resources.RecipeCreate,    '/recipes')
api.add_resource(resources.RecipeData,      '/recipes/<int:recipe_id>')


if __name__ == "__main__":
    app.run(debug=True)
