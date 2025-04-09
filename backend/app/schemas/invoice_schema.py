from marshmallow import Schema, fields, validate

class InvoiceItemSchema(Schema):
    """
    Schema für die Validierung und Serialisierung von Rechnungspositionen
    """
    invoice_item_id = fields.Int(dump_only=True)
    invoice_id = fields.Int(required=True)
    item_id = fields.Int(allow_none=True)
    position = fields.Int(required=True)
    quantity = fields.Decimal(required=True, places=2)
    unit = fields.Str(default='Stück')
    price_net = fields.Decimal(required=True, places=2)
    vat_rate = fields.Decimal(required=True, places=2, default=19.0)
    total_net = fields.Decimal(dump_only=True, places=2)
    total_vat = fields.Decimal(dump_only=True, places=2)
    total_gross = fields.Decimal(dump_only=True, places=2)
    description = fields.Str(allow_none=True)

    class Meta:
        fields = (
            'invoice_item_id', 'invoice_id', 'item_id', 'position', 'quantity',
            'unit', 'price_net', 'vat_rate', 'total_net', 'total_vat',
            'total_gross', 'description'
        )

class InvoiceSchema(Schema):
    """
    Schema für die Validierung und Serialisierung von Rechnungen
    """
    invoice_id = fields.Int(dump_only=True)
    invoice_number = fields.Str(required=True)
    customer_id = fields.Int(required=True)
    invoice_date = fields.Date(required=True)
    due_date = fields.Date(required=True)
    delivery_date = fields.Date(required=True)
    status = fields.Str(default='erstellt')
    payment_status = fields.Str(default='offen')
    payment_method = fields.Str(allow_none=True)
    total_net = fields.Decimal(dump_only=True, places=2)
    total_vat = fields.Decimal(dump_only=True, places=2)
    total_gross = fields.Decimal(dump_only=True, places=2)
    notes = fields.Str(allow_none=True)
    terms = fields.Str(allow_none=True)
    is_cancelled = fields.Bool(default=False)
    cancellation_date = fields.Date(allow_none=True)
    cancellation_reason = fields.Str(allow_none=True)
    original_invoice_id = fields.Int(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    is_recurring = fields.Bool(default=False)
    email_sent = fields.Bool(default=False)
    email_sent_date = fields.DateTime(allow_none=True)
    
    # Verschachtelte Beziehungen
    items = fields.List(fields.Nested(InvoiceItemSchema), dump_only=True)
    customer = fields.Nested('CustomerSchema', dump_only=True, only=('customer_id', 'company_name', 'first_name', 'last_name', 'full_name', 'full_address'))

    class Meta:
        fields = (
            'invoice_id', 'invoice_number', 'customer_id', 'invoice_date',
            'due_date', 'delivery_date', 'status', 'payment_status',
            'payment_method', 'total_net', 'total_vat', 'total_gross',
            'notes', 'terms', 'is_cancelled', 'cancellation_date',
            'cancellation_reason', 'original_invoice_id', 'created_at',
            'updated_at', 'is_recurring', 'email_sent', 'email_sent_date',
            'items', 'customer'
        )

# Instanzen der Schemas erstellen
invoice_item_schema = InvoiceItemSchema()
invoice_items_schema = InvoiceItemSchema(many=True)
invoice_schema = InvoiceSchema()
invoices_schema = InvoiceSchema(many=True)
