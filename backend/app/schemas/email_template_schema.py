from marshmallow import Schema, fields, validate

class EmailTemplateSchema(Schema):
    """
    Schema für die Validierung und Serialisierung von E-Mail-Vorlagen
    """
    template_id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    subject = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    body = fields.Str(required=True)
    is_default = fields.Bool(default=False)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    class Meta:
        fields = (
            'template_id', 'name', 'subject', 'body', 'is_default',
            'created_at', 'updated_at'
        )

class EmailLogSchema(Schema):
    """
    Schema für die Validierung und Serialisierung von E-Mail-Protokolleinträgen
    """
    log_id = fields.Int(dump_only=True)
    invoice_id = fields.Int(allow_none=True)
    customer_id = fields.Int(allow_none=True)
    template_id = fields.Int(allow_none=True)
    sent_date = fields.DateTime(dump_only=True)
    recipient = fields.Email(required=True)
    subject = fields.Str(required=True)
    body = fields.Str(required=True)
    status = fields.Str(dump_only=True)
    error_message = fields.Str(dump_only=True, allow_none=True)

    class Meta:
        fields = (
            'log_id', 'invoice_id', 'customer_id', 'template_id',
            'sent_date', 'recipient', 'subject', 'body', 'status',
            'error_message'
        )

# Instanzen der Schemas erstellen
email_template_schema = EmailTemplateSchema()
email_templates_schema = EmailTemplateSchema(many=True)
email_log_schema = EmailLogSchema()
email_logs_schema = EmailLogSchema(many=True)
