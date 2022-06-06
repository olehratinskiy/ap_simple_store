import base64

from flask import Flask, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager
from flask_cors import CORS
from wsgiref.simple_server import make_server
from greeting import api
from flask_bcrypt import Bcrypt
from schema import *
from models import Session
from datetime import timedelta
session = Session()
app = Flask(__name__)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
app.config["JWT_SECRET_KEY"] = "super-secret"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=10)
cors = CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/item', methods=["POST"])
@jwt_required()
def add_item():
    current_identity_username = get_jwt_identity()
    if current_identity_username != 'admin':
        return {'message': 'Access is denied'}, 403

    data = request.get_json()
    if data['name'] == '' or data['storage_quantity'] == '' or data['price'] == '':
        return {'message': 'Invalid name/storage_quantity/price supplied'}, 400

    new_item = Item(name=data['name'], storage_quantity=data['storage_quantity'], price=data['price'], status=data['status'])
    quantity = session.query(Item.item_id).count()
    if quantity >= 8:
        return {'message': 'Exceed number of items'}, 400
    if session.query(Item).filter_by(name=data['name']).first() is None:
        session.add(new_item)
        session.commit()
        return 'Successful operation', 200
    else:
        return {'message': 'Product with this name already exists'}, 405


@app.route('/items', methods=["POST"])
def get_items():
    items = session.query(Item).all()
    schema = ItemSchema(many=True)
    return jsonify(schema.dump(items))


@app.route('/item/<item_id>', methods=["POST"])
def get_item_by_id(item_id):
    item = session.query(Item).filter_by(item_id=int(item_id)).first()
    if item is not None:
        return ItemSchema().dump(item), 200
    elif not item_id:
        return 'Invalid item id', 400
    else:
        return 'Item was not found', 404


@app.route('/item/<name>', methods=["PUT"])
@jwt_required()
def put_item_by_name(name):
    current_identity_username = get_jwt_identity()
    if current_identity_username != 'admin':
        return {'message': 'Access is denied'}, 403

    item = request.get_json()
    if item['name'] == '' or item['storage_quantity'] == '' or item['price'] == '':
        return {'message': 'Invalid name/storage_quantity/price supplied'}, 400

    if item is None:
        return {'message': 'Invalid input'}, 400
    else:
        _name = item['name']
        _quantity = item['storage_quantity']
        _price = item['price']
        _status = item['status']
        item_1 = session.query(Item).filter_by(name=name).first()
        if item_1 is not None:
            item_1.name = _name
            item_1.storage_quantity = _quantity
            item_1.price = _price
            item_1.status = _status
            session.commit()
            return 'Successful operation', 200
        else:
            return {'message': 'Item was not found'}, 400


@app.route('/item/<item_id>', methods=["DELETE"])
@jwt_required()
def delete_item(item_id):
    current_identity_username = get_jwt_identity()
    if current_identity_username != 'admin':
        return {'message': 'Access is denied'}, 403

    if not item_id:
        return {'message': 'Invalid input'}, 400
    item = session.query(Item).filter_by(item_id=int(item_id)).first()
    if item is None:
        return {'message': 'Item not found'}, 404
    else:
        item_in_order = session.query(Orders).filter_by(item_id=item.item_id).first()
        if item is not None and item_in_order is None:
            session.delete(item)
            session.commit()
            return {'message': 'Successful operation'}, 200
        elif item_in_order is not None:
            return {'message': 'Item can not be deleted'}, 400


@app.route('/order', methods=["POST"])
@jwt_required()
def add_order():
    admin_id = -1
    admin_data = session.query(User).filter_by(username='admin').first()
    if admin_data:
        admin_id = admin_data.user_id

    current_identity_username = get_jwt_identity()
    data = request.get_json()
    if data is None:
        return {'message': 'Invalid input'}, 400
    elif int(data['user_id']) == admin_id:
        return {'message': 'Cannot add order with admin id'}, 403

    user = session.query(User).filter_by(username=current_identity_username).first()
    if user is not None:
        if user.user_id != int(data['user_id']):
            return {'message': 'Access is denied'}, 403

    new_order = Orders(user_id=data['user_id'], item_id=data['item_id'], item_quantity=data['item_quantity'], price=data['price'])
    if not session.query(User).filter_by(user_id=data['user_id']).first():
        return {'message': 'Invalid input'}, 400
    elif not session.query(Item).filter_by(item_id=data['item_id']).first():
        return {'message': 'Invalid input'}, 400
    elif session.query(Item).filter_by(item_id=data['item_id']).first().status == 'sold out':
        return {'message': 'Can not be bought'}, 400
    else:
        item = session.query(Item).filter_by(item_id=data['item_id']).first()
        if new_order.item_quantity == '':
            return {'message': 'Invalid input'}, 400
        if item.storage_quantity - int(new_order.item_quantity) < 0:
            return {'message': 'Invalid input'}, 400
        session.add(new_order)
        item.storage_quantity -= int(new_order.item_quantity)
        if item.storage_quantity == 0:
            item.status = 'sold out'
        session.commit()
        return 'Successful operation', 200


