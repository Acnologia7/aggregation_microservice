import requests, logging, os

from uuid import UUID
from app import base_app
from sqlalchemy.dialects.postgresql import insert

from .models import db, Token, Product, Offer
from .views import applifting_api


def periodic_update_offers_task(update_offers_test_values=None):
    
    with base_app.app_context():
        try:
            products = db.session.query(Product).all()
            
            if not products:
                return None
            
            for product in products:
                
                update_offers = applifting_api.get_product_offers(product.id) if not update_offers_test_values else update_offers_test_values
                
                if isinstance(update_offers, dict):
                    logging.warning('No offers from applifting api (issue with connection or invalid token), skipping update until next run...')
                    return None
                
                current_offers = db.session.query(Offer).filter_by(product_id=product.id).all()
                co_ids = [id.id for id in current_offers]
                uo_ids = [UUID(id['id']) for id in update_offers]
            
                for offer in update_offers:
                    insert_q = insert(Offer).values(
                        id=UUID(offer['id']), 
                        price=offer['price'], 
                        items_in_stock=offer['items_in_stock'], 
                        product_id=product.id
                    )
                        
                    update_on_conflict = insert_q.on_conflict_do_update(
                        index_elements=['id'],
                        set_=dict(price=offer['price'], items_in_stock=offer['items_in_stock'])
                    )
                    db.session.execute(update_on_conflict)  
                
                to_delete_ids = [x for x in co_ids if x not in uo_ids]

                if to_delete_ids:
                    to_detele_records = Offer.query.where(Offer.id.in_(to_delete_ids))
                    to_detele_records.delete()
                
                db.session.commit()
        
        except Exception as e:
            logging.exception(e)

            
def periodic_update_token() -> None:
    url = f"{os.getenv('BASE_URL')}auth"
    try:
        res = requests.post(url, headers={'Bearer': os.getenv('REFRESH_TOKEN')})
        
        if res.status_code == 201:
            with base_app.app_context():
                token_to_update = db.session.get(Token, UUID('d2e96009-eea8-477d-ae7a-e1fdf2eaaaaa'))
                
                if not token_to_update:
                    to_insert = Token(token=res.json()['access_token'])
                    db.session.add(to_insert)
                
                else:
                    token_to_update.token = res.json()['access_token']
                
                db.session.commit()

    except Exception as e:
        logging.exception(e)
