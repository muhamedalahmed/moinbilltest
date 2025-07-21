# Buchhaltungssoftware / German Accounting Software

Eine moderne, webbasierte Buchhaltungssoftware für deutsche Unternehmen, die alle steuerrechtlichen Anforderungen erfüllt und auf die E-Rechnungspflicht ab 2025 vorbereitet ist.

*A modern, web-based accounting software for German businesses that complies with all tax law requirements and is prepared for the e-invoice mandate starting in 2025.*

## Was ist das für ein Projekt? / What kind of project is this?

Dies ist eine umfassende Buchhaltungslösung, die speziell für die Anforderungen deutscher Unternehmen entwickelt wurde. Die Software unterstützt die vollständige Abwicklung von Rechnungsstellung, Kundenverwaltung und Zahlungsüberwachung unter Einhaltung aller deutschen Steuer- und Handelsrechtsbestimmungen.

*This is a comprehensive accounting solution specifically developed for the requirements of German businesses. The software supports complete invoice processing, customer management, and payment monitoring while complying with all German tax and commercial law regulations.*

## Hauptfunktionen / Key Features

### 🧾 Rechnungsmanagement / Invoice Management
- **Rechnungserstellung** mit allen Pflichtangaben nach § 14 UStG
- **PDF-Generierung** mit professionellen Layouts
- **Stornorechnungen** mit korrekter Referenzierung
- **Kleinbetragsrechnungen** mit vereinfachten Angaben
- **E-Rechnung** Vorbereitung für 2025 (EN16931 Standard)

### 🔄 Intervallrechnungen / Recurring Invoices
- **Automatische Rechnungsgenerierung** für wiederkehrende Leistungen
- **Flexible Zeitpläne** (monatlich, quartalsweise, jährlich)
- **Individuelle Anpassungen** pro Intervallrechnung

### 👥 Kundenverwaltung / Customer Management
- **Umfassende Kundendatenbank** mit Validierung
- **Unternehmens- und Privatkunden** Unterstützung
- **Steuerliche Klassifizierung** (USt-ID Pflicht, etc.)

### 📦 Artikelverwaltung / Item Management
- **Produkte und Dienstleistungen** Katalog
- **Steuersätze** und Preisgestaltung
- **Kategorisierung** und Suchfunktionen

### 💰 Zahlungsüberwachung / Payment Tracking
- **Zahlungseingänge** verfolgen
- **Mahnwesen** mit automatischen Erinnerungen
- **Zahlungshistorie** und Berichte

### 📧 E-Mail Integration
- **Automatischer Versand** von Rechnungen
- **Anpassbare Vorlagen** für verschiedene Szenarien
- **Versandprotokollierung** für Nachverfolgung

### 📊 Berichtswesen / Reporting
- **Umsatzberichte** nach Zeiträumen
- **Steuerberichte** für das Finanzamt
- **Kundenanalysen** und Statistiken

## Technologie-Stack / Technology Stack

### Backend
- **Python 3.10+** mit **Flask** Framework
- **PostgreSQL** Datenbank mit SQLAlchemy ORM
- **JWT** Authentifizierung
- **ReportLab** für PDF-Generierung
- **Flask-Mail** für E-Mail-Versand
- **pytest** für Tests

### Frontend
- **Vue.js 3** mit Composition API
- **Vuetify** Material Design Komponenten
- **Pinia** State Management
- **Axios** HTTP Client
- **vue-i18n** Internationalisierung

## Rechtliche Compliance / Legal Compliance

### Deutsche Steuergesetze / German Tax Laws
- ✅ **§ 14 UStG** Pflichtangaben auf Rechnungen
- ✅ **§ 14a UStG** Aufbewahrungspflicht
- ✅ **GoBD** Grundsätze ordnungsmäßiger Buchführung
- ✅ **Kleinbetragsrechnungen** bis 250€
- ✅ **Stornorechnungen** mit korrekter Behandlung

### E-Rechnung Vorbereitung / E-Invoice Preparation
- 🚀 **EN16931** Standard Unterstützung (ab 2025 Pflicht)
- 🚀 **ZUGFeRD** Format Kompatibilität
- 🚀 **XRechnung** Standard für öffentliche Auftraggeber

## Installation und Setup / Installation and Setup

### Voraussetzungen / Prerequisites
```bash
# Python 3.10+
python --version

# Node.js 16+
node --version

# PostgreSQL 12+
psql --version
```

### Backend Setup
```bash
cd backend

# Virtual Environment erstellen / Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder / or
venv\Scripts\activate     # Windows

# Dependencies installieren / Install dependencies
pip install -r requirements.txt

# Datenbank konfigurieren / Configure database
cp .env.example .env
# .env Datei bearbeiten / Edit .env file

# Datenbank initialisieren / Initialize database
flask db upgrade

# Development Server starten / Start development server
python run.py
```

### Frontend Setup
```bash
cd frontend

# Dependencies installieren / Install dependencies
npm install

# Development Server starten / Start development server
npm run serve
```

## Projektstruktur / Project Structure

```
moinbilltest/
├── backend/                 # Python Flask API
│   ├── app/
│   │   ├── api/            # REST API Endpunkte
│   │   ├── models/         # Datenbankmodelle
│   │   ├── services/       # Geschäftslogik
│   │   ├── schemas/        # Datenvalidierung
│   │   └── ...
│   ├── tests/              # Backend Tests
│   └── requirements.txt    # Python Dependencies
├── frontend/               # Vue.js Frontend
│   ├── src/
│   │   ├── components/     # Vue Komponenten
│   │   ├── views/          # Seiten/Views
│   │   ├── locales/        # Übersetzungen
│   │   └── ...
│   └── package.json        # Frontend Dependencies
├── docs/                   # Dokumentation
│   ├── anwendungsarchitektur.md
│   ├── datenbankschema.md
│   └── ...
├── research/               # Rechtliche Anforderungen
│   ├── rechnungsanforderungen.md
│   ├── stornorechnungen.md
│   └── ...
└── README.md              # Dieses Dokument
```

## Tests / Testing

```bash
# Backend Tests
cd backend
python -m pytest

# Frontend Tests (wenn implementiert / if implemented)
cd frontend
npm run test
```

## Beitragen / Contributing

1. Fork das Repository / Fork the repository
2. Feature Branch erstellen / Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Änderungen committen / Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Branch pushen / Push branch (`git push origin feature/AmazingFeature`)
5. Pull Request erstellen / Open Pull Request

## Lizenz / License

Dieses Projekt steht unter [MIT Lizenz](LICENSE).

## Support

Bei Fragen oder Problemen bitte ein Issue erstellen oder Kontakt aufnehmen.

*For questions or issues, please create an issue or get in touch.*

---

**Wichtiger Hinweis:** Diese Software ist für deutsche Steuergesetze optimiert. Bei Verwendung in anderen Ländern müssen entsprechende Anpassungen vorgenommen werden.

*Important Note: This software is optimized for German tax laws. When used in other countries, appropriate adjustments must be made.*
