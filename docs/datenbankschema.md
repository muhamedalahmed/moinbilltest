# Datenbankschema für die Buchhaltungssoftware

Basierend auf den recherchierten Anforderungen des deutschen Steuer- und Handelsrechts wird folgendes Datenbankschema für die Buchhaltungssoftware entworfen.

## Hauptentitäten

### 1. Kunden (customers)
- customer_id (PK): Eindeutige ID des Kunden
- company_name: Firmenname
- first_name: Vorname (bei natürlichen Personen)
- last_name: Nachname (bei natürlichen Personen)
- street: Straße
- house_number: Hausnummer
- postal_code: Postleitzahl
- city: Stadt
- country: Land
- tax_id: Steuernummer des Kunden
- vat_id: Umsatzsteuer-Identifikationsnummer
- email: E-Mail-Adresse (für Rechnungsversand)
- phone: Telefonnummer
- created_at: Erstellungsdatum
- updated_at: Letztes Aktualisierungsdatum
- is_active: Aktiv/Inaktiv Status

### 2. Unternehmensdaten (company_data)
- company_id (PK): Eindeutige ID des eigenen Unternehmens
- company_name: Firmenname
- legal_form: Rechtsform
- street: Straße
- house_number: Hausnummer
- postal_code: Postleitzahl
- city: Stadt
- country: Land
- tax_id: Steuernummer des Unternehmens
- vat_id: Umsatzsteuer-Identifikationsnummer
- email: E-Mail-Adresse
- phone: Telefonnummer
- website: Webseite
- bank_name: Name der Bank
- iban: IBAN
- bic: BIC
- logo_path: Pfad zum Unternehmenslogo

### 3. Artikel/Leistungen (items)
- item_id (PK): Eindeutige ID des Artikels/der Leistung
- item_number: Artikelnummer
- name: Name des Artikels/der Leistung
- description: Beschreibung
- unit: Einheit (Stück, Stunden, etc.)
- price_net: Nettopreis
- vat_rate: Umsatzsteuersatz (z.B. 19%, 7%, 0%)
- is_active: Aktiv/Inaktiv Status
- created_at: Erstellungsdatum
- updated_at: Letztes Aktualisierungsdatum

### 4. Rechnungen (invoices)
- invoice_id (PK): Eindeutige ID der Rechnung
- invoice_number: Rechnungsnummer (fortlaufend)
- customer_id (FK): Verweis auf den Kunden
- invoice_date: Rechnungsdatum
- due_date: Fälligkeitsdatum
- delivery_date: Lieferdatum/Leistungsdatum
- status: Status der Rechnung (erstellt, versendet, bezahlt, storniert)
- payment_status: Zahlungsstatus (offen, teilweise bezahlt, vollständig bezahlt)
- payment_method: Zahlungsmethode
- total_net: Gesamtbetrag netto
- total_vat: Gesamtbetrag Umsatzsteuer
- total_gross: Gesamtbetrag brutto
- notes: Anmerkungen/Notizen
- terms: Zahlungsbedingungen
- is_cancelled: Storniert (ja/nein)
- cancellation_date: Datum der Stornierung
- cancellation_reason: Grund der Stornierung
- original_invoice_id (FK): Verweis auf die Originalrechnung (bei Stornorechnungen)
- created_at: Erstellungsdatum
- updated_at: Letztes Aktualisierungsdatum
- is_recurring: Handelt es sich um eine Intervallrechnung
- email_sent: Wurde die Rechnung per E-Mail versendet
- email_sent_date: Datum des E-Mail-Versands

### 5. Rechnungspositionen (invoice_items)
- invoice_item_id (PK): Eindeutige ID der Rechnungsposition
- invoice_id (FK): Verweis auf die Rechnung
- item_id (FK): Verweis auf den Artikel/die Leistung
- position: Position auf der Rechnung
- quantity: Menge
- unit: Einheit
- price_net: Nettopreis pro Einheit
- vat_rate: Umsatzsteuersatz
- total_net: Gesamtbetrag netto
- total_vat: Gesamtbetrag Umsatzsteuer
- total_gross: Gesamtbetrag brutto
- description: Beschreibung (kann von der Standardbeschreibung des Artikels abweichen)