@app.route('/orders', methods=["POST"])
@jwt_required()
def get_orders():
    current_identity_username = get_jwt_identity()
    user = session.query(User).filter_by(username=current_identity_username).first()
    orders = session.query(Orders).filter_by(user_id=user.user_id).all()
    schema = OrdersSchema(many=True)
    return jsonify(schema.dump(orders))


@app.route('/order/<order_id>', methods=["DELETE"])
@jwt_required()
def delete_order(order_id):
    current_identity_username = get_jwt_identity()
    user = session.query(User).filter_by(username=current_identity_username).first()

    if not order_id:
        return {'message': 'Invalid input'}, 400
    order = session.query(Orders).filter_by(order_id=int(order_id)).first()
    if order is None:
        return {'message': 'Invalid input'}, 400
    elif order.user_id != user.user_id:
        return {'message': 'Access is denied'}, 403
    else:
        item = session.query(Item).filter_by(item_id=order.item_id).first()
        if item.status == 'sold out':
            item.status = 'available'
        item.storage_quantity += int(order.item_quantity)
        session.delete(order)
        session.commit()
        return 'Successful operation', 200


@app.route('/user', methods=['POST'])
def add_user():
    data = request.get_json()
    if data['username'] == '' or data['username'] == 'admin' or data['password'] == '' or data is None:
        return {'message': "Invalid username/password supplied"}, 400

    if len(data['password']) < 8:
        return {'message': 'Number of characters in password is less than 8'}, 400

    new_user = User(username=data['username'], first_name=data['first_name'], last_name=data['last_name'],
                    email=data['email'], password=base64.b64encode(data['password'].encode("utf-8")))

    if session.query(User).filter_by(email=data['email']).first():
        return {'message': "Email is already in use"}, 400

    if session.query(User).filter_by(username=data['username']).first() is None:
        session.add(new_user)
        session.commit()
        access_token = create_access_token(identity=new_user.username)
        return jsonify({'message': 'User created',
                        'token': access_token}), 200
    else:
        return {'message': "Username is already in use"}, 400


@app.route('/user/login', methods=["POST"])
def login_user():
    data = request.get_json()

    if not data or 'username' not in data or 'password' not in data:
        return {'message': 'Wrong input data provided'}, 400

    if data['username'] == 'admin' and data['password'] == 'adminpassword':
        access_token = create_access_token(identity='admin')
        return {'token': access_token}

    user = session.query(User).filter_by(username=data['username']).first()

    if user is None:
        return {'message': 'User not found'}, 404
    if base64.b64decode(user.password).decode('utf-8') != data['password']:
        return {'message': 'Invalid username or password provided'}, 400

    access_token = create_access_token(identity=user.username)
    session.close()

    return {'token': access_token}


@app.route('/user/<username>', methods=['POST'])
@jwt_required()
def get_user(username):
    current_identity_username = get_jwt_identity()

    user = session.query(User).filter_by(username=username).first()
    if user is None:
        return 'Invalid username supplied', 400

    if current_identity_username != username:
        return 'Access is denied', 403
    return UserSchema().dump(user), 200


@app.route('/user/info/<username>', methods=["PUT"])
@jwt_required()
def put_user_by_username(username):
    current_identity_username = get_jwt_identity()

    data = request.get_json()
    if not data or not username:
        return {'message': "Invalid username or data supplied"}, 400
    _username = data['username']
    _first_name = data['first_name']
    _last_name = data['last_name']
    _email = data['email']
    _password = data['password']

    user_1 = session.query(User).filter_by(username=username).first()

    if user_1 is None:
        return {'message': 'User was not found'}, 404
    if session.query(User).filter_by(username=data['username']).first() and data['username'] != \
            current_identity_username:
        return {'message': "Username is already in use"}, 400
    if session.query(User).filter_by(email=data['email']).first() and \
            session.query(User).filter_by(email=data['email']).first().username != current_identity_username:
        return {'message': "Email is already in use"}, 400
    if current_identity_username != user_1.username:
        return {'message': 'Access is denied'}, 403

    user_1.username = _username
    user_1.first_name = _first_name
    user_1.last_name = _last_name
    user_1.email = _email
    if 0 < len(_password) < 8:
        return {'message': 'Number of characters in password is less than 8'}, 400
    elif len(_password) >= 8:
        user_1.password = base64.b64encode(_password.encode("utf-8"))
    session.commit()
    access_token = create_access_token(identity=user_1.username)
    return jsonify({'token': access_token})


@app.route('/user/<username>', methods=["DELETE"])
@jwt_required()
def delete_user(username):
    if not username:
        return {'message': 'Invalid username supplied'}, 400
    user = session.query(User).filter_by(username=username).first()
    if user is None:
        return {'message': 'User not found'}, 404
    else:
        current_identity_username = get_jwt_identity()
        user_in_order = session.query(Orders).filter_by(user_id=user.user_id).first()

        if user is not None and user_in_order is None:
            if current_identity_username != user.username:
                return {'message': 'Access is denied'}, 403
            session.delete(user)
            session.commit()
            return {'message': 'Successful operation'}, 200
        elif user_in_order is not None:
            return {'message': 'You need to delete all orders first'}, 400


with make_server('', 5000, app) as server:
    app.register_blueprint(api, url_prefix="/")
    # server.serve_forever()
