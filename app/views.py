import os, jwt, datetime, sqlalchemy, logging

from uuid import UUID
from app import create_base_app
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import BadRequest
from flask import request, jsonify, make_response, json

from .models import db, Product, Offer
from .utils.wraps import token_required
from .APIs.applifting.applifting_api import AppliftingAPI
from .schemas import ProductSchema, OfferSchema, OffersSchema
from .constants.http_status_codes import HTTP_404_NOT_FOUND, \
    HTTP_500_INTERNAL_SERVER_ERROR, HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_200_OK

base_app, sched = create_base_app()

product_schema = ProductSchema(many=False)
products_schema = ProductSchema(many=True)
offer_schema = OfferSchema(many=False)
offers_schema = OffersSchema(many=True)

applifting_api = AppliftingAPI()

def create_flask_app_with_bp():
    return base_app, sched


@base_app.errorhandler(HTTPException)
def handler_generic(e):
    response = e.get_response()
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response


@base_app.route('/auth', methods=['POST'])
def authenicate():
    #Lepší řešení by bylo s db, ale tohle je spíš pro rychlou demostraci
    auth = request.authorization

    if auth and auth.password == os.getenv('PASSWORD_TO_API'):
        token = jwt.encode({'user': auth.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, os.getenv('SECRET_KEY'))
        return jsonify({'token': token})

    return make_response('Could not verify', 401, {'WWW-Authnticate': 'Basic realm="Login Required"'})


@base_app.route('/product', methods=['POST'])
@token_required
def add_product():
    
    name = request.json.get('name') or None
    description = request.json.get('description') or None
    
    try:
        new_product = Product(name, description)
        db.session.add(new_product)
        db.session.flush()
    
        product_to_register = {
            "id": str(new_product.id),
            "name": name,
            "description": description
        }

        res = applifting_api.register_product(product_info=product_to_register)
        if res.get('id') != str(new_product.id):
            return jsonify({
                "code": HTTP_500_INTERNAL_SERVER_ERROR, 
                "name": 'Registration error', 
                "description": f"There was a problem with registration of product {str(new_product.id)} on server."
            }), HTTP_500_INTERNAL_SERVER_ERROR

        offers = applifting_api.get_product_offers(new_product.id)
        if isinstance(offers, dict):
            return jsonify({
                "code": HTTP_500_INTERNAL_SERVER_ERROR, 
                "name": 'Registration error', 
                "description": f"There was a problem with getting offers for product {str(new_product.id)} on server."
            }), HTTP_500_INTERNAL_SERVER_ERROR

        for index in range(len(offers)):
            new_offer = Offer(
                id=offers[index]['id'],
                price=offers[index]['price'],
                items_in_stock=offers[index]['items_in_stock'],
                product_id=new_product.id
            )
            db.session.add(new_offer)
        
        db.session.commit() 
        return product_schema.dump(new_product), HTTP_201_CREATED
    
    except sqlalchemy.exc.IntegrityError:
       return jsonify({
            "code": HTTP_400_BAD_REQUEST, 
            "name": 'Bad request', 
            "description": "Record already exists or name field is empty"
        }), HTTP_400_BAD_REQUEST
    
    except BadRequest:
        return jsonify({
            "code": HTTP_400_BAD_REQUEST, 
            "name": 'Bad request', 
            "description": "Check format of request, content-type (app/json)."
        }), HTTP_400_BAD_REQUEST
           
    except Exception as e:
        logging.exception(e)
        

@base_app.route('/products', methods=['GET'])
@token_required
def get_products():
    try:
        products = db.session.query(Product).all()
    
        if not products:
            return jsonify({
                "code": HTTP_404_NOT_FOUND, 
                "name": 'Not found', 
                "description": "There are no records of products to be found"
            }), HTTP_404_NOT_FOUND
        
        res = products_schema.dump(products)
        return jsonify(res), HTTP_200_OK
    
    except Exception as e:
        logging.exception(e)
    

@base_app.route('/product', methods=['GET'])
@token_required
def get_product():
    try:
        product_id = request.json.get('id')
        product = db.session.get(Product, UUID(product_id))
    
        if not product:
            return jsonify({
                "code": HTTP_404_NOT_FOUND, 
                "name": 'Not found', 
                "description": f"There is no record of product {product_id} to be found"
            }), HTTP_404_NOT_FOUND
                
        res = product_schema.dump(product)
        return res, HTTP_200_OK
    
    except ValueError:
        return jsonify({
                "code": HTTP_400_BAD_REQUEST, 
                "name": 'Bad request', 
                "description": "ID is in wrong hexadecimal format or missing"
        }), HTTP_400_BAD_REQUEST
    
    except BadRequest:
        return jsonify({
            "code": HTTP_400_BAD_REQUEST, 
            "name": 'Bad request', 
            "description": "Check format of request, content-type (app/json)."
        }), HTTP_400_BAD_REQUEST

    except Exception as e:
        logging.exception(e)

@base_app.route('/product', methods=['PUT'])
@token_required
def update_product():
    try:
        product_id = request.json.get('id')
        product_to_update = db.session.get(Product, (UUID(product_id)))
        
        if not product_to_update :
            return jsonify({
                "code": HTTP_404_NOT_FOUND, 
                "name": 'Not found', 
                "description": f"There is no record of product {product_id} to be found"
            }), HTTP_404_NOT_FOUND
            
        product_to_update.name = request.json.get('name')
        product_to_update.description = request.json.get('description')
        db.session.commit()

        res = product_schema.dump(product_to_update)
        return res, HTTP_200_OK
    
    except ValueError:
        return jsonify({
                "code": HTTP_400_BAD_REQUEST, 
                "name": 'Bad request', 
                "description": "ID is in wrong hexadecimal format or missing"
        }), HTTP_400_BAD_REQUEST
    
    except BadRequest:
        return jsonify({
            "code": HTTP_400_BAD_REQUEST, 
            "name": 'Bad request', 
            "description": "Check format of request, content-type (app/json)."
        }), HTTP_400_BAD_REQUEST
    
    except Exception as e:
        logging.exception(e)

@base_app.route('/product', methods=['DELETE'])
@token_required
def delete_product():
    
    try:
        product_id = request.json.get('id')
        product_to_delete = db.session.get(Product, (UUID(product_id)))
        
        if not product_to_delete:
            return jsonify({
                    "code": HTTP_404_NOT_FOUND, 
                    "name": 'Not found', 
                    "description": f"There is no record of product {product_id} to be found"
                }), HTTP_404_NOT_FOUND
            
        db.session.delete(product_to_delete)
        db.session.commit()

        return jsonify({
                    "code": HTTP_200_OK, 
                    "name": 'Deleted', 
                    "description": f"Product {product_id} successfuly deleted"
                }), HTTP_200_OK
    
    except ValueError:
        return jsonify({
                "code": HTTP_400_BAD_REQUEST, 
                "name": 'Bad request', 
                "description": "ID is in wrong hexadecimal format or missing"
        }), HTTP_400_BAD_REQUEST
    
    except BadRequest:
        return jsonify({
            "code": HTTP_400_BAD_REQUEST, 
            "name": 'Bad request', 
            "description": "Check format of request, content-type (app/json)."
        }), HTTP_400_BAD_REQUEST
    
    except Exception as e:
        logging.exception(e)


@base_app.route('/product/offers', methods=['GET'])
@token_required
def get_product_offers():

    try:
        product_id = request.json.get('id')
        product_offers = db.session.query(Offer).filter_by(product_id=UUID(product_id)).all()
        
        if not product_offers:
            return jsonify({
                "code": HTTP_404_NOT_FOUND, 
                "name": 'Not found', 
                "description": f"There is no records of offers for product {product_id} to be found"
            }), HTTP_404_NOT_FOUND

        res = offers_schema.dump(product_offers)
        return res, 200
    
    except ValueError:
        return jsonify({
                "code": HTTP_400_BAD_REQUEST, 
                "name": 'Bad request', 
                "description": "ID is in wrong hexadecimal format or missing"
        }), HTTP_400_BAD_REQUEST
    
    except BadRequest:
        return jsonify({
            "code": HTTP_400_BAD_REQUEST, 
            "name": 'Bad request', 
            "description": "Check format of request, content-type (app/json)."
        }), HTTP_400_BAD_REQUEST
    
    except Exception as e:
        logging.exception(e)


@base_app.route('/offer', methods=['GET'])
@token_required
def get_offer():

    try:
        offer_id = request.json.get('id')
        product_offer = db.session.get(Offer, UUID(offer_id))
        
        if not product_offer:
            return jsonify({
                "code": HTTP_404_NOT_FOUND, 
                "name": 'Not found', 
                "description": f"There is no record of offer {offer_id} to be found"
            }), HTTP_404_NOT_FOUND

        res = offer_schema.dump(product_offer)
        return res, HTTP_200_OK
    
    except ValueError:
        return jsonify({
                "code": HTTP_400_BAD_REQUEST, 
                "name": 'Bad request', 
                "description": "ID is in wrong hexadecimal format or missing"
        }), HTTP_400_BAD_REQUEST
    
    except BadRequest:
        return jsonify({
            "code": HTTP_400_BAD_REQUEST, 
            "name": 'Bad request', 
            "description": "Check format of request, content-type (app/json)."
        }), HTTP_400_BAD_REQUEST
    
    except Exception as e:
        logging.exception(e)
