from flask import Blueprint, request, jsonify
from app.models.recurring_invoice import RecurringInvoice, RecurringInvoiceItem
from app.models.invoice import Invoice, InvoiceItem
from app.models.customer import Customer
from app.models.item import Item
from app.schemas.recurring_invoice_schema import recurring_invoice_schema, recurring_invoices_schema
from app.schemas.invoice_schema import invoice_schema
from app import db
from flask_jwt_extended import jwt_required
from datetime import datetime, timedelta
import calendar

recurring_invoices_bp = Blueprint('recurring_invoices', __name__)

@recurring_invoices_bp.route('', methods=['GET'])
@jwt_required()
def get_recurring_invoices():
    """
    Gibt alle Intervallrechnungen zurück
    """
    recurring_invoices = RecurringInvoice.query.all()
    return jsonify(recurring_invoices_schema.dump(recurring_invoices)), 200

@recurring_invoices_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_recurring_invoice(id):
    """
    Gibt eine Intervallrechnung anhand ihrer ID zurück
    """
    recurring_invoice = RecurringInvoice.query.get_or_404(id)
    return jsonify(recurring_invoice_schema.dump(recurring_invoice)), 200

@recurring_invoices_bp.route('', methods=['POST'])
@jwt_required()
def create_recurring_invoice():
    """
    Erstellt eine neue Intervallrechnung
    """
    data = request.get_json()
    
    # Validiere die Daten mit dem Schema
    errors = recurring_invoice_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    # Prüfe, ob der Kunde existiert
    customer = Customer.query.get(data.get('customer_id'))
    if not customer:
        return jsonify({"error": "Kunde nicht gefunden"}), 404
    
    # Erstelle neue Intervallrechnung
    new_recurring_invoice = RecurringInvoice(
        customer_id=data.get('customer_id'),
        start_date=data.get('start_date'),
        end_date=data.get('end_date'),
        interval_type=data.get('interval_type'),
        interval_value=data.get('interval_value', 1),
        next_invoice_date=data.get('next_invoice_date'),
        status=data.get('status', 'aktiv'),
        notes=data.get('notes')
    )
    
    db.session.add(new_recurring_invoice)
    db.session.flush()  # Um die recurring_id zu erhalten
    
    # Füge Positionen hinzu, falls vorhanden
    if 'items' in data and isinstance(data['items'], list):
        for i, item_data in enumerate(data['items']):
            # Prüfe, ob der Artikel existiert, falls eine item_id angegeben ist
            item = None
            if 'item_id' in item_data and item_data['item_id']:
                item = Item.query.get(item_data['item_id'])
                if not item:
                    return jsonify({"error": f"Artikel mit ID {item_data['item_id']} nicht gefunden"}), 404
            
            # Erstelle Position
            recurring_item = RecurringInvoiceItem(
                recurring_id=new_recurring_invoice.recurring_id,
                item_id=item.item_id if item else None,
                position=i + 1,
                quantity=item_data.get('quantity', 1),
                unit=item_data.get('unit', item.unit if item else 'Stück'),
                price_net=item_data.get('price_net', item.price_net if item else 0),
                vat_rate=item_data.get('vat_rate', item.vat_rate if item else 19.0),
                description=item_data.get('description', item.description if item else '')
            )
            
            db.session.add(recurring_item)
    
    db.session.commit()
    
    return jsonify(recurring_invoice_schema.dump(new_recurring_invoice)), 201

