from flask import Blueprint, request, jsonify
from app.models.invoice import Invoice, InvoiceItem
from app.models.customer import Customer
from app.models.item import Item
from app.schemas.invoice_schema import invoice_schema, invoices_schema, invoice_item_schema
from app import db
from flask_jwt_extended import jwt_required
from datetime import datetime, timedelta
import uuid

invoices_bp = Blueprint('invoices', __name__)

@invoices_bp.route('', methods=['GET'])
@jwt_required()
def get_invoices():
    """
    Gibt alle Rechnungen zurück
    """
    invoices = Invoice.query.all()
    return jsonify(invoices_schema.dump(invoices)), 200

@invoices_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_invoice(id):
    """
    Gibt eine Rechnung anhand ihrer ID zurück
    """
    invoice = Invoice.query.get_or_404(id)
    return jsonify(invoice_schema.dump(invoice)), 200

@invoices_bp.route('', methods=['POST'])
@jwt_required()
def create_invoice():
    """
    Erstellt eine neue Rechnung
    """
    data = request.get_json()
    
    # Validiere die Daten mit dem Schema
    errors = invoice_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    # Prüfe, ob der Kunde existiert
    customer = Customer.query.get(data.get('customer_id'))
    if not customer:
        return jsonify({"error": "Kunde nicht gefunden"}), 404
    
    # Generiere Rechnungsnummer, falls nicht angegeben
    if not data.get('invoice_number'):
        # Format: JAHR-MONAT-LAUFENDE_NUMMER
        today = datetime.now()
        prefix = f"{today.year}-{today.month:02d}-"
        last_invoice = Invoice.query.filter(
            Invoice.invoice_number.like(f"{prefix}%")
        ).order_by(Invoice.invoice_number.desc()).first()
        
        if last_invoice:
            last_number = int(last_invoice.invoice_number.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        
        invoice_number = f"{prefix}{new_number:04d}"
    else:
        invoice_number = data.get('invoice_number')
    
    # Setze Standardwerte für Datumsfelder, falls nicht angegeben
    today = datetime.now().date()
    invoice_date = data.get('invoice_date', today)
    due_date = data.get('due_date', today + timedelta(days=14))
    delivery_date = data.get('delivery_date', today)
    
    # Erstelle neue Rechnung
    new_invoice = Invoice(
        invoice_number=invoice_number,
        customer_id=data.get('customer_id'),
        invoice_date=invoice_date,
        due_date=due_date,
        delivery_date=delivery_date,
        status=data.get('status', 'erstellt'),
        payment_status=data.get('payment_status', 'offen'),
        payment_method=data.get('payment_method'),
        notes=data.get('notes'),
        terms=data.get('terms'),
        is_recurring=data.get('is_recurring', False),
        original_invoice_id=data.get('original_invoice_id')
    )
    
    db.session.add(new_invoice)
    db.session.flush()  # Um die invoice_id zu erhalten
    
    # Füge Rechnungspositionen hinzu, falls vorhanden
    if 'items' in data and isinstance(data['items'], list):
        for i, item_data in enumerate(data['items']):
            # Prüfe, ob der Artikel existiert, falls eine item_id angegeben ist
            item = None
            if 'item_id' in item_data and item_data['item_id']:
                item = Item.query.get(item_data['item_id'])
                if not item:
                    return jsonify({"error": f"Artikel mit ID {item_data['item_id']} nicht gefunden"}), 404
            
            # Erstelle Rechnungsposition
            invoice_item = InvoiceItem(
                invoice_id=new_invoice.invoice_id,
                item_id=item.item_id if item else None,
                position=i + 1,
                quantity=item_data.get('quantity', 1),
                unit=item_data.get('unit', item.unit if item else 'Stück'),
                price_net=item_data.get('price_net', item.price_net if item else 0),
                vat_rate=item_data.get('vat_rate', item.vat_rate if item else 19.0),
                description=item_data.get('description', item.description if item else '')
            )
            
            # Berechne Gesamtbeträge
            invoice_item.calculate_totals()
            
            db.session.add(invoice_item)
    
    # Berechne Gesamtbeträge der Rechnung
    new_invoice.calculate_totals()
    
    db.session.commit()
    
    return jsonify(invoice_schema.dump(new_invoice)), 201

@invoices_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_invoice(id):
    """
    Aktualisiert eine bestehende Rechnung
    """
    invoice = Invoice.query.get_or_404(id)
    
    # Stornierte Rechnungen können nicht bearbeitet werden
    if invoice.is_cancelled:
        return jsonify({"error": "Stornierte Rechnungen können nicht bearbeitet werden"}), 400
    
    data = request.get_json()
    
    # Validiere die Daten mit dem Schema
    errors = invoice_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    # Aktualisiere Rechnungsdaten
    invoice.invoice_number = data.get('invoice_number', invoice.invoice_number)
    invoice.customer_id = data.get('customer_id', invoice.customer_id)
    invoice.invoice_date = data.get('invoice_date', invoice.invoice_date)
    invoice.due_date = data.get('due_date', invoice.due_date)
    invoice.delivery_date = data.get('delivery_date', invoice.delivery_date)
    invoice.status = data.get('status', invoice.status)
    invoice.payment_status = data.get('payment_status', invoice.payment_status)
    invoice.payment_method = data.get('payment_method', invoice.payment_method)
    invoice.notes = data.get('notes', invoice.notes)
    invoice.terms = data.get('terms', invoice.terms)
    invoice.is_recurring = data.get('is_recurring', invoice.is_recurring)
    
    # Aktualisiere Rechnungspositionen, falls vorhanden
    if 'items' in data and isinstance(data['items'], list):
        # Lösche bestehende Positionen
        InvoiceItem.query.filter_by(invoice_id=invoice.invoice_id).delete()
        
        # Füge neue Positionen hinzu
        for i, item_data in enumerate(data['items']):
            # Prüfe, ob der Artikel existiert, falls eine item_id angegeben ist
            item = None
            if 'item_id' in item_data and item_data['item_id']:
                item = Item.query.get(item_data['item_id'])
            
            # Erstelle Rechnungsposition
            invoice_item = InvoiceItem(
                invoice_id=invoice.invoice_id,
                item_id=item.item_id if item else None,
                position=i + 1,
                quantity=item_data.get('quantity', 1),
                unit=item_data.get('unit', item.unit if item else 'Stück'),
                price_net=item_data.get('price_net', item.price_net if item else 0),
                vat_rate=item_data.get('vat_rate', item.vat_rate if item else 19.0),
                description=item_data.get('description', item.description if item else '')
            )
            
            # Berechne Gesamtbeträge
            invoice_item.calculate_totals()
            
            db.session.add(invoice_item)
    
    # Berechne Gesamtbeträge der Rechnung
    invoice.calculate_totals()
    
    db.session.commit()
    
    return jsonify(invoice_schema.dump(invoice)), 200

@invoices_bp.route('/<int:id>/cancel', methods=['POST'])
@jwt_required()
def cancel_invoice(id):
    """
    Storniert eine Rechnung und erstellt eine Stornorechnung
    """
    invoice = Invoice.query.get_or_404(id)
    
    # Bereits stornierte Rechnungen können nicht erneut storniert werden
    if invoice.is_cancelled:
        return jsonify({"error": "Rechnung wurde bereits storniert"}), 400
    
    data = request.get_json() or {}
    
    # Markiere die Originalrechnung als storniert
    invoice.is_cancelled = True
    invoice.cancellation_date = datetime.now().date()
    invoice.cancellation_reason = data.get('reason', 'Keine Angabe')
    invoice.status = 'storniert'
    
    # Erstelle eine Stornorechnung
    storno_invoice = Invoice(
        invoice_number=f"STORNO-{invoice.invoice_number}",
        customer_id=invoice.customer_id,
        invoice_date=datetime.now().date(),
        due_date=datetime.now().date(),
        delivery_date=invoice.delivery_date,
        status='erstellt',
        payment_status='offen',
        payment_method=invoice.payment_method,
        notes=f"Stornorechnung zu Rechnung {invoice.invoice_number}",
        terms=invoice.terms,
        is_cancelled=False,
        original_invoice_id=invoice.invoice_id
    )
    
    db.session.add(storno_invoice)
    db.session.flush()  # Um die invoice_id zu erhalten
    
    # Kopiere die Rechnungspositionen mit negativen Beträgen
    for item in invoice.items:
        storno_item = InvoiceItem(
            invoice_id=storno_invoice.invoice_id,
            item_id=item.item_id,
            position=item.position,
            quantity=-item.quantity,  # Negative Menge für Storno
            unit=item.unit,
            price_net=item.price_net,
            vat_rate=item.vat_rate,
            description=item.description
        )
        
        # Berechne Gesamtbeträge (werden automatisch negativ durch negative Menge)
        storno_item.calculate_totals()
        
        db.session.add(storno_item)
    
    # Berechne Gesamtbeträge der Stornorechnung
    storno_invoice.calculate_totals()
    
    db.session.commit()
    
    return jsonify({
        "message": "Rechnung erfolgreich storniert",
        "original_invoice": invoice_schema.dump(invoice),
        "storno_invoice": invoice_schema.dump(storno_invoice)
    }), 200

@invoices_bp.route('/search', methods=['GET'])
@jwt_required()
def search_invoices():
    """
    Sucht nach Rechnungen basierend auf verschiedenen Kriterien
    """
    # Suchparameter
    invoice_number = request.args.get('invoice_number', '')
    customer_id = request.args.get('customer_id')
    status = request.args.get('status')
    payment_status = request.args.get('payment_status')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Basisabfrage
    query = Invoice.query
    
    # Filtere nach Rechnungsnummer
    if invoice_number:
        query = query.filter(Invoice.invoice_number.ilike(f'%{invoice_number}%'))
    
    # Filtere nach Kunde
    if customer_id:
        query = query.filter(Invoice.customer_id == customer_id)
    
    # Filtere nach Status
    if status:
        query = query.filter(Invoice.status == status)
    
    # Filtere nach Zahlungsstatus
    if payment_status:
        query = query.filter(Invoice.payment_status == payment_status)
    
    # Filtere nach Datumsbereich
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(Invoice.invoice_date >= date_from)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(Invoice.invoice_date <= date_to)
        except ValueError:
            pass
    
    # Führe die Abfrage aus
    invoices = query.all()
    
    return jsonify(invoices_schema.dump(invoices)), 200
