# Testplan für die Buchhaltungssoftware

## 1. Einhaltung der deutschen Rechtsvorschriften

### 1.1 Rechnungspflichtangaben gemäß § 14 UStG
- [ ] Vollständiger Name und Anschrift des leistenden Unternehmers
- [ ] Vollständiger Name und Anschrift des Leistungsempfängers
- [ ] Steuernummer oder USt-IdNr. des leistenden Unternehmers
- [ ] Ausstellungsdatum der Rechnung
- [ ] Fortlaufende Rechnungsnummer
- [ ] Menge und Art der gelieferten Gegenstände oder Umfang und Art der sonstigen Leistung
- [ ] Zeitpunkt der Lieferung oder sonstigen Leistung
- [ ] Nach Steuersätzen und -befreiungen aufgeschlüsseltes Entgelt
- [ ] Anzuwendender Steuersatz und Steuerbetrag oder Hinweis auf Steuerbefreiung
- [ ] Hinweis auf Aufbewahrungspflicht für Unternehmer (bei Rechnungen unter 250 Euro)

### 1.2 Stornorechnungen
- [ ] Eindeutige Kennzeichnung als Stornorechnung
- [ ] Referenz zur ursprünglichen Rechnung
- [ ] Negative Beträge für stornierte Positionen
- [ ] Korrekte Darstellung der Mehrwertsteuer

### 1.3 Intervallrechnungen
- [ ] Korrekte Kennzeichnung als Dauerrechnung
- [ ] Angabe des Leistungszeitraums
- [ ] Korrekte Berechnung der Mehrwertsteuer

### 1.4 GoBD-Konformität
- [ ] Unveränderbarkeit der erstellten Rechnungen
- [ ] Nachvollziehbare Änderungshistorie
- [ ] Protokollierung aller relevanten Vorgänge

## 2. Funktionalitätstests

### 2.1 Kundenverwaltung
- [ ] Anlegen neuer Kunden mit allen erforderlichen Daten
- [ ] Bearbeiten bestehender Kundendaten
- [ ] Suchen nach Kunden
- [ ] Deaktivieren von Kunden (statt physisches Löschen)

### 2.2 Artikelverwaltung
- [ ] Anlegen neuer Artikel mit allen erforderlichen Daten
- [ ] Bearbeiten bestehender Artikeldaten
- [ ] Suchen nach Artikeln
- [ ] Korrekte Berechnung von Bruttopreisen und Mehrwertsteuer

### 2.3 Rechnungserstellung
- [ ] Erstellen einer neuen Rechnung
- [ ] Hinzufügen von Positionen zu einer Rechnung
- [ ] Automatische Berechnung von Zwischensummen, Mehrwertsteuer und Gesamtbetrag
- [ ] Speichern und Bearbeiten von Rechnungsentwürfen
- [ ] Generierung von Rechnungsnummern
- [ ] PDF-Generierung und Vorschau

### 2.4 Stornorechnungen
- [ ] Stornieren einer bestehenden Rechnung
- [ ] Automatische Erstellung einer Stornorechnung
- [ ] Korrekte Darstellung der negativen Beträge
- [ ] Korrekte Verknüpfung zwischen Original- und Stornorechnung

### 2.5 Intervallrechnungen
- [ ] Erstellen einer Intervallrechnung mit verschiedenen Intervalltypen
- [ ] Automatische Generierung von Rechnungen basierend auf Intervallen
- [ ] Pausieren und Fortsetzen von Intervallrechnungen
- [ ] Beenden von Intervallrechnungen

### 2.6 E-Mail-Funktionalität
- [ ] Erstellen und Bearbeiten von E-Mail-Vorlagen
- [ ] Versenden von Rechnungen per E-Mail
- [ ] Korrekte Anhänge (PDF-Rechnungen)
- [ ] Protokollierung gesendeter E-Mails