@recurring_invoices_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_recurring_invoice(id):
    """
    Aktualisiert eine bestehende Intervallrechnung
    """
    recurring_invoice = RecurringInvoice.query.get_or_404(id)
    data = request.get_json()
    
    # Validiere die Daten mit dem Schema
    errors = recurring_invoice_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    # Aktualisiere Daten
    recurring_invoice.customer_id = data.get('customer_id', recurring_invoice.customer_id)
    recurring_invoice.start_date = data.get('start_date', recurring_invoice.start_date)
    recurring_invoice.end_date = data.get('end_date', recurring_invoice.end_date)
    recurring_invoice.interval_type = data.get('interval_type', recurring_invoice.interval_type)
    recurring_invoice.interval_value = data.get('interval_value', recurring_invoice.interval_value)
    recurring_invoice.next_invoice_date = data.get('next_invoice_date', recurring_invoice.next_invoice_date)
    recurring_invoice.status = data.get('status', recurring_invoice.status)
    recurring_invoice.notes = data.get('notes', recurring_invoice.notes)
    
    # Aktualisiere Positionen, falls vorhanden
    if 'items' in data and isinstance(data['items'], list):
        # Lösche bestehende Positionen
        RecurringInvoiceItem.query.filter_by(recurring_id=recurring_invoice.recurring_id).delete()
        
        # Füge neue Positionen hinzu
        for i, item_data in enumerate(data['items']):
            # Prüfe, ob der Artikel existiert, falls eine item_id angegeben ist
            item = None
            if 'item_id' in item_data and item_data['item_id']:
                item = Item.query.get(item_data['item_id'])
            
            # Erstelle Position
            recurring_item = RecurringInvoiceItem(
                recurring_id=recurring_invoice.recurring_id,
                item_id=item.item_id if item else None,
                position=i + 1,
                quantity=item_data.get('quantity', 1),
                unit=item_data.get('unit', item.unit if item else 'Stück'),
                price_net=item_data.get('price_net', item.price_net if item else 0),
                vat_rate=item_data.get('vat_rate', item.vat_rate if item else 19.0),
                description=item_data.get('description', item.description if item else '')
            )
            
            db.session.add(recurring_item)
    
    db.session.commit()
    
    return jsonify(recurring_invoice_schema.dump(recurring_invoice)), 200

@recurring_invoices_bp.route('/<int:id>/generate-invoice', methods=['POST'])
@jwt_required()
def generate_invoice(id):
    """
    Generiert eine Rechnung aus einer Intervallrechnung
    """
    recurring_invoice = RecurringInvoice.query.get_or_404(id)
    
    # Prüfe, ob die Intervallrechnung aktiv ist
    if recurring_invoice.status != 'aktiv':
        return jsonify({"error": "Intervallrechnung ist nicht aktiv"}), 400
    
    # Prüfe, ob das Enddatum erreicht ist
    if recurring_invoice.end_date and recurring_invoice.end_date < datetime.now().date():
        return jsonify({"error": "Intervallrechnung ist abgelaufen"}), 400
    
    # Generiere Rechnungsnummer
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
    
    # Erstelle neue Rechnung
    new_invoice = Invoice(
        invoice_number=invoice_number,
        customer_id=recurring_invoice.customer_id,
        invoice_date=datetime.now().date(),
        due_date=datetime.now().date() + timedelta(days=14),
        delivery_date=datetime.now().date(),
        status='erstellt',
        payment_status='offen',
        notes=f"Automatisch generiert aus Intervallrechnung {recurring_invoice.recurring_id}",
        is_recurring=True
    )
    
    db.session.add(new_invoice)
    db.session.flush()  # Um die invoice_id zu erhalten
    
    # Kopiere Positionen
    for item in recurring_invoice.items:
        invoice_item = InvoiceItem(
            invoice_id=new_invoice.invoice_id,
            item_id=item.item_id,
            position=item.position,
            quantity=item.quantity,
            unit=item.unit,
            price_net=item.price_net,
            vat_rate=item.vat_rate,
            description=item.description
        )
        
        # Berechne Gesamtbeträge
        invoice_item.calculate_totals()
        
        db.session.add(invoice_item)
    
    # Berechne Gesamtbeträge der Rechnung
    new_invoice.calculate_totals()
    
    # Aktualisiere Intervallrechnung
    recurring_invoice.last_invoice_date = datetime.now().date()
    
    # Berechne nächstes Rechnungsdatum
    if recurring_invoice.interval_type == 'monatlich':
        next_date = add_months(recurring_invoice.next_invoice_date, recurring_invoice.interval_value)
    elif recurring_invoice.interval_type == 'quartalsweise':
        next_date = add_months(recurring_invoice.next_invoice_date, 3 * recurring_invoice.interval_value)
    elif recurring_invoice.interval_type == 'halbjährlich':
        next_date = add_months(recurring_invoice.next_invoice_date, 6 * recurring_invoice.interval_value)
    elif recurring_invoice.interval_type == 'jährlich':
        next_date = add_months(recurring_invoice.next_invoice_date, 12 * recurring_invoice.interval_value)
    else:
        next_date = recurring_invoice.next_invoice_date + timedelta(days=30 * recurring_invoice.interval_value)
    
    recurring_invoice.next_invoice_date = next_date
    
    db.session.commit()
    
    return jsonify({
        "message": "Rechnung erfolgreich generiert",
        "invoice": invoice_schema.dump(new_invoice),
        "next_invoice_date": recurring_invoice.next_invoice_date.isoformat()
    }), 201

