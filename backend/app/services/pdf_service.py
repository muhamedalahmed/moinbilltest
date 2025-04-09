from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from app.models.invoice import Invoice
from app.models.company_data import CompanyData
from datetime import datetime
import os

def generate_invoice_pdf(invoice, output_path):
    """
    Generiert eine PDF-Datei für eine Rechnung
    
    Args:
        invoice: Das Invoice-Objekt
        output_path: Der Pfad, unter dem die PDF-Datei gespeichert werden soll
    """
    # Hole Unternehmensdaten
    company_data = CompanyData.query.first()
    if not company_data:
        raise ValueError("Keine Unternehmensdaten gefunden")
    
    # Erstelle PDF-Dokument
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # Styles für Text
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='RightAlign',
        parent=styles['Normal'],
        alignment=2  # 2 = rechts ausgerichtet
    ))
    styles.add(ParagraphStyle(
        name='CenterAlign',
        parent=styles['Normal'],
        alignment=1  # 1 = zentriert
    ))
    styles.add(ParagraphStyle(
        name='Bold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        name='Title',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1
    ))
    
    # Elemente für das PDF
    elements = []
    
    # Firmenlogo (falls vorhanden)
    if company_data.logo_path and os.path.exists(company_data.logo_path):
        img = Image(company_data.logo_path, width=5*cm, height=2*cm)
        elements.append(img)
    
    # Absender und Empfänger
    sender_data = [
        [Paragraph(f"<font size='8'>{company_data.company_name} · {company_data.street} {company_data.house_number} · {company_data.postal_code} {company_data.city}</font>", styles['Normal'])],
    ]
    sender_table = Table(sender_data, colWidths=[10*cm])
    sender_table.setStyle(TableStyle([
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0.5*cm),
    ]))
    elements.append(sender_table)
    
    # Empfängerdaten
    recipient_data = [
        [Paragraph(f"<b>{invoice.customer.full_name}</b>", styles['Normal'])],
        [Paragraph(f"{invoice.customer.street} {invoice.customer.house_number}", styles['Normal'])],
        [Paragraph(f"{invoice.customer.postal_code} {invoice.customer.city}", styles['Normal'])],
        [Paragraph(f"{invoice.customer.country}", styles['Normal'])],
    ]
    recipient_table = Table(recipient_data, colWidths=[10*cm])
    recipient_table.setStyle(TableStyle([
        ('TOPPADDING', (0, 0), (-1, -1), 0.1*cm),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0.1*cm),
    ]))
    elements.append(recipient_table)
    elements.append(Spacer(1, 1*cm))
    
    # Rechnungsinformationen
    if invoice.is_cancelled:
        elements.append(Paragraph("STORNORECHNUNG", styles['Title']))
    else:
        elements.append(Paragraph("RECHNUNG", styles['Title']))
    elements.append(Spacer(1, 0.5*cm))
    
    invoice_info_data = [
        ["Rechnungsnummer:", invoice.invoice_number],
        ["Rechnungsdatum:", invoice.invoice_date.strftime("%d.%m.%Y")],
        ["Lieferdatum:", invoice.delivery_date.strftime("%d.%m.%Y")],
        ["Fälligkeitsdatum:", invoice.due_date.strftime("%d.%m.%Y")],
    ]
    
    # Wenn es eine Stornorechnung ist, füge Referenz zur Originalrechnung hinzu
    if invoice.is_cancelled:
        invoice_info_data.append(["Storniert am:", invoice.cancellation_date.strftime("%d.%m.%Y")])
        if invoice.original_invoice:
            invoice_info_data.append(["Original-Rechnungsnummer:", invoice.original_invoice.invoice_number])
    
    # Wenn es eine Rechnung zu einer Stornorechnung ist, füge Referenz zur Stornorechnung hinzu
    if invoice.original_invoice_id:
        invoice_info_data.append(["Bezieht sich auf Rechnung:", invoice.original_invoice.invoice_number])
    
    invoice_info_table = Table(invoice_info_data, colWidths=[5*cm, 10*cm])
    invoice_info_table.setStyle(TableStyle([
        ('TOPPADDING', (0, 0), (-1, -1), 0.1*cm),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0.1*cm),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
    ]))
    elements.append(invoice_info_table)
    elements.append(Spacer(1, 1*cm))
    
    # Rechnungspositionen
    if invoice.items:
        # Tabellenkopf
        position_data = [
            ["Pos.", "Beschreibung", "Menge", "Einheit", "Einzelpreis (netto)", "MwSt.", "Gesamtpreis (netto)"]
        ]
        
        # Tabelleninhalt
        for item in invoice.items:
            position_data.append([
                str(item.position),
                item.description or "",
                str(item.quantity),
                item.unit,
                f"{float(item.price_net):.2f} €",
                f"{float(item.vat_rate):.1f} %",
                f"{float(item.total_net):.2f} €"
            ])
        
        # Tabelle erstellen
        position_table = Table(position_data, colWidths=[1*cm, 7*cm, 1.5*cm, 1.5*cm, 3*cm, 1.5*cm, 3*cm])
        position_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Pos.
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),   # Menge
            ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # Einheit
            ('ALIGN', (4, 1), (6, -1), 'RIGHT'),   # Preise und MwSt.
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(position_table)
        elements.append(Spacer(1, 0.5*cm))
    
    # Zusammenfassung
    summary_data = [
        ["Nettobetrag:", f"{float(invoice.total_net):.2f} €"],
        ["Mehrwertsteuer:", f"{float(invoice.total_vat):.2f} €"],
        ["Gesamtbetrag:", f"{float(invoice.total_gross):.2f} €"],
    ]
    
    summary_table = Table(summary_data, colWidths=[15*cm, 3*cm])
    summary_table.setStyle(TableStyle([
        ('TOPPADDING', (0, 0), (-1, -1), 0.1*cm),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0.1*cm),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 2), (1, 2), 'Helvetica-Bold'),  # Gesamtbetrag fett
        ('LINEABOVE', (0, 2), (1, 2), 1, colors.black),  # Linie über Gesamtbetrag
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 1*cm))
    
    # Zahlungsinformationen
    payment_info = []
    payment_info.append(Paragraph("Zahlungsinformationen:", styles['Bold']))
    payment_info.append(Spacer(1, 0.2*cm))
    
    if invoice.payment_method:
        payment_info.append(Paragraph(f"Zahlungsmethode: {invoice.payment_method}", styles['Normal']))
    
    payment_info.append(Paragraph(f"Bankverbindung: {company_data.bank_name}", styles['Normal']))
    payment_info.append(Paragraph(f"IBAN: {company_data.iban}", styles['Normal']))
    payment_info.append(Paragraph(f"BIC: {company_data.bic}", styles['Normal']))
    payment_info.append(Paragraph(f"Verwendungszweck: {invoice.invoice_number}", styles['Normal']))
    
    if invoice.terms:
        payment_info.append(Spacer(1, 0.5*cm))
        payment_info.append(Paragraph("Zahlungsbedingungen:", styles['Bold']))
        payment_info.append(Paragraph(invoice.terms, styles['Normal']))
    
    for item in payment_info:
        elements.append(item)
    
    # Notizen
    if invoice.notes:
        elements.append(Spacer(1, 0.5*cm))
        elements.append(Paragraph("Hinweise:", styles['Bold']))
        elements.append(Paragraph(invoice.notes, styles['Normal']))
    
    # Fußzeile
    elements.append(Spacer(1, 1*cm))
    footer_data = [
        [
            Paragraph(company_data.company_name, styles['Normal']),
            Paragraph(f"Steuernummer: {company_data.tax_id}", styles['Normal']),
            Paragraph(f"USt-IdNr.: {company_data.vat_id}", styles['Normal'])
        ],
        [
            Paragraph(f"{company_data.street} {company_data.house_number}", styles['Normal']),
            Paragraph(f"Tel.: {company_data.phone}", styles['Normal']),
            Paragraph(f"Bank: {company_data.bank_name}", styles['Normal'])
        ],
        [
            Paragraph(f"{company_data.postal_code} {company_data.city}", styles['Normal']),
            Paragraph(f"E-Mail: {company_data.email}", styles['Normal']),
            Paragraph(f"IBAN: {company_data.iban}", styles['Normal'])
        ]
    ]
    
    footer_table = Table(footer_data, colWidths=[6*cm, 6*cm, 6*cm])
    footer_table.setStyle(TableStyle([
        ('TOPPADDING', (0, 0), (-1, -1), 0.1*cm),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0.1*cm),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
    ]))
    elements.append(footer_table)
    
    # PDF erstellen
    doc.build(elements)
    
    return output_path
