from datetime import date
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
            start = fields.Date.today() if not record.create_date else record.create_date
            record.date_deadline = start + relativedelta(days=+record.validity)

    def _inverse_deadline(self):
        for record in self:
            start = fields.Date.to_date(record.create_date)
            diff = relativedelta(record.date_deadline, start)
            record.validity = diff.days

    date_deadline = fields.Date(
        string='Deadline',
        compute='_compute_deadline',
        inverse='_inverse_deadline'
    )
