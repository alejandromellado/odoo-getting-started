from odoo import models, fields


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
