import uuid, os

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy
from uuid import UUID as default_uuid
from dotenv import load_dotenv


load_dotenv()

db = SQLAlchemy()
default_id = default_uuid(os.getenv('DEFAULT_UUID_ID'))


class Product(db.Model):
    
    __tablename__ = 'product'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(255))
    offers = db.relationship(
                                'Offer',
                                backref='product',
                                cascade="all,delete-orphan",
                                lazy=True
                            )

    def __init__(self, name, description):
        self.name = name
        self.description = description


class Offer(db.Model):
 
    __tablename__ = 'offer'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    price = db.Column(db.Integer)
    items_in_stock = db.Column(db.Integer)
    product_id = db.Column(UUID(as_uuid=True), db.ForeignKey('product.id'))


class Token(db.Model):

    __tablename__ = 'token'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=default_id)
    token = db.Column(db.String(255))
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    time_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())
