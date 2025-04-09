from flask import Blueprint, request, jsonify, send_file
from app.models.invoice import Invoice
from app.schemas.invoice_schema import invoice_schema
from app import db
from flask_jwt_extended import jwt_required
from app.services.pdf_service import generate_invoice_pdf
import os
import tempfile

pdf_bp = Blueprint('pdf', __name__)

@pdf_bp.route('/invoices/<int:id>/pdf', methods=['GET'])
@jwt_required()
def generate_invoice_pdf_endpoint(id):
    """
    Generiert eine PDF-Datei für eine Rechnung
    """
    invoice = Invoice.query.get_or_404(id)
    
    # Temporäre Datei für die PDF erstellen
    fd, path = tempfile.mkstemp(suffix='.pdf')
    os.close(fd)
    
    # PDF generieren
    generate_invoice_pdf(invoice, path)
    
    # PDF als Datei zurückgeben
    return send_file(
        path,
        as_attachment=True,
        download_name=f"Rechnung_{invoice.invoice_number}.pdf",
        mimetype='application/pdf'
    )

@pdf_bp.route('/invoices/<int:id>/preview', methods=['GET'])
@jwt_required()
def preview_invoice_pdf(id):
    """
    Generiert eine Vorschau der PDF-Datei für eine Rechnung
    """
    invoice = Invoice.query.get_or_404(id)
    
    # Temporäre Datei für die PDF erstellen
    fd, path = tempfile.mkstemp(suffix='.pdf')
    os.close(fd)
    
    # PDF generieren
    generate_invoice_pdf(invoice, path)
    
    # PDF als Datei zurückgeben (nicht als Anhang)
    return send_file(
        path,
        as_attachment=False,
        mimetype='application/pdf'
    )
