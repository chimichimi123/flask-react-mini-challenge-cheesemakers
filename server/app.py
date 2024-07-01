from flask import Flask, jsonify, make_response, request
from flask_cors import CORS
from flask_migrate import Migrate
from models import Cheese, Producer, db
from datetime import datetime

# from flask_restful import Api, Resource


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

# api = Api(app)


@app.route("/")
def index():
    response = make_response({"message": "Hello Fromagers!"}, 200)
    return response

@app.route('/producers', methods=['GET'])
def get_producers():
    producer_query = Producer.query.all()
    
    producers = []
    for producer in producer_query:
        producers.append({
            "id": producer.id,
            "name": producer.name,
            "founding_year": producer.founding_year,
            "operation_size": producer.operation_size,
            "region": producer.region,
            "image": producer.image
        })
    
    return jsonify(producers)

@app.route('/producers/<int:producer_id>', methods=['GET'])
def get_producer_by_id(producer_id):
    producer = Producer.query.get(producer_id)
    
    if producer is None:
        return jsonify({"error": "Producer not found"}), 404
    
    producer_data = {
        "id": producer.id,
        "name": producer.name,
        "founding_year": producer.founding_year,
        "operation_size": producer.operation_size,
        "region": producer.region,
        "image": producer.image,
        "cheeses": [
            {
                "id": cheese.id,
                "image": cheese.image,
                "is_raw_milk": cheese.is_raw_milk,
                "kind": cheese.kind,
                "price": cheese.price,
                "producer_id": cheese.producer_id,
                "production_date": cheese.production_date.strftime("%Y-%m-%d %H:%M:%S")
            } for cheese in producer.cheeses
        ]
    }
    
    return jsonify(producer_data)

@app.route('/producers/<int:producer_id>', methods=['DELETE'])
def delete_producer(producer_id):
    producer = Producer.query.get(producer_id)
    
    if producer is None:
        return jsonify({"error": "Resource not found"}), 404
    
    Cheese.query.filter_by(producer_id=producer_id).delete()
    
    db.session.delete(producer)
    
    db.session.commit()
    
    return ('', 204)

@app.route('/cheeses', methods=['POST'])
def create_cheese():
    data = request.json
    
    required_fields = ['kind', 'is_raw_milk', 'production_date', 'image', 'price', 'producer_id']
    if not all(field in data for field in required_fields):
        return jsonify({"errors": ["Missing fields"]}), 400
    
    producer = Producer.query.get(data['producer_id'])
    if not producer:
        return jsonify({"errors": ["Producer not found"]}), 404
    
    try:
        cheese = Cheese(
            kind=data['kind'],
            is_raw_milk=data['is_raw_milk'],
            production_date=datetime.date(data['production_date'], '%Y-%m-%d'),
            image=data['image'],
            price=data['price'],
            producer_id=data['producer_id']
        )
        
        db.session.add(cheese)
        db.session.commit()
    
        return jsonify({
            "id": cheese.id,
            "image": cheese.image,
            "is_raw_milk": cheese.is_raw_milk,
            "kind": cheese.kind,
            "price": cheese.price,
            "producer": {
                "name": producer.name
            },
            "producer_id": cheese.producer_id,
            "production_date": cheese.production_date.strftime("%Y-%m-%d %H:%M:%S")
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"errors": ["validation errors", str(e)]}), 400
    
@app.route('/cheeses/<int:id>', methods=['PATCH'])
def update_cheese(id):
    cheese = Cheese.query.get(id)
    if cheese is None:
        return jsonify({"error": "Resource not found"}), 404
    
    data = request.json
    for key, value in data.items():
        if hasattr(cheese, key):
            setattr(cheese, key, value)
    
    db.session.commit()
    return jsonify(cheese.serialize()), 200

@app.route('/cheeses/<int:id>', methods=['DELETE'])
def delete_cheese(id):
    cheese = Cheese.query.get(id)
    if cheese is None:
        return jsonify({"error": "Resource not found"}), 404
    
    db.session.delete(cheese)
    db.session.commit()
    
    return '', 204

if __name__ == "__main__":
    app.run(port=5555, debug=True)
