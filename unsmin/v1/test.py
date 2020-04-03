from flask_restful import Resource, Api
from flask import Blueprint, render_template

hello = Blueprint('hello', __name__)
api = Api(hello)

class Hello(Resource):
    def get(self):
        #return render_template('index.html')
        return {"message": "Hello, World!"}


api.add_resource(Hello, '/Hello')

