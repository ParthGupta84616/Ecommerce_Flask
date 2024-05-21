from flask import Flask, jsonify
from flask_restful import Api, Resource
from flask_pymongo import PyMongo
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Your existing code
api = Api(app)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/Ecommerce'
mongo = PyMongo(app)
products = mongo.db.product

class Product(Resource):
    def get(self, product_id):
        product = products.find_one({'id': product_id})
        if product:
            return jsonify(product)
        else:
            return {'message': 'Product not found'}, 404

api.add_resource(Product, '/products/<string:product_id>')

if __name__ == '__main__':
    app.run(debug=True, port=8080)
