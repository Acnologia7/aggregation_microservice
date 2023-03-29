try:
    from dotenv import load_dotenv
    load_dotenv()
    
    from app.views import base_app
    from app.models import db
    
except Exception as e:
    raise e

else:
    with base_app.app_context():
        db.create_all()

    print("Database created successfully.")
