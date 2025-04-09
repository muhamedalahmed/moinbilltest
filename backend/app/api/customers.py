from flask import Blueprint, request, jsonify
from app.models.customer import Customer
from app.schemas.customer_schema import customer_schema, customers_schema
from app import db
from flask_jwt_extended import jwt_required

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('', methods=['GET'])
@jwt_required()
def get_customers():
    """
    Gibt alle Kunden zurück
    """
    customers = Customer.query.all()
    return jsonify(customers_schema.dump(customers)), 200

@customers_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_customer(id):
    """
    Gibt einen Kunden anhand seiner ID zurück
    """
    customer = Customer.query.get_or_404(id)
    return jsonify(customer_schema.dump(customer)), 200

@customers_bp.route('', methods=['POST'])
@jwt_required()
def create_customer():
    """
    Erstellt einen neuen Kunden
    """
    data = request.get_json()
    
    # Validiere die Daten mit dem Schema
    errors = customer_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    # Erstelle neuen Kunden
    new_customer = Customer(
        company_name=data.get('company_name'),
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        street=data.get('street'),
        house_number=data.get('house_number'),
        postal_code=data.get('postal_code'),
        city=data.get('city'),
        country=data.get('country'),
        tax_id=data.get('tax_id'),
        vat_id=data.get('vat_id'),
        email=data.get('email'),
        phone=data.get('phone'),
        is_active=data.get('is_active', True)
    )
    
    db.session.add(new_customer)
    db.session.commit()
    
    return jsonify(customer_schema.dump(new_customer)), 201

@customers_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_customer(id):
    """
    Aktualisiert einen bestehenden Kunden
    """
    customer = Customer.query.get_or_404(id)
    data = request.get_json()
    
    # Validiere die Daten mit dem Schema
    errors = customer_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    # Aktualisiere Kundendaten
    customer.company_name = data.get('company_name', customer.company_name)
    customer.first_name = data.get('first_name', customer.first_name)
    customer.last_name = data.get('last_name', customer.last_name)
    customer.street = data.get('street', customer.street)
    customer.house_number = data.get('house_number', customer.house_number)
    customer.postal_code = data.get('postal_code', customer.postal_code)
    customer.city = data.get('city', customer.city)
    customer.country = data.get('country', customer.country)
    customer.tax_id = data.get('tax_id', customer.tax_id)
    customer.vat_id = data.get('vat_id', customer.vat_id)
    customer.email = data.get('email', customer.email)
    customer.phone = data.get('phone', customer.phone)
    customer.is_active = data.get('is_active', customer.is_active)
    
    db.session.commit()
    
    return jsonify(customer_schema.dump(customer)), 200

@customers_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_customer(id):
    """
    Löscht einen Kunden (setzt is_active auf False)
    """
    customer = Customer.query.get_or_404(id)
    
    # Statt physisches Löschen, setzen wir is_active auf False
    customer.is_active = False
    db.session.commit()
    
    return jsonify({"message": "Kunde erfolgreich deaktiviert"}), 200

@customers_bp.route('/search', methods=['GET'])
@jwt_required()
def search_customers():
    """
    Sucht nach Kunden basierend auf Suchkriterien
    """
    query = request.args.get('query', '')
    
    # Suche in verschiedenen Feldern
    customers = Customer.query.filter(
        (Customer.company_name.ilike(f'%{query}%')) |
        (Customer.first_name.ilike(f'%{query}%')) |
        (Customer.last_name.ilike(f'%{query}%')) |
        (Customer.email.ilike(f'%{query}%'))
    ).all()
    
    return jsonify(customers_schema.dump(customers)), 200
