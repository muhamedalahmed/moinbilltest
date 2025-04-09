from marshmallow import Schema, fields, validate

class ItemSchema(Schema):
    """
    Schema für die Validierung und Serialisierung von Artikel-/Leistungsdaten
    """
    item_id = fields.Int(dump_only=True)
    item_number = fields.Str(allow_none=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    description = fields.Str(allow_none=True)
    unit = fields.Str(default='Stück')
    price_net = fields.Decimal(required=True, places=2)
    vat_rate = fields.Decimal(required=True, places=2, default=19.0)
    is_active = fields.Bool(default=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Berechnete Felder
    price_gross = fields.Decimal(dump_only=True, places=2)
    vat_amount = fields.Decimal(dump_only=True, places=2)

    class Meta:
        # Felder, die immer geladen werden sollen
        fields = (
            'item_id', 'item_number', 'name', 'description', 'unit',
            'price_net', 'vat_rate', 'is_active', 'created_at', 'updated_at',
            'price_gross', 'vat_amount'
        )

# Instanzen des Schemas erstellen
item_schema = ItemSchema()
items_schema = ItemSchema(many=True)
