from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from utils import ApiHandler


app = Flask(__name__)
app.config.from_pyfile('config.py')


api = ApiHandler(app)
db = SQLAlchemy(app)
jwt = JWTManager(app)


@app.before_first_request
def create_tables():
    db.create_all()


@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_data):
    jti = jwt_data['jti']
    return models.RevokedToken.is_jti_blacklisted(jti)


import resources, models


api.add_resource(resources.HelloWorld,      '/hello') # GET

api.add_resource(resources.AccountRegister, '/account/register') # POST
api.add_resource(resources.AccountLogin,    '/account/login') # POST
api.add_resource(resources.AccountRefresh,  '/account/refresh') # POST
api.add_resource(resources.AccountLogout,   '/account/logout') # POST
api.add_resource(resources.AccountDelete,   '/account/delete') # POST

api.add_resource(resources.UserSearch,      '/users') # GET
api.add_resource(resources.UserData,        '/users/<int:user_id>') # GET PATCH
api.add_resource(resources.UserRecipe,      '/users/<int:user_id>/recipes') # GET PUT
api.add_resource(resources.UserRecipeData,  '/users/<int:user_id>/recipes/<int:recipe_id>') # GET PATCH DELETE
api.add_resource(resources.RecipeStepData,  '/users/<int:user_id>/recipes/<int:recipe_id>/<int:step_num>') # GET PATCH DELETE


if __name__ == "__main__":
    app.run(debug=True)
