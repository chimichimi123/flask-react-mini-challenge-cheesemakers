from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates, relationship
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime

db = SQLAlchemy()


class Producer(db.Model, SerializerMixin):
    __tablename__ = "producers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    founding_year = db.Column(db.Integer)
    operation_size = db.Column(db.String)
    region = db.Column(db.String)
    image = db.Column(db.String)
    
    cheeses = relationship("Cheese", back_populates="producer")

    @validates("name")
    def validate_name(self, key, name):
        if not name:
            raise AssertionError("Name is required")
        return name
    
    @validates('founding_year')
    def validate_founding_year(self, key, year):
        current_year = datetime.now().year
        if year < 1900 or year > current_year:
            raise AssertionError('Founding year must be between 1900 and the current year')
        return year
    
    @validates('operation_size')
    def validate_operation_size(self, key, size):
        valid_sizes = ["small", "medium", "large", "family", "corporate"]
        if size not in valid_sizes:
            raise AssertionError('Operation size must be one of "small", "medium", "large", "family", "corporate"')
        return size
    
    def __repr__(self):
        return f"<Producer {self.id}>"
    

class Cheese(db.Model, SerializerMixin):
    __tablename__ = "cheeses"

    id = db.Column(db.Integer, primary_key=True)
    producer_id = db.Column(db.Integer, db.ForeignKey("producers.id"))
    production_date = db.Column(db.Date)
    price = db.Column(db.Float)
    is_raw_milk = db.Column(db.Boolean)
    kind = db.Column(db.String)
    image = db.Column(db.String)
    
    producer = relationship("Producer", back_populates="cheeses")
    
    @validates('production_date')
    def validate_production_date(self, key, date):
        if date >= datetime.now().date():
            raise AssertionError('Production date must be before today')
        return date
    
    @validates('price')
    def validate_price(self, key, price):
        if price < 1.00 or price > 45.00:
            raise AssertionError('Price must be between 1.00 and 45.00')
        return price

    def __repr__(self):
        return f"<Cheese {self.id}>"
