import responses, os

from pytest import fixture
from uuid import UUID

from app.tasks import periodic_update_token, periodic_update_offers_task
from app.models import db, Token, Product, Offer


@fixture
def data_in_db(test_app):
    with test_app.app_context():
        p1 = Product('TEST1', 'TESTING1')
        db.session.add(p1)
        db.session.flush()
        id1 = p1.id
        o1 = Offer(id=UUID('d2e96009-eea8-477d-ae7a-e1fdf2eaaaa1'), price=1, items_in_stock=1, product_id=p1.id)
        o2 = Offer(id=UUID('d2e96009-eea8-477d-ae7a-e1fdf2eaaaa2'), price=2, items_in_stock=2, product_id=p1.id)
        oid1 = o1.id
        oid2 = o2.id
        db.session.add(o1)
        db.session.add(o2)
        db.session.commit()
    yield [id1, oid1, oid2]




def test_update_token_task(test_app):
    url = f'{os.getenv("BASE_URL")}auth'
    with responses.RequestsMock() as rsps:
        
        rsps.add(
            responses.POST,
            url,
            body='{"access_token": "string-token"}',
            status=201,
            content_type="application/json",
        )
        periodic_update_token()

    with test_app.app_context():
        r = db.session.get(Token, UUID('d2e96009-eea8-477d-ae7a-e1fdf2eaaaaa'))

    assert r.token == 'string-token'

def update_token_task_token_still_valid(test_app):
    url = f'{os.getenv("BASE_URL")}auth'
    with responses.RequestsMock() as rsps:
        
        rsps.add(
            responses.POST,
            url,
            body='{"detail": "Cannot generate access token because another is valid"}',
            status=400,
            content_type="application/json",
        )
        periodic_update_token()

    with test_app.app_context():
        r = db.session.get(Token, UUID('d2e96009-eea8-477d-ae7a-e1fdf2eaaaaa'))

    assert r == None

    
def test_update_offers_task(test_app, data_in_db):
    testing_response = [
        {"id": "3fa85f64-5717-4562-b3fc-2c963f66afa6","price": 0,"items_in_stock": 0},
        {"id": "d2e96009-eea8-477d-ae7a-e1fdf2eaaaa1", "price": 100, "items_in_stock": 100}
    ]
    periodic_update_offers_task(update_offers_test_values=testing_response)

    with test_app.app_context():
        r = db.session.query(Offer).all()
        assert len(r) == 2

        r = db.session.get(Offer, UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6"))
        assert r.price == 0 and r.items_in_stock == 0

        r = db.session.get(Offer, UUID("d2e96009-eea8-477d-ae7a-e1fdf2eaaaa1"))
        assert r.price == 100 and r.items_in_stock == 100

        r = db.session.get(Offer, UUID('d2e96009-eea8-477d-ae7a-e1fdf2eaaaa2'))
        assert r == None    
