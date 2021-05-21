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


import resources, models


api.add_resource(resources.HelloWorld, '/hello')


if __name__ == "__main__":
    app.run(debug=True)
