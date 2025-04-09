from marshmallow import Schema, fields, validate

class RecurringInvoiceItemSchema(Schema):
    """
    Schema für die Validierung und Serialisierung von Intervallrechnungspositionen
    """
    recurring_item_id = fields.Int(dump_only=True)
    recurring_id = fields.Int(required=True)
    item_id = fields.Int(allow_none=True)
    position = fields.Int(required=True)
    quantity = fields.Decimal(required=True, places=2)
    unit = fields.Str(default='Stück')
    price_net = fields.Decimal(required=True, places=2)
    vat_rate = fields.Decimal(required=True, places=2, default=19.0)
    description = fields.Str(allow_none=True)

    class Meta:
        fields = (
            'recurring_item_id', 'recurring_id', 'item_id', 'position', 'quantity',
            'unit', 'price_net', 'vat_rate', 'description'
        )

class RecurringInvoiceSchema(Schema):
    """
    Schema für die Validierung und Serialisierung von Intervallrechnungen
    """
    recurring_id = fields.Int(dump_only=True)
    customer_id = fields.Int(required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(allow_none=True)
    interval_type = fields.Str(required=True, validate=validate.OneOf(['monatlich', 'quartalsweise', 'halbjährlich', 'jährlich']))
    interval_value = fields.Int(default=1)
    next_invoice_date = fields.Date(required=True)
    last_invoice_date = fields.Date(allow_none=True)
    status = fields.Str(default='aktiv', validate=validate.OneOf(['aktiv', 'pausiert', 'beendet']))
    notes = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Verschachtelte Beziehungen
    items = fields.List(fields.Nested(RecurringInvoiceItemSchema), dump_only=True)
    customer = fields.Nested('CustomerSchema', dump_only=True, only=('customer_id', 'company_name', 'first_name', 'last_name', 'full_name', 'full_address'))

    class Meta:
        fields = (
            'recurring_id', 'customer_id', 'start_date', 'end_date',
            'interval_type', 'interval_value', 'next_invoice_date',
            'last_invoice_date', 'status', 'notes', 'created_at',
            'updated_at', 'items', 'customer'
        )

# Instanzen der Schemas erstellen
recurring_invoice_item_schema = RecurringInvoiceItemSchema()
recurring_invoice_items_schema = RecurringInvoiceItemSchema(many=True)
recurring_invoice_schema = RecurringInvoiceSchema()
recurring_invoices_schema = RecurringInvoiceSchema(many=True)
