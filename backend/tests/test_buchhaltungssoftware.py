#!/usr/bin/env python3
"""
Testskript für die Buchhaltungssoftware
Führt automatisierte Tests für die Backend-Funktionalität durch
"""

import unittest
import json
import os
import sys
from datetime import datetime, timedelta

# Füge das Backend-Verzeichnis zum Pfad hinzu
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importiere die Flask-App im Testmodus
os.environ['FLASK_ENV'] = 'testing'
from app import create_app, db
from app.models.customer import Customer
from app.models.item import Item
from app.models.invoice import Invoice, InvoiceItem
from app.models.recurring_invoice import RecurringInvoice, RecurringInvoiceItem
from app.models.company_data import CompanyData
from app.models.email_template import EmailTemplate

class BuchhaltungssoftwareTests(unittest.TestCase):
    """Testklasse für die Buchhaltungssoftware"""

    def setUp(self):
        """Testumgebung einrichten"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
        # Datenbank für Tests erstellen
        db.create_all()
        
        # Testdaten erstellen
        self._create_test_data()
    
    def tearDown(self):
        """Testumgebung aufräumen"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def _create_test_data(self):
        """Testdaten für die Tests erstellen"""
        # Unternehmensdaten
        company = CompanyData(
            company_name="Muster GmbH",
            legal_form="GmbH",
            street="Musterstraße",
            house_number="123",
            postal_code="12345",
            city="Musterstadt",
            country="Deutschland",
            tax_id="123/456/78901",
            vat_id="DE123456789",
            email="info@muster-gmbh.de",
            phone="+49 123 4567890",
            bank_name="Musterbank",
            iban="DE12345678901234567890",
            bic="MUBADE123"
        )
        db.session.add(company)
        
        # Kunde
        customer = Customer(
            company_name="Kunde GmbH",
            street="Kundenstraße",
            house_number="456",
            postal_code="54321",
            city="Kundenstadt",
            country="Deutschland",
            email="info@kunde-gmbh.de",
            phone="+49 987 6543210"
        )
        db.session.add(customer)
        
        # Artikel
        item = Item(
            item_number="ART-001",
            name="Testprodukt",
            description="Ein Produkt für Testzwecke",
            unit="Stück",
            price_net=100.00,
            vat_rate=19.0
        )
        db.session.add(item)
        
        # E-Mail-Vorlage
        email_template = EmailTemplate(
            name="Standard-Rechnungsvorlage",
            subject="Ihre Rechnung {invoice_number}",
            body="Sehr geehrte Damen und Herren,\n\nim Anhang finden Sie Ihre Rechnung {invoice_number} vom {invoice_date}.\n\nMit freundlichen Grüßen\n{company_name}",
            is_default=True
        )
        db.session.add(email_template)
        
        db.session.commit()
        
        self.company = company
        self.customer = customer
        self.item = item
        self.email_template = email_template
    
    def test_customer_creation(self):
        """Test: Kunde erstellen"""
        # Neuen Kunden erstellen
        new_customer = Customer(
            company_name="Neuer Kunde GmbH",
            street="Neustraße",
            house_number="789",
            postal_code="98765",
            city="Neustadt",
            country="Deutschland",
            email="info@neuer-kunde.de"
        )
        db.session.add(new_customer)
        db.session.commit()
        
        # Kunden aus der Datenbank abrufen
        retrieved_customer = Customer.query.filter_by(company_name="Neuer Kunde GmbH").first()
        
        # Überprüfen, ob der Kunde korrekt erstellt wurde
        self.assertIsNotNone(retrieved_customer)
        self.assertEqual(retrieved_customer.company_name, "Neuer Kunde GmbH")
        self.assertEqual(retrieved_customer.email, "info@neuer-kunde.de")
    
    def test_invoice_creation(self):
        """Test: Rechnung erstellen"""
        # Neue Rechnung erstellen
        invoice = Invoice(
            invoice_number="2025-04-001",
            customer_id=self.customer.customer_id,
            invoice_date=datetime.now().date(),
            due_date=datetime.now().date() + timedelta(days=14),
            delivery_date=datetime.now().date()
        )
        db.session.add(invoice)
        db.session.flush()  # Um die invoice_id zu erhalten
        
        # Rechnungsposition hinzufügen
        invoice_item = InvoiceItem(
            invoice_id=invoice.invoice_id,
            item_id=self.item.item_id,
            position=1,
            quantity=2,
            unit="Stück",
            price_net=self.item.price_net,
            vat_rate=self.item.vat_rate
        )
        invoice_item.calculate_totals()
        db.session.add(invoice_item)
        
        # Gesamtbeträge berechnen
        invoice.calculate_totals()
        db.session.commit()
        
        # Rechnung aus der Datenbank abrufen
        retrieved_invoice = Invoice.query.filter_by(invoice_number="2025-04-001").first()
        
        # Überprüfen, ob die Rechnung korrekt erstellt wurde
        self.assertIsNotNone(retrieved_invoice)
        self.assertEqual(retrieved_invoice.invoice_number, "2025-04-001")
        self.assertEqual(retrieved_invoice.customer_id, self.customer.customer_id)
        
        # Überprüfen, ob die Beträge korrekt berechnet wurden
        self.assertEqual(float(retrieved_invoice.total_net), 200.00)  # 2 * 100.00
        self.assertEqual(float(retrieved_invoice.total_vat), 38.00)   # 200.00 * 19%
        self.assertEqual(float(retrieved_invoice.total_gross), 238.00)  # 200.00 + 38.00
    
    def test_invoice_cancellation(self):
        """Test: Rechnung stornieren"""
        # Neue Rechnung erstellen
        invoice = Invoice(
            invoice_number="2025-04-002",
            customer_id=self.customer.customer_id,
            invoice_date=datetime.now().date(),
            due_date=datetime.now().date() + timedelta(days=14),
            delivery_date=datetime.now().date()
        )
        db.session.add(invoice)
        db.session.flush()  # Um die invoice_id zu erhalten
        
        # Rechnungsposition hinzufügen
        invoice_item = InvoiceItem(
            invoice_id=invoice.invoice_id,
            item_id=self.item.item_id,
            position=1,
            quantity=1,
            unit="Stück",
            price_net=self.item.price_net,
            vat_rate=self.item.vat_rate
        )
        invoice_item.calculate_totals()
        db.session.add(invoice_item)
        
        # Gesamtbeträge berechnen
        invoice.calculate_totals()
        db.session.commit()
        
        # Rechnung stornieren
        invoice.is_cancelled = True
        invoice.cancellation_date = datetime.now().date()
        invoice.cancellation_reason = "Testfall: Stornierung"
        invoice.status = "storniert"
        
        # Stornorechnung erstellen
        storno_invoice = Invoice(
            invoice_number=f"STORNO-{invoice.invoice_number}",
            customer_id=invoice.customer_id,
            invoice_date=datetime.now().date(),
            due_date=datetime.now().date(),
            delivery_date=invoice.delivery_date,
            status="erstellt",
            payment_status="offen",
            notes=f"Stornorechnung zu Rechnung {invoice.invoice_number}",
            original_invoice_id=invoice.invoice_id
        )
        db.session.add(storno_invoice)
        db.session.flush()  # Um die invoice_id zu erhalten
        
        # Kopiere die Rechnungspositionen mit negativen Beträgen
        for item in invoice.items:
            storno_item = InvoiceItem(
                invoice_id=storno_invoice.invoice_id,
                item_id=item.item_id,
                position=item.position,
                quantity=-item.quantity,  # Negative Menge für Storno
                unit=item.unit,
                price_net=item.price_net,
                vat_rate=item.vat_rate,
                description=item.description
            )
            storno_item.calculate_totals()
            db.session.add(storno_item)
        
        # Gesamtbeträge der Stornorechnung berechnen
        storno_invoice.calculate_totals()
        db.session.commit()
        
        # Überprüfen, ob die Originalrechnung als storniert markiert wurde
        self.assertTrue(invoice.is_cancelled)
        self.assertEqual(invoice.status, "storniert")
        
        # Überprüfen, ob die Stornorechnung korrekt erstellt wurde
        self.assertEqual(storno_invoice.invoice_number, f"STORNO-{invoice.invoice_number}")
        self.assertEqual(storno_invoice.original_invoice_id, invoice.invoice_id)
        
        # Überprüfen, ob die Beträge in der Stornorechnung negativ sind
        self.assertEqual(float(storno_invoice.total_net), -100.00)
        self.assertEqual(float(storno_invoice.total_vat), -19.00)
        self.assertEqual(float(storno_invoice.total_gross), -119.00)
    
    def test_recurring_invoice(self):
        """Test: Intervallrechnung erstellen und Rechnung generieren"""
        # Neue Intervallrechnung erstellen
        today = datetime.now().date()
        recurring_invoice = RecurringInvoice(
            customer_id=self.customer.customer_id,
            start_date=today,
            interval_type="monatlich",
            interval_value=1,
            next_invoice_date=today,
            status="aktiv"
        )
        db.session.add(recurring_invoice)
        db.session.flush()  # Um die recurring_id zu erhalten
        
        # Position zur Intervallrechnung hinzufügen
        recurring_item = RecurringInvoiceItem(
            recurring_id=recurring_invoice.recurring_id,
            item_id=self.item.item_id,
            position=1,
            quantity=1,
            unit="Stück",
            price_net=self.item.price_net,
            vat_rate=self.item.vat_rate
        )
        db.session.add(recurring_item)
        db.session.commit()
        
        # Rechnung aus der Intervallrechnung generieren
        from app.services.recurring_invoice_service import check_and_generate_recurring_invoices
        generated_invoices = check_and_generate_recurring_invoices()
        
        # Überprüfen, ob eine Rechnung generiert wurde
        self.assertEqual(len(generated_invoices), 1)
        
        # Generierte Rechnung aus der Datenbank abrufen
        invoice_id = generated_invoices[0]["invoice_id"]
        generated_invoice = Invoice.query.get(invoice_id)
        
        # Überprüfen, ob die generierte Rechnung korrekt ist
        self.assertIsNotNone(generated_invoice)
        self.assertEqual(generated_invoice.customer_id, self.customer.customer_id)
        self.assertEqual(generated_invoice.is_recurring, True)
        
        # Überprüfen, ob die Intervallrechnung aktualisiert wurde
        self.assertEqual(recurring_invoice.last_invoice_date, today)
        next_month = today.replace(month=today.month + 1 if today.month < 12 else 1,
                                  year=today.year if today.month < 12 else today.year + 1)
        self.assertEqual(recurring_invoice.next_invoice_date, next_month)
    
    def test_invoice_validation(self):
        """Test: Validierung der Rechnungspflichtangaben"""
        # Neue Rechnung erstellen
        invoice = Invoice(
            invoice_number="2025-04-003",
            customer_id=self.customer.customer_id,
            invoice_date=datetime.now().date(),
            due_date=datetime.now().date() + timedelta(days=14),
            delivery_date=datetime.now().date()
        )
        db.session.add(invoice)
        db.session.flush()  # Um die invoice_id zu erhalten
        
        # Rechnungsposition hinzufügen
        invoice_item = InvoiceItem(
            invoice_id=invoice.invoice_id,
            item_id=self.item.item_id,
            position=1,
            quantity=1,
            unit="Stück",
            price_net=self.item.price_net,
            vat_rate=self.item.vat_rate
        )
        invoice_item.calculate_totals()
        db.session.add(invoice_item)
        
        # Gesamtbeträge berechnen
        invoice.calculate_totals()
        db.session.commit()
        
        # PDF generieren
        import tempfile
        from app.services.pdf_service import generate_invoice_pdf
        
        fd, pdf_path = tempfile.mkstemp(suffix='.pdf')
        os.close(fd)
        
        try:
            # PDF generieren
            generate_invoice_pdf(invoice, pdf_path)
            
            # Überprüfen, ob die PDF-Datei erstellt wurde
            self.assertTrue(os.path.exists(pdf_path))
            self.assertTrue(os.path.getsize(pdf_path) > 0)
            
            # Hier könnten weitere Tests zur Überprüfung des PDF-Inhalts folgen
            # z.B. mit einer PDF-Parsing-Bibliothek
            
        finally:
            # Temporäre Datei löschen
            if os.path.exists(pdf_path):
                os.remove(pdf_path)

if __name__ == '__main__':
    unittest.main()
