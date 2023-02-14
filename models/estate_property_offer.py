from dateutil.relativedelta import relativedelta
from odoo import models, fields, api


class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'An amount a potential buyer offers to the seller for a property.'

    price = fields.Float()
    status = fields.Selection(
        copy=False,
        selection=[
            ('accepted', 'Accepted'),
            ('refused', 'Refused')
        ],
    )
    partner_id = fields.Many2one('res.partner', required=True, string='Partner')
    property_id = fields.Many2one('estate.property', required=True, string='Property')

    # Deadline
    create_date = fields.Datetime()
    validity = fields.Integer(string='Validity (days)', default=7)

    @api.depends('validity')
    def _compute_deadline(self):
        for record in self:
            # Fallback to fields.Datetime.now() if record hasn't been created
            # Displayed incorrect date and validity before adjusting to timezone
            start_datetime = record.create_date if record.create_date else fields.Datetime.now()
            end_datetime = start_datetime + relativedelta(days=record.validity)
            timezone_adjusted_datetime = fields.Datetime.context_timestamp(record, end_datetime)
            record.date_deadline = fields.Date.to_date(timezone_adjusted_datetime)

    def _inverse_deadline(self):
        for record in self:
            start_datetime = fields.Datetime.context_timestamp(record, record.create_date)
            start_date = fields.Date.to_date(start_datetime)
            record.validity = relativedelta(record.date_deadline, start_date).days

    # create_date (Datetime) and date_deadline (Date) are different types and need to be converted.
    date_deadline = fields.Date(
        string='Deadline',
        compute='_compute_deadline',
        inverse='_inverse_deadline'
    )
