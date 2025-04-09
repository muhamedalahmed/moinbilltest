from app import db
from app.models.recurring_invoice import RecurringInvoice
from app.models.invoice import Invoice, InvoiceItem
from datetime import datetime, timedelta
import calendar
import logging

# Konfiguriere Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_and_generate_recurring_invoices():
    """
    Überprüft, welche Intervallrechnungen fällig sind und generiert entsprechende Rechnungen
    """
    logger.info("Starte Überprüfung der fälligen Intervallrechnungen")
    today = datetime.now().date()
    
    # Finde alle aktiven Intervallrechnungen, die fällig sind
    due_recurring_invoices = RecurringInvoice.query.filter(
        RecurringInvoice.status == 'aktiv',
        RecurringInvoice.next_invoice_date <= today,
        (RecurringInvoice.end_date.is_(None) | (RecurringInvoice.end_date >= today))
    ).all()
    
    logger.info(f"Gefunden: {len(due_recurring_invoices)} fällige Intervallrechnungen")
    
    generated_invoices = []
    
    for recurring_invoice in due_recurring_invoices:
        try:
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
            
            logger.info(f"Rechnung {invoice_number} für Intervallrechnung {recurring_invoice.recurring_id} erstellt")
        
        except Exception as e:
            logger.error(f"Fehler bei der Generierung der Rechnung für Intervallrechnung {recurring_invoice.recurring_id}: {str(e)}")
            db.session.rollback()
    
    db.session.commit()
    logger.info(f"Insgesamt {len(generated_invoices)} Rechnungen generiert")
    
    return generated_invoices

def add_months(sourcedate, months):
    """
    Hilfsfunktion zum Hinzufügen von Monaten zu einem Datum
    """
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime(year, month, day).date()

def create_recurring_invoice(customer_id, start_date, interval_type, interval_value=1, end_date=None, items=None):
    """
    Erstellt eine neue Intervallrechnung
    
    Args:
        customer_id: ID des Kunden
        start_date: Startdatum
        interval_type: Art des Intervalls (monatlich, quartalsweise, halbjährlich, jährlich)
        interval_value: Wert des Intervalls (z.B. 1 für jeden Monat, 3 für alle 3 Monate)
        end_date: Enddatum (optional)
        items: Liste der Rechnungspositionen
        
    Returns:
        Die erstellte Intervallrechnung
    """
    # Erstelle neue Intervallrechnung
    recurring_invoice = RecurringInvoice(
        customer_id=customer_id,
        start_date=start_date,
        end_date=end_date,
        interval_type=interval_type,
        interval_value=interval_value,
        next_invoice_date=start_date,
        status='aktiv'
    )
    
    db.session.add(recurring_invoice)
    db.session.flush()  # Um die recurring_id zu erhalten
    
    # Füge Positionen hinzu, falls vorhanden
    if items:
        for i, item_data in enumerate(items):
            from app.models.recurring_invoice import RecurringInvoiceItem
            
            # Erstelle Position
            recurring_item = RecurringInvoiceItem(
                recurring_id=recurring_invoice.recurring_id,
                item_id=item_data.get('item_id'),
                position=i + 1,
                quantity=item_data.get('quantity', 1),
                unit=item_data.get('unit', 'Stück'),
                price_net=item_data.get('price_net'),
                vat_rate=item_data.get('vat_rate', 19.0),
                description=item_data.get('description', '')
            )
            
            db.session.add(recurring_item)
    
    db.session.commit()
    
    return recurring_invoice

def update_recurring_invoice_status(recurring_id, status):
    """
    Aktualisiert den Status einer Intervallrechnung
    
    Args:
        recurring_id: ID der Intervallrechnung
        status: Neuer Status (aktiv, pausiert, beendet)
        
    Returns:
        Die aktualisierte Intervallrechnung oder None, wenn nicht gefunden
    """
    recurring_invoice = RecurringInvoice.query.get(recurring_id)
    if not recurring_invoice:
        return None
    
    recurring_invoice.status = status
    
    # Wenn die Intervallrechnung beendet wird, setze das Enddatum auf heute
    if status == 'beendet' and not recurring_invoice.end_date:
        recurring_invoice.end_date = datetime.now().date()
    
    db.session.commit()
    
    return recurring_invoice
