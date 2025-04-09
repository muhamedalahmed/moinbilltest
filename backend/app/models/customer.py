from datetime import datetime
from app import db

class Customer(db.Model):
    """
    Kundenmodell für die Buchhaltungssoftware
    """
    __tablename__ = 'customers'
    
    customer_id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(255))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    street = db.Column(db.String(255))
    house_number = db.Column(db.String(20))
    postal_code = db.Column(db.String(20))
    city = db.Column(db.String(100))
    country = db.Column(db.String(100), default='Deutschland')
    tax_id = db.Column(db.String(50))
    vat_id = db.Column(db.String(50))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Beziehungen
    invoices = db.relationship('Invoice', backref='customer', lazy=True)
    recurring_invoices = db.relationship('RecurringInvoice', backref='customer', lazy=True)
    
    def __repr__(self):
        return f'<Customer {self.company_name or self.last_name}>'
    
    @property
    def full_name(self):
        """
        Gibt den vollständigen Namen des Kunden zurück
        """
        if self.company_name:
            return self.company_name
        else:
            return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def full_address(self):
        """
        Gibt die vollständige Adresse des Kunden zurück
        """
        return f"{self.street} {self.house_number}, {self.postal_code} {self.city}, {self.country}"
