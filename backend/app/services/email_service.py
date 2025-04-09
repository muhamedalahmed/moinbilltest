from flask import Flask, request, jsonify
from app.models.invoice import Invoice
from app.models.email_template import EmailTemplate, EmailLog
from app.models.company_data import CompanyData
from app import db, mail
from flask_mail import Message
import os
import tempfile
from app.services.pdf_service import generate_invoice_pdf
import logging
from datetime import datetime

# Konfiguriere Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_invoice_email(invoice_id, template_id=None, custom_subject=None, custom_body=None, recipient=None):
    """
    Sendet eine Rechnung per E-Mail
    
    Args:
        invoice_id: ID der Rechnung
        template_id: ID der E-Mail-Vorlage (optional)
        custom_subject: Benutzerdefinierter Betreff (optional)
        custom_body: Benutzerdefinierter Text (optional)
        recipient: Benutzerdefinierter Empfänger (optional)
        
    Returns:
        Ein Dictionary mit Informationen über den Versand
    """
    try:
        # Hole Rechnung
        invoice = Invoice.query.get(invoice_id)
        if not invoice:
            logger.error(f"Rechnung mit ID {invoice_id} nicht gefunden")
            return {"success": False, "error": f"Rechnung mit ID {invoice_id} nicht gefunden"}
        
        # Hole Unternehmensdaten
        company_data = CompanyData.query.first()
        if not company_data:
            logger.error("Keine Unternehmensdaten gefunden")
            return {"success": False, "error": "Keine Unternehmensdaten gefunden"}
        
        # Bestimme Empfänger
        if recipient:
            email_recipient = recipient
        elif invoice.customer.email:
            email_recipient = invoice.customer.email
        else:
            logger.error(f"Kein E-Mail-Empfänger für Rechnung {invoice_id} gefunden")
            return {"success": False, "error": "Kein E-Mail-Empfänger gefunden"}
        
        # Bestimme E-Mail-Vorlage
        if template_id:
            template = EmailTemplate.query.get(template_id)
        else:
            template = EmailTemplate.query.filter_by(is_default=True).first()
        
        if not template and not (custom_subject and custom_body):
            logger.error("Keine E-Mail-Vorlage gefunden und keine benutzerdefinierten Inhalte angegeben")
            return {"success": False, "error": "Keine E-Mail-Vorlage gefunden und keine benutzerdefinierten Inhalte angegeben"}
        
        # Bestimme Betreff und Text
        if custom_subject:
            subject = custom_subject
        elif template:
            subject = template.subject
        else:
            subject = f"Rechnung {invoice.invoice_number}"
        
        if custom_body:
            body = custom_body
        elif template:
            body = template.body
        else:
            body = f"Sehr geehrte Damen und Herren,\n\nim Anhang finden Sie Ihre Rechnung {invoice.invoice_number}.\n\nMit freundlichen Grüßen\n{company_data.company_name}"
        
        # Ersetze Platzhalter
        subject = subject.replace("{invoice_number}", invoice.invoice_number)
        subject = subject.replace("{company_name}", company_data.company_name)
        subject = subject.replace("{customer_name}", invoice.customer.full_name)
        
        body = body.replace("{invoice_number}", invoice.invoice_number)
        body = body.replace("{invoice_date}", invoice.invoice_date.strftime("%d.%m.%Y"))
        body = body.replace("{due_date}", invoice.due_date.strftime("%d.%m.%Y"))
        body = body.replace("{total_amount}", f"{float(invoice.total_gross):.2f} €")
        body = body.replace("{company_name}", company_data.company_name)
        body = body.replace("{customer_name}", invoice.customer.full_name)
        
        # Generiere PDF
        fd, pdf_path = tempfile.mkstemp(suffix='.pdf')
        os.close(fd)
        generate_invoice_pdf(invoice, pdf_path)
        
        # Erstelle E-Mail
        msg = Message(
            subject=subject,
            recipients=[email_recipient],
            body=body,
            sender=company_data.email or "noreply@example.com"
        )
        
        # Füge PDF als Anhang hinzu
        with open(pdf_path, 'rb') as pdf:
            msg.attach(
                filename=f"Rechnung_{invoice.invoice_number}.pdf",
                content_type="application/pdf",
                data=pdf.read()
            )
        
        # Sende E-Mail
        mail.send(msg)
        
        # Lösche temporäre PDF-Datei
        try:
            os.remove(pdf_path)
        except:
            pass
        
        # Protokolliere E-Mail
        email_log = EmailLog(
            invoice_id=invoice.invoice_id,
            customer_id=invoice.customer_id,
            template_id=template.template_id if template else None,
            recipient=email_recipient,
            subject=subject,
            body=body,
            status='gesendet'
        )
        
        db.session.add(email_log)
        
        # Aktualisiere Rechnungsstatus
        invoice.email_sent = True
        invoice.email_sent_date = datetime.utcnow()
        if invoice.status == 'erstellt':
            invoice.status = 'versendet'
        
        db.session.commit()
        
        logger.info(f"E-Mail für Rechnung {invoice.invoice_number} erfolgreich an {email_recipient} gesendet")
        
        return {
            "success": True,
            "invoice_id": invoice.invoice_id,
            "invoice_number": invoice.invoice_number,
            "recipient": email_recipient,
            "subject": subject,
            "email_log_id": email_log.log_id
        }
    
    except Exception as e:
        logger.error(f"Fehler beim Senden der E-Mail für Rechnung {invoice_id}: {str(e)}")
        db.session.rollback()
        
        # Protokolliere Fehler
        try:
            email_log = EmailLog(
                invoice_id=invoice_id,
                customer_id=invoice.customer_id if 'invoice' in locals() else None,
                template_id=template.template_id if 'template' in locals() else None,
                recipient=email_recipient if 'email_recipient' in locals() else "unbekannt",
                subject=subject if 'subject' in locals() else "unbekannt",
                body=body if 'body' in locals() else "unbekannt",
                status='fehlgeschlagen',
                error_message=str(e)
            )
            
            db.session.add(email_log)
            db.session.commit()
        except:
            pass
        
        return {"success": False, "error": str(e)}

