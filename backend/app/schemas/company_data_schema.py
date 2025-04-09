from marshmallow import Schema, fields, validate

class CompanyDataSchema(Schema):
    """
    Schema für die Validierung und Serialisierung von Unternehmensdaten
    """
    company_id = fields.Int(dump_only=True)
    company_name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    legal_form = fields.Str(allow_none=True)
    street = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    house_number = fields.Str(required=True, validate=validate.Length(min=1, max=20))
    postal_code = fields.Str(required=True, validate=validate.Length(min=1, max=20))
    city = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    country = fields.Str(default='Deutschland')
    tax_id = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    vat_id = fields.Str(allow_none=True)
    email = fields.Email(allow_none=True)
    phone = fields.Str(allow_none=True)
    website = fields.Str(allow_none=True)
    bank_name = fields.Str(allow_none=True)
    iban = fields.Str(allow_none=True)
    bic = fields.Str(allow_none=True)
    logo_path = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Berechnete Felder
    full_address = fields.Str(dump_only=True)

    class Meta:
        fields = (
            'company_id', 'company_name', 'legal_form', 'street', 'house_number',
            'postal_code', 'city', 'country', 'tax_id', 'vat_id', 'email',
            'phone', 'website', 'bank_name', 'iban', 'bic', 'logo_path',
            'created_at', 'updated_at', 'full_address'
        )

# Instanzen des Schemas erstellen
company_data_schema = CompanyDataSchema()
