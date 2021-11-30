from flask import Flask, request, jsonify
# from flask_jwt import JWT, jwt_required, current_identity
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager
from wsgiref.simple_server import make_server
from werkzeug.security import safe_str_cmp
from greeting import api
from sqlalchemy.exc import NoResultFound
from flask_bcrypt import Bcrypt
from schema import *
from models import Session
from datetime import timedelta
session = Session()
app = Flask(__name__)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
app.config["JWT_SECRET_KEY"] = "super-secret"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

if session.query(User).filter_by(username='admin').first() is None:
    admin = User(username='admin', first_name='Ake', last_name='Harwood', email='email1@gmail.com',
                 password=bcrypt.generate_password_hash('adminpassword').decode('utf-8'))
    session.add(admin)
    session.commit()


@app.route('/api/v1/item',methods =["POST"])
@jwt_required()
def add_item():
    current_identity_username = get_jwt_identity()
    if current_identity_username != 'admin':
        return 'Access is denied', 403

    data = request.get_json()
    new_item = Item(name=data['name'], quantity=data['quantity'], price=data['price'], status=data['status'])
    quantity = session.query(Item.item_id).count()
    if quantity >= 8:
        return 'Exceed number of items', 400
    if session.query(Item).filter_by(name=data['name']).first() is None:
        session.add(new_item)
        session.commit()
        return 'Successful operation', 200
    else:
        return 'Invalid input', 405


@app.route('/api/v1/item/<id>', methods = ["GET"])
def get_item_by_id(id):
    item = session.query(Item).filter_by(item_id = int(id)).first()
    if item is not None:
        return ItemSchema().dump(item), 200
    elif not id:
        return 'Invalid id', 400
    else:
        return 'Item was not found', 404


@app.route('/api/v1/item/<id>',methods = ["PUT"])
@jwt_required()
def put_item_by_id(id):
    current_identity_username = get_jwt_identity()
    if current_identity_username != 'admin':
        return 'Access is denied', 403

    item = request.get_json()
    if item is None:
        return 'Invalid input', 400
    else:
        _name = item['name']
        _quantity = item['quantity']
        _price = item['price']
        _status = item['status']
        item_1 = session.query(Item).filter_by(item_id=int(id)).first()
        if item_1 is not None:
            item_1.name = _name
            item_1.quantity = _quantity
            item_1.price = _price
            item_1.status = _status
            session.commit()
            return 'Successful operation', 200
        else:
            return 'Item was not found', 400


@app.route('/api/v1/item/<id>', methods = ["DELETE"])
@jwt_required()
def delete_item(id):
    current_identity_username = get_jwt_identity()
    if current_identity_username != 'admin':
        return 'Access is denied', 403

    if not id:
        return 'Invalid input', 400
    item = session.query(Item).filter_by(item_id=int(id)).first()
    if item is None:
        return 'Item not found', 404
    else:
        item_in_order = session.query(Orders).filter_by(item_id=item.item_id).first()
        if item is not None and item_in_order is None:
            session.delete(item)
            session.commit()
            return 'Successful operation', 200
        elif item_in_order is not None:
            return 'Item can not be deleted', 400


@app.route('/api/v1/store',methods =["POST"])
@jwt_required()
def add_store():
    admin_id = -1
    admin_data = session.query(User).filter_by(username='admin').first()
    if admin_data:
        admin_id = admin_data.user_id

    current_identity_username = get_jwt_identity()
    data = request.get_json()

    if data is None:
        return 'Invalid input', 400
    elif int(data['user_id']) == admin_id:
        return 'Cannot add order with admin id', 403

    user = session.query(User).filter_by(username=current_identity_username).first()
    if user is not None:
        if user.user_id != int(data['user_id']):
            return 'Access is denied', 403

    new_store = Orders(user_id=data['user_id'], item_id=data['item_id'], price=data['price'])
    if not session.query(User).filter_by(user_id=data['user_id']).first():
        return 'Invalid input', 400
    elif not session.query(Item).filter_by(item_id=data['item_id']).first():
        return 'Invalid input', 400
    elif session.query(Orders).filter_by(item_id=data['item_id']).first():
        return 'Can not be bought', 400
    else:
        session.add(new_store)
        item = session.query(Item).filter_by(item_id=data['item_id']).first()
        item.status = 'sold out'
        session.commit()
        return 'Successful operation', 200


