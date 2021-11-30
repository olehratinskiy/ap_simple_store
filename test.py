# from flask import url_for
import pytest
from app import app
from app import session
from models import User
import base64


@pytest.fixture(scope='session')
def client():
    return app.test_client()


class Data:
    def __init__(self, username, password):
        self.username = username
        self.password = password


class TestUser:

    user1 = "{\"username\": \"user1\", \"first_name\": \"Andrii\", \"last_name\":" \
            " \"Sydor\", \"email\": \"abc@gmail.com\", \"password\": \"1234\"}"
    user2 = "{\"username\": \"user2\", \"first_name\": \"Vasyl\", \"last_name\":" \
            " \"Usual\", \"email\": \"def@gmail.com\", \"password\": \"12345\"}"
    wrong_user1 = "{\"username\": \"user1\", \"first_name\": \"Vasyl\", \"last_name\":" \
                  " \"Usual\", \"email\": \"def@gmail.com\", \"password\": \"1234\"}"
    wrong_username = "123123213"

    json_headers = {'Content-Type': 'application/json'}
    basic_headers = {'Authorization': 'Basic '}
    jwt_headers = {'Authorization': 'Bearer '}

    admin_credentials = "admin:adminpassword"
    admin_wrong_credentials = "admin:admin123password"
    user1_credentials = "user1:1234"
    user1_wrong_credentials = "user1:12345555"

    def test_create_user(self, client):
        response = client.post('http://127.0.0.1:5000/api/v1/user', headers=self.json_headers, data=self.user1)
        assert response.status_code == 200
        response2 = client.post('http://127.0.0.1:5000/api/v1/user', headers=self.json_headers, data=self.wrong_user1)
        assert response2.status_code == 404

        user = session.query(User).filter_by(username='user1').first()
        if user:
            session.delete(user)
            session.commit()

        response3 = client.post('http://127.0.0.1:5000/api/v1/user', headers=self.json_headers, data=0)
        assert response3.status_code == 400

    def test_login_user(self, client):

        headers = self.basic_headers.copy()
        headers["Authorization"] += base64.b64encode(self.user1_credentials.encode()).decode("utf-8")
        response = client.get('http://127.0.0.1:5000/api/v1/user/login', headers=headers)
        assert response.status_code == 404

        response = client.post('http://127.0.0.1:5000/api/v1/user', headers=self.json_headers, data=self.user1)

        response = client.get('http://127.0.0.1:5000/api/v1/user/login', headers=headers)
        assert response.status_code == 200

        headers = self.basic_headers.copy()
        response = client.get('http://127.0.0.1:5000/api/v1/user/login', headers=headers)
        assert response.status_code == 401

        headers = self.basic_headers.copy()
        headers["Authorization"] += base64.b64encode(self.user1_wrong_credentials.encode()).decode("utf-8")
        response = client.get('http://127.0.0.1:5000/api/v1/user/login', headers=headers)
        assert response.status_code == 400

        user = session.query(User).filter_by(username='user1').first()
        if user:
            session.delete(user)
            session.commit()

    def test_get_user(self, client):
        response = client.post('http://127.0.0.1:5000/api/v1/user', headers=self.json_headers, data=self.user1)
        headers = self.basic_headers.copy()
        headers["Authorization"] += base64.b64encode(self.user1_credentials.encode()).decode("utf-8")
        response = client.get('http://127.0.0.1:5000/api/v1/user/login', headers=headers)
        user1_token = response.json['token']

        headers = self.jwt_headers.copy()
        headers['Authorization'] += user1_token
        response = client.get('http://127.0.0.1:5000/api/v1/user/user1', headers=headers)
        assert response.status_code == 200
        assert response.json['username'] == 'user1'

        response = client.get(f'http://127.0.0.1:5000/api/v1/user/{self.wrong_username}', headers=headers)
        assert response.status_code == 400

        response = client.post('http://127.0.0.1:5000/api/v1/user', headers=self.json_headers, data=self.user2)
        response = client.get('http://127.0.0.1:5000/api/v1/user/user2', headers=headers)
        assert response.status_code == 403

        user = session.query(User).filter_by(username='user1').first()
        if user:
            session.delete(user)
            session.commit()
        user = session.query(User).filter_by(username='user2').first()
        if user:
            session.delete(user)
            session.commit()

