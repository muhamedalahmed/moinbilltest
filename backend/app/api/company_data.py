from flask import Blueprint, request, jsonify
from app.models.company_data import CompanyData
from app.schemas.company_data_schema import company_data_schema
from app import db
from flask_jwt_extended import jwt_required
import os

company_data_bp = Blueprint('company_data', __name__)

@company_data_bp.route('', methods=['GET'])
@jwt_required()
def get_company_data():
    """
    Gibt die Unternehmensdaten zurück
    """
    company_data = CompanyData.query.first()
    if not company_data:
        return jsonify({"message": "Keine Unternehmensdaten gefunden"}), 404
    
    return jsonify(company_data_schema.dump(company_data)), 200

@company_data_bp.route('', methods=['POST'])
@jwt_required()
def create_company_data():
    """
    Erstellt neue Unternehmensdaten
    """
    # Prüfe, ob bereits Unternehmensdaten existieren
    existing_data = CompanyData.query.first()
    if existing_data:
        return jsonify({"error": "Unternehmensdaten existieren bereits. Verwenden Sie PUT zum Aktualisieren."}), 400
    
    data = request.get_json()
    
    # Validiere die Daten mit dem Schema
    errors = company_data_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    # Erstelle neue Unternehmensdaten
    new_company_data = CompanyData(
        company_name=data.get('company_name'),
        legal_form=data.get('legal_form'),
        street=data.get('street'),
        house_number=data.get('house_number'),
        postal_code=data.get('postal_code'),
        city=data.get('city'),
        country=data.get('country', 'Deutschland'),
        tax_id=data.get('tax_id'),
        vat_id=data.get('vat_id'),
        email=data.get('email'),
        phone=data.get('phone'),
        website=data.get('website'),
        bank_name=data.get('bank_name'),
        iban=data.get('iban'),
        bic=data.get('bic'),
        logo_path=data.get('logo_path')
    )
    
    db.session.add(new_company_data)
    db.session.commit()
    
    return jsonify(company_data_schema.dump(new_company_data)), 201

@company_data_bp.route('', methods=['PUT'])
@jwt_required()
def update_company_data():
    """
    Aktualisiert die Unternehmensdaten
    """
    company_data = CompanyData.query.first()
    if not company_data:
        return jsonify({"error": "Keine Unternehmensdaten gefunden. Verwenden Sie POST zum Erstellen."}), 404
    
    data = request.get_json()
    
    # Validiere die Daten mit dem Schema
    errors = company_data_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    # Aktualisiere Unternehmensdaten
    company_data.company_name = data.get('company_name', company_data.company_name)
    company_data.legal_form = data.get('legal_form', company_data.legal_form)
    company_data.street = data.get('street', company_data.street)
    company_data.house_number = data.get('house_number', company_data.house_number)
    company_data.postal_code = data.get('postal_code', company_data.postal_code)
    company_data.city = data.get('city', company_data.city)
    company_data.country = data.get('country', company_data.country)
    company_data.tax_id = data.get('tax_id', company_data.tax_id)
    company_data.vat_id = data.get('vat_id', company_data.vat_id)
    company_data.email = data.get('email', company_data.email)
    company_data.phone = data.get('phone', company_data.phone)
    company_data.website = data.get('website', company_data.website)
    company_data.bank_name = data.get('bank_name', company_data.bank_name)
    company_data.iban = data.get('iban', company_data.iban)
    company_data.bic = data.get('bic', company_data.bic)
    
    # Aktualisiere Logo-Pfad, falls angegeben
    if 'logo_path' in data:
        # Wenn ein neues Logo hochgeladen wurde, lösche das alte Logo
        if company_data.logo_path and os.path.exists(company_data.logo_path) and company_data.logo_path != data.get('logo_path'):
            try:
                os.remove(company_data.logo_path)
            except:
                pass  # Ignoriere Fehler beim Löschen
        
        company_data.logo_path = data.get('logo_path')
    
    db.session.commit()
    
    return jsonify(company_data_schema.dump(company_data)), 200

@company_data_bp.route('/logo', methods=['POST'])
@jwt_required()
def upload_logo():
    """
    Lädt ein Firmenlogo hoch
    """
    if 'logo' not in request.files:
        return jsonify({"error": "Keine Datei übermittelt"}), 400
    
    file = request.files['logo']
    
    if file.filename == '':
        return jsonify({"error": "Keine Datei ausgewählt"}), 400
    
    # Prüfe Dateityp
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify({"error": "Ungültiger Dateityp. Erlaubt sind: png, jpg, jpeg, gif"}), 400
    
    # Erstelle Verzeichnis, falls es nicht existiert
    upload_dir = os.path.join(os.getcwd(), 'uploads', 'logos')
    os.makedirs(upload_dir, exist_ok=True)
    
    # Speichere Datei
    filename = f"company_logo.{file.filename.rsplit('.', 1)[1].lower()}"
    file_path = os.path.join(upload_dir, filename)
    file.save(file_path)
    
    # Aktualisiere Unternehmensdaten
    company_data = CompanyData.query.first()
    if company_data:
        # Lösche altes Logo, falls vorhanden
        if company_data.logo_path and os.path.exists(company_data.logo_path):
            try:
                os.remove(company_data.logo_path)
            except:
                pass  # Ignoriere Fehler beim Löschen
        
        company_data.logo_path = file_path
        db.session.commit()
    
    return jsonify({
        "message": "Logo erfolgreich hochgeladen",
        "logo_path": file_path
    }), 201
