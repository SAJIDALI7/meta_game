# backend/app.py
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from pymongo import MongoClient
from flask_cors import CORS
from bson import ObjectId
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# MongoDB configuration
# app.config["MONGO_URI"] = os.environ.get("MONGO_URI", "mongodb://localhost:27017/meta_store")
# mongo = PyMongo(app)
# print(mongo)

try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client['meta_store']  # Use your actual database name
    collection = db['meta_store']  # Use your actual collection name

    print("Connected to MongoDB successfully!")
except Exception as e:
    print(f"MongoDB connection error: {e}")

# Helper function to convert MongoDB ObjectId to string
def parse_json(data):
    if isinstance(data, list):
        return [{**item, '_id': str(item['_id'])} for item in data]
    else:
        return {**data, '_id': str(data['_id'])}

@app.route('/api/apps', methods=['GET'])
@app.route('/api/apps')
def get_apps():
    apps = list(collection.find({}, {'_id': 0}))
    return jsonify({"success": True, "data": apps})
# def get_apps():
#     """Get all apps with optional filtering, pagination, and search."""
#     try:
#         # Query parameters
#         page = int(request.args.get('page', 1))
#         per_page = int(request.args.get('per_page', 10))
#         category = request.args.get('category')
#         min_rating = request.args.get('min_rating')
#         search_query = request.args.get('q')
#         sort_by = request.args.get('sort_by', 'app_name')
#         sort_order = int(request.args.get('sort_order', 1))  # 1 for ascending, -1 for descending
        
#         # Build filter query
#         query = {}
#         if category:
#             query['category'] = category
#         if min_rating:
#             query['ratings'] = {'$gte': float(min_rating)}
#         if search_query:
#             query['$or'] = [
#                 {'app_name': {'$regex': search_query, '$options': 'i'}},
#                 {'description': {'$regex': search_query, '$options': 'i'}}
#             ]
        
#         # Get total number of matching documents
#         total = mongo.db.apps.count_documents(query)
        
#         # Apply pagination and sorting
#         apps = list(mongo.db.apps.find(query)
#                     .sort(sort_by, sort_order)
#                     .skip((page - 1) * per_page)
#                     .limit(per_page))
        
#         # Prepare response
#         result = {
#             'apps': parse_json(apps),
#             'page': page,
#             'per_page': per_page,
#             'total': total,
#             'total_pages': (total + per_page - 1) // per_page  # Ceiling division
#         }
        
#         return jsonify(result)
    
#     except Exception as e:
#         logger.error(f"Error fetching apps: {e}")
#         return jsonify({'error': str(e)}), 500

@app.route('/api/apps/<app_id>', methods=['GET'])
def get_app(app_id):
    """Get a single app by ID."""
    try:
        app = mongo.db.apps.find_one({'app_id': app_id})
        if app:
            return jsonify(parse_json(app))
        else:
            return jsonify({'error': 'App not found'}), 404
    except Exception as e:
        logger.error(f"Error fetching app {app_id}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/apps/<app_id>', methods=['PUT'])
def update_app(app_id):
    """Update an app's details."""
    try:
        data = request.json
        # Prevent overwriting the app_id
        if 'app_id' in data:
            del data['app_id']
            
        result = mongo.db.apps.update_one(
            {'app_id': app_id},
            {'$set': data}
        )
        
        if result.matched_count:
            updated_app = mongo.db.apps.find_one({'app_id': app_id})
            return jsonify(parse_json(updated_app))
        else:
            return jsonify({'error': 'App not found'}), 404
    except Exception as e:
        logger.error(f"Error updating app {app_id}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/apps/<app_id>', methods=['DELETE'])
def delete_app(app_id):
    """Delete an app."""
    try:
        result = mongo.db.apps.delete_one({'app_id': app_id})
        if result.deleted_count:
            return jsonify({'success': True, 'message': f'App {app_id} deleted successfully'})
        else:
            return jsonify({'error': 'App not found'}), 404
    except Exception as e:
        logger.error(f"Error deleting app {app_id}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all unique categories."""
    try:
        categories = mongo.db.apps.distinct('category')
        return jsonify({'categories': categories})
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        return jsonify({'error': str(e)}), 500

# Script to import scraped data into MongoDB
@app.route('/api/import', methods=['POST'])
def import_data():
    """Import scraped data into MongoDB (admin endpoint)."""
    try:
        data = request.json
        if not data or not isinstance(data, list):
            return jsonify({'error': 'Invalid data format. Expected a list of apps.'}), 400
        
        # Clear existing data if specified
        if request.args.get('clear', 'false').lower() == 'true':
            mongo.db.apps.delete_many({})
        
        # Insert new data
        for app in data:
            # Use app_id as the unique identifier
            mongo.db.apps.update_one(
                {'app_id': app['app_id']},
                {'$set': app},
                upsert=True
            )
        
        return jsonify({'success': True, 'message': f'{len(data)} apps imported successfully'})
    except Exception as e:
        logger.error(f"Error importing data: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)


# from flask import Flask, request, jsonify
# from flask_pymongo import PyMongo
# from pymongo import MongoClient
# from flask_cors import CORS
# from bson import ObjectId
# import os
# import logging

# app = Flask(__name__)
# app.config["MONGO_URI"] = "mongodb://localhost:27017/meta_store"
# mongo = PyMongo(app)
# CORS(app)

# @app.route('/api/apps', methods=['GET'])
# def get_apps():
#     try:
#         # Now you can use mongo.db.apps
#         apps = list(mongo.db.apps.find({}, {'_id': 0}))
#         return jsonify({"success": True, "data": apps})
#     except Exception as e:
#         return jsonify({"success": False, "error": str(e)}), 500