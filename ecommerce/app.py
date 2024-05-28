from flask import Flask, jsonify , request
from flask_restful import Api, Resource
from flask_pymongo import PyMongo
from flask_cors import CORS  # Import CORS
from flask_jwt_extended import JWTManager, create_access_token
from datetime import timedelta
import os

app = Flask(__name__)
CORS(app)

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', '#9G8G8LLVJ@pg')  # Default value for development
jwt = JWTManager(app)

# MongoDB Atlas Configuration
app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb+srv://parthgupta221092:9G8G8LLVJ@ecommerce-cluster.wjmddqr.mongodb.net/Ecommerce?retryWrites=true&w=majority')
mongo = PyMongo(app)

# Define collections in the Ecommerce database
products = mongo.db.product
brands = mongo.db.brands
categories = mongo.db.categories
users = mongo.db.users
cart = mongo.db.cart
orders = mongo.db.orders
api = Api(app)

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
            product_info = request.json
            new_product = products.insert_one(product_info)

            # Retrieve the inserted product using its ID
            inserted_id = new_product.inserted_id
            inserted_product = products.find_one({'_id': inserted_id})

            # Check if the product was successfully inserted
            if inserted_product:
                # Convert ObjectId to string for JSON serialization
                inserted_product['_id'] = str(inserted_product['_id'])

                # Return the inserted product data as is
                return inserted_product, 201
            else:
                return '', 500  # Return empty response with status code 500
        except Exception as e:
            return '', 500

    def delete(self,product_id):
        result = products.delete_one({'id': product_id})
        if result.deleted_count == 1:
            return {"message": f'Successfully deleted product with id {product_id}'}
        else:
            return {"message": f'Product with id {product_id} not found'}, 404
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
class User(Resource):
    def post(self):
        user_data = request.get_json()
        if 'email' in user_data and 'password' in user_data:
            already_user = users.find_one({"email": user_data['email']})
            if already_user:
                return {"message": "Already a user"}, 400
            result = users.insert_one(user_data)
            if result.inserted_id:
                user_data['_id'] = str(user_data['_id'])
                return {"user": user_data}, 201
            else:
                return {"message": "Failed to create user"}, 500
        else:
            return {"message": "Kam 25"}, 200
    def get(self):
        email = request.args.get('email')
        password = request.args.get('password')

        user = users.find_one({"email": email})
        if user and user['password'] == password:
            user["_id"] = str(user["_id"])  
            access_token = create_access_token(
                identity={"email": email,"password": password},
                expires_delta=timedelta(hours=1)
            )
            response_data = {
                "access_token": access_token,
                "user": user
            }
            return jsonify(response_data)
        return {"msg": "Invalid credentials"}, 401


class Cart(Resource):
    def post(self):
        data = request.get_json()

        # Check if userId and id are present in the request data
        if "userId" not in data or "id" not in data:
            return {"error": "Missing userId or id in request data"}, 400

        try:
            # Check if the document exists
            result = cart.find_one({"userId": data["userId"], "id": data["id"]})
            if result:
                # Increment the quantity field by 1
                cart.update_one({"userId": data["userId"], "id": data["id"]}, {"$inc": {"quantity": 1}})
                # Retrieve the updated document
                updated_result = cart.find_one({"userId": data["userId"], "id": data["id"]})
                # Convert ObjectId to string
                updated_result['_id'] = str(updated_result['_id'])
                return {"data": updated_result}, 200
            else:
                inserted_id = cart.insert_one(data).inserted_id
                new_document = cart.find_one({"_id": inserted_id})
                new_document['_id'] = str(new_document['_id'])
                return {"data": new_document}, 201
        except Exception as e:
            return {"error": str(e)}, 500

    def get(self):
        userId = request.args.get("userId")

        if not userId:
            return {"error": "Missing userId in request parameters"}, 400

        try:
            # Find all documents with the specified userId, sorted by the 'id' field
            results = cart.find({"userId": userId}).sort("id")

            # Convert the results to a list and ObjectId to string
            documents = []
            for document in results:
                document['_id'] = str(document['_id'])
                documents.append(document)

            return documents, 200
        except Exception as e:
            return {"error": str(e)}, 500

    def delete(self):
        item = request.get_json()
        itemId = item["itemId"]
        user = item["user"]
        if not itemId or not user:
            return {"error": "Missing itemId or user in request parameters"}, 400

        try:
            # Find and delete the object using an AND operation
            result = cart.delete_one({"id": itemId, "userId": user})

            if result.deleted_count > 0:
                return {"message": "Successfully deleted"}, 200
            else:
                return {"message": "Item not found"}, 404
        except Exception as e:
            return {"error": str(e)}, 500

    def patch(self):
        details = request.get_json()

        if "id" not in details or "addresses" not in details:
            return {"error": "Missing id or addresses in request data"}, 400

        try:
            # Find the document by id in the user collection
            user_document = users.find_one({"id": details["id"]})

            if user_document:
                users.update_one({"id": details["id"]}, {"$set": {"addresses": details["addresses"]}})
                # Retrieve the updated document
                updated_document = users.find_one({"id": details["id"]})
                # Convert ObjectId to string
                updated_document['_id'] = str(updated_document['_id'])
                return {"data": updated_document}, 200
            else:
                return {"error": "User not found"}, 404
        except Exception as e:
            return {"error": str(e)}, 500
