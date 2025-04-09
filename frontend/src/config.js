// Hauptkonfigurationsdatei für Vue.js Frontend

const config = {
  // API-Basis-URL
  apiBaseUrl: process.env.VUE_APP_API_BASE_URL || 'http://localhost:5000/api',
  
  // Anwendungsname
  appName: 'Buchhaltungssoftware',
  
  // Standardsprache
  defaultLocale: 'de',
  
  // Verfügbare Sprachen
  availableLocales: ['de'],
  
  // Datumsformate
  dateFormats: {
    short: 'DD.MM.YYYY',
    long: 'DD. MMMM YYYY',
    time: 'HH:mm',
    dateTime: 'DD.MM.YYYY HH:mm'
  },
  
  // Währungsformat
  currencyFormat: {
    currency: 'EUR',
    symbol: '€',
    decimalSeparator: ',',
    thousandsSeparator: '.',
    symbolPosition: 'after',
    format: '{value} {symbol}'
  },
  
  // Mehrwertsteuersätze in Deutschland
  vatRates: [
    { value: 19, label: '19% (Standard)' },
    { value: 7, label: '7% (Ermäßigt)' },
    { value: 0, label: '0% (Steuerfrei)' }
  ],
  
  // Intervalltypen für wiederkehrende Rechnungen
  recurringIntervals: [
    { value: 'monatlich', label: 'Monatlich' },
    { value: 'quartalsweise', label: 'Quartalsweise' },
    { value: 'halbjährlich', label: 'Halbjährlich' },
    { value: 'jährlich', label: 'Jährlich' }
  ],
  
  // Rechnungsstatus
  invoiceStatus: [
    { value: 'erstellt', label: 'Erstellt', color: 'blue' },
    { value: 'versendet', label: 'Versendet', color: 'orange' },
    { value: 'bezahlt', label: 'Bezahlt', color: 'green' },
    { value: 'storniert', label: 'Storniert', color: 'red' }
  ],
  
  // Zahlungsstatus
  paymentStatus: [
    { value: 'offen', label: 'Offen', color: 'orange' },
    { value: 'teilweise bezahlt', label: 'Teilweise bezahlt', color: 'blue' },
    { value: 'vollständig bezahlt', label: 'Vollständig bezahlt', color: 'green' }
  ],
  
  // Zahlungsmethoden
  paymentMethods: [
    { value: 'Überweisung', label: 'Überweisung' },
    { value: 'Lastschrift', label: 'Lastschrift' },
    { value: 'Kreditkarte', label: 'Kreditkarte' },
    { value: 'PayPal', label: 'PayPal' },
    { value: 'Bar', label: 'Barzahlung' }
  ],
  
  // Standardeinheiten für Artikel
  defaultUnits: [
    { value: 'Stück', label: 'Stück' },
    { value: 'Stunde', label: 'Stunde' },
    { value: 'Tag', label: 'Tag' },
    { value: 'Monat', label: 'Monat' },
    { value: 'kg', label: 'Kilogramm' },
    { value: 'l', label: 'Liter' },
    { value: 'm', label: 'Meter' },
    { value: 'm²', label: 'Quadratmeter' },
    { value: 'Pauschal', label: 'Pauschal' }
  ],
  
  // Standardzahlungsbedingungen
  defaultPaymentTerms: 'Zahlbar innerhalb von 14 Tagen ohne Abzug.',
  
  // Standardfußzeile für Rechnungen
  defaultInvoiceFooter: 'Vielen Dank für Ihr Vertrauen. Bei Fragen stehen wir Ihnen gerne zur Verfügung.'
};

export default config;
