from marshmallow import Schema, fields, validate

class CustomerSchema(Schema):
    """
    Schema für die Validierung und Serialisierung von Kundendaten
    """
    customer_id = fields.Int(dump_only=True)
    company_name = fields.Str(allow_none=True)
    first_name = fields.Str(allow_none=True)
    last_name = fields.Str(allow_none=True)
    street = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    house_number = fields.Str(required=True, validate=validate.Length(min=1, max=20))
    postal_code = fields.Str(required=True, validate=validate.Length(min=1, max=20))
    city = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    country = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    tax_id = fields.Str(allow_none=True)
    vat_id = fields.Str(allow_none=True)
    email = fields.Email(allow_none=True)
    phone = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    is_active = fields.Bool(default=True)
    
    # Berechnete Felder
    full_name = fields.Str(dump_only=True)
    full_address = fields.Str(dump_only=True)

    class Meta:
        # Felder, die immer geladen werden sollen
        fields = (
            'customer_id', 'company_name', 'first_name', 'last_name', 
            'street', 'house_number', 'postal_code', 'city', 'country',
            'tax_id', 'vat_id', 'email', 'phone', 'created_at', 'updated_at',
            'is_active', 'full_name', 'full_address'
        )

# Instanzen des Schemas erstellen
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
