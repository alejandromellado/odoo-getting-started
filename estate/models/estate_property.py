from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'An estate property listing.'
    _order = "id desc"

    # Lifecycle

    @api.ondelete(at_uninstall=False)
    def _unlink_if_new_or_cancelled(self):
        for record in self:
            if record.state not in ["new", "canceled"]:
                raise UserError("Only new or canceled records can be deleted.")

    # Attributes

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

    def action_cancel_property(self):
        for record in self:
            if record.state == 'sold':
                raise UserError('A sold property cannot be canceled.')
            record.state = 'canceled'
        return True

    def action_sold_property(self):
        for record in self:
            if record.state != 'offer_accepted':
                message = 'Canceled properties cannot be sold.' if record.state == 'canceled' \
                    else 'You cannot sell a property without an accepted offer.'
                raise UserError(message)

            record.state = 'sold'
        return True

    # Constraints
    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price > 0)', 'A property expected price must be strictly positive'),
        ('check_selling_price', 'CHECK(selling_price >= 0)', 'A property selling price must be positive'),
    ]

    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price(self):
        for record in self:
            if fields.float_is_zero(record.selling_price, precision_digits=2):
                # No offer has been accepted yet
                continue
            if fields.float_compare(record.selling_price, record.expected_price * .90, precision_digits=2) < 0:
                if record.state == 'offer_accepted':
                    message = 'The selling price must be at least 90% of the expected price!'
                else:
                    message = 'The selling price must be at least 90% of the expected price!,' \
                              ' you must reduce the expected price if you want to accept this offer.'
                raise ValidationError(message)
