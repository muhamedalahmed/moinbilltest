from datetime import datetime
from app import db

class Invoice(db.Model):
    """
    Rechnungsmodell für die Buchhaltungssoftware
    """
    __tablename__ = 'invoices'
    
    invoice_id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'), nullable=False)
    invoice_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    due_date = db.Column(db.Date, nullable=False)
    delivery_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='erstellt')  # erstellt, versendet, bezahlt, storniert
    payment_status = db.Column(db.String(20), default='offen')  # offen, teilweise bezahlt, vollständig bezahlt
    payment_method = db.Column(db.String(50))
    total_net = db.Column(db.Numeric(10, 2), default=0.0)
    total_vat = db.Column(db.Numeric(10, 2), default=0.0)
    total_gross = db.Column(db.Numeric(10, 2), default=0.0)
    notes = db.Column(db.Text)
    terms = db.Column(db.Text)
    is_cancelled = db.Column(db.Boolean, default=False)
    cancellation_date = db.Column(db.Date)
    cancellation_reason = db.Column(db.Text)
    original_invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.invoice_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_recurring = db.Column(db.Boolean, default=False)
    email_sent = db.Column(db.Boolean, default=False)
    email_sent_date = db.Column(db.DateTime)
    
    # Beziehungen
    items = db.relationship('InvoiceItem', backref='invoice', lazy=True, cascade="all, delete-orphan")
    payments = db.relationship('Payment', backref='invoice', lazy=True)
    original_invoice = db.relationship('Invoice', remote_side=[invoice_id], backref='cancellation_invoices')
    
    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'
    
    def calculate_totals(self):
        """
        Berechnet die Gesamtbeträge der Rechnung
        """
        self.total_net = sum(item.total_net for item in self.items)
        self.total_vat = sum(item.total_vat for item in self.items)
        self.total_gross = sum(item.total_gross for item in self.items)
        
    def is_paid(self):
        """
        Prüft, ob die Rechnung vollständig bezahlt ist
        """
        paid_amount = sum(payment.amount for payment in self.payments)
        return paid_amount >= self.total_gross
    
    def update_payment_status(self):
        """
        Aktualisiert den Zahlungsstatus basierend auf den eingegangenen Zahlungen
        """
        paid_amount = sum(payment.amount for payment in self.payments)
        
        if paid_amount <= 0:
            self.payment_status = 'offen'
        elif paid_amount < self.total_gross:
            self.payment_status = 'teilweise bezahlt'
        else:
            self.payment_status = 'vollständig bezahlt'


class InvoiceItem(db.Model):
    """
    Modell für Rechnungspositionen
    """
    __tablename__ = 'invoice_items'
    
    invoice_item_id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.invoice_id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.item_id'))
    position = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Numeric(10, 2), nullable=False, default=1.0)
    unit = db.Column(db.String(50), default='Stück')
    price_net = db.Column(db.Numeric(10, 2), nullable=False)
    vat_rate = db.Column(db.Numeric(5, 2), nullable=False, default=19.0)
    total_net = db.Column(db.Numeric(10, 2), nullable=False)
    total_vat = db.Column(db.Numeric(10, 2), nullable=False)
    total_gross = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text)
    
    def __repr__(self):
        return f'<InvoiceItem {self.position} on Invoice {self.invoice_id}>'
    
    def calculate_totals(self):
        """
        Berechnet die Gesamtbeträge der Rechnungsposition
        """
        self.total_net = float(self.quantity) * float(self.price_net)
        self.total_vat = self.total_net * (float(self.vat_rate) / 100)
        self.total_gross = self.total_net + self.total_vat