class Orders(Resource):
    def post(self):
        order_data = request.get_json()
        try:
            insert_result = orders.insert_one(order_data)
            created_order = orders.find_one({"_id": insert_result.inserted_id})
            if created_order:
                created_order['_id'] = str(created_order['_id'])
                return created_order, 201
            else:
                return {"message": "Error finding the created order"}, 500
        except Exception as e:
            return {"message": str(e)}, 500

    # http://127.0.0.1:8080/order?orderId=6cbebdd5-6568-4512-b22d-2bcac49a514f
    def get(self):
        orderId = request.args.get("orderId")
        userId = request.args.get("userId")

        if orderId:
            if not orderId:
                return {"message": "Missing orderId parameter"}, 400

            try:
                # Find the order by orderId
                requiredOrder = orders.find_one({"id": orderId})

                if requiredOrder:
                    # Convert the ObjectId to a string for JSON serialization
                    requiredOrder["_id"] = str(requiredOrder["_id"])
                    return requiredOrder, 200
                else:
                    return {"message": "No Order Found"}, 404
            except Exception as e:
                return {"message": str(e)}, 500
        elif userId:
            if not userId:
                return {"message": "Missing userId parameter"}, 400

            try:
                # Find all orders for the specified user ID
                orders_list = list(orders.find({"user.id": userId}))

                if orders_list:
                    # Convert the ObjectId to a string for JSON serialization
                    for order in orders_list:
                        order["_id"] = str(order["_id"])
                    return orders_list, 200
                else:
                    return {"message": "No Orders Found"}, 404
            except Exception as e:
                return {"message": str(e)}, 500
        else:
            try:
                orders_list = list(orders.find({}))
                for order in orders_list:
                    order["_id"] = str(order["_id"])

                return orders_list, 200
            except Exception as e:
                return {"message": str(e)}, 500

    def patch(self):
        data = request.get_json()

        # Check if both "id" and "status" are present in the data
        if "id" not in data or "status" not in data:
            return {"message": "Missing id or status"}, 400

        try:
            # Find the order to update
            toupdate = orders.find_one({"id": data["id"]})

            if not toupdate:
                return {"message": "Order not found"}, 404

            # Update the order's status
            update_result = orders.update_one(
                {"id": data["id"]},
                {"$set": {"status": data["status"]}}
            )

            if update_result.modified_count > 0:
                # Find the updated order to return it
                updated_order = orders.find_one({"id": data["id"]})
                updated_order["_id"] = str(updated_order["_id"])
                return {"data": updated_order}, 200
            else:
                return {"message": "No changes made to the order"}, 304

        except Exception as e:
            return {"message": str(e)}, 500

api.add_resource(ProductFilter, '/productfilter')
api.add_resource(Product, '/products/<string:product_id>',"/products/")
api.add_resource(Brands, '/brands')
api.add_resource(Categories, '/categories')
api.add_resource(User, '/users',"/users/")
api.add_resource(Cart,"/cart")
api.add_resource(Orders , "/order")


if __name__ == '__main__':
    app.run(debug=True, port=8080)