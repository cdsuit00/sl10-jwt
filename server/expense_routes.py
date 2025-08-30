from decimal import Decimal, InvalidOperation
from datetime import date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .extensions import db
from .models import Expense
from .schemas import ExpenseSchema

bp_exp = Blueprint("expenses", __name__)
expense_schema = ExpenseSchema()
expenses_schema = ExpenseSchema(many=True)

ALLOWED_CATEGORIES = {"Travel", "Lodging", "Food"}

def parse_decimal(value):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError):
        return None

@bp_exp.get("/expenses")
@jwt_required()
def list_expenses():
    """Paginated index: /expenses?page=1&per_page=10"""
    uid = get_jwt_identity()
    page = max(int(request.args.get("page", 1)), 1)
    per_page = min(max(int(request.args.get("per_page", 10)), 1), 100)

    q = Expense.query.filter_by(user_id=uid).order_by(Expense.date.desc(), Expense.id.desc())
    pagination = q.paginate(page=page, per_page=per_page, error_out=False)
    items = expenses_schema.dump(pagination.items)
    meta = {
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages,
    }
    return jsonify({"data": items, "meta": meta}), 200

@bp_exp.post("/expenses")
@jwt_required()
def create_expense():
    uid = get_jwt_identity()
    data = request.get_json() or {}

    category = data.get("category")
    if category not in ALLOWED_CATEGORIES:
        return jsonify({"error": "category must be one of Travel, Lodging, Food"}), 422

    amount = parse_decimal(data.get("amount"))
    if amount is None or amount <= 0:
        return jsonify({"error": "amount must be a positive number"}), 422

    try:
        d = date.fromisoformat(data.get("date"))
    except Exception:
        return jsonify({"error": "date must be ISO format YYYY-MM-DD"}), 422

    exp = Expense(
        user_id=uid,
        category=category,
        description=(data.get("description") or "").strip() or None,
        amount=amount,
        date=d,
    )
    db.session.add(exp)
    db.session.commit()
    return jsonify(expense_schema.dump(exp)), 201

@bp_exp.get("/expenses/<int:expense_id>")
@jwt_required()
def get_expense(expense_id):
    uid = get_jwt_identity()
    exp = Expense.query.filter_by(id=expense_id, user_id=uid).first()
    if not exp:
        return jsonify({"error": "not found"}), 404
    return jsonify(expense_schema.dump(exp)), 200

@bp_exp.patch("/expenses/<int:expense_id>")
@jwt_required()
def update_expense(expense_id):
    uid = get_jwt_identity()
    exp = Expense.query.filter_by(id=expense_id, user_id=uid).first()
    if not exp:
        return jsonify({"error": "not found"}), 404

    data = request.get_json() or {}

    if "category" in data:
        if data["category"] not in ALLOWED_CATEGORIES:
            return jsonify({"error": "category must be one of Travel, Lodging, Food"}), 422
        exp.category = data["category"]

    if "amount" in data:
        amt = parse_decimal(data["amount"])
        if amt is None or amt <= 0:
            return jsonify({"error": "amount must be a positive number"}), 422
        exp.amount = amt

    if "description" in data:
        desc = (data["description"] or "").strip()
        exp.description = desc or None

    if "date" in data:
        try:
            exp.date = date.fromisoformat(data["date"])
        except Exception:
            return jsonify({"error": "date must be ISO format YYYY-MM-DD"}), 422

    db.session.commit()
    return jsonify(expense_schema.dump(exp)), 200

@bp_exp.delete("/expenses/<int:expense_id>")
@jwt_required()
def delete_expense(expense_id):
    uid = get_jwt_identity()
    exp = Expense.query.filter_by(id=expense_id, user_id=uid).first()
    if not exp:
        return jsonify({"error": "not found"}), 404
    db.session.delete(exp)
    db.session.commit()
    return jsonify({"message": "deleted"}), 200
