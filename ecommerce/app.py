from flask import Flask, jsonify , request
from flask_restful import Api, Resource
from flask_pymongo import PyMongo
from flask_cors import CORS  # Import CORS
from bson import ObjectId

app = Flask(__name__)
CORS(app)

api = Api(app)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/Ecommerce'
mongo = PyMongo(app)
products = mongo.db.product
brands = mongo.db.brands
categories = mongo.db.categories

class Product(Resource):
    def get(self, product_id):
        product = products.find_one({'id': product_id})
        if product:
            # Convert ObjectId to string for JSON serialization
            product['_id'] = str(product['_id'])
            return jsonify(product)
        else:
            return {'message': 'Product not found'}, 404

    def post(self):
        try:
            # Extract product information from the request JSON
            product_info = request.json
            new_product = products.insert_one(product_info)

            return {'message': 'Product added successfully', 'product_id': str(new_product.inserted_id)}, 201
        except Exception as e:
            return {'error': str(e)}, 500  # Return an error response with status code 500
class ProductFilter(Resource):
    def get(self):
        page = int(request.args.get('_page', 1))
        per_page = int(request.args.get('_per_page', 20))
        categories = request.args.get("category")
        sort = request.args.get('_sort')
        brand = request.args.get('brand')
        total_itemss = products.count_documents({})
        per_page = max(per_page, 1)
        skip = (page - 1) * per_page
        filtered_products = products
        total_itemsss = 0
        if categories and brand:
            categories = categories.split(',')
            brand = brand.split(",")
            filter_criteria = {"category": {"$in": categories}, "brand": {"$in": brand}}
            filtered_products = products.find(filter_criteria)
            total_itemsss += products.count_documents(filter_criteria)

        elif categories and not brand:
            categories = categories.split(',')
            filter_criteria = {"category": {"$in": categories}}
            filtered_products = products.find(filter_criteria)
            total_itemsss += products.count_documents(filter_criteria)

        elif brand and not categories:
            brand = brand.split(",")
            filter_criteria = {"brand": {"$in": brand}}
            filtered_products = products.find(filter_criteria)
            total_itemsss += products.count_documents(filter_criteria)
        else:
            total_itemsss = total_itemss
            filtered_products = products.find({})

        if sort:
            sort_key = 'price' if sort == "price" else 'rating'
            filtered_products = filtered_products.sort(sort_key, 1)
        filtered_products = filtered_products.limit(per_page).skip(skip)
        products_list = list(filtered_products)
        for product in products_list:
            product['_id'] = str(product['_id'])

        # Pagination metadata
        total_items = len(products_list)
        total_pages = max(1, round(total_items / per_page))
        current_page = min(page, total_pages)
        next_page = skip+2
        prev_page = max(current_page - 1, 1)
        if len(products_list)<per_page:
            next_page = skip +1

        return jsonify({
            "data": products_list,
            "first": 1,
            "items": len(products_list),
            "last": round(total_itemss/per_page),
            "total_items": total_itemsss,
            "next": next_page,
            "pages": round(total_itemss/per_page),
            "prev": skip
        })

class Brands(Resource):
    def get(self):
        brand = brands.find({})
        serialized_brands = []
        for doc in brand:
            doc['_id'] = str(doc['_id'])  # Convert ObjectId to string
            serialized_brands.append(doc)
        return jsonify(serialized_brands)
class Categories(Resource):
    def get(self):
        brand = categories.find({})
        serialized_brands = []
        for doc in brand:
            doc['_id'] = str(doc['_id'])  # Convert ObjectId to string
            serialized_brands.append(doc)
        return jsonify(serialized_brands)





api.add_resource(ProductFilter, '/productfilter')
api.add_resource(Product, '/products/<string:product_id>')
api.add_resource(Brands, '/brands')
api.add_resource(Categories, '/categories')
# api.add_resource(ProductFilter, '/productfilter')
if __name__ == '__main__':
    app.run(debug=True, port=8080)