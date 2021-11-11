from flask import Flask, request, jsonify
from wsgiref.simple_server import make_server
from greeting import api
from flask_bcrypt import Bcrypt
from schema import *
from models import Session
session = Session()
app = Flask(__name__)
bcrypt = Bcrypt(app)

@app.route('/api/v1/item',methods =["POST"])
def add_item():
        data = request.get_json()
        new_item = Item(name = data['name'], quantity = data['quantity'], price = data['price'],status=data['status'])
        quantity = session.query(Item.item_id).count()
        if quantity >= 8:
            return 'Exceed number of items',400
        if session.query(Item).filter_by(name=data['name']).first() is None:
            session.add(new_item)
            session.commit()
            return 'Successful operation',200
        else:
         return 'Invalid input',405

@app.route('/api/v1/item/<id>', methods = ["GET"])
def get_item_by_id(id):
    item = session.query(Item).filter_by(item_id = int(id)).first()
    if item is not None:
        return ItemSchema().dump(item),200
    elif not id:
        return 'Invalid id',400
    else:
        return 'Item was not found',404

@app.route('/api/v1/item/<id>',methods = ["PUT"])
def put_item_by_id(id):
        item = request.get_json()
        if item is None:
            return 'Invalid input',400
        else:
            _name = item['name']
            _quantity = item['quantity']
            _price = item['price']
            _status = item['status']
            item_1 = session.query(Item).filter_by(item_id = int(id)).first()
            if item_1 is not None:
                item_1.name = _name
                item_1.quantity = _quantity
                item_1.price = _price
                item_1.status = _status
                session.commit()
                return 'Successful operation',200
            else:
                return 'Item was not found',400


@app.route('/api/v1/item/<id>', methods = ["DELETE"])
def delete_item(id):
        if not id:
            return 'Invalid input',400
        item = session.query(Item).filter_by(item_id = int(id)).first()
        if item is None:
            return 'Item not found',404
        else:
            item_in_order = session.query(Orders).filter_by(item_id = item.item_id).first()
            if item is not None and item_in_order is None:
                session.delete(item)
                session.commit()
                return 'Successful operation',200
            elif item_in_order is not None:
                return 'Item can not be deleted',400

@app.route('/api/v1/store',methods =["POST"])
def add_store():
        data = request.get_json()
        if data is None:
            return 'Invalid input',400
        new_store = Orders(user_id = data['user_id'],item_id = data['item_id'],price= data['price'])
        if not session.query(User).filter_by(user_id=data['user_id']).first():
            return 'Invalid input',400
        elif not session.query(Item).filter_by(item_id=data['item_id']).first():
            return 'Invalid input',400
        elif  session.query(Orders).filter_by(item_id=data['item_id']).first():
            return 'Can not be bought',400
        else:
            session.add(new_store)
            item = session.query(Item).filter_by(item_id = data['item_id']).first()
            item.status = 'sold out'
            session.commit()
            return 'Successful operation',200


@app.route('/api/v1/store/<id>', methods = ["GET"])
def get_store_by_id(id):
    store = session.query(Orders).filter_by(order_id = int(id)).first()
    if store is not None:
        return OrdersSchema().dump(store),200
    elif id not in session.query(Orders.order_id).first():
        return 'Invalid input',400
    else:
        return 'Order was not found',404

@app.route('/api/v1/store/<id>', methods = ["DELETE"])
def delete_store(id):
        if not id:
            return 'Invalid input',400
        else:
            store = session.query(Orders).filter_by(order_id = int(id)).first()
            if store is None:
                return 'Invalid input', 400
            else:
                session.delete(store)
                session.commit()
                return 'Successful operation',200


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

@app.route('/api/v1/user/login', methods = ['GET'])
def login_user():
    data = request.get_json()
    user = session.query(User).filter_by(username = data['username']).first()
    if user is not None:
        if not bcrypt.check_password_hash(user.password,data['password']):
            return 'Invalid username or password supplied',400
        return UserSchema().dump(user),200
    else:
        return 'User not found',404


@app.route('/api/v1/user/logout', methods = ['GET'])
def logout_user():
     pass

