from flask import Flask
from flask_restful import Api
from config import app
from resources import UserRegister, UserLogin, PostResource, PostListResource
from flasgger import Swagger

api = Api(app)
swagger = Swagger(app)

api.add_resource(UserRegister, '/register')
api.add_resource(UserLogin, '/login')
api.add_resource(PostListResource, '/posts')
api.add_resource(PostResource, '/posts/<int:post_id>')

if __name__ == '__main__':
    app.run(debug=True)
