# from flask import url_for
import pytest
from app import app, bcrypt
from app import session
from models import User, Item, Orders
import base64
from sqlalchemy.orm.session import make_transient
# from models import BaseModel, engine
# from alembic import command
# from alembic.config import Config


@pytest.fixture(scope='session')
def client():
    return app.test_client()


@pytest.fixture
def jwt_headers():
    return {'Authorization': 'Bearer '}.copy()


@pytest.fixture
def basic_headers():
    return {'Authorization': 'Basic '}.copy()


@pytest.fixture
def combined_headers():
    return {'Authorization': 'Bearer ', 'Content-Type': 'application/json'}


@pytest.fixture
def json_headers():
    return {'Content-Type': 'application/json'}.copy()


@pytest.fixture
def user1_create():
    object_user1 = User(username="user1", first_name="Andrii", last_name="Sydor",
                        email="abc@gmail.com", password=bcrypt.generate_password_hash('1234').decode('utf-8'))
    make_transient(object_user1)
    session.add(object_user1)
    session.commit()
    yield "user1:1234"
    session.delete(object_user1)
    session.commit()


@pytest.fixture
def user1_login():
    headers = {'Authorization': 'Basic '}.copy()
    client = app.test_client()
    headers["Authorization"] += base64.b64encode(user1_credentials.encode()).decode("utf-8")
    response = client.get('http://127.0.0.1:5000/api/v1/user/login', headers=headers)
    user1_token = response.json['token']
    yield user1_token


@pytest.fixture
def admin_login():
    headers = {'Authorization': 'Basic '}.copy()
    client = app.test_client()
    headers["Authorization"] += base64.b64encode(admin_credentials.encode()).decode("utf-8")
    response = client.get('http://127.0.0.1:5000/api/v1/user/login', headers=headers)
    user_token = response.json['token']
    yield user_token


@pytest.fixture
def item_with_id_1():
    item = Item(item_id=1, name="Book", quantity=25, price=215, status="available")
    session.add(item)
    session.commit()
    yield
    session.delete(item)
    session.commit()


admin_credentials = "admin:adminpassword"
admin_wrong_credentials = "admin:admin123password"
user1_credentials = "user1:1234"


class TestGreeting:
    def test_student_id_page(self, client):
        response = client.get('http://127.0.0.1:5000/api/v1/hello-world-6')
        assert response.status_code == 200
        assert response.data == b'Hello World 6'


