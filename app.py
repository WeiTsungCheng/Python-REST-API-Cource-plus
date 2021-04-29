
from flask import Flask, jsonify
from flask_restful import Api

# 使用者註冊認證改用 flask_jwt
from flask_jwt_extended import JWTManager
# from flask_jwt import JWT

# from security import authenticate, identity
from resources.user import UserRegister, User, UserLogin, TokenRefresh, UserLogout
from resources.item import Item, ItemList
from resources.store import Store, StoreList

from blacklist import BLACKLIST

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 若PROPAGATE_EXCEPTIONS 設為 False, Flask APP 出現錯誤時 將不會回傳 Flask Extension (Flask-JWT )的錯誤， 而是return 500 ,
# 若PROPAGATE_EXCEPTIONS 設為 True, Flask APP 出現錯誤時 將會回傳 錯誤 例如當認證 User 失敗時, Flask-JWT 將會告訴你 401
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

app.secret_key = 'jose'
api = Api(app)


@app.before_first_request
def create_tables():
    db.create_all()


# jwt = JWT(app, authenticate, identity)  # /auth
jwt = JWTManager(app)
# 與 JWTManager 連結
# 添加 claims 做為 JWT 額外的資訊

# Flask-JWT-Extended 在 4.0.0 版 將 @jwt.user_claims_loader 改成 @jwt.additional_claims_loader
@jwt.additional_claims_loader
def add_claims_to_jwt(identity):
    if identity == 1: # Instead of hard-coding, you should read from your config file or database
        return {"is_admin": True}
    return {"is_admin": False}

# 檢查是否在已經不能使用的用戶名單中
# 官方更新文件錯誤 user_in_blocklist_loader
# source code 應該是 token_in_blocklist_loader , 並且應該有兩個參數
@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    print(jwt_header)
    print(jwt_payload)

    return jwt_payload['jti'] in BLACKLIST

@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({
        "des": "the token has expired",
        "err": "token_expired"
    }), 401

# 如果請求未提供 JWT token
@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        "des": "Request does not contain an access token",
        "err": "authorization_required"
    }), 401

# 如果 token 不合格式會觸發(例如token 改成隨意字串)
@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        "des": "Signature verification failed",
        "err": "invalid_token"
    }), 401

# 檢查用的的token是否 fresh
@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    return jsonify({
        "des": "The token is not fresh",
        "err": "fresh_token_required"
    }), 401

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({
        "des": "Then token has been revoked",
        "err": "token_revoked"
    }), 401


api.add_resource(Store, '/store/<string:name>')
api.add_resource(StoreList, '/stores')
api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(UserRegister, '/register')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserLogin, '/login')
api.add_resource(TokenRefresh, '/refresh')
api.add_resource(UserLogout, "/logout")

if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run(port=5000, debug=True)
