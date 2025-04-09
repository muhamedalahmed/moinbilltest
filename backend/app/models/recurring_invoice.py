from datetime import datetime
from app import db

class RecurringInvoice(db.Model):
    """
    Modell für Intervallrechnungen (wiederkehrende Rechnungen)
    """
    __tablename__ = 'recurring_invoices'
    
    recurring_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)  # Optional, für unbefristete Intervalle leer
    interval_type = db.Column(db.String(20), nullable=False)  # monatlich, quartalsweise, halbjährlich, jährlich
    interval_value = db.Column(db.Integer, default=1)  # z.B. 1 für jeden Monat, 3 für alle 3 Monate
    next_invoice_date = db.Column(db.Date, nullable=False)
    last_invoice_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='aktiv')  # aktiv, pausiert, beendet
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Beziehungen
    items = db.relationship('RecurringInvoiceItem', backref='recurring_invoice', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<RecurringInvoice {self.recurring_id} for Customer {self.customer_id}>'
    
    def is_active(self):
        """
        Prüft, ob die Intervallrechnung aktiv ist
        """
        return self.status == 'aktiv' and (self.end_date is None or self.end_date >= datetime.now().date())


class RecurringInvoiceItem(db.Model):
    """
    Modell für Positionen auf Intervallrechnungen
    """
    __tablename__ = 'recurring_invoice_items'
    
    recurring_item_id = db.Column(db.Integer, primary_key=True)
    recurring_id = db.Column(db.Integer, db.ForeignKey('recurring_invoices.recurring_id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.item_id'))
    position = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Numeric(10, 2), nullable=False, default=1.0)
    unit = db.Column(db.String(50), default='Stück')
    price_net = db.Column(db.Numeric(10, 2), nullable=False)
    vat_rate = db.Column(db.Numeric(5, 2), nullable=False, default=19.0)
    description = db.Column(db.Text)
    
    def __repr__(self):
        return f'<RecurringInvoiceItem {self.position} on RecurringInvoice {self.recurring_id}>'
    
    def calculate_totals(self):
        """
        Berechnet die Gesamtbeträge der Position
        """
        total_net = float(self.quantity) * float(self.price_net)
        total_vat = total_net * (float(self.vat_rate) / 100)
        total_gross = total_net + total_vat
        
        return {
            'total_net': total_net,
            'total_vat': total_vat,
            'total_gross': total_gross
        }
