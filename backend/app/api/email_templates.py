from flask import Blueprint, request, jsonify
from app.models.email_template import EmailTemplate
from app.schemas.email_template_schema import email_template_schema, email_templates_schema
from app import db
from flask_jwt_extended import jwt_required

email_templates_bp = Blueprint('email_templates', __name__)

@email_templates_bp.route('', methods=['GET'])
@jwt_required()
def get_email_templates():
    """
    Gibt alle E-Mail-Vorlagen zurück
    """
    email_templates = EmailTemplate.query.all()
    return jsonify(email_templates_schema.dump(email_templates)), 200

@email_templates_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_email_template(id):
    """
    Gibt eine E-Mail-Vorlage anhand ihrer ID zurück
    """
    email_template = EmailTemplate.query.get_or_404(id)
    return jsonify(email_template_schema.dump(email_template)), 200

@email_templates_bp.route('/default', methods=['GET'])
@jwt_required()
def get_default_template():
    """
    Gibt die Standard-E-Mail-Vorlage zurück
    """
    default_template = EmailTemplate.query.filter_by(is_default=True).first()
    if not default_template:
        return jsonify({"error": "Keine Standard-Vorlage gefunden"}), 404
    
    return jsonify(email_template_schema.dump(default_template)), 200

@email_templates_bp.route('', methods=['POST'])
@jwt_required()
def create_email_template():
    """
    Erstellt eine neue E-Mail-Vorlage
    """
    data = request.get_json()
    
    # Validiere die Daten mit dem Schema
    errors = email_template_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    # Wenn diese Vorlage als Standard gesetzt werden soll, setze alle anderen auf nicht-Standard
    if data.get('is_default', False):
        EmailTemplate.query.filter_by(is_default=True).update({'is_default': False})
    
    # Erstelle neue E-Mail-Vorlage
    new_template = EmailTemplate(
        name=data.get('name'),
        subject=data.get('subject'),
        body=data.get('body'),
        is_default=data.get('is_default', False)
    )
    
    db.session.add(new_template)
    db.session.commit()
    
    return jsonify(email_template_schema.dump(new_template)), 201

@email_templates_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_email_template(id):
    """
    Aktualisiert eine bestehende E-Mail-Vorlage
    """
    template = EmailTemplate.query.get_or_404(id)
    data = request.get_json()
    
    # Validiere die Daten mit dem Schema
    errors = email_template_schema.validate(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    # Wenn diese Vorlage als Standard gesetzt werden soll, setze alle anderen auf nicht-Standard
    if data.get('is_default', False) and not template.is_default:
        EmailTemplate.query.filter_by(is_default=True).update({'is_default': False})
    
    # Aktualisiere Vorlagendaten
    template.name = data.get('name', template.name)
    template.subject = data.get('subject', template.subject)
    template.body = data.get('body', template.body)
    template.is_default = data.get('is_default', template.is_default)
    
    db.session.commit()
    
    return jsonify(email_template_schema.dump(template)), 200

@email_templates_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_email_template(id):
    """
    Löscht eine E-Mail-Vorlage
    """
    template = EmailTemplate.query.get_or_404(id)
    
    # Verhindere das Löschen der Standard-Vorlage
    if template.is_default:
        return jsonify({"error": "Die Standard-Vorlage kann nicht gelöscht werden"}), 400
    
    db.session.delete(template)
    db.session.commit()
    
    return jsonify({"message": "E-Mail-Vorlage erfolgreich gelöscht"}), 200

@email_templates_bp.route('/<int:id>/set-default', methods=['PUT'])
@jwt_required()
def set_default_template(id):
    """
    Setzt eine E-Mail-Vorlage als Standard
    """
    template = EmailTemplate.query.get_or_404(id)
    
    # Setze alle Vorlagen auf nicht-Standard
    EmailTemplate.query.filter_by(is_default=True).update({'is_default': False})
    
    # Setze diese Vorlage als Standard
    template.is_default = True
    db.session.commit()
    
    return jsonify({
        "message": f"Vorlage '{template.name}' wurde als Standard gesetzt",
        "template": email_template_schema.dump(template)
    }), 200
