from flask import Blueprint, jsonify, request, session

from auth import login_required
from extensions import db
from models import InventoryItem

inventory_bp = Blueprint('inventory', __name__)

# Create a new inventory item
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

# Get all inventory items for the logged-in user
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

# Get a single inventory item by its ID
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

# Update an inventory item
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

# Delete an inventory item
@inventory_bp.route('/inventory/<int:item_id>', methods=['DELETE'])
@login_required
def delete_item(item_id):
    item = InventoryItem.query.filter_by(id=item_id, user_id=session['user_id']).first()
    
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    db.session.delete(item)
    db.session.commit()
    
    return jsonify({'message': 'Item deleted successfully'}), 200
