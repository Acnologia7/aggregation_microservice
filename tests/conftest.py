import os

from pytest import fixture
from app.views import create_flask_app_with_bp
from app import base_app
from requests.auth import _basic_auth_str
from app.models import db
from dotenv import load_dotenv

load_dotenv()

@fixture
def test_app():
    if os.getenv('TESTING_MODE') == '1':
        with base_app.app_context():
            db.create_all()
            app, sched = create_flask_app_with_bp()
            yield app
            db.session.remove()
            db.drop_all()
    else:
        print('Not in testing mode')

@fixture
def client(test_app):
    client = test_app.test_client()
    yield client


@fixture
def token(client):
    response = client.post("/auth", headers={"Authorization": _basic_auth_str('tester', os.getenv('PASSWORD_TO_API'))})
    r = response.data.decode()[10:-3]
    yield r
