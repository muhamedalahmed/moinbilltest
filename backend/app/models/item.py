from datetime import datetime
from app import db

class Item(db.Model):
    """
    Modell für Artikel/Leistungen in der Buchhaltungssoftware
    """
    __tablename__ = 'items'
    
    item_id = db.Column(db.Integer, primary_key=True)
    item_number = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    unit = db.Column(db.String(50), default='Stück')
    price_net = db.Column(db.Numeric(10, 2), nullable=False)
    vat_rate = db.Column(db.Numeric(5, 2), nullable=False, default=19.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Beziehungen
    invoice_items = db.relationship('InvoiceItem', backref='item', lazy=True)
    recurring_invoice_items = db.relationship('RecurringInvoiceItem', backref='item', lazy=True)
    
    def __repr__(self):
        return f'<Item {self.name}>'
    
    @property
    def price_gross(self):
        """
        Berechnet den Bruttopreis (inkl. Mehrwertsteuer)
        """
        return float(self.price_net) * (1 + float(self.vat_rate) / 100)
    
    @property
    def vat_amount(self):
        """
        Berechnet den Mehrwertsteuerbetrag
        """
        return float(self.price_net) * (float(self.vat_rate) / 100)