### 6. Intervallrechnungen (recurring_invoices)
- recurring_id (PK): Eindeutige ID der Intervallrechnung
- customer_id (FK): Verweis auf den Kunden
- start_date: Startdatum
- end_date: Enddatum (optional, für unbefristete Intervalle leer)
- interval_type: Art des Intervalls (monatlich, quartalsweise, halbjährlich, jährlich)
- interval_value: Wert des Intervalls (z.B. 1 für jeden Monat, 3 für alle 3 Monate)
- next_invoice_date: Datum der nächsten Rechnungserstellung
- last_invoice_date: Datum der letzten Rechnungserstellung
- status: Status (aktiv, pausiert, beendet)
- template_invoice_id (FK): Verweis auf eine Vorlagerechnung
- notes: Anmerkungen/Notizen
- created_at: Erstellungsdatum
- updated_at: Letztes Aktualisierungsdatum

### 7. Intervallrechnungspositionen (recurring_invoice_items)
- recurring_item_id (PK): Eindeutige ID der Intervallrechnungsposition
- recurring_id (FK): Verweis auf die Intervallrechnung
- item_id (FK): Verweis auf den Artikel/die Leistung
- position: Position auf der Rechnung
- quantity: Menge
- unit: Einheit
- price_net: Nettopreis pro Einheit
- vat_rate: Umsatzsteuersatz
- description: Beschreibung

### 8. Zahlungen (payments)
- payment_id (PK): Eindeutige ID der Zahlung
- invoice_id (FK): Verweis auf die Rechnung
- payment_date: Zahlungsdatum
- amount: Zahlungsbetrag
- payment_method: Zahlungsmethode
- reference: Referenz/Verwendungszweck
- notes: Anmerkungen/Notizen
- created_at: Erstellungsdatum
- updated_at: Letztes Aktualisierungsdatum

### 9. E-Mail-Vorlagen (email_templates)
- template_id (PK): Eindeutige ID der Vorlage
- name: Name der Vorlage
- subject: Betreff
- body: Inhalt
- is_default: Ist dies die Standardvorlage
- created_at: Erstellungsdatum
- updated_at: Letztes Aktualisierungsdatum

### 10. E-Mail-Protokoll (email_log)
- log_id (PK): Eindeutige ID des Protokolleintrags
- invoice_id (FK): Verweis auf die Rechnung
- customer_id (FK): Verweis auf den Kunden
- template_id (FK): Verweis auf die verwendete Vorlage
- sent_date: Sendedatum
- recipient: Empfänger
- subject: Betreff
- body: Inhalt
- status: Status (gesendet, fehlgeschlagen)
- error_message: Fehlermeldung (falls vorhanden)

### 11. Benutzer (users)
- user_id (PK): Eindeutige ID des Benutzers
- username: Benutzername
- password_hash: Passwort-Hash
- first_name: Vorname
- last_name: Nachname
- email: E-Mail-Adresse
- role: Rolle (Administrator, Benutzer)
- is_active: Aktiv/Inaktiv Status
- last_login: Letzter Login
- created_at: Erstellungsdatum
- updated_at: Letztes Aktualisierungsdatum

### 12. Einstellungen (settings)
- setting_id (PK): Eindeutige ID der Einstellung
- category: Kategorie
- key: Schlüssel
- value: Wert
- description: Beschreibung
- created_at: Erstellungsdatum
- updated_at: Letztes Aktualisierungsdatum

## Beziehungen

1. Kunden (1) zu Rechnungen (n): Ein Kunde kann mehrere Rechnungen haben
2. Kunden (1) zu Intervallrechnungen (n): Ein Kunde kann mehrere Intervallrechnungen haben
3. Rechnungen (1) zu Rechnungspositionen (n): Eine Rechnung kann mehrere Positionen haben
4. Artikel/Leistungen (1) zu Rechnungspositionen (n): Ein Artikel kann in mehreren Rechnungspositionen vorkommen
5. Intervallrechnungen (1) zu Intervallrechnungspositionen (n): Eine Intervallrechnung kann mehrere Positionen haben
6. Artikel/Leistungen (1) zu Intervallrechnungspositionen (n): Ein Artikel kann in mehreren Intervallrechnungspositionen vorkommen
7. Rechnungen (1) zu Zahlungen (n): Eine Rechnung kann mehrere Zahlungen haben
8. Rechnungen (1) zu E-Mail-Protokoll (n): Eine Rechnung kann mehrmals per E-Mail versendet werden
9. E-Mail-Vorlagen (1) zu E-Mail-Protokoll (n): Eine Vorlage kann für mehrere E-Mails verwendet werden
10. Rechnungen (1) zu Rechnungen (1): Eine Stornorechnung bezieht sich auf eine Originalrechnung

Dieses Datenbankschema berücksichtigt alle Anforderungen des deutschen Steuer- und Handelsrechts und ermöglicht die Erstellung von regulären Rechnungen, Stornorechnungen und Intervallrechnungen sowie den automatischen Versand per E-Mail.
