from requests.auth import _basic_auth_str
from pytest import fixture
from sqlalchemy.dialects.postgresql import insert
from uuid import UUID

from app.models import db, Product, Offer

@fixture
def data_in_db(test_app):
    with test_app.app_context():
        p1 = Product('TEST1', 'TESTING1')
        p2 = Product('TEST2', 'TESTING2')
        db.session.add(p1)
        db.session.add(p2)
        db.session.flush()
        id1 = p1.id
        id2 = p2.id
        o1 = Offer(id=UUID('d2e96009-eea8-477d-ae7a-e1fdf2eaaaa1'), price=1, items_in_stock=1, product_id=p1.id)
        o2 = Offer(id=UUID('d2e96009-eea8-477d-ae7a-e1fdf2eaaaa2'), price=2, items_in_stock=2, product_id=p2.id)
        oid1 = o1.id
        oid2 = o2.id
        db.session.add(o1)
        db.session.add(o2)
        db.session.commit()
    yield [id1, id2, oid1, oid2]


def clean_up(test_app=None, data_in_db=None) -> None:
    with test_app.app_context():
        p1 = db.session.get(Product, data_in_db[0])
        p2 = db.session.get(Product, data_in_db[1])
        if p1:
            db.session.delete(p1)
        db.session.delete(p2)
        db.session.commit()


def test_auth(client):
    response = client.post("/auth", headers={"Authorization": _basic_auth_str('admin', 'PASSWORD123')})
    assert response.data[:12] == b'{"token":"ey'


def test_register_product_negative(client, token, test_app, data_in_db):
    headers0 = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
    headers1 = {}
    headers3 = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
    headers2 = {'Authorization': 'Bearer ' + 'xxxxxxxxxxJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiYWRtaW4iLCJleHAiOjE2NzYzOTI5NDZ9.NKViFsmOmdKR-qb3P9MUM-q16RmQPs0kDPtQ6b86ECA','Content-Type': 'application/json'}
    
    json = {
        "name": "TEST1",
        "description": "description"
    }
    
    response0 = client.post("/product", headers=headers0, json=json)
    assert response0.data == b'{"code":400,"description":"Record already exists or name field is empty","name":"Bad request"}\n'
    clean_up(test_app=test_app, data_in_db=data_in_db)
    
    response1 = client.post("/product", headers=headers1, json=json)
    assert response1.data == b'{"code":400,"description":"Token is missing!","name":"Not found"}\n'

    response2 = client.post("/product", headers=headers2, json=json)
    assert response2.data == b'{"code":403,"description":"Token is not valid!","name":"Forbidden"}\n'

    response3 = client.post("/product", headers=headers3)
    assert response3.data == b'{"code": 400, "description": "The browser (or proxy) sent a request that this server could not understand.", "name": "Bad Request"}'


def test_get_products(client, token, test_app, data_in_db):
    
    headers0 = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
    headers1 = {}
    headers3 = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
    headers2 = {'Authorization': 'Bearer ' + 'xxxxxxxxxxJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiYWRtaW4iLCJleHAiOjE2NzYzOTI5NDZ9.NKViFsmOmdKR-qb3P9MUM-q16RmQPs0kDPtQ6b86ECA','Content-Type': 'application/json'}
    
    response0 = client.get("/products", headers=headers0)
    assert response0.data.decode() =='[{"description":"TESTING1","id":"'+str(data_in_db[0])+'","name":"TEST1"},{"description":"TESTING2","id":"'+str(data_in_db[1])+'","name":"TEST2"}]\n'
    clean_up(test_app=test_app, data_in_db=data_in_db)

    response1 = client.get("/products", headers=headers1)
    assert response1.data == b'{"code":400,"description":"Token is missing!","name":"Not found"}\n'

    response2 = client.get("/products", headers=headers2)
    assert response2.data == b'{"code":403,"description":"Token is not valid!","name":"Forbidden"}\n'

    response3 = client.get("/products", headers=headers3)
    assert response3.data == b'{"code":404,"description":"There are no records of products to be found","name":"Not found"}\n'


def test_get_product(test_app, token, client, data_in_db):
    
    headers0 = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
    headers1 = {}
    headers2 = {'Authorization': 'Bearer ' + 'xxxxxxxxxxJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiYWRtaW4iLCJleHAiOjE2NzYzOTI5NDZ9.NKViFsmOmdKR-qb3P9MUM-q16RmQPs0kDPtQ6b86ECA','Content-Type': 'application/json'}
    headers3 = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}

    response0 = client.get("/product", headers=headers0, json={'id': str(data_in_db[0])})
    assert response0.data.decode() == '{"description":"TESTING1","id":"'+str(data_in_db[0])+'","name":"TEST1"}\n'
    clean_up(test_app=test_app, data_in_db=data_in_db)

    response1 = client.get("/product", headers=headers1)
    assert response1.data == b'{"code":400,"description":"Token is missing!","name":"Not found"}\n'

    response2 = client.get("/product", headers=headers2)
    assert response2.data == b'{"code":403,"description":"Token is not valid!","name":"Forbidden"}\n'

    response3 = client.get("/product", headers=headers3,  json={'id': str(data_in_db[0])})
    assert response3.data.decode() == '{"code":404,"description":"There is no record of product '+ str(data_in_db[0])+' to be found","name":"Not found"}\n'
  

