from auth import login_required
from bson import ObjectId
from extensions import db, mongo
from flask import Blueprint, jsonify, request, session
from models import InventoryItem

inventory_bp = Blueprint('inventory', __name__)


#serializing (converts objectID to string)
def serialize_mongo_inventory(item):
    """
    Serialize a MongoDB inventory item into JSON-compatible format.
    """
    return {
        '_id': str(item['_id']),
        'name': item.get('name'),
        'description': item.get('description'),
        'quantity': item.get('quantity'),
        'price': item.get('price'),
        'user_id': item.get('user_id')
    }

#MongoDB Routes

#mongdb - GET
@inventory_bp.route('/mongo/inventory', methods=['GET'])
def get_all_mongo_inventory():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not authenticared'}), 401
        
        inventory = list(mongo.db.inventory.find({'user_id': user_id}))
        serialized_inventory = [serialize_mongo_inventory(item) for item in inventory]
        return jsonify(serialized_inventory)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#mongdb - GET (sepcific)
@inventory_bp.route('/mongo/inventory/<item_id>', methods=['GET'])
def get_specific_mongo_inventory(item_id):
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not authenticared'}), 401
        item = mongo.db.inventory.find_one({"_id": ObjectId(item_id)})
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        return jsonify(serialize_mongo_inventory(item))
    except Exception as e:
        return jsonify({'error': str(e)}), 400

#mongodb - POST
@inventory_bp.route('/mongo/inventory', methods=['POST'])
def create_mongo_inventory():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not authenticared'}), 401
        
        data = request.json
        if not data or 'name' not in data or 'quantity' not in data or 'price' not in data:
            return jsonify({'error':'Missing required fields'}), 400 
        
        new_item = {
            'name': data['name'],
            'description': data.get('description', ''),
            'quantity': data['quantity'],
            'price': data['price'],
            'user_id': user_id
        }
        result = mongo.db.inventory.insert_one(new_item)
        new_item['_id'] = str(result.inserted_id)
        return jsonify(serialize_mongo_inventory(new_item)), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#mongodb - PUT (specific)
@inventory_bp.route('/mongo/inventory/<item_id>', methods=['PUT'])
def update_mongo_inventory(item_id):
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not authenticared'}), 401
        
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        item = mongo.db.inventory.find_one({"_id": ObjectId(item_id), "user_id": user_id})
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        update_fields = {}
        if 'name' in data:
            update_fields['name'] = data['name']
        if 'description' in data:
            update_fields['description'] = data['description']
        if 'quantity' in data:
            update_fields['quantity'] = data['quantity']
        if 'price' in data:
            update_fields['price'] = data['price']
        
        mongo.db.inventory.update_one({"_id": ObjectId(item_id)}, {"$set": update_fields})
        
        updated_item = mongo.db.inventory.find_one({"_id": ObjectId(item_id)})
        return jsonify(serialize_mongo_inventory(updated_item))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


#mongodb - DELETE (specific)
@inventory_bp.route('/mongo/inventory/<item_id>', methods=['DELETE'])
def delete_mongo_inventory(item_id):
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'User not authenticared'}), 401
        
        item = mongo.db.inventory.find_one({"_id": ObjectId(item_id), "user_id": user_id})
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        mongo.db.inventory.delete_one({"_id": ObjectId(item_id)})
        
        return jsonify({'message': 'Item deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500



#MySQL Routes

#mysql - GET
@inventory_bp.route('/inventory', methods=['GET'])
@login_required
def get_items():
    items = InventoryItem.query.filter_by(user_id=session['user_id']).all()
    return jsonify([{
        'id': item.id,
        'name': item.name,
        'description': item.description,
        'quantity': item.quantity,
        'price': item.price,
        'created_at': item.created_at.isoformat()
    } for item in items]), 200

#mysql - GET (sepcific)
@inventory_bp.route('/inventory/<int:item_id>', methods=['GET'])
@login_required
def get_item(item_id):
    item = InventoryItem.query.filter_by(id=item_id, user_id=session['user_id']).first()
    
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    return jsonify({
        'id': item.id,
        'name': item.name,
        'description': item.description,
        'quantity': item.quantity,
        'price': item.price,
        'created_at': item.created_at.isoformat()
    }), 200

#mysql - POST
@inventory_bp.route('/inventory', methods=['POST'])
@login_required
def create_item():
    data = request.get_json()
    
    if not all(k in data for k in ['name', 'quantity', 'price']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    new_item = InventoryItem(
        name=data['name'],
        description=data.get('description', ''),
        quantity=data['quantity'],
        price=data['price'],
        user_id=session['user_id']
    )
    
    db.session.add(new_item)
    db.session.commit()

    return jsonify({
        'message': 'Item created successfully',
        'item_id': new_item.id
    }), 201

#mysql - PUT
@inventory_bp.route('/inventory/<int:item_id>', methods=['PUT'])
@login_required
def update_item(item_id):
    item = InventoryItem.query.filter_by(id=item_id, user_id=session['user_id']).first()
    
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    data = request.get_json()
    
    if 'name' in data:
        item.name = data['name']
    if 'description' in data:
        item.description = data['description']
    if 'quantity' in data:
        item.quantity = data['quantity']
    if 'price' in data:
        item.price = data['price']
    
    db.session.commit()
    
    return jsonify({'message': 'Item updated successfully'}), 200


#mysql - DELETE (specific)
@inventory_bp.route('/inventory/<int:item_id>', methods=['DELETE'])
@login_required
def delete_item(item_id):
    item = InventoryItem.query.filter_by(id=item_id, user_id=session['user_id']).first()
    
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    db.session.delete(item)
    db.session.commit()
    
    return jsonify({'message': 'Item deleted successfully'}), 200