@recurring_invoices_bp.route('/<int:id>/status', methods=['PUT'])
@jwt_required()
def update_status(id):
    """
    Aktualisiert den Status einer Intervallrechnung
    """
    recurring_invoice = RecurringInvoice.query.get_or_404(id)
    data = request.get_json()
    
    if 'status' not in data:
        return jsonify({"error": "Status muss angegeben werden"}), 400
    
    status = data.get('status')
    if status not in ['aktiv', 'pausiert', 'beendet']:
        return jsonify({"error": "Ungültiger Status. Erlaubte Werte: aktiv, pausiert, beendet"}), 400
    
    recurring_invoice.status = status
    
    # Wenn die Intervallrechnung beendet wird, setze das Enddatum auf heute
    if status == 'beendet' and not recurring_invoice.end_date:
        recurring_invoice.end_date = datetime.now().date()
    
    db.session.commit()
    
    return jsonify({
        "message": f"Status erfolgreich auf '{status}' aktualisiert",
        "recurring_invoice": recurring_invoice_schema.dump(recurring_invoice)
    }), 200

@recurring_invoices_bp.route('/check-due', methods=['GET'])
@jwt_required()
def check_due_invoices():
    """
    Prüft, welche Intervallrechnungen fällig sind und generiert Rechnungen
    """
    today = datetime.now().date()
    
    # Finde alle aktiven Intervallrechnungen, die fällig sind
    due_recurring_invoices = RecurringInvoice.query.filter(
        RecurringInvoice.status == 'aktiv',
        RecurringInvoice.next_invoice_date <= today,
        (RecurringInvoice.end_date.is_(None) | (RecurringInvoice.end_date >= today))
    ).all()
    
    generated_invoices = []
    
    for recurring_invoice in due_recurring_invoices:
        # Generiere Rechnungsnummer
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
        
        # Erstelle neue Rechnung
        new_invoice = Invoice(
            invoice_number=invoice_number,
            customer_id=recurring_invoice.customer_id,
            invoice_date=today,
            due_date=today + timedelta(days=14),
            delivery_date=today,
            status='erstellt',
            payment_status='offen',
            notes=f"Automatisch generiert aus Intervallrechnung {recurring_invoice.recurring_id}",
            is_recurring=True
        )
        
        db.session.add(new_invoice)
        db.session.flush()  # Um die invoice_id zu erhalten
        
        # Kopiere Positionen
        for item in recurring_invoice.items:
            invoice_item = InvoiceItem(
                invoice_id=new_invoice.invoice_id,
                item_id=item.item_id,
                position=item.position,
                quantity=item.quantity,
                unit=item.unit,
                price_net=item.price_net,
                vat_rate=item.vat_rate,
                description=item.description
            )
            
            # Berechne Gesamtbeträge
            invoice_item.calculate_totals()
            
            db.session.add(invoice_item)
        
        # Berechne Gesamtbeträge der Rechnung
        new_invoice.calculate_totals()
        
        # Aktualisiere Intervallrechnung
        recurring_invoice.last_invoice_date = today
        
        # Berechne nächstes Rechnungsdatum
        if recurring_invoice.interval_type == 'monatlich':
            next_date = add_months(recurring_invoice.next_invoice_date, recurring_invoice.interval_value)
        elif recurring_invoice.interval_type == 'quartalsweise':
            next_date = add_months(recurring_invoice.next_invoice_date, 3 * recurring_invoice.interval_value)
        elif recurring_invoice.interval_type == 'halbjährlich':
            next_date = add_months(recurring_invoice.next_invoice_date, 6 * recurring_invoice.interval_value)
        elif recurring_invoice.interval_type == 'jährlich':
            next_date = add_months(recurring_invoice.next_invoice_date, 12 * recurring_invoice.interval_value)
        else:
            next_date = recurring_invoice.next_invoice_date + timedelta(days=30 * recurring_invoice.interval_value)
        
        recurring_invoice.next_invoice_date = next_date
        
        generated_invoices.append({
            "recurring_invoice_id": recurring_invoice.recurring_id,
            "invoice_id": new_invoice.invoice_id,
            "invoice_number": new_invoice.invoice_number,
            "next_invoice_date": next_date.isoformat()
        })
    
    db.session.commit()
    
    return jsonify({
        "message": f"{len(generated_invoices)} Rechnungen generiert",
        "generated_invoices": generated_invoices
    }), 200

def add_months(sourcedate, months):
    """
    Hilfsfunktion zum Hinzufügen von Monaten zu einem Datum
    """
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime(year, month, day).date()