class TestUser:

    user1 = "{\"username\": \"user1\", \"first_name\": \"Andrii\", \"last_name\":" \
            " \"Sydor\", \"email\": \"abc@gmail.com\", \"password\": \"1234\"}"
    user2 = "{\"username\": \"user2\", \"first_name\": \"Vasyl\", \"last_name\":" \
            " \"Usual\", \"email\": \"def@gmail.com\", \"password\": \"12345\"}"
    wrong_user1 = "{\"username\": \"user1\", \"first_name\": \"Vasyl\", \"last_name\":" \
                  " \"Usual\", \"email\": \"def@gmail.com\", \"password\": \"1234\"}"
    wrong_username = "123123213"

    user1_update = "{\"username\": \"new_user1\", \"first_name\": \"Andrii\", \"last_name\":" \
                   " \"Usual\", \"email\": \"de@gmail.com\", \"password\": \"1234\"}"
    user1_update_back = "{\"username\": \"user1\", \"first_name\": \"Andrii\", \"last_name\":" \
                        " \"Sydor\", \"email\": \"abc@gmail.com\", \"password\": \"1234\"}"
    user1_update_no_username = "{\"first_name\": \"Andrii\", \"last_name\":" \
                               " \"Usual\", \"email\": \"de@gmail.com\", \"password\": \"1234\"}"
    user1_update_2 = "{\"username\": \"user123\", \"first_name\": \"Andrii\", \"last_name\":" \
                     " \"Usual\", \"email\": \"de@gmail.com\", \"password\": \"1234\"}"

    # json_headers = {'Content-Type': 'application/json'}
    # basic_headers = {'Authorization': 'Basic '}
    # jwt_headers = {'Authorization': 'Bearer '}
    # combined_headers = {'Authorization': 'Bearer ', 'Content-Type': 'application/json'}

    admin_credentials = "admin:adminpassword"
    admin_wrong_credentials = "admin:admin123password"
    user1_credentials = "user1:1234"
    user1_wrong_credentials = "user1:12345555"

    object_user1 = User(username="user1", first_name="Andrii", last_name="Sydor",
                        email="abc@gmail.com", password=bcrypt.generate_password_hash('1234').decode('utf-8'))
    object_user2 = User(username="user2", first_name="Vasyl", last_name="Usual",
                        email="def@gmail.com", password=bcrypt.generate_password_hash('12345').decode('utf-8'))

    def test_create_user(self, client, json_headers):
        response = client.post('http://127.0.0.1:5000/api/v1/user', headers=json_headers, data=self.user1)
        assert response.status_code == 200
        user = session.query(User).filter_by(username='user1').first()
        assert user
        response2 = client.post('http://127.0.0.1:5000/api/v1/user', headers=json_headers, data=self.wrong_user1)
        assert response2.status_code == 404

        session.delete(user)
        session.commit()

        response3 = client.post('http://127.0.0.1:5000/api/v1/user', headers=json_headers, data=0)
        assert response3.status_code == 400

    def test_login_user(self, client, basic_headers, user1_create):
        a = user1_create
        headers = basic_headers.copy()
        headers["Authorization"] += base64.b64encode(self.user1_credentials.encode()).decode("utf-8")

        response = client.get('http://127.0.0.1:5000/api/v1/user/login', headers=headers)
        assert response.status_code == 200

        headers = basic_headers.copy()
        response = client.get('http://127.0.0.1:5000/api/v1/user/login', headers=headers)
        assert response.status_code == 401

        headers = basic_headers.copy()
        headers["Authorization"] += base64.b64encode(self.user1_wrong_credentials.encode()).decode("utf-8")
        response = client.get('http://127.0.0.1:5000/api/v1/user/login', headers=headers)
        assert response.status_code == 400

    def test_login_of_unreal_user(self, client, basic_headers):
        headers = basic_headers.copy()
        headers["Authorization"] += base64.b64encode(self.user1_credentials.encode()).decode("utf-8")
        response = client.get('http://127.0.0.1:5000/api/v1/user/login', headers=headers)
        assert response.status_code == 404

    def test_get_user(self, client, basic_headers, jwt_headers, user1_create):
        a = user1_create
        headers = basic_headers.copy()
        headers["Authorization"] += base64.b64encode(self.user1_credentials.encode()).decode("utf-8")
        response = client.get('http://127.0.0.1:5000/api/v1/user/login', headers=headers)
        user1_token = response.json['token']

        headers = jwt_headers.copy()
        headers['Authorization'] += user1_token
        response = client.get('http://127.0.0.1:5000/api/v1/user/user1', headers=headers)
        assert response.status_code == 200
        user123 = session.query(User).filter_by(username='user1').first()
        user1_json = {"user_id": user123.user_id, "username": "user1", "first_name": "Andrii",
                      "last_name":  "Sydor", "email": "abc@gmail.com",
                      "password": user123.password}
        assert response.json == user1_json

        response = client.get(f'http://127.0.0.1:5000/api/v1/user/{self.wrong_username}', headers=headers)
        assert response.status_code == 400

        make_transient(self.object_user2)
        session.add(self.object_user2)
        session.commit()
        response = client.get('http://127.0.0.1:5000/api/v1/user/user2', headers=headers)
        assert response.status_code == 403

        session.delete(self.object_user2)
        session.commit()

    def test_put_user(self, client, basic_headers, combined_headers, user1_create):
        a = user1_create
        headers = basic_headers.copy()
        headers["Authorization"] += base64.b64encode(self.user1_credentials.encode()).decode("utf-8")
        response = client.get('http://127.0.0.1:5000/api/v1/user/login', headers=headers)
        user1_token = response.json['token']

        headers = combined_headers.copy()
        headers['Authorization'] += user1_token
        response = client.put('http://127.0.0.1:5000/api/v1/user/user1', headers=headers, data=self.user1_update)
        assert response.status_code == 200

        user1_token = response.json['token']
        headers = combined_headers.copy()
        headers['Authorization'] += user1_token
        response = client.put('http://127.0.0.1:5000/api/v1/user/new_user1', headers=headers, data=self.user1_update)
        assert response.status_code == 400

        response = client.put('http://127.0.0.1:5000/api/v1/user/new_us', headers=headers, data=self.user1_update)
        assert response.status_code == 404

        make_transient(self.object_user2)
        session.add(self.object_user2)
        response = client.put('http://127.0.0.1:5000/api/v1/user/user2', headers=headers,
                              data=self.user1_update_2)
        assert response.status_code == 403

        response = client.put('http://127.0.0.1:5000/api/v1/user/new_user1', headers=headers,
                              data=self.user1_update_back)
        assert response.status_code == 200
        session.delete(self.object_user2)
        session.commit()

    def test_delete_user(self, client, basic_headers, jwt_headers):
        make_transient(self.object_user1)
        session.add(self.object_user1)
        session.commit()

        headers = basic_headers.copy()
        headers["Authorization"] += base64.b64encode(self.user1_credentials.encode()).decode("utf-8")
        response = client.get('http://127.0.0.1:5000/api/v1/user/login', headers=headers)
        # assert response.status_code == 'a'
        user1_token = response.json['token']

        headers = jwt_headers.copy()
        headers['Authorization'] += user1_token
        response = client.delete('http://127.0.0.1:5000/api/v1/user/user2', headers=headers)
        assert response.status_code == 404

        make_transient(self.object_user2)
        session.add(self.object_user2)
        response = client.delete('http://127.0.0.1:5000/api/v1/user/user2', headers=headers)
        assert response.status_code == 403

        response = client.delete('http://127.0.0.1:5000/api/v1/user/user1', headers=headers)
        assert response.status_code == 200

        # session.delete(self.object_user1)
        session.delete(self.object_user2)
        session.commit()

    def test_admin(self, client):
        user = session.query(User).filter_by(username='admin').first()
        assert user