def test_update_product(test_app, token, client, data_in_db):
    headers0 = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
    headers1 = {}
    headers2 = {'Authorization': 'Bearer ' + 'xxxxxxxxxxJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiYWRtaW4iLCJleHAiOjE2NzYzOTI5NDZ9.NKViFsmOmdKR-qb3P9MUM-q16RmQPs0kDPtQ6b86ECA','Content-Type': 'application/json'}
    headers3 = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}

    response0 = client.put("/product", headers=headers0, json={'id': str(data_in_db[0]), 'name': 'UPDATED', 'description':'upt description'})
    assert response0.data.decode() == '{"description":"upt description","id":"'+str(data_in_db[0])+'","name":"UPDATED"}\n'
    clean_up(test_app=test_app, data_in_db=data_in_db)

    response1 = client.put("/product", headers=headers1)
    assert response1.data == b'{"code":400,"description":"Token is missing!","name":"Not found"}\n'

    response2 = client.put("/product", headers=headers2)
    assert response2.data == b'{"code":403,"description":"Token is not valid!","name":"Forbidden"}\n'

    response3 = client.put("/product", headers=headers3,  json={'id': str(data_in_db[0])})
    assert response3.data.decode() == '{"code":404,"description":"There is no record of product '+ str(data_in_db[0])+' to be found","name":"Not found"}\n'


def test_delete_product(test_app, token, client, data_in_db):
    headers0 = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
    headers1 = {}
    headers2 = {'Authorization': 'Bearer ' + 'xxxxxxxxxxJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiYWRtaW4iLCJleHAiOjE2NzYzOTI5NDZ9.NKViFsmOmdKR-qb3P9MUM-q16RmQPs0kDPtQ6b86ECA','Content-Type': 'application/json'}
    headers3 = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}

    response0 = client.delete("/product", headers=headers0, json={'id': str(data_in_db[0])})
    assert response0.data.decode() == '{"code":200,"description":"Product '+str(data_in_db[0])+' successfuly deleted","name":"Deleted"}\n'
    clean_up(test_app=test_app, data_in_db=data_in_db)

    response1 = client.delete("/product", headers=headers1)
    assert response1.data == b'{"code":400,"description":"Token is missing!","name":"Not found"}\n'

    response2 = client.delete("/product", headers=headers2)
    assert response2.data == b'{"code":403,"description":"Token is not valid!","name":"Forbidden"}\n'

    response3 = client.delete("/product", headers=headers3,  json={'id': str(data_in_db[0])})
    assert response3.data.decode() == '{"code":404,"description":"There is no record of product '+ str(data_in_db[0])+' to be found","name":"Not found"}\n'


def test_get_product_offers(test_app, token, client, data_in_db):
    headers0 = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
    headers1 = {}
    headers2 = {'Authorization': 'Bearer ' + 'xxxxxxxxxxJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiYWRtaW4iLCJleHAiOjE2NzYzOTI5NDZ9.NKViFsmOmdKR-qb3P9MUM-q16RmQPs0kDPtQ6b86ECA','Content-Type': 'application/json'}
    headers3 = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}

    response0 = client.get("/product/offers", headers=headers0, json={'id': str(data_in_db[0])})
    assert response0.data.decode() ==  '[{"id":"'+str(data_in_db[2])+'","items_in_stock":1,"price":1}]\n'
    clean_up(test_app=test_app, data_in_db=data_in_db)

    response1 = client.get("/product/offers", headers=headers1)
    assert response1.data == b'{"code":400,"description":"Token is missing!","name":"Not found"}\n'

    response2 = client.get("/product/offers", headers=headers2)
    assert response2.data == b'{"code":403,"description":"Token is not valid!","name":"Forbidden"}\n'

    response3 = client.get("/product/offers", headers=headers3,  json={'id': str(data_in_db[0])})
    assert response3.data.decode() == '{"code":404,"description":"There is no records of offers for product '+ str(data_in_db[0])+' to be found","name":"Not found"}\n'
    

def test_get_offer(test_app, token, client, data_in_db):
    headers0 = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
    headers1 = {}
    headers2 = {'Authorization': 'Bearer ' + 'xxxxxxxxxxJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiYWRtaW4iLCJleHAiOjE2NzYzOTI5NDZ9.NKViFsmOmdKR-qb3P9MUM-q16RmQPs0kDPtQ6b86ECA','Content-Type': 'application/json'}
    headers3 = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}

    response0 = client.get("/offer", headers=headers0, json={'id': str(data_in_db[2])})
    assert response0.data.decode() ==  '{"id":"'+str(data_in_db[2])+'","items_in_stock":1,"price":1,"product.description":"TESTING1","product.name":"TEST1"}\n'
    clean_up(test_app=test_app, data_in_db=data_in_db)

    response1 = client.get("/offer", headers=headers1)
    assert response1.data == b'{"code":400,"description":"Token is missing!","name":"Not found"}\n'

    response2 = client.get("/offer", headers=headers2)
    assert response2.data == b'{"code":403,"description":"Token is not valid!","name":"Forbidden"}\n'

    response3 = client.get("/offer", headers=headers3,  json={'id': str(data_in_db[2])})
    assert response3.data.decode() == '{"code":404,"description":"There is no record of offer '+str(data_in_db[2])+' to be found","name":"Not found"}\n'

