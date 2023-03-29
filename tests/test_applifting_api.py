import responses, os

from pytest import fixture
from app.models import db, Token
from app.APIs.applifting.applifting_api import AppliftingAPI


@fixture
def insert_token_to_db(test_app):
    with test_app.app_context():
        token = Token(token='xxxxxxxxxxJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiYWRtaW4iLCJleHAiOjE2NzYzOTI5NDZ9.NKViFsmOmdKR-qb3P9MUM-q16RmQPs0kDPtQ6b86ECA')
        db.session.add(token)
        db.session.commit()


def clean_up(test_app):
    with test_app.app_context():
        db.session.query(Token).delete()
        db.session.commit()
        

def test_applifting_api_positive(insert_token_to_db, test_app):
    
    api = AppliftingAPI()
    
    token_from_db = api._get_token()
    assert token_from_db == 'xxxxxxxxxxJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiYWRtaW4iLCJleHAiOjE2NzYzOTI5NDZ9.NKViFsmOmdKR-qb3P9MUM-q16RmQPs0kDPtQ6b86ECA'
    
    clean_up(test_app=test_app)

    url1 = f'{os.getenv("BASE_URL")}products/register'
    url2 = f'{os.getenv("BASE_URL")}products/3fa85f64-5717-4562-b3fc-2c963f66afa6/offers'

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            url1,
            body='{"id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"}',
            status=201,
            content_type="application/json",
        )

        registered_product = api.register_product({"id": "3fa85f64-5717-4562-b3fc-2c963f66afa6","name": "string","description": "string"})
    
        rsps.add(
            responses.GET,
            url2,
            body='[{"id": "3fa85f64-5717-4562-b3fc-2c963f66afa6","price": 0,"items_in_stock": 0}]',
            status=200,
            content_type="application/json",    
        )

        product_offers = api.get_product_offers("3fa85f64-5717-4562-b3fc-2c963f66afa6")
    
    assert registered_product == {"id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"}
    assert product_offers == [{"id": "3fa85f64-5717-4562-b3fc-2c963f66afa6","price": 0,"items_in_stock": 0}]


def test_applifting_api_negative():
    api = AppliftingAPI()
    
    token_from_db = api._get_token()
    assert token_from_db == ''

    url1 = f'{os.getenv("BASE_URL")}products/register'
    url2 = f'{os.getenv("BASE_URL")}products/3fa85f64-5717-4562-b3fc-2c963f66afa6/offers'

    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            url1,
            body='{"detail": "Access token invalid"}',
            status=401,
            content_type="application/json",
        )

        registered_product = api.register_product({"id": "3fa85f64-5717-4562-b3fc-2c963f66afa6","name": "string","description": "string"})
    
        rsps.add(
            responses.GET,
            url2,
            body='{"code": 500, "name": "INTERNAL_SERVER_ERROR", "description": "something broken"}',
            status=500,
            content_type="application/json",    
        )

        product_offers = api.get_product_offers("3fa85f64-5717-4562-b3fc-2c963f66afa6")
    
    assert registered_product == {"detail": "Access token invalid"}
    assert product_offers == {'code': 500, 'description': 'something broken', 'name': 'INTERNAL_SERVER_ERROR'}