@app.route('/api/v1/store/<id>', methods = ["GET"])
@jwt_required()
def get_store_by_id(id):
    store = session.query(Orders).filter_by(order_id = int(id)).first()
    current_identity_username = get_jwt_identity()
    user = session.query(User).filter_by(username=current_identity_username).first()
    if store is not None:
        if user is not None:
            if user.user_id != store.user_id:
                return 'Access is denied', 403
            return OrdersSchema().dump(store), 200
        else:
            return 'User with this token does not exist', 404
    elif id not in session.query(Orders.order_id).first():
        return 'Invalid input', 400
    else:
        return 'Order was not found', 404


@app.route('/api/v1/store/<id>', methods = ["DELETE"])
@jwt_required()
def delete_store(id):
    current_identity_username = get_jwt_identity()
    user = session.query(User).filter_by(username=current_identity_username).first()

    if not id:
        return 'Invalid input', 400
    store = session.query(Orders).filter_by(order_id=int(id)).first()
    if store is None:
        return 'Invalid input', 400
    elif store.user_id != user.user_id:
        return 'Access is denied', 403
    else:
        item = session.query(Item).filter_by(item_id=store.item_id).first()
        item.status = 'available'
        session.delete(store)
        session.commit()
        return 'Successful operation', 200


@app.route('/api/v1/user', methods = ['POST'])
def add_user():
    data = request.get_json()
    if data is None:
        return "Invalid username/password supplied",400
    new_user = User(username = data['username'],first_name = data['first_name'],last_name = data['last_name'], email = data['email'],
    password = bcrypt.generate_password_hash(data['password']).decode('utf-8'))
    if session.query(User).filter_by(username=data['username']).first() is None:
        session.add(new_user)
        session.commit()
        return jsonify ({'message': 'user created'})
    else:
        return "Username is already in use",404


@app.route('/api/v1/user/login', methods = ["GET"])
def login_user():
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return 'Wrong data provided', 401

    user = session.query(User).filter_by(username=auth.username).first()

    if user is not None:
        if not bcrypt.check_password_hash(user.password, auth.password):
            return 'Invalid username or password supplied', 400
        access_token = create_access_token(identity=user.username)
        return jsonify({'token': access_token})
    else:
        return 'User not found', 404


@app.route('/api/v1/user/<username>', methods = ['GET'])
@jwt_required()
def get_user(username):
    current_identity_username = get_jwt_identity()

    user = session.query(User).filter_by(username=username).first()
    if user is None:
        return 'Invalid username supplied', 400

    if current_identity_username != username:
        return 'Access is denied', 403
    return UserSchema().dump(user), 200


@app.route('/api/v1/user/<username>', methods = ["PUT"])
@jwt_required()
def put_user_by_username(username):
    current_identity_username = get_jwt_identity()

    data = request.get_json()
    if not data or not username:
        return "Invalid username or data supplied", 400
    _username = data['username']
    _first_name = data['first_name']
    _last_name = data['last_name']
    _email = data['email']
    user_1 = session.query(User).filter_by(username=username).first()

    if user_1 is None:
        return 'User was not found', 404
    elif session.query(User).filter_by(username=data['username']).first():
        return 'Username with this query exists', 400
    elif current_identity_username != user_1.username:
        return 'Access is denied', 403
    else:
        user_1.username = _username
        user_1.first_name = _first_name
        user_1.last_name = _last_name
        user_1.email = _email
        session.commit()
        access_token = create_access_token(identity=user_1.username)
        return jsonify({'token': access_token})


@app.route('/api/v1/user/<username>', methods = ["DELETE"])
@jwt_required()
def delete_user(username):
    if not username:
        return 'Invalid username supplied', 400
    user = session.query(User).filter_by(username=username).first()
    if user is None:
        return 'User not found', 404
    else:
        current_identity_username = get_jwt_identity()
        user_in_order = session.query(Orders).filter_by(user_id = user.user_id).first()

        if user is not None and user_in_order is None:
            if current_identity_username != user.username:
                return 'Access is denied', 403
            session.delete(user)
            session.commit()
            return 'Successful operation', 200
        elif user_in_order is not None:
            return 'User can not be deleted', 400


with make_server('', 5000, app) as server:
    app.register_blueprint(api, url_prefix="/api/v1")
    # server.serve_forever()