@app.route('/api/v1/user/<username>', methods = ['GET'])
def get_user(username):
    user = session.query(User).filter_by(username=username).first()
    if user is not None:
        return UserSchema().dump(user), 200
    elif username not in session.query(User.username):
        return 'Invalid username supplied',400
    else:
        return 'User was not found',404

@app.route('/api/v1/user/<username>',methods = ["PUT"])
def put_user_by_username(username):
        data = request.get_json()
        if not data or not username:
            return "Invalid username supplied", 400
        _username = data['username']
        _first_name = data['first_name']
        _last_name = data['last_name']
        _email = data['email']
        user_1 = session.query(User).filter_by(username= username).first()
        if session.query(User).filter_by(username=data['username']).first():
            return 'Username with this query exists',400
        if  user_1 is not None:
            user_1.username = _username
            user_1.first_name = _first_name
            user_1.last_name = _last_name
            user_1.email = _email
            session.commit()
            return 'Successful operation',200
        else:
           return 'User was not found', 404


@app.route('/api/v1/user/<username>', methods = ["DELETE"])
def delete_user(username):
    if not username:
       return 'Invalid username supplied',400
    user = session.query(User).filter_by(username=username).first()
    if user is None:
        return 'User not found',404
    else:
        user_in_order = session.query(Orders).filter_by(user_id = user.user_id).first()
        if user is not None and user_in_order is None:
            session.delete(user)
            session.commit()
            return 'Successful operation', 200
        elif user_in_order is not None:
            return 'User can not be deleted', 400




with make_server('', 5000, app) as server:
    app.register_blueprint(api, url_prefix="/api/v1")
    server.serve_forever()

# Users method
# curl -X POST http://127.0.0.1:5000/api/v1/user -H "Content-Type: application/json" --data "{\"username\": \"user3\", \"first_name\": \"Lana\", \"last_name\": \"Chulup\", \"email\": \"chulup@gmail.com\", \"password\": \"8932\"}"
# curl -X POST http://127.0.0.1:5000/api/v1/user -H "Content-Type: application/json" --data "{\"username\": \"mia\", \"first_name\": \"Lucy\", \"last_name\": \"Hale\", \"email\": \"abcd@gmail.com\", \"password\": \"5678\"}"
# curl -X GET  http://127.0.0.1:5000/api/v1/user/login -H "Content-Type: application/json" --data "{\"username\": \"user\",\"password\": \"8932\"}"
# curl -X GET http://127.0.0.1:5000/api/v1/user/user2
# curl -X PUT http://127.0.0.1:5000/api/v1/user/user2 -H "Content-Type: application/json" --data "{\"username\": \"user8\",\"first_name\": \"Maria\", \"last_name\": \"Markiv\", \"email\": \"abc@gmail.com\"}"
# curl -X DELETE http://127.0.0.1:5000/api/v1/user/user8

# Item method
# curl -X POST http://127.0.0.1:5000/api/v1/item -H "Content-Type: application/json" --data "{\"name\": \"pen\", \"quantity\": \"200\", \"price\": \"300\", \"status\": \"available\"}"
# curl -X POST http://127.0.0.1:5000/api/v1/item -H "Content-Type: application/json" --data "{\"name\": \"kiwi\", \"quantity\": \"300\", \"price\": \"450\", \"status\": \"available\"}"
# curl -X GET http://127.0.0.1:5000/api/v1/item/110
# curl -X PUT http://127.0.0.1:5000/api/v1/item/110 -H "Content-Type: application/json" --data "{\"name\": \"kiwi\", \"quantity\": \"200\", \"price\": \"300\", \"status\": \"available\"}"
# curl -X DELETE http://127.0.0.1:5000/api/v1/item/<id>

# Store method
# curl -X POST http://127.0.0.1:5000/api/v1/store -H "Content-Type: application/json" --data "{\"user_id\": \"10\", \"item_id\": \"7\", \"price\": \"300\"}"
# curl -X GET http://127.0.0.1:5000/api/v1/store/24
# curl -X DELETE http://127.0.0.1:5000/api/v1/store/25
