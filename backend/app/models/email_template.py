from datetime import datetime
from app import db

class EmailTemplate(db.Model):
    """
    Modell für E-Mail-Vorlagen
    """
    __tablename__ = 'email_templates'
    
    template_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Beziehungen
    email_logs = db.relationship('EmailLog', backref='template', lazy=True)
    
    def __repr__(self):
        return f'<EmailTemplate {self.name}>'


class EmailLog(db.Model):
    """
    Modell für E-Mail-Protokolleinträge
    """
    __tablename__ = 'email_logs'
    
    log_id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.invoice_id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'))
    template_id = db.Column(db.Integer, db.ForeignKey('email_templates.template_id'))
    sent_date = db.Column(db.DateTime, default=datetime.utcnow)
    recipient = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='gesendet')  # gesendet, fehlgeschlagen
    error_message = db.Column(db.Text)
    
    def __repr__(self):
        return f'<EmailLog {self.log_id} for Invoice {self.invoice_id}>'
