# Anwendungsarchitektur für die Buchhaltungssoftware

Die Buchhaltungssoftware wird als moderne Webanwendung mit einer klaren Trennung zwischen Backend und Frontend implementiert. Diese Architektur ermöglicht eine hohe Wartbarkeit, Skalierbarkeit und eine gute Benutzererfahrung.

## Technologie-Stack

### Backend
- **Programmiersprache**: Python 3.10+
- **Web-Framework**: Flask (leichtgewichtiges Framework für APIs)
- **ORM (Object-Relational Mapping)**: SQLAlchemy (für Datenbankoperationen)
- **Datenbank**: PostgreSQL (robust, unterstützt komplexe Datentypen und Transaktionen)
- **API-Stil**: RESTful API
- **Authentifizierung**: JWT (JSON Web Tokens)
- **E-Mail-Versand**: Flask-Mail mit SMTP-Integration
- **PDF-Generierung**: ReportLab oder WeasyPrint
- **Validierung**: Marshmallow (für Datenvalidierung)
- **Testen**: pytest

### Frontend
- **Framework**: Vue.js 3 (mit Composition API)
- **UI-Bibliothek**: Vuetify (Material Design Komponenten)
- **State Management**: Pinia
- **HTTP-Client**: Axios
- **Formularvalidierung**: Vuelidate
- **Internationalisierung**: vue-i18n (für deutsche Benutzeroberfläche)
- **Testen**: Jest

## Architekturübersicht

Die Anwendung folgt einer Schichtenarchitektur:

1. **Präsentationsschicht** (Frontend)
   - Vue.js Single-Page-Application
   - Responsive Design für Desktop und mobile Geräte
   - Komponenten-basierte Architektur

2. **API-Schicht** (Backend)
   - RESTful API-Endpunkte
   - Authentifizierung und Autorisierung
   - Anfrageverarbeitung und Validierung

3. **Geschäftslogikschicht** (Backend)
   - Services für Geschäftslogik
   - Implementierung der Buchhaltungsregeln
   - Validierung der steuerrechtlichen Anforderungen

4. **Datenzugriffsschicht** (Backend)
   - ORM-Modelle
   - Repository-Pattern für Datenbankzugriff
   - Transaktionsmanagement

5. **Datenbankschicht**
   - PostgreSQL-Datenbank
   - Tabellen gemäß dem entworfenen Datenbankschema

## Modulare Struktur

Die Anwendung wird in folgende Hauptmodule unterteilt:

1. **Kundenverwaltung**
   - Anlegen, Bearbeiten, Löschen von Kunden
   - Kundendaten-Validierung
   - Kundensuche und -filterung

2. **Artikelverwaltung**
   - Verwaltung von Produkten und Dienstleistungen
   - Preisgestaltung und Steuersätze
   - Artikelkategorisierung

3. **Rechnungsmodul**
   - Rechnungserstellung
   - Rechnungsvorschau
   - PDF-Generierung
   - Stornorechnungen

4. **Intervallrechnungsmodul**
   - Einrichtung wiederkehrender Rechnungen
   - Zeitplanverwaltung
   - Automatische Rechnungsgenerierung

5. **E-Mail-Modul**
   - E-Mail-Vorlagenverwaltung
   - Automatischer Versand
   - E-Mail-Protokollierung

6. **Zahlungsmodul**
   - Erfassung von Zahlungseingängen
   - Zahlungsverfolgung
   - Mahnwesen

7. **Berichtswesen**
   - Umsatzberichte
   - Steuerberichte
   - Kundenanalysen

8. **Benutzerverwaltung**
   - Benutzerkonten
   - Rollen und Berechtigungen
   - Authentifizierung

9. **Systemkonfiguration**
   - Unternehmensdaten
   - Steuereinstellungen
   - E-Mail-Konfiguration

## Verzeichnisstruktur

