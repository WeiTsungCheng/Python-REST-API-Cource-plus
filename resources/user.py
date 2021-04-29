from blacklist import BLACKLIST
from typing import FrozenSet
from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from models.user import UserModel

_user_parser = reqparse.RequestParser()
_user_parser.add_argument('username',
                          type=str,
                          required=True,
                          help="This field cannot be blank."
                          )
_user_parser.add_argument('password',
                          type=str,
                          required=True,
                          help="This field cannot be blank."
                          )

class UserRegister(Resource):
    # parser = reqparse.RequestParser()
    # parser.add_argument('username',
    #                     type=str,
    #                     required=True,
    #                     help="This field cannot be blank."
    #                     )
    # parser.add_argument('password',
    #                     type=str,
    #                     required=True,
    #                     help="This field cannot be blank."
    #                     )

    def post(self):
        data = _user_parser.parse_args()

        if UserModel.find_by_username(data['username']):
            return {"message": "A user with that username already exists"}, 400

        user = UserModel(**data)
        user.save_to_db()

        return {"message": "User created successfully."}, 201


class User(Resource):

    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User Not Found'}, 404
        return user.json(), 200

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User Not Found'}, 404
        user.delete_from_db()
        return {'message': 'User deleted.'}, 200


class UserLogin(Resource):
    # parser = reqparse.RequestParser()
    # parser.add_argument('username',
    #                     type=str,
    #                     required=True,
    #                     help="This field cannot be blank."
    #                     )
    # parser.add_argument('password',
    #                     type=str,
    #                     required=True,
    #                     help="This field cannot be blank."
    #                     )

    @classmethod
    def post(self):
        data = _user_parser.parse_args()

        user = UserModel.find_by_username(data['username'])

        # this is what the `authenticate()` function did in security.py
        if user and safe_str_cmp(user.password, data['password']):
            # identity= is what the identity() function did in security.py—now stored in the JWT
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200

        return {"message": "Invalid Credentials!"}, 401

class UserLogout(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti'] # jti is "JWD ID", a unique identifier for a JWT
        BLACKLIST.add(jti)
        return {"message": "Successfully logout out"}, 200

class TokenRefresh(Resource):

    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200
