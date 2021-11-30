# from flask import url_for
import pytest
from app import app
from app import session
from models import User


@pytest.fixture(scope='session')
def client():
    return app.test_client()


class TestUser:

    def test_create_user(self, client):
        h = {'Content-Type': 'application/json'}
        data = "{\"username\": \"user3\", \"first_name\": \"Lucy\", \"last_name\":" \
               " \"Hale\", \"email\": \"abcd@gmail.com\", \"password\": \"user2\"}"
        res = client.post('http://127.0.0.1:5000/api/v1/user', headers=h, data=data)
        assert res.status_code == 200
        user = session.query(User).filter_by(username='user3').first()
        if user:
            session.delete(user)
            session.commit()