class TestItem:

    item_pen = "{\"name\": \"pen\", \"quantity\": \"200\", \"price\": \"300\", \"status\": \"available\"}"

    def test_post_item(self, client, jwt_headers, user1_create, user1_login, admin_login, combined_headers):
        headers = jwt_headers.copy()
        credentials = user1_create
        user1_token = user1_login

        headers['Authorization'] += user1_token
        response = client.post('http://127.0.0.1:5000/api/v1/item', headers=headers, data=self.item_pen)
        assert response.status_code == 403

        headers = combined_headers.copy()
        headers['Authorization'] += admin_login
        response = client.post('http://127.0.0.1:5000/api/v1/item', headers=headers, data=self.item_pen)
        assert response.status_code == 200

        item = session.query(Item).filter_by(name='pen').first()
        session.delete(item)
        session.commit()

    def test_post_nine_items(self, client, combined_headers, admin_login):
        items = []
        for i in range(8):
            items.append(Item(name=f"item{i}", quantity=10, price=100, status="available"))
            session.add(items[i])
        session.commit()

        headers = combined_headers.copy()
        headers['Authorization'] += admin_login
        response = client.post('http://127.0.0.1:5000/api/v1/item', headers=headers, data=self.item_pen)
        assert response.status_code == 400

        for i in range(8):
            session.delete(items[i])
        session.commit()

    def test_post_item_with_the_same_name(self, client, combined_headers, admin_login):
        headers = combined_headers.copy()
        headers['Authorization'] += admin_login
        response = client.post('http://127.0.0.1:5000/api/v1/item', headers=headers, data=self.item_pen)
        response = client.post('http://127.0.0.1:5000/api/v1/item', headers=headers, data=self.item_pen)
        assert response.status_code == 405

        item = session.query(Item).filter_by(name='pen').first()
        session.delete(item)
        session.commit()

    def test_get_item(self, client):
        response = client.get('http://127.0.0.1:5000/api/v1/item/1')
        assert response.status_code == 404

        item = Item(item_id=1, name="Book", quantity=25, price=215, status="available")
        session.add(item)
        session.commit()
        response = client.get('http://127.0.0.1:5000/api/v1/item/1')
        assert response.status_code == 200
        assert response.json['name'] == 'Book'

        session.delete(item)
        session.commit()

    def test_put_item(self, client, combined_headers, admin_login):
        headers = combined_headers.copy()
        headers['Authorization'] += admin_login
        data = "{\"name\": \"kiwi\", \"quantity\": \"200\", \"price\": \"300\", \"status\": \"available\"}"

        response = client.put('http://127.0.0.1:5000/api/v1/item/1', headers=headers, data=data)
        assert response.status_code == 400

        item = Item(item_id=1, name="Book", quantity=25, price=215, status="available")
        session.add(item)
        session.commit()

        response = client.put('http://127.0.0.1:5000/api/v1/item/1', headers=headers, data=data)
        assert response.status_code == 200
        assert item.name == 'kiwi'

        session.delete(item)
        session.commit()

    def test_put_item_by_not_admin(self, client, combined_headers, user1_create, user1_login, item_with_id_1):
        user = user1_create
        headers = combined_headers.copy()
        headers['Authorization'] += user1_login
        data = "{\"name\": \"kiwi\", \"quantity\": \"200\", \"price\": \"300\", \"status\": \"available\"}"

        response = client.put('http://127.0.0.1:5000/api/v1/item/1', headers=headers, data=data)
        assert response.status_code == 403

    def test_delete_item(self, client, jwt_headers, admin_login):
        headers = jwt_headers.copy()
        headers['Authorization'] += admin_login
        response = client.delete('http://127.0.0.1:5000/api/v1/item/1', headers=headers)
        assert response.status_code == 404

        item = Item(item_id=1, name="Book", quantity=25, price=215, status="available")
        session.add(item)
        session.commit()

        response = client.delete('http://127.0.0.1:5000/api/v1/item/1', headers=headers)
        assert response.status_code == 200
        i = session.query(Item).filter_by(item_id=1).first()
        assert not i

    def test_delete_item_by_not_admin(self, client, jwt_headers, user1_create, user1_login, item_with_id_1):
        a = user1_create
        headers = jwt_headers.copy()
        headers['Authorization'] += user1_login

        response = client.delete('http://127.0.0.1:5000/api/v1/item/1', headers=headers)
        assert response.status_code == 403
        i = session.query(Item).filter_by(item_id=1).first()
        assert i


