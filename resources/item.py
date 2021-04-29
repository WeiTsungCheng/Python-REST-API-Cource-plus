
# flask_jwt 改為 flask_jwt_extended, 同時裝飾器 jwt_required() -> jwt_required
# from flask_jwt import jwt_required
from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    jwt_required,
    get_jwt,
    get_jwt_identity
)
from models import item
from models.item import ItemModel


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price',
                        type=float,
                        required=True,
                        help="This field cannot be left blank!"
                        )
    parser.add_argument('store_id',
                        type=int,
                        required=True,
                        help="Every item needs a store_id."
                        )

# Flask-JWT-Extended 在 4.0.0 版 將  @jwt_required 改為 @jwt_required()
#  @jwt_required 可以接受 fresh 和 not fresh 的 access_token
    @jwt_required()
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json()
        return {'message': 'Item not found'}, 404

    #  @jwt_required(fresh=True) 只可以接受 fresh 的 access_token
    # 這表示只有tojen 是 fresh 的時候才能創建 Item
    @jwt_required(fresh=True)
    def post(self, name):
        if ItemModel.find_by_name(name):
            return {'message': "An item with name '{}' already exists.".format(name)}, 400

        data = Item.parser.parse_args()

        item = ItemModel(name, **data)

        try:
            item.save_to_db()
        except:
            return {"message": "An error occurred inserting the item."}, 500

        return item.json(), 201

    @jwt_required()
    def delete(self, name):
        # Flask-JWT-Extended 在 4.0.0 版 將  get_jwt_claims 改為 get_jwt
        claims = get_jwt()
        if not claims['is_admin']:
            return {"message" : "you do not have admin privilege"}, 401

        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {'message': 'Item deleted.'}
        return {'message': 'Item not found.'}, 404

    def put(self, name):
        data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)

        if item:
            item.price = data['price']
        else:
            item = ItemModel(name, **data)

        item.save_to_db()

        return item.json()


class ItemList(Resource):

    # Flask-JWT-Extended 在 4.0.0 版 將  @jwt_optional 改為 @jwt_required(optional=True)
    @jwt_required(optional=True)
    def get(self):
        user_id = get_jwt_identity()
        print(user_id)

        items = [item.json() for item in ItemModel.find_all()]

        if user_id:
            return {'items': items}, 200

        return {
            "items": [item['name'] for item in items],
            "message": "More data availabl if you login"
        }, 200
        # return {'items': [x.json() for x in ItemModel.query.all()]}
        # return {'items': list(map(lambda x: x.json(), ItemModel.query.all()))}