### 2.7 Benutzer- und Rechteverwaltung
- [ ] Anlegen und Bearbeiten von Benutzern
- [ ] Zuweisen von Rollen und Berechtigungen
- [ ] Anmeldung und Abmeldung
- [ ] Passwortänderung

## 3. Benutzerfreundlichkeit

### 3.1 Allgemeine Benutzbarkeit
- [ ] Intuitive Navigation
- [ ] Konsistentes Design
- [ ] Verständliche Fehlermeldungen
- [ ] Hilfetexte und Tooltips

### 3.2 Formulare
- [ ] Klare Beschriftungen
- [ ] Sinnvolle Validierung
- [ ] Autovervollständigung wo sinnvoll
- [ ] Fehlertoleranz bei Eingaben

### 3.3 Responsive Design
- [ ] Korrekte Darstellung auf Desktop-Computern
- [ ] Korrekte Darstellung auf Tablets
- [ ] Korrekte Darstellung auf Smartphones

### 3.4 Barrierefreiheit
- [ ] Ausreichende Farbkontraste
- [ ] Tastaturnavigation
- [ ] Screenreader-Unterstützung

### 3.5 Performance
- [ ] Schnelle Ladezeiten
- [ ] Flüssige Interaktionen
- [ ] Effiziente Suche und Filterung

## 4. Sicherheit

### 4.1 Authentifizierung und Autorisierung
- [ ] Sichere Anmeldung
- [ ] Passwortrichtlinien
- [ ] Rollenbasierte Zugriffssteuerung

### 4.2 Datenschutz
- [ ] Verschlüsselung sensibler Daten
- [ ] Einhaltung der DSGVO-Anforderungen
- [ ] Datenschutzerklärung

### 4.3 Allgemeine Sicherheit
- [ ] Schutz vor Cross-Site Scripting (XSS)
- [ ] Schutz vor SQL-Injection
- [ ] Schutz vor Cross-Site Request Forgery (CSRF)

## 5. Integrationstests

### 5.1 Backend-Frontend-Integration
- [ ] Korrekte Datenübertragung zwischen Frontend und Backend
- [ ] Fehlerbehandlung bei API-Aufrufen
- [ ] Konsistente Statusaktualisierungen

### 5.2 E-Mail-Integration
- [ ] Korrekte Konfiguration des E-Mail-Servers
- [ ] Erfolgreicher Versand von E-Mails
- [ ] Korrekte Darstellung in verschiedenen E-Mail-Clients

### 5.3 PDF-Generierung
- [ ] Korrekte Darstellung aller Elemente in generierten PDFs
- [ ] Korrekte Formatierung und Seitenumbrüche
- [ ] Konsistente Darstellung auf verschiedenen PDF-Viewern

## 6. Testumgebungen

### 6.1 Lokale Entwicklungsumgebung
- [ ] Erfolgreiche Installation und Konfiguration
- [ ] Korrekte Funktionsweise aller Komponenten
- [ ] Debugging-Möglichkeiten

### 6.2 Testserver
- [ ] Erfolgreiche Bereitstellung der Anwendung
- [ ] Korrekte Konfiguration der Datenbank
- [ ] Korrekte Konfiguration des E-Mail-Servers

### 6.3 Produktionsumgebung
- [ ] Erfolgreiche Bereitstellung der Anwendung
- [ ] Performance unter Last
- [ ] Backup- und Wiederherstellungsprozesse

## 7. Testdokumentation

### 7.1 Testfälle
- [ ] Detaillierte Beschreibung der Testfälle
- [ ] Erwartete Ergebnisse
- [ ] Tatsächliche Ergebnisse

### 7.2 Fehlerdokumentation
- [ ] Beschreibung gefundener Fehler
- [ ] Schritte zur Reproduktion
- [ ] Schweregrad und Priorität

### 7.3 Testberichte
- [ ] Zusammenfassung der Testergebnisse
- [ ] Empfehlungen für Verbesserungen
- [ ] Freigabeempfehlung