def send_invoice_emails(status='erstellt', limit=50):
    """
    Sendet E-Mails für Rechnungen mit einem bestimmten Status
    
    Args:
        status: Status der Rechnungen (erstellt, versendet, bezahlt, storniert)
        limit: Maximale Anzahl der zu versendenden E-Mails
        
    Returns:
        Ein Dictionary mit Informationen über den Versand
    """
    logger.info(f"Starte Versand von E-Mails für Rechnungen mit Status '{status}'")
    
    # Hole Rechnungen, die noch nicht per E-Mail versendet wurden
    invoices = Invoice.query.filter_by(status=status, email_sent=False).limit(limit).all()
    
    logger.info(f"Gefunden: {len(invoices)} Rechnungen zum Versenden")
    
    results = {
        "total": len(invoices),
        "success": 0,
        "failed": 0,
        "details": []
    }
    
    for invoice in invoices:
        # Prüfe, ob der Kunde eine E-Mail-Adresse hat
        if not invoice.customer.email:
            logger.warning(f"Kunde für Rechnung {invoice.invoice_number} hat keine E-Mail-Adresse")
            results["details"].append({
                "invoice_id": invoice.invoice_id,
                "invoice_number": invoice.invoice_number,
                "success": False,
                "error": "Kunde hat keine E-Mail-Adresse"
            })
            results["failed"] += 1
            continue
        
        # Sende E-Mail
        result = send_invoice_email(invoice.invoice_id)
        
        if result["success"]:
            results["success"] += 1
        else:
            results["failed"] += 1
        
        results["details"].append({
            "invoice_id": invoice.invoice_id,
            "invoice_number": invoice.invoice_number,
            "success": result["success"],
            "error": result.get("error")
        })
    
    logger.info(f"E-Mail-Versand abgeschlossen: {results['success']} erfolgreich, {results['failed']} fehlgeschlagen")
    
    return results
