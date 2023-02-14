from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api


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

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = ''

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    total_area = fields.Integer(string='Total Area (sqm)', compute='_compute_total_area')

    # Other Info
    salesperson_id = fields.Many2one('res.users', default=lambda self: self.env.user, string='Salesman')
    buyer_id = fields.Many2one('res.partner', string='Buyer', copy=False)

    # Offers
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string='Offers')

    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for record in self:
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped('price'))
                continue
            record.best_price = 0

    best_price = fields.Float(string='Best Offer', compute='_compute_best_price')

    # Additional
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
