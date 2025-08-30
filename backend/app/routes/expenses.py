from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Expense, User

# Create blueprint
expenses_bp = Blueprint('expenses', __name__)

@expenses_bp.route('/expenses', methods=['GET'])
@jwt_required()
def get_expenses():
    try:
        user_id = get_jwt_identity()
        
        # Pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Query expenses for current user
        expenses = Expense.query.filter_by(user_id=user_id).order_by(Expense.date.desc())
        
        # Paginate results
        paginated_expenses = expenses.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'expenses': [expense.to_dict() for expense in paginated_expenses.items],
            'total': paginated_expenses.total,
            'pages': paginated_expenses.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@expenses_bp.route('/expenses', methods=['POST'])
@jwt_required()
def create_expense():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data.get('category') or not data.get('amount'):
            return jsonify({'error': 'Category and amount are required'}), 400
        
        # Create expense
        expense = Expense(
            category=data['category'],
            amount=data['amount'],
            description=data.get('description', ''),
            user_id=user_id
        )
        
        db.session.add(expense)
        db.session.commit()
        
        return jsonify(expense.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@expenses_bp.route('/expenses/<int:id>', methods=['GET'])
@jwt_required()
def get_expense(id):
    try:
        user_id = get_jwt_identity()
        expense = Expense.query.filter_by(id=id, user_id=user_id).first()
        
        if expense:
            return jsonify(expense.to_dict()), 200
        else:
            return jsonify({'error': 'Expense not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@expenses_bp.route('/expenses/<int:id>', methods=['PATCH'])
@jwt_required()
def update_expense(id):
    try:
        user_id = get_jwt_identity()
        expense = Expense.query.filter_by(id=id, user_id=user_id).first()
        
        if not expense:
            return jsonify({'error': 'Expense not found'}), 404
        
        data = request.get_json()
        
        # Update fields if provided
        if 'category' in data:
            expense.category = data['category']
        if 'amount' in data:
            expense.amount = data['amount']
        if 'description' in data:
            expense.description = data['description']
        
        db.session.commit()
        
        return jsonify(expense.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@expenses_bp.route('/expenses/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_expense(id):
    try:
        user_id = get_jwt_identity()
        expense = Expense.query.filter_by(id=id, user_id=user_id).first()
        
        if not expense:
            return jsonify({'error': 'Expense not found'}), 404
        
        db.session.delete(expense)
        db.session.commit()
        
        return jsonify({'message': 'Expense deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500