from datetime import datetime
from app import db

class CompanyData(db.Model):
    """
    Modell für die eigenen Unternehmensdaten
    """
    __tablename__ = 'company_data'
    
    company_id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(255), nullable=False)
    legal_form = db.Column(db.String(50))
    street = db.Column(db.String(255), nullable=False)
    house_number = db.Column(db.String(20), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), default='Deutschland')
    tax_id = db.Column(db.String(50), nullable=False)
    vat_id = db.Column(db.String(50))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    website = db.Column(db.String(255))
    bank_name = db.Column(db.String(255))
    iban = db.Column(db.String(50))
    bic = db.Column(db.String(20))
    logo_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<CompanyData {self.company_name}>'
    
    @property
    def full_address(self):
        """
        Gibt die vollständige Adresse des Unternehmens zurück
        """
        return f"{self.street} {self.house_number}, {self.postal_code} {self.city}, {self.country}"
