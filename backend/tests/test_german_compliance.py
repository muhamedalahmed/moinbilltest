#!/usr/bin/env python3
"""
Testskript für die Einhaltung der deutschen Rechtsvorschriften
Überprüft, ob die Buchhaltungssoftware alle rechtlichen Anforderungen erfüllt
"""

import unittest
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
from app.models.company_data import CompanyData

# PDF-Parser für die Überprüfung der generierten PDFs
import tempfile
import re
from app.services.pdf_service import generate_invoice_pdf
from PyPDF2 import PdfReader

class GermanComplianceTests(unittest.TestCase):
    """Testklasse für die Einhaltung der deutschen Rechtsvorschriften"""

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
        
        db.session.commit()
        
        self.company = company
        self.customer = customer
        self.item = item
    
    def _create_test_invoice(self):
        """Erstellt eine Testrechnung für die Überprüfung"""
        # Neue Rechnung erstellen
        invoice = Invoice(
            invoice_number="2025-04-TEST",
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
            vat_rate=self.item.vat_rate,
            description="Testprodukt für Rechtskonformitätstests"
        )
        invoice_item.calculate_totals()
        db.session.add(invoice_item)
        
        # Gesamtbeträge berechnen
        invoice.calculate_totals()
        db.session.commit()
        
        return invoice
    
    def _extract_text_from_pdf(self, pdf_path):
        """Extrahiert Text aus einer PDF-Datei"""
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    
    def test_invoice_mandatory_fields(self):
        """Test: Pflichtangaben auf Rechnungen gemäß § 14 UStG"""
        invoice = self._create_test_invoice()
        
        # PDF generieren
        fd, pdf_path = tempfile.mkstemp(suffix='.pdf')
        os.close(fd)
        
        try:
            # PDF generieren
            generate_invoice_pdf(invoice, pdf_path)
            
            # Text aus PDF extrahieren
            pdf_text = self._extract_text_from_pdf(pdf_path)
            
            # Pflichtangaben überprüfen
            
            # 1. Vollständiger Name und Anschrift des leistenden Unternehmers
            self.assertIn(self.company.company_name, pdf_text)
            self.assertIn(self.company.street, pdf_text)
            self.assertIn(self.company.house_number, pdf_text)
            self.assertIn(self.company.postal_code, pdf_text)
            self.assertIn(self.company.city, pdf_text)
            
            # 2. Vollständiger Name und Anschrift des Leistungsempfängers
            self.assertIn(self.customer.company_name, pdf_text)
            self.assertIn(self.customer.street, pdf_text)
            self.assertIn(self.customer.house_number, pdf_text)
            self.assertIn(self.customer.postal_code, pdf_text)
            self.assertIn(self.customer.city, pdf_text)
            
            # 3. Steuernummer oder USt-IdNr. des leistenden Unternehmers
            self.assertIn(self.company.tax_id, pdf_text)
            self.assertIn(self.company.vat_id, pdf_text)
            
            # 4. Ausstellungsdatum der Rechnung
            self.assertIn(invoice.invoice_date.strftime("%d.%m.%Y"), pdf_text)
            
            # 5. Fortlaufende Rechnungsnummer
            self.assertIn(invoice.invoice_number, pdf_text)
            
            # 6. Menge und Art der gelieferten Gegenstände
            self.assertIn(str(invoice.items[0].quantity), pdf_text)
            self.assertIn(invoice.items[0].unit, pdf_text)
            self.assertIn(invoice.items[0].description, pdf_text)
            
            # 7. Zeitpunkt der Lieferung
            self.assertIn(invoice.delivery_date.strftime("%d.%m.%Y"), pdf_text)
            
            # 8. Nach Steuersätzen aufgeschlüsseltes Entgelt
            self.assertIn(f"{float(invoice.total_net):.2f}", pdf_text.replace(',', '.'))
            
            # 9. Anzuwendender Steuersatz und Steuerbetrag
            self.assertIn(f"{float(invoice.items[0].vat_rate):.1f}", pdf_text.replace(',', '.'))
            self.assertIn(f"{float(invoice.total_vat):.2f}", pdf_text.replace(',', '.'))
            
        finally:
            # Temporäre Datei löschen
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
    
    def test_storno_invoice_compliance(self):
        """Test: Einhaltung der Anforderungen für Stornorechnungen"""
        # Originalrechnung erstellen
        original_invoice = self._create_test_invoice()
        
        # Rechnung stornieren
        original_invoice.is_cancelled = True
        original_invoice.cancellation_date = datetime.now().date()
        original_invoice.cancellation_reason = "Testfall: Stornierung"
        original_invoice.status = "storniert"
        
        # Stornorechnung erstellen
        storno_invoice = Invoice(
            invoice_number=f"STORNO-{original_invoice.invoice_number}",
            customer_id=original_invoice.customer_id,
            invoice_date=datetime.now().date(),
            due_date=datetime.now().date(),
            delivery_date=original_invoice.delivery_date,
            status="erstellt",
            payment_status="offen",
            notes=f"Stornorechnung zu Rechnung {original_invoice.invoice_number}",
            original_invoice_id=original_invoice.invoice_id
        )
        db.session.add(storno_invoice)
        db.session.flush()  # Um die invoice_id zu erhalten
        
        # Kopiere die Rechnungspositionen mit negativen Beträgen
        for item in original_invoice.items:
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
        
        # PDF generieren
        fd, pdf_path = tempfile.mkstemp(suffix='.pdf')
        os.close(fd)
        
        try:
            # PDF generieren
            generate_invoice_pdf(storno_invoice, pdf_path)
            
            # Text aus PDF extrahieren
            pdf_text = self._extract_text_from_pdf(pdf_path)
            
            # Anforderungen für Stornorechnungen überprüfen
            
            # 1. Eindeutige Kennzeichnung als Stornorechnung
            self.assertIn("STORNORECHNUNG", pdf_text.upper())
            
            # 2. Referenz zur ursprünglichen Rechnung
            self.assertIn(original_invoice.invoice_number, pdf_text)
            
            # 3. Negative Beträge
            # Überprüfen, ob negative Beträge vorhanden sind (mit Minuszeichen)
            self.assertTrue(re.search(r'-\s*\d+,\d+\s*€', pdf_text) is not None)
            
            # 4. Korrekte Darstellung der Mehrwertsteuer
            # Überprüfen, ob die Mehrwertsteuer negativ ist
            vat_amount = float(storno_invoice.total_vat)
            self.assertTrue(vat_amount < 0)
            
        finally:
            # Temporäre Datei löschen
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
    
    def test_invoice_number_format(self):
        """Test: Format der Rechnungsnummer"""
        invoice = self._create_test_invoice()
        
        # Überprüfen, ob die Rechnungsnummer dem erwarteten Format entspricht
        # Format: JAHR-MONAT-LAUFENDE_NUMMER
        pattern = r'\d{4}-\d{2}-[A-Z0-9]+'
        self.assertTrue(re.match(pattern, invoice.invoice_number) is not None)
    
    def test_vat_calculation(self):
        """Test: Korrekte Berechnung der Mehrwertsteuer"""
        invoice = self._create_test_invoice()
        
        # Überprüfen, ob die Mehrwertsteuer korrekt berechnet wurde
        expected_net = 2 * 100.00  # 2 Stück à 100,00 €
        expected_vat = expected_net * 0.19  # 19% MwSt.
        expected_gross = expected_net + expected_vat
        
        self.assertEqual(float(invoice.total_net), expected_net)
        self.assertEqual(float(invoice.total_vat), expected_vat)
        self.assertEqual(float(invoice.total_gross), expected_gross)

if __name__ == '__main__':
    unittest.main()
