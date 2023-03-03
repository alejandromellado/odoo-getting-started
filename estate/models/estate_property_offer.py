from dateutil.relativedelta import relativedelta
from odoo import _, models, fields, api
from odoo.exceptions import UserError


class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'An amount a potential buyer offers to the seller for a property.'
    _order = "price desc"

    # Lifecycle

    @api.model
    def create(self, vals):
        property_record = self.env["estate.property"].browse(vals["property_id"])
        if property_record.state == 'sold':
            raise UserError(_('You cannot create an offer for a sold property.'))
        if fields.float_compare(vals['price'], property_record.best_price, precision_digits=2) < 0:
            raise UserError(f"The offer must be higher than {property_record.best_price}")
        if property_record.state == "new":
            property_record.state = "offer_received"
        return super().create(vals)

    # Status
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
    property_type_id = fields.Many2one(related='property_id.property_type_id', store=True)

    def action_accept_offer(self):
        for record in self:
            property_record = record.property_id
            if property_record.state in ['offer_accepted', 'sold']:
                raise UserError(_('An offer has already been accepted.'))

            # Update related property listing
            property_record.selling_price = record.price
            property_record.buyer_id = record.partner_id
            property_record.state = 'offer_accepted'

            record.status = 'accepted'
        return True

    def action_refuse_offer(self):
        for record in self:
            record.status = 'refused'
        return True

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

    # Constraints
    _sql_constraints = [
        ('check_price', 'CHECK(price > 0)', 'An offer price must be strictly positive'),
    ]
