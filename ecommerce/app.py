from flask import Flask, jsonify , request
from flask_restful import Api, Resource
from flask_pymongo import PyMongo
from flask_cors import CORS  # Import CORS
from bson import ObjectId

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Your existing code
api = Api(app)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/Ecommerce'
mongo = PyMongo(app)
products = mongo.db.product

  # Import ObjectId from bson module

class Product(Resource):
    def get(self, product_id):
        product = products.find_one({'id': product_id})
        if product:
            # Convert ObjectId to string for JSON serialization
            product['_id'] = str(product['_id'])
            return jsonify(product)
        else:
            return {'message': 'Product not found'}, 404
class ProductFilter(Resource):
    def get(self):
        page = int(request.args.get('_page', 1))
        per_page = int(request.args.get('_per_page', 20))
        categories = request.args.get("category")
        sort = request.args.get('_sort')
        brand = request.args.get('brand')
        total_itemss = products.count_documents({})

        # Ensure per_page is at least 1 to avoid division by zero
        per_page = max(per_page, 1)

        # Calculate the skip value based on the page number and items per page
        skip = (page - 1) * per_page

        # Start with unfiltered products
        filtered_products = products


        # Filter by category and brand if provided
        if categories and brand:
            categories = categories.split(',')
            brand = brand.split(",")
            filtered_products = products.find({"category": {"$in": categories}, "brand": {"$in": brand}})
        # Filter by category if provided
        elif categories and not brand:
            categories = categories.split(',')
            filtered_products = filtered_products.find({"category": {"$in": categories}})
        # Filter by brand if provided
        elif brand and not categories:
            brand = brand.split(",")
            filtered_products = filtered_products.find({"brand": {"$in": brand}})
        else:
            filtered_products = products.find({})

        # Sort by price or rating if provided
        if sort:
            sort_key = 'price' if sort == "price" else 'rating'
            filtered_products = filtered_products.sort(sort_key, 1)

        # Skip the first skip products and limit the result to per_page products
        filtered_products = filtered_products.limit(per_page).skip(skip)


        # Convert MongoDB cursor to a list of dictionaries
        products_list = list(filtered_products)

        # Convert ObjectId to string in the result
        for product in products_list:
            product['_id'] = str(product['_id'])

        # Pagination metadata
        total_items = len(products_list)  # Total number of items without filters
        total_pages = max(1, round(total_items / per_page))  # Ensure at least 1 page
        current_page = min(page, total_pages)  # Ensure current page does not exceed total pages
        next_page = min(current_page + 1, total_pages)
        prev_page = max(current_page - 1, 1)
        print(total_itemss)
        # Return JSON response with filtered, sorted, and limited products along with pagination metadata
        return jsonify({
            "data": products_list,
            "first": 1,
            "items": len(products_list),
            "last": round(total_itemss/per_page),
            "next": skip+2,
            "pages": round(total_itemss/per_page),
            "prev": skip
        })


api.add_resource(ProductFilter, '/productfilter')

api.add_resource(Product, '/products/<string:product_id>')
if __name__ == '__main__':
    app.run(debug=True, port=8080)