class TestOrder:
    def test_add_order_by_admin(self, client, admin_login, combined_headers):
        headers = combined_headers.copy()
        headers['Authorization'] += admin_login
        data = "{\"user_id\": \"1\", \"item_id\": \"1\", \"price\": \"300\"}"
        response = client.post('http://127.0.0.1:5000/api/v1/store', headers=headers, data=data)
        assert response.status_code == 403

    def test_add_order_by_user(self, client, combined_headers, user1_create, user1_login, item_with_id_1):
        headers = combined_headers.copy()
        a = user1_create
        headers['Authorization'] += user1_login
        user = session.query(User).filter_by(username='user1').first()

        data = "{\"user_id\": \" " + str(123) + " \", \"item_id\": \"1\", \"price\": \"300\"}"
        response = client.post('http://127.0.0.1:5000/api/v1/store', headers=headers, data=data)
        assert response.status_code == 403

        data = "{\"user_id\": \" " + str(user.user_id) + " \", \"item_id\": \"123\", \"price\": \"300\"}"
        response = client.post('http://127.0.0.1:5000/api/v1/store', headers=headers, data=data)
        assert response.status_code == 400

        data = "{\"user_id\": \" " + str(user.user_id) + " \", \"item_id\": \"1\", \"price\": \"300\"}"
        response = client.post('http://127.0.0.1:5000/api/v1/store', headers=headers, data=data)
        assert response.status_code == 200

        data = "{\"user_id\": \" " + str(user.user_id) + " \", \"item_id\": \"1\", \"price\": \"300\"}"
        response = client.post('http://127.0.0.1:5000/api/v1/store', headers=headers, data=data)
        assert response.status_code == 400

        order = session.query(Orders).filter_by(price=300).first()
        session.delete(order)
        session.commit()

    def test_get_order(self, client, jwt_headers, user1_create, user1_login, item_with_id_1):
        a = user1_create
        headers = jwt_headers.copy()
        headers['Authorization'] += user1_login

        user = session.query(User).filter_by(username='user1').first()
        order = Orders(order_id=1, user_id=user.user_id, item_id=1, price=300)
        session.add(order)
        session.commit()

        response = client.get('http://127.0.0.1:5000/api/v1/store/1', headers=headers)
        assert response.status_code == 200

        response = client.get('http://127.0.0.1:5000/api/v1/store/2', headers=headers)
        assert response.status_code in [400, 404]

        order2 = Orders(order_id=2, user_id=1, item_id=1, price=300)
        session.add(order2)
        session.commit()

        response = client.get('http://127.0.0.1:5000/api/v1/store/2', headers=headers)
        assert response.status_code == 403

        session.delete(order)
        session.commit()
        session.delete(order2)
        session.commit()

    def test_delete_order(self, client, jwt_headers, user1_create, user1_login, item_with_id_1):
        a = user1_create
        headers = jwt_headers.copy()
        headers['Authorization'] += user1_login

        response = client.delete('http://127.0.0.1:5000/api/v1/store/1', headers=headers)
        assert response.status_code == 400

        user = session.query(User).filter_by(username='user1').first()
        order = Orders(order_id=1, user_id=user.user_id, item_id=1, price=300)
        session.add(order)
        session.commit()

        response = client.delete('http://127.0.0.1:5000/api/v1/store/1', headers=headers)
        assert response.status_code == 200

        order2 = Orders(order_id=2, user_id=1, item_id=1, price=300)
        session.add(order2)
        session.commit()

        response = client.delete('http://127.0.0.1:5000/api/v1/store/2', headers=headers)
        assert response.status_code == 403

        session.delete(order)
        session.commit()
        session.delete(order2)
        session.commit()

    def test_delete_user_with_order(self, client, user1_create, user1_login, item_with_id_1, jwt_headers):
        a = user1_create
        headers = jwt_headers.copy()
        headers['Authorization'] += user1_login

        user = session.query(User).filter_by(username='user1').first()
        order = Orders(order_id=1, user_id=user.user_id, item_id=1, price=300)
        session.add(order)
        session.commit()

        response = client.delete('http://127.0.0.1:5000/api/v1/user/user1', headers=headers)
        assert response.status_code == 400

        session.delete(order)
        session.commit()

    def test_delete_item_with_order(self, client, item_with_id_1, user1_create,  jwt_headers, admin_login):
        headers = jwt_headers.copy()
        headers['Authorization'] += admin_login

        user = session.query(User).filter_by(username='user1').first()
        order = Orders(order_id=1, user_id=user.user_id, item_id=1, price=300)
        session.add(order)
        session.commit()

        response = client.delete('http://127.0.0.1:5000/api/v1/item/1', headers=headers)
        assert response.status_code == 400

        session.delete(order)
        session.commit()
