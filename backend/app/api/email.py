from flask import Blueprint, request, jsonify
from app.models.invoice import Invoice
from app.models.email_template import EmailTemplate, EmailLog
from app.schemas.email_template_schema import email_log_schema, email_logs_schema
from app import db
from flask_jwt_extended import jwt_required
from app.services.email_service import send_invoice_email

email_bp = Blueprint('email', __name__)

@email_bp.route('/invoices/<int:id>/send', methods=['POST'])
@jwt_required()
def send_invoice(id):
    """
    Sendet eine Rechnung per E-Mail
    """
    invoice = Invoice.query.get_or_404(id)
    data = request.get_json() or {}
    
    # Prüfe, ob der Kunde eine E-Mail-Adresse hat
    if not invoice.customer.email and 'recipient' not in data:
        return jsonify({
            "error": "Kunde hat keine E-Mail-Adresse und kein alternativer Empfänger angegeben"
        }), 400
    
    # Sende E-Mail
    result = send_invoice_email(
        invoice_id=invoice.invoice_id,
        template_id=data.get('template_id'),
        custom_subject=data.get('subject'),
        custom_body=data.get('body'),
        recipient=data.get('recipient')
    )
    
    if result["success"]:
        return jsonify(result), 200
    else:
        return jsonify({"error": result["error"]}), 500

@email_bp.route('/logs', methods=['GET'])
@jwt_required()
def get_email_logs():
    """
    Gibt alle E-Mail-Protokolleinträge zurück
    """
    # Optionale Filter
    invoice_id = request.args.get('invoice_id')
    customer_id = request.args.get('customer_id')
    status = request.args.get('status')
    
    # Basisabfrage
    query = EmailLog.query
    
    # Filtere nach Rechnung
    if invoice_id:
        query = query.filter(EmailLog.invoice_id == invoice_id)
    
    # Filtere nach Kunde
    if customer_id:
        query = query.filter(EmailLog.customer_id == customer_id)
    
    # Filtere nach Status
    if status:
        query = query.filter(EmailLog.status == status)
    
    # Sortiere nach Datum (neueste zuerst)
    query = query.order_by(EmailLog.sent_date.desc())
    
    # Führe die Abfrage aus
    logs = query.all()
    
    return jsonify(email_logs_schema.dump(logs)), 200

@email_bp.route('/logs/<int:id>', methods=['GET'])
@jwt_required()
def get_email_log(id):
    """
    Gibt einen E-Mail-Protokolleintrag anhand seiner ID zurück
    """
    log = EmailLog.query.get_or_404(id)
    return jsonify(email_log_schema.dump(log)), 200

@email_bp.route('/batch-send', methods=['POST'])
@jwt_required()
def batch_send_invoices():
    """
    Sendet mehrere Rechnungen per E-Mail
    """
    data = request.get_json()
    
    if not data or 'invoice_ids' not in data:
        return jsonify({"error": "Keine Rechnungs-IDs angegeben"}), 400
    
    invoice_ids = data.get('invoice_ids')
    template_id = data.get('template_id')
    
    results = {
        "total": len(invoice_ids),
        "success": 0,
        "failed": 0,
        "details": []
    }
    
    for invoice_id in invoice_ids:
        # Prüfe, ob die Rechnung existiert
        invoice = Invoice.query.get(invoice_id)
        if not invoice:
            results["details"].append({
                "invoice_id": invoice_id,
                "success": False,
                "error": "Rechnung nicht gefunden"
            })
            results["failed"] += 1
            continue
        
        # Prüfe, ob der Kunde eine E-Mail-Adresse hat
        if not invoice.customer.email:
            results["details"].append({
                "invoice_id": invoice_id,
                "invoice_number": invoice.invoice_number,
                "success": False,
                "error": "Kunde hat keine E-Mail-Adresse"
            })
            results["failed"] += 1
            continue
        
        # Sende E-Mail
        result = send_invoice_email(invoice_id, template_id)
        
        if result["success"]:
            results["success"] += 1
        else:
            results["failed"] += 1
        
        results["details"].append({
            "invoice_id": invoice_id,
            "invoice_number": invoice.invoice_number,
            "success": result["success"],
            "error": result.get("error")
        })
    
    return jsonify(results), 200
