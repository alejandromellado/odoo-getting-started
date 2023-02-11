from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import models, fields


class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'An estate property listing.'

    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    property_type_id = fields.Many2one('estate.property.type', string='Property Type')
    name = fields.Char(required=True, string='Title')
    postcode = fields.Char()
    date_availability = fields.Date(
        string='Available From',
        copy=False,
        default=lambda self: date.today() + relativedelta(months=+3)
    )
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)

    # Description
    description = fields.Text()
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer(string='Living Area (sqm)')
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer(string='Garden Area (sqm)')
    garden_orientation = fields.Selection(
        string='Garden Orientation',
        selection=[
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West'),
        ],
    )

    # Other Info
    salesperson_id = fields.Many2one('res.users', default=lambda self: self.env.user, string='Salesman')
    buyer_id = fields.Many2one('res.partner', string='Buyer', copy=False)

    # Offers
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string='Offers')

    active = fields.Boolean(default=True)
    state = fields.Selection(
        required=True,
        copy=False,
        selection=[
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('canceled', 'Canceled'),
        ],
        default='new',
    )
