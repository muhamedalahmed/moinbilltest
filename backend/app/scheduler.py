from flask import Flask, request, jsonify
from app.services.recurring_invoice_service import check_and_generate_recurring_invoices
from app.services.email_service import send_invoice_emails
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit
import logging

# Konfiguriere Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_scheduler(app):
    """
    Erstellt und konfiguriert den Scheduler für wiederkehrende Aufgaben
    """
    with app.app_context():
        scheduler = BackgroundScheduler()
        
        # Aufgabe für die Generierung von Intervallrechnungen (täglich um 3 Uhr morgens)
        scheduler.add_job(
            func=check_and_generate_recurring_invoices,
            trigger=CronTrigger(hour=3, minute=0),
            id='generate_recurring_invoices',
            name='Generiere fällige Intervallrechnungen',
            replace_existing=True
        )
        
        # Aufgabe für den Versand von Rechnungen per E-Mail (täglich um 8 Uhr morgens)
        scheduler.add_job(
            func=send_invoice_emails,
            trigger=CronTrigger(hour=8, minute=0),
            id='send_invoice_emails',
            name='Versende Rechnungen per E-Mail',
            replace_existing=True
        )
        
        # Starte den Scheduler
        scheduler.start()
        logger.info("Scheduler gestartet mit Jobs: %s", scheduler.get_jobs())
        
        # Stelle sicher, dass der Scheduler beim Beenden der Anwendung gestoppt wird
        atexit.register(lambda: scheduler.shutdown())
        
        return scheduler
