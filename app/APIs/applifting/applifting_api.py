import requests, logging, os

from app.constants.http_status_codes import HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_500_INTERNAL_SERVER_ERROR
from uuid import UUID
from app import base_app
from sqlalchemy.exc import ProgrammingError
from dotenv import load_dotenv

from app.models import Token, db

load_dotenv()

class AppliftingAPI:

    def __init__(self):
        self._base_url = os.getenv('BASE_URL')
        self._token = self._get_token()
    
    def _get_token(self):
        resp_token = ''
        
        try:
            with base_app.app_context():
                r = db.session.get(Token, (UUID(os.getenv('DEFAULT_UUID_ID'))))
                if r:
                    resp_token = r.token

        except ProgrammingError as e:
            if os.getenv('TESTING_MODE') != '1':
                logging.exception(e)
            
            else:
                pass

        except Exception as e:
            logging.exception(e)
        
        return resp_token

    def register_product(self, product_info): 
        
        url = f"{self._base_url}products/register"
        
        try:
            res = requests.post(url, json=product_info, headers={'Bearer': self._token})
            
            if res.status_code == HTTP_401_UNAUTHORIZED:
                self._token = self._get_token()
                res = requests.post(url, json=product_info, headers={'Bearer': self._token})
                logging.warning(msg='!!! TESTING !!! REGISTER PRODUCT - JWT token is invalid..., refreshing it from db and trying again...' if os.getenv('TESTING_MODE') == '1' \
                    else 'REGISTER PRODUCT - JWT token is invalid..., refreshing it from db and trying again...')
                
                if res.status_code != HTTP_201_CREATED:
                    logging.warning(msg='!!! TESTING !!! REGISTER PRODUCT - JWT token still invalid... was not able to register product...' if os.getenv('TESTING_MODE') == '1' \
                        else 'REGISTER PRODUCT - JWT token still invalid... was not able to register product...')

            elif res.status_code == HTTP_500_INTERNAL_SERVER_ERROR:
                logging.warning(msg='!!! TESTING !!! SERVICE NOT AVAIABLE' if os.getenv('TESTING_MODE') == '1' \
                    else 'SERVICE NOT AVAIABLE')
            
            return res.json()
        
        except Exception as e:
            logging.exception(e)
        
        return {}
        

    def get_product_offers(self, product_id):
        url = f"{self._base_url}products/{str(product_id)}/offers"
        
        try:
            res = requests.get(url, headers={"Bearer": self._token})
            
            if res.status_code == HTTP_401_UNAUTHORIZED:
                self._token = self._get_token()
                res = requests.get(url, headers={'Bearer': self._token})
                logging.warning(msg='!!! TESTING !!! GET PRODUCT OFFERS - JWT token is invalid..., refreshing it from db and trying again...' if os.getenv('TESTING_MODE') == '1' \
                    else 'GET PRODUCT OFFERS - JWT token is invalid..., refreshing it from db and trying again...')
                
                if res.status_code != HTTP_201_CREATED:
                    logging.warning(msg='!!! TESTING !!! GET PRODUCT OFFERS - JWT token still invalid... was not able to get product offers...' if os.getenv('TESTING_MODE') == '1' \
                        else 'GET PRODUCT OFFERS - JWT token still invalid... was not able to get product offers...')
            
            elif res.status_code == HTTP_500_INTERNAL_SERVER_ERROR:
                logging.warning(msg='!!! TESTING !!! SERVICE NOT AVAIABLE' if os.getenv('TESTING_MODE') == '1' \
                    else 'SERVICE NOT AVAIABLE')
            
            return res.json()

        except Exception as e:
            logging.exception(e)
        
        return {}
