from odoo import models, fields


class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Represents the type of property that is listed.'
    _order = "sequence, name"

    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
    name = fields.Char(required=True)
    property_ids = fields.One2many('estate.property', 'property_type_id')

    # Constraints
    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)', 'A property type name must be unique')
    ]
