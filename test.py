# from flask import url_for
import pytest
from app import app, bcrypt
from app import session
from models import User, Item
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


admin_credentials = "admin:adminpassword"
admin_wrong_credentials = "admin:admin123password"
user1_credentials = "user1:1234"


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
        response2 = client.post('http://127.0.0.1:5000/api/v1/user', headers=json_headers, data=self.wrong_user1)
        assert response2.status_code == 404

        user = session.query(User).filter_by(username='user1').first()
        session.delete(user)
        session.commit()

        response3 = client.post('http://127.0.0.1:5000/api/v1/user', headers=json_headers, data=0)
        assert response3.status_code == 400

    def test_login_user(self, client, basic_headers):

        headers = basic_headers.copy()
        headers["Authorization"] += base64.b64encode(self.user1_credentials.encode()).decode("utf-8")
        response = client.get('http://127.0.0.1:5000/api/v1/user/login', headers=headers)
        assert response.status_code == 404

        session.add(self.object_user1)
        session.commit()

        response = client.get('http://127.0.0.1:5000/api/v1/user/login', headers=headers)
        assert response.status_code == 200

        headers = basic_headers.copy()
        response = client.get('http://127.0.0.1:5000/api/v1/user/login', headers=headers)
        assert response.status_code == 401

        headers = basic_headers.copy()
        headers["Authorization"] += base64.b64encode(self.user1_wrong_credentials.encode()).decode("utf-8")
        response = client.get('http://127.0.0.1:5000/api/v1/user/login', headers=headers)
        assert response.status_code == 400

        session.delete(self.object_user1)
        session.commit()

    def test_get_user(self, client, basic_headers, jwt_headers):
        make_transient(self.object_user1)
        session.add(self.object_user1)
        headers = basic_headers.copy()
        headers["Authorization"] += base64.b64encode(self.user1_credentials.encode()).decode("utf-8")
        response = client.get('http://127.0.0.1:5000/api/v1/user/login', headers=headers)
        user1_token = response.json['token']

        headers = jwt_headers.copy()
        headers['Authorization'] += user1_token
        response = client.get('http://127.0.0.1:5000/api/v1/user/user1', headers=headers)
        assert response.status_code == 200
        assert response.json['username'] == 'user1'

        response = client.get(f'http://127.0.0.1:5000/api/v1/user/{self.wrong_username}', headers=headers)
        assert response.status_code == 400

        make_transient(self.object_user2)
        session.add(self.object_user2)
        session.commit()
        response = client.get('http://127.0.0.1:5000/api/v1/user/user2', headers=headers)
        assert response.status_code == 403

        session.delete(self.object_user1)
        session.commit()
        session.delete(self.object_user2)
        session.commit()

    def test_put_user(self, client, basic_headers, combined_headers):
        make_transient(self.object_user1)
        session.add(self.object_user1)
        session.commit()
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

        session.delete(self.object_user1)
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

        headers = combined_headers
        headers['Authorization'] += admin_login
        response = client.post('http://127.0.0.1:5000/api/v1/item', headers=headers, data=self.item_pen)
        assert response.status_code == 200

        item = session.query(Item).filter_by(name='pen').first()
        session.delete(item)
        session.commit()