```
buchhaltungssoftware/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── customers.py
│   │   │   ├── invoices.py
│   │   │   ├── items.py
│   │   │   ├── recurring_invoices.py
│   │   │   ├── payments.py
│   │   │   ├── email_templates.py
│   │   │   └── users.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── customer.py
│   │   │   ├── company_data.py
│   │   │   ├── item.py
│   │   │   ├── invoice.py
│   │   │   ├── invoice_item.py
│   │   │   ├── recurring_invoice.py
│   │   │   ├── recurring_invoice_item.py
│   │   │   ├── payment.py
│   │   │   ├── email_template.py
│   │   │   ├── email_log.py
│   │   │   ├── user.py
│   │   │   └── setting.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── customer_service.py
│   │   │   ├── invoice_service.py
│   │   │   ├── recurring_invoice_service.py
│   │   │   ├── email_service.py
│   │   │   ├── pdf_service.py
│   │   │   └── auth_service.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── customer_schema.py
│   │   │   ├── invoice_schema.py
│   │   │   └── ...
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── validators.py
│   │   │   ├── pdf_generator.py
│   │   │   └── email_sender.py
│   │   ├── config.py
│   │   └── __init__.py
│   ├── migrations/
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_customers.py
│   │   ├── test_invoices.py
│   │   └── ...
│   ├── .env
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   │   ├── customers/
│   │   │   ├── invoices/
│   │   │   ├── recurring-invoices/
│   │   │   ├── items/
│   │   │   ├── payments/
│   │   │   ├── email-templates/
│   │   │   └── common/
│   │   ├── views/
│   │   ├── router/
│   │   ├── store/
│   │   ├── services/
│   │   ├── locales/
│   │   │   ├── de.json
│   │   │   └── en.json
│   │   ├── App.vue
│   │   └── main.js
│   ├── tests/
│   ├── package.json
│   └── vue.config.js
├── docs/
│   ├── datenbankschema.md
│   ├── anwendungsarchitektur.md
│   └── ...
└── README.md
```

## API-Endpunkte

Die RESTful API wird folgende Hauptendpunkte bereitstellen:

1. `/api/customers` - Kundenverwaltung
2. `/api/items` - Artikel-/Leistungsverwaltung
3. `/api/invoices` - Rechnungsverwaltung
4. `/api/recurring-invoices` - Intervallrechnungsverwaltung
5. `/api/payments` - Zahlungsverwaltung
6. `/api/email-templates` - E-Mail-Vorlagenverwaltung
7. `/api/users` - Benutzerverwaltung
8. `/api/settings` - Systemeinstellungen
9. `/api/reports` - Berichtswesen
10. `/api/auth` - Authentifizierung

## Sicherheitsaspekte

- **Authentifizierung**: JWT-basierte Authentifizierung
- **Autorisierung**: Rollenbasierte Zugriffssteuerung
- **Datenschutz**: Verschlüsselung sensibler Daten
- **Validierung**: Strenge Eingabevalidierung
- **HTTPS**: Sichere Kommunikation
- **Logging**: Umfassende Protokollierung für Audit-Zwecke

## Berücksichtigung deutscher Steuer- und Handelsrecht-Anforderungen

- Implementierung aller Pflichtangaben für Rechnungen gemäß § 14 UStG
- Unterstützung für Stornorechnungen mit allen erforderlichen Angaben
- Korrekte Handhabung von Intervallrechnungen
- Vorbereitung auf die E-Rechnungspflicht ab 01.01.2025
- Einhaltung der GoBD (Grundsätze zur ordnungsmäßigen Führung und Aufbewahrung von Büchern, Aufzeichnungen und Unterlagen in elektronischer Form sowie zum Datenzugriff)

Diese Architektur bietet eine solide Grundlage für die Entwicklung der Buchhaltungssoftware und stellt sicher, dass alle funktionalen und rechtlichen Anforderungen erfüllt werden können.
