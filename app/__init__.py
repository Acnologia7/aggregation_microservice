import os
import logging
from logging import FileHandler, ERROR, CRITICAL, WARNING

from flask import Flask
from dotenv import load_dotenv
from flask_apscheduler import APScheduler
from apscheduler.schedulers.background import BackgroundScheduler

from .models import db
from .schemas import ma

load_dotenv()

dirname = os.path.dirname(__file__)

file_handler_warrning = FileHandler(os.path.join(dirname, 'logs/warrning.log'))
file_handler_error = FileHandler(os.path.join(dirname, 'logs/errors.log'))
file_handler_critical = FileHandler(os.path.join(dirname, 'logs/critical.log'))

file_handler_warrning.setLevel(WARNING)
file_handler_error.setLevel(ERROR)
file_handler_critical.setLevel(CRITICAL)

logging.basicConfig(level=WARNING,handlers=[file_handler_error, file_handler_critical, file_handler_warrning], format='%(asctime)s :: %(name)s :: %(levelname)-8s :: %(message)s')

base_app = Flask(__name__)

def create_base_app():
    try:
        #if os.getenv('TESTING_MODE') == '0':
        base_app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('POSTGRES_DEV_URI')
        
        #else: 
            #base_app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv('POSTGRES_TEST_URI')
        
        base_app.config["SECRET_KEY"] = os.getenv('SECRET_KEY')
        
        bsched = BackgroundScheduler(daemon=True)
        sched = APScheduler(app=base_app, scheduler=bsched)

        db.init_app(base_app)
        ma.init_app(base_app)    
        sched.init_app(base_app)
        base_app.app_context().push()
    
    except Exception as e:
        logging.exception(e)

    return base_app, sched
    
   


