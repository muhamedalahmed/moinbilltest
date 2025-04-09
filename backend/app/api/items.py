from flask import Blueprint, request, jsonify
from app.models.item import Item
from app.schemas.item_schema import item_schema, items_schema
from app import db
from flask_jwt_extended import jwt_required

items_bp = Blueprint('items', __name__)

@items_bp.route('', methods=['GET'])
@jwt_required()
def get_items():
    """
    Gibt alle Artikel/Leistungen zurück
    """
    items = Item.query.all()
    return jsonify(items_schema.dump(items)), 200

@items_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_item(id):
    """
    Gibt einen Artikel/eine Leistung anhand seiner ID zurück
    """
    item = Item.query.get_or_404(id)
    return jsonify(item_schema.dump(item)), 200

@items_bp.route('', methods=['POST'])
@jwt_required()
def create_item():
    """
    Erstellt einen neuen Artikel/eine neue Leistung
    """
    data = request.get_json()
    
    # Validiere die Daten mit dem Schema
    errors = item_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    # Erstelle neuen Artikel
    new_item = Item(
        item_number=data.get('item_number'),
        name=data.get('name'),
        description=data.get('description'),
        unit=data.get('unit', 'Stück'),
        price_net=data.get('price_net'),
        vat_rate=data.get('vat_rate', 19.0),
        is_active=data.get('is_active', True)
    )
    
    db.session.add(new_item)
    db.session.commit()
    
    return jsonify(item_schema.dump(new_item)), 201

@items_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_item(id):
    """
    Aktualisiert einen bestehenden Artikel/eine bestehende Leistung
    """
    item = Item.query.get_or_404(id)
    data = request.get_json()
    
    # Validiere die Daten mit dem Schema
    errors = item_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    # Aktualisiere Artikeldaten
    item.item_number = data.get('item_number', item.item_number)
    item.name = data.get('name', item.name)
    item.description = data.get('description', item.description)
    item.unit = data.get('unit', item.unit)
    item.price_net = data.get('price_net', item.price_net)
    item.vat_rate = data.get('vat_rate', item.vat_rate)
    item.is_active = data.get('is_active', item.is_active)
    
    db.session.commit()
    
    return jsonify(item_schema.dump(item)), 200

@items_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_item(id):
    """
    Löscht einen Artikel/eine Leistung (setzt is_active auf False)
    """
    item = Item.query.get_or_404(id)
    
    # Statt physisches Löschen, setzen wir is_active auf False
    item.is_active = False
    db.session.commit()
    
    return jsonify({"message": "Artikel/Leistung erfolgreich deaktiviert"}), 200

@items_bp.route('/search', methods=['GET'])
@jwt_required()
def search_items():
    """
    Sucht nach Artikeln/Leistungen basierend auf Suchkriterien
    """
    query = request.args.get('query', '')
    
    # Suche in verschiedenen Feldern
    items = Item.query.filter(
        (Item.name.ilike(f'%{query}%')) |
        (Item.item_number.ilike(f'%{query}%')) |
        (Item.description.ilike(f'%{query}%'))
    ).all()
    
    return jsonify(items_schema.dump(items)), 200